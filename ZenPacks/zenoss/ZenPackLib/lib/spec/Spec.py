##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import inspect
import os
import sys
import imp
import importlib
import operator
import re
import logging
from collections import OrderedDict

from Products import Zuul
from Products.Zuul import marshal
from Products.Zuul.infos import ProxyProperty
from Products.ZenRelations import ToOneRelationship, ToManyRelationship
from zope.interface.interface import InterfaceClass
from Products.Zuul.interfaces import IInfo

from ..helpers.ZenPackLibLog import DEFAULTLOG


def MethodInfoProperty(method_name, entity=False):
    """Return a property with the Infos for object(s) returned by a method.

    A list of Info objects is returned for methods returning a list, or a single
    one for those returning a single value.
    """
    def getter(self):
        try:
            result = Zuul.info(getattr(self._object, method_name)())
        except TypeError:
            # If not callable avoid the traceback and send the property
            result = Zuul.info(getattr(self._object, method_name))
        if entity:
            # rather than returning entire object(s), return just
            # the fields needed by the UI renderer for creating links.
            return marshal(
                result,
                keys=('name', 'meta_type', 'class_label', 'uid'))
        else:
            return result

    return property(getter)

def EnumInfoProperty(data, enum):
    """Return a property filtered via an enum."""
    def getter(self, data, enum):
        if not enum:
            return ProxyProperty(data)
        else:
            data = getattr(self._object, data, None)
            try:
                data = int(data)
                return Zuul.info(enum[data])
            except Exception:
                return Zuul.info(data)

    return property(lambda x: getter(x, data, enum))

def DeviceInfoStatusProperty():
    """Return property for DeviceBaseInfo.status."""
    def getter(self):
        status = self._object.getStatus()
        return None if status is None else status < 1

    return property(getter)

def RelationshipGetter(relationship_name):
    """Return getter for id or ids in relationship_name."""
    def getter(self):
        try:
            relationship = getattr(self, relationship_name)
            if isinstance(relationship, ToManyRelationship):
                return self.getIdsInRelationship(getattr(self, relationship_name))
            elif isinstance(relationship, ToOneRelationship):
                return self.getIdForRelationship(relationship)
        except Exception:
            DEFAULTLOG.error(
                "error getting {} ids for {}".format(
                relationship_name, self.getPrimaryUrlPath()))
            raise

    return getter

def RelationshipSetter(relationship_name):
    """Return setter for id or ides in relationship_name."""
    def setter(self, id_or_ids):
        try:
            relationship = getattr(self, relationship_name)
            if isinstance(relationship, ToManyRelationship):
                self.setIdsInRelationship(relationship, id_or_ids)
            elif isinstance(relationship, ToOneRelationship):
                self.setIdForRelationship(relationship, id_or_ids)
        except Exception:
            DEFAULTLOG.error(
                "error setting {} ids for {}".format(
                relationship_name, self.getPrimaryUrlPath()))
            raise

    return setter

def RelationshipInfoProperty(relationship_name):
    """Return a property with the Infos for object(s) in the relationship.

    A list of Info objects is returned for ToMany relationships, and a
    single Info object is returned for ToOne relationships.

    """
    def getter(self):
        # rather than returning entire object(s), return just the fields
        # required by the UI renderer for creating links.
        return marshal(
            Zuul.info(getattr(self._object, relationship_name)()),
            keys=('name', 'meta_type', 'class_label', 'uid'))

    return property(getter)

def RelationshipLengthProperty(relationship_name):
    """Return a property representing number of objects in relationship."""
    def getter(self):
        relationship = getattr(self._object, relationship_name)
        try:
            return relationship.countObjects()
        except Exception:
            return len(relationship())

    return property(getter)


