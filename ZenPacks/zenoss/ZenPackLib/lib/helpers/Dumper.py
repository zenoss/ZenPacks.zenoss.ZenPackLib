##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import yaml
import re
from yaml.representer import SafeRepresenter
from collections import OrderedDict
from .ZenPackLibLog import DEFAULTLOG


def get_zproperty_type(z_type):
    """
        For zproperties, the actual data type of a default value
        depends on the defined type of the zProperty.
    """
    map = {'boolean': 'bool',
           'int': 'int',
           'float': 'float',
           'string': 'str',
           'password': 'str',
           'lines': 'list(str)'
    }
    return map.get(z_type, 'str')


class Dumper(yaml.Dumper):
    """
        These subclasses exist so that each copy of zenpacklib installed on a
        zenoss system provide their own loader (for add_constructor and yaml.load)
        and its own dumper (for add_representer) so that the proper methods will
        be used for this specific zenpacklib.
    """

    LOG = DEFAULTLOG

    def dict_representer(self, data):
        return yaml.MappingNode(u'tag:yaml.org,2002:map', data.items())

    def get_representation(self, value, v_type):
        ''''''
        if v_type.startswith("dict"):
            return self.represent_dict(value)
        elif v_type.startswith('list'):
            if 'ExtraPath' in v_type:
                # Represent this as a list of lists of quoted strings (each on one line).
                paths = []
                for path in list(value):
                    # Force the regular expressions to be quoted, so we don't have any issues with that.
                    pathnodes = [self.represent_scalar(u'tag:yaml.org,2002:str', x, style="'") for x in path]
                    paths.append(yaml.SequenceNode(u'tag:yaml.org,2002:seq', pathnodes, flow_style=True))
                return yaml.SequenceNode(u'tag:yaml.org,2002:seq', paths, flow_style=False)
            elif 'class' in v_type:
                # The "class" in this context is either a class reference or
                # a class name (string) that refers to a class defined in
                # this ZenPackSpec.
                classes = [isinstance(x, type) and self.class_to_str(x) or x for x in value]
                return self.represent_list(classes)
            else:
                return self.represent_list(value)
        else:
            m = re.match('^SpecsParameter\((.*)\)$', v_type)
            if m:
                spectype = m.group(1)
                specmapping = OrderedDict()
                defaults = value.get('DEFAULTS', None)
                if defaults:
                    value.pop('DEFAULTS')
                for key, spec in value.items():
                    if type(spec).__name__ != spectype:
                        raise yaml.representer.RepresenterError(
                            "Unable to serialize {} object ({}):  Expected an object of type {}".format(
                            type(spec).__name__, key, spectype))
                    else:
                        specmapping[self.represent_str(key)] = self.represent_spec(spec, defaults=defaults)
                return self.dict_representer(specmapping)

            else:
                self.LOG.debug("Using represent_data for {} ({})".format(value, v_type))
                return self.represent_data(value)
        return None

    def represent_relschemaspec(self, data):
        """
        Generic representer for serializing relation specs to YAML.
        """
        return self.represent_str(self.relschemaspec_to_str(data))

    def represent_zenpackspec(self, obj):
        """
        Generic representer for serializing ZenPack specs to YAML.
        """
        return self.represent_spec(obj, yaml_tag=u'!ZenPackSpec')

    def represent_spec(self, obj, yaml_tag=u'tag:yaml.org,2002:map', defaults=None):
        """
        Generic representer for serializing specs to YAML.  Rather than using
        the default PyYAML representer for python objects, we very carefully
        build up the YAML according to the parameter definitions in the __init__
        of each spec class.  This same format is used by construct_spec (the YAML
        constructor) to ensure that the spec objects are built consistently,
        whether it is done via YAML or the API.
        """
        from ..spec.RRDDatapointSpec import RRDDatapointSpec
        cls = obj.__class__
        if isinstance(obj, RRDDatapointSpec) and obj.shorthand and obj.use_shorthand():
            # Special case- we allow for a shorthand in specifying datapoints
            # as specs as strings rather than explicitly as a map.
            return self.represent_str(str(obj.shorthand))

        mapping = OrderedDict()

        param_defs = cls.init_params

        for p_name, p_data in param_defs.iteritems():
            # determine what type of object this is
            type_ = p_data.get('type')

            try:
                value = getattr(obj, p_name)
            except AttributeError:
                raise yaml.representer.RepresenterError(
                    "Unable to serialize {} object: {}, a supported parameter, is not accessible as a property.".format(
                    cls.__name__, p_name))
                continue

            # Figure out what the default value is.  First, consider the default
            # value for this parameter (globally):
            default_value = p_data.get('default', None)

            # Now, we need to handle 'DEFAULTS'.  If we're in a situation
            # where that is supported, and we're outputting a spec that
            # would be affected by it (not DEFAULTS itself, in other words),
            # then we look at the default value for this parameter, in case
            # it has changed the global default for this parameter.
            if hasattr(obj, 'name') and obj.name != 'DEFAULTS' and defaults is not None:
                default_value = getattr(defaults, p_name, default_value)

            # If the value is a default value, we can omit it from the export.
            if value == default_value:
                continue

            # If the value is null and the type is a list or dictionary, we can
            # assume it was some optional nested data and omit it.
            if value is None and (type_.startswith('dict') or type_.startswith('list') or type_.startswith('SpecsParameter')):
                continue

            if type_ == 'ZPropertyDefaultValue':
                # For zproperties, the actual data type of a default value
                # depends on the defined type of the zProperty.
                type_ = get_zproperty_type(obj.type_)

            yaml_param = self.represent_str(p_data.get('yaml_param'))
            try:
                if type_ == 'ExtraParams':
                    # ExtraParams is a special case, where any 'extra'
                    # parameters not otherwise defined in the init_params
                    # definition are tacked into a dictionary with no specific
                    # schema validation.  This is meant to be used in situations
                    # where it is impossible to know what parameters will be
                    # needed ahead of time, such as with a datasource
                    # that has been subclassed and had new properties added.
                    #
                    # Note: the extra parameters are required to have scalar
                    # values only.
                    for extra_param in value:
                        # add any values from an extraparams dict onto the spec's parameter list directly.
                        yaml_extra_param = self.represent_str(extra_param)
                        mapping[yaml_extra_param] = self.represent_data(value[extra_param])
                else:
                    mapping[yaml_param] = self.get_representation(value, type_)

            except yaml.representer.RepresenterError:
                raise
            except Exception, e:
                raise yaml.representer.RepresenterError(
                    "Unable to serialize {} object (param {}, type {}, value {}): {}".format(
                    cls.__name__, p_name, type_, value, e))

            if p_name in param_defs and p_data.get('yaml_block_style'):
                mapping[yaml_param].flow_style = False

        # Return a node describing the mapping (dictionary) of the params
        # used to build this spec.
        node = yaml.MappingNode(yaml_tag, mapping.items())
        return node

    def represent_ordereddict(self, data):
        value = []
        for item_key, item_value in data.items():
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            value.append((node_key, node_value))
        return yaml.MappingNode(u'tag:yaml.org,2002:map', value)

    def represent_severity(self, data):
        """represent Severity"""
        orig = getattr(data, 'orig')
        if orig is None:
            raise ValueError("'{}' is not a valid value for severity.".format(orig))
        else:
            if isinstance(orig, str):
                return self.represent_str(orig)
            elif isinstance(orig, int):
                return self.represent_int(orig)

    def represent_multiline(self, data):
        """Represent multi-line text"""
        for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
            if c in unicode(data):
                return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return self.represent_str(data)

    def relschemaspec_to_str(self, spec):
        # Omit relation names that are their defaults.
        left_optrelname = "" if spec.left_relname == spec.default_left_relname else "({})".format(spec.left_relname)
        right_optrelname = "" if spec.right_relname == spec.default_right_relname else "({})".format(spec.right_relname)

        return "{}{} {}:{} {}{}".format(
            spec.left_class,
            left_optrelname,
            spec.left_cardinality,
            spec.right_cardinality,
            right_optrelname,
            spec.right_class
        )

    def severity_to_str(self, value):
        '''
        Return string representation for severity given a numeric value.
        '''
        severity = {
            5: 'crit',
            4: 'err',
            3: 'warn',
            2: 'info',
            1: 'debug',
            0: 'clear'
            }.get(value, None)

        if severity is None:
            raise ValueError("'{}' is not a valid value for severity.".format(value))

        return severity

    def class_to_str(self, class_):
        return class_.__module__ + "." + class_.__name__


