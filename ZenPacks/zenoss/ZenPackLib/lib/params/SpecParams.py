##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from collections import OrderedDict
from ..spec.Spec import Spec
from ..helpers.ZenPackLibLog import DEFAULTLOG
from ..base.ClassProperty import ClassProperty
import copy

class SpecParams(object):
    """SpecParams"""

    LOG = DEFAULTLOG
    _init_params = None

    def __init__(self, **kwargs):
        # Initialize with default values
        self.LOG = kwargs.get('zplog', DEFAULTLOG)

        params = self.__class__.init_params
        for param in params:
            if 'default' in params[param]:
                setattr(self, param, params[param]['default'])

        # Overlay any named parameters
        self.__dict__.update(kwargs)

    @ClassProperty
    @classmethod
    def init_params(cls):
        if not cls._init_params:
            cls._init_params = cls.get_init_params()
        return cls._init_params

    @classmethod
    def get_init_params(cls):
        # Pull over the params for the underlying Spec class,
        # correcting nested Specs to SpecsParams instead.
        try:
            spec_base = [x for x in cls.__bases__ if issubclass(x, Spec)][0]
        except Exception:
            raise Exception("Spec Base Not Found for %s" % cls.__name__)

        params = copy.deepcopy(spec_base.init_params)
        for p in params:
            params[p]['type'] = params[p]['type'].replace("Spec)", "SpecParams)")

        return params

    def handle_prop(self, ob, proto, prop_name, spec_prop=None):
        """Set default value and possible instance value"""
        if not spec_prop:
            spec_prop = prop_name

        # find the default for the class
        default_val = None
        if hasattr(proto, prop_name):
            default_val = getattr(proto, prop_name, None)
            setattr(self, '_{}_defaultvalue'.format(spec_prop), default_val)

        # set it locally if our property differs from the class default
        local_val = getattr(ob, prop_name, None)
        if local_val is not None and local_val != default_val:
            setattr(self, spec_prop, local_val)

    @classmethod
    def fromObject(cls, ob, prop_map={}):
        """Generate SpecParams from example object and list of properties"""
        self = object.__new__(cls)
        SpecParams.__init__(self)

        ob = aq_base(ob)
        # Weed out any values that are the same as they would by by default.
        # We do this by instantiating a "blank" object and comparing
        # to it.
        proto = ob.__class__(ob.id)

        # these have to be handled separately
        ignore = ['extra_params', 'aliases']
        # Spec fields
        propnames = [k for k, v in cls.init_params.items() if k not in ignore and 'SpecsParameter' not in v['type']]

        for propname in propnames:
            # print 'handling', propname
            self.handle_prop(ob, proto, propname)

        # some object properties might be mapped to differently-named spec properties
        for ob_prop, spec_prop in prop_map.items():
            self.handle_prop(ob, proto, ob_prop, spec_prop)

        # any custom object properties not defined in the spec will go in extra_params
        self.extra_params = OrderedDict()
        ob_propnames = [x['id'] for x in ob._properties if x['id'] not in cls.init_params]
        for propname in ob_propnames:
            if getattr(ob, propname, None) != getattr(proto, propname, None):
                self.extra_params[propname] = getattr(ob, propname, None)

        return self

    @classmethod
    def fromClass(cls, klass, prop_map={}):
        """Generate SpecParams from given class"""
        return cls.fromObject(klass('ob'), prop_map)