class Spec(object):
    """Abstract base class for specifications."""

    source_location = None
    speclog = None

    LOG = DEFAULTLOG

    def __init__(self, _source_location=None, zplog=None):
        if zplog:
            self.LOG = zplog

        class LogAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                return '{} {}'.format(self.extra['context'], msg), kwargs

        self.source_location = _source_location
        self.speclog = LogAdapter(self.LOG, {'context': self})

    def __str__(self):
        parts = []

        if self.source_location:
            parts.append(self.source_location)
        if hasattr(self, 'name') and self.name:
            if callable(self.name):
                parts.append(self.name())
            else:
                parts.append(self.name)
        else:
            parts.append(super(Spec, self).__str__())

        return "{}({})".format(self.__class__.__name__, ' - '.join(parts))

    def apply_data_defaults(self, dictionary, default_defaults=None, leave_defaults=False):
        """Modify dictionary to put values from DEFAULTS key into other keys.
    
        Unless leave_defaults is set to True, the DEFAULTS key will no longer exist
        in dictionary. dictionary must be a dictionary of dictionaries.
    
        Example usage:
    
            >>> mydict = {
            ...     'DEFAULTS': {'is_two': False},
            ...     'key1': {'number': 1},
            ...     'key2': {'number': 2, 'is_two': True},
            ... }
            >>> apply_defaults(mydict)
            >>> print mydict
            {
                'key1': {'number': 1, 'is_two': False},
                'key2': {'number': 2, 'is_two': True},
            }
    
        """
        if default_defaults:
            dictionary.setdefault('DEFAULTS', {})
            for default_key, default_value in default_defaults.iteritems():
                dictionary['DEFAULTS'].setdefault(default_key, default_value)

        if 'DEFAULTS' in dictionary:
            if leave_defaults:
                defaults = dictionary.get('DEFAULTS')
            else:
                defaults = dictionary.pop('DEFAULTS')
            for k, v in dictionary.iteritems():
                dictionary[k] = dict(defaults, **v)
                if 'extra_params' in dictionary[k].keys():
                    extra_params = defaults.get('extra_params',{})
                    dictionary_params = dictionary[k]['extra_params']
                    for i, j in extra_params.items():
                        if i not in dictionary_params.keys():
                            dictionary_params[i] = j

    def specs_from_param(self, spec_type, param_name, param_dict, apply_defaults=True, leave_defaults=False, zplog=DEFAULTLOG):
        """Return a normalized dictionary of spec_type instances."""
        if param_dict is None:
            param_dict = OrderedDict()
        elif not isinstance(param_dict, dict):
            raise TypeError(
                "{!r} argument must be dict or None, not {!r}"
                .format(
                    '{}.{}'.format(spec_type.__name__, param_name),
                    type(param_dict).__name__))
        else:
            if apply_defaults:
                self.apply_data_defaults(param_dict, leave_defaults=leave_defaults)

        specs = OrderedDict()
        keys = param_dict.keys()
        keys.sort()
        for k in keys:
            v = param_dict.get(k)
            args = self.fix_kwargs(v)
            args['zplog'] = zplog
            specs[k] = spec_type(self, k, **(args))

        return specs

    @classmethod
    def init_params(cls):
        """Return a dictionary describing the parameters accepted by __init__"""

        argspec = inspect.getargspec(cls.__init__)
        if argspec.defaults:
            defaults = dict(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
        else:
            defaults = {}

        params = OrderedDict()
        for op, param, value in re.findall(
            "^\s*:(type|param|yaml_param|yaml_block_style)\s+(\S+):\s*(.*)$",
            cls.__init__.__doc__,
            flags=re.MULTILINE
        ):
            if param not in params:
                params[param] = {'description': None,
                                 'type': None,
                                 'yaml_param': param,
                                 'yaml_block_style': False}
                if param in defaults:
                    params[param]['default'] = defaults[param]

            if op == 'type':
                params[param]['type'] = value

                if 'default' not in params[param] or \
                   params[param]['default'] is None:
                    # For certain types, we know that None doesn't really mean
                    # None.
                    if params[param]['type'].startswith("dict"):
                        params[param]['default'] = {}
                    elif params[param]['type'].startswith("list"):
                        params[param]['default'] = []
                    elif params[param]['type'].startswith("SpecsParameter("):
                        params[param]['default'] = {}
            elif op == 'yaml_param':
                params[param]['yaml_param'] = value
            elif op == 'yaml_block_style':
                params[param]['yaml_block_style'] = bool(value)
            else:
                params[param]['description'] = value

        return params

    def __eq__(self, other, ignore_params=[]):
        if type(self) != type(other):
            return False

        params = self.init_params()
        for p in params:
            if p in ignore_params:
                continue

            default_p = '_{}_defaultvalue'.format(p)
            self_val = getattr(self, p)
            other_val = getattr(other, p)
            self_val_or_default = self_val or getattr(self, default_p, None)
            other_val_or_default = other_val or getattr(other, default_p, None)

            # Order doesn't matter, for purposes of comparison.  Cast it away.
            if isinstance(self_val, OrderedDict):
                self_val = dict(self_val)

            if isinstance(other_val, OrderedDict):
                other_val = dict(other_val)

            if isinstance(self_val_or_default, OrderedDict):
                self_val_or_default = dict(self_val_or_default)

            if isinstance(other_val_or_default, OrderedDict):
                other_val_or_default = dict(other_val_or_default)

            if self_val == other_val:
                continue

            if self_val_or_default != other_val_or_default:
                self.LOG.debug("Comparing {} to {}, parameter {} does not match ({} != {})".format(
                          self, other, p, self_val_or_default, other_val_or_default))
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def create_class(self, module, schema_module, classname, bases, attributes):
        """Create and return described class."""
        if isinstance(module, basestring):
            module = self.create_module(module)
    
        schema_class = self.create_schema_class(
            schema_module, classname, bases, attributes)
    
        return self.create_stub_class(module, schema_class, classname)

    def create_schema_class(self, schema_module, classname, bases, attributes):
        """Create and return described schema class."""
        if isinstance(schema_module, basestring):
            schema_module = self.create_module(schema_module)

        schema_class = getattr(schema_module, classname, None)
        if schema_class:
            return schema_class

        class_factory = self.get_class_factory(bases[0])
        schema_class = class_factory(classname, tuple(bases), attributes)
        schema_class.__module__ = schema_module.__name__
        setattr(schema_module, classname, schema_class)

        return schema_class

    def create_stub_class(self, module, schema_class, classname):
        """Create and return described stub class."""
        if isinstance(module, basestring):
            module = self.create_module(module)

        concrete_class = getattr(module, classname, None)
        if concrete_class:
            return concrete_class

        class_factory = self.get_class_factory(schema_class)

        stub_class = class_factory(classname, (schema_class,), {})

        stub_class.__module__ = module.__name__

        setattr(module, classname, stub_class)

        return stub_class

    def get_class_factory(self, klass):
        """Return class factory for class."""
        if issubclass(klass, IInfo):
            return InterfaceClass
        else:
            return type