from ..spec.ZenPackSpec import ZenPackSpec
from ..spec.DeviceClassSpec import DeviceClassSpec
from ..spec.ZPropertySpec import ZPropertySpec
from ..spec.ClassSpec import ClassSpec
from ..spec.ClassPropertySpec import ClassPropertySpec
from ..spec.ClassRelationshipSpec import ClassRelationshipSpec
from ..spec.RelationshipSchemaSpec import RelationshipSchemaSpec

from ..params.ZenPackSpecParams import ZenPackSpecParams
from ..params.DeviceClassSpecParams import DeviceClassSpecParams
from ..params.EventClassSpecParams import EventClassSpecParams
from ..params.EventClassMappingSpecParams import EventClassMappingSpec
from ..params.ZPropertySpecParams import ZPropertySpecParams
from ..params.ClassSpecParams import ClassSpecParams
from ..params.ClassPropertySpecParams import ClassPropertySpecParams
from ..params.ClassRelationshipSpecParams import ClassRelationshipSpecParams
from ..params.RRDTemplateSpecParams import RRDTemplateSpecParams
from ..params.RRDThresholdSpecParams import RRDThresholdSpecParams
from ..params.RRDDatasourceSpecParams import RRDDatasourceSpecParams
from ..params.RRDDatapointSpecParams import RRDDatapointSpecParams
from ..params.GraphDefinitionSpecParams import GraphDefinitionSpecParams
from ..params.GraphPointSpecParams import GraphPointSpecParams
from ..params.ProcessClassSpecParams import ProcessClassSpecParams
from ..params.ProcessClassOrganizerSpecParams import ProcessClassOrganizerSpecParams
from ..params.ImpactTriggerSpecParams import ImpactTriggerSpecParams
from ..params.LinkProviderSpecParams import LinkProviderSpecParams

# Spec subclasses
Dumper.add_representer(ZenPackSpec, Dumper.represent_zenpackspec)
Dumper.add_representer(DeviceClassSpec, Dumper.represent_spec)
Dumper.add_representer(ZPropertySpec, Dumper.represent_spec)
Dumper.add_representer(ClassSpec, Dumper.represent_spec)
Dumper.add_representer(ClassPropertySpec, Dumper.represent_spec)
Dumper.add_representer(ClassRelationshipSpec, Dumper.represent_spec)
Dumper.add_representer(RelationshipSchemaSpec, Dumper.represent_relschemaspec)
# SpecParams subclasses
Dumper.add_representer(ZenPackSpecParams, Dumper.represent_zenpackspec)
Dumper.add_representer(DeviceClassSpecParams, Dumper.represent_spec)
Dumper.add_representer(ZPropertySpecParams, Dumper.represent_spec)
Dumper.add_representer(ClassSpecParams, Dumper.represent_spec)
Dumper.add_representer(ClassPropertySpecParams, Dumper.represent_spec)
Dumper.add_representer(ClassRelationshipSpecParams, Dumper.represent_spec)
Dumper.add_representer(RRDTemplateSpecParams, Dumper.represent_spec)
Dumper.add_representer(RRDThresholdSpecParams, Dumper.represent_spec)
Dumper.add_representer(RRDDatasourceSpecParams, Dumper.represent_spec)
Dumper.add_representer(RRDDatapointSpecParams, Dumper.represent_spec)
Dumper.add_representer(GraphDefinitionSpecParams, Dumper.represent_spec)
Dumper.add_representer(GraphPointSpecParams, Dumper.represent_spec)
# representers for python types
Dumper.add_representer(OrderedDict, Dumper.represent_ordereddict)
Dumper.add_representer(unicode, SafeRepresenter.represent_unicode)
Dumper.add_representer(float, SafeRepresenter.represent_float)
Dumper.add_representer(int, SafeRepresenter.represent_int)
Dumper.add_representer(str, SafeRepresenter.represent_str)
Dumper.add_representer(bool, SafeRepresenter.represent_bool)
Dumper.add_representer(EventClassSpecParams, Dumper.represent_spec)
Dumper.add_representer(EventClassMappingSpec, Dumper.represent_spec)
Dumper.add_representer(ProcessClassOrganizerSpecParams, Dumper.represent_spec)
Dumper.add_representer(ProcessClassSpecParams, Dumper.represent_spec)
Dumper.add_representer(ImpactTriggerSpecParams, Dumper.represent_spec)
Dumper.add_representer(LinkProviderSpecParams, Dumper.represent_spec)
# representers for custom types
from ..base.types import Color, Severity, multiline
Dumper.add_representer(Color, SafeRepresenter.represent_str)
Dumper.add_representer(Severity, Dumper.represent_severity)
Dumper.add_representer(multiline, Dumper.represent_multiline)


