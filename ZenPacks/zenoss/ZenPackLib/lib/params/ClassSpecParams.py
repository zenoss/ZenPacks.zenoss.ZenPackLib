##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from collections import OrderedDict
from Acquisition import aq_base
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.Device import Device as BaseDevice
from .SpecParams import SpecParams
from .ClassPropertySpecParams import ClassPropertySpecParams
from .ClassRelationshipSpecParams import ClassRelationshipSpecParams
from .RelationshipSchemaSpecParams import RelationshipSchemaSpecParams
from .ImpactTriggerSpecParams import ImpactTriggerSpecParams
from ..spec.RelationshipSchemaSpec import RelationshipSchemaSpec
from ..spec.ClassSpec import ClassSpec
from ..spec.ZenPackSpec import ZenPackSpec
from ..functions import pluralize

from ..base.Device import Device
from ..base.Component import (
    Component,
    HWComponent,
    HardwareComponent,
    CPU,
    ExpansionCard,
    Fan,
    HardDisk,
    PowerSupply,
    TemperatureSensor,
    OSComponent,
    FileSystem,
    IpInterface,
    IpRouteEntry,
    OSProcess,
    Service,
    IpService,
    WinService
)



class ClassSpecParams(SpecParams, ClassSpec):
    def __init__(self, zenpack_spec, name, base=None, properties=None, relationships=None, impact_triggers=None, monitoring_templates=[], **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.zenpack_spec = zenpack_spec

        if isinstance(base, (tuple, list, set)):
            self.base = tuple(base)
        else:
            self.base = (base,)

        for b in self.base:
            if isinstance(b, str):
                continue
            if 'ModelTypeFactory' in b.__module__:
                b.__module__ = 'zenpacklib'

        if isinstance(monitoring_templates, (tuple, list, set)):
            self.monitoring_templates = list(monitoring_templates)
        else:
            self.monitoring_templates = [monitoring_templates]

        self.properties = self.specs_from_param(
            ClassPropertySpecParams, 'properties', properties, leave_defaults=True, zplog=self.LOG)

        self.relationships = self.specs_from_param(
            ClassRelationshipSpecParams, 'relationships', relationships, leave_defaults=True, zplog=self.LOG)

        self.impact_triggers = self.specs_from_param(
            ImpactTriggerSpecParams, 'impact_triggers', impact_triggers, leave_defaults=True, zplog=self.LOG)

    @classmethod
    def fromObject(cls, ob, zenpack=None):
        self = super(ClassSpecParams, cls).fromObject(ob)

        ob = aq_base(ob)

        self.name = ob.__class__.__name__

        klass = ob.__class__
        bases = cls.get_my_bases(klass)
        # this might be a non-ZPL class
        # so we substitute a ZPL proxy classes?\
        if len(bases) == 0:
            bases = [cls.find_proxy(klass)]

        self.base = tuple([x.__name__ if 'zenpacklib' not in x.__module__ else 'zenpacklib.{}'.format(x.__name__) for x in bases])

        # proto for this should be a ClassSpec with same bases
        if zenpack:
            zp_spec = ZenPackSpec(zenpack)
        else:
            zp_spec = ZenPackSpec('ZenPacks.zenoss.ZenPackLib')

        proto_spec = ClassSpec(zp_spec, self.name, bases)
        proto = proto_spec.model_class

        # these have to be handled separately
        ignore = ['extra_params', 'aliases']
        # Spec fields
        propnames = [k for k, v in cls.init_params.items() if k not in ignore and 'SpecsParameter' not in v['type']]

        for propname in propnames:
            self.handle_prop(ob, proto, propname)

        prop_map = {'class_label': 'label',
                    'class_plural_label': 'plural_label',
                    'class_short_label':'short_label',
                    'class_plural_short_label':'plural_short_label',
                    'zenpack_name': zp_spec.name}
        # some object properties might be mapped to differently-named spec properties
        for ob_prop, spec_prop in prop_map.items():
            self.handle_prop(ob, proto, ob_prop, spec_prop)

        # any custom object properties not defined in the spec will go in extra_params
        ignore = [x['id'] for x in ManagedEntity._properties] + cls.init_params.keys()
        props = [x for x in ob._properties if x['id'] not in ignore]

        self.properties = {x['id']: ClassPropertySpecParams.fromObject(x['id'], ob) for x in props}

        ignore = [x[0] for x in BaseDevice._relations]
        rels = [x for x in ob._relations if x[0] not in ignore]
        self.relationships = {x[0]: ClassRelationshipSpecParams.fromObject(x, ob) for x in rels}

        self.monitoring_templates = [t for t in list(getattr(ob, '_templates', [])) if t not in cls.get_base_names(ob.__class__)]

        # some of these should be removed if they are defaults
        meta_type = getattr(self, 'meta_type', None) or getattr(self, 'name', None)
        label = getattr(self, 'label', None) or getattr(self, 'meta_type', None) or getattr(self, 'name', None)
        plural_label = pluralize(label)
        short_label = getattr(self, 'short_label', None) or label
        plural_short_label = getattr(self, 'plural_short_label', None) or pluralize(short_label)

        dv_group = getattr(self, 'dynamicview_group', None) or {}

        if dv_group.get('name') == plural_short_label:
            setattr(self, 'dynamicview_group', None)

        if getattr(self, 'plural_short_label', None) == plural_label:
            setattr(self, 'plural_short_label', None)

        if getattr(self, 'plural_label', None) == plural_label:
            setattr(self, 'plural_label', None)

        if getattr(self, 'short_label', None) == label:
            setattr(self, 'short_label', None)

        if getattr(self, 'label', None) == meta_type:
            setattr(self, 'label', None)

        if getattr(self, 'meta_type', None) == getattr(self, 'name', None):
            setattr(self, 'meta_type', None)

        return self

    @classmethod
    def fromClass(cls, klass, zenpack=None):
        """Generate SpecParams from given class"""
        return cls.fromObject(klass('ob'), zenpack)

    @classmethod
    def find_proxy(cls, klass):
        bases = cls.get_base_classes(klass, skip_self=False, skip_base=False)
        for b in bases:
            if b == ManagedEntity:
                continue
            for x in [CPU, ExpansionCard, Fan,
                      HardDisk, PowerSupply, TemperatureSensor,
                      OSComponent, FileSystem, IpInterface,
                      IpRouteEntry, OSProcess, Service, IpService,
                      WinService, HardwareComponent, HWComponent, Component, Device]:
                if issubclass(x, b):
                    x.__module__ = 'zenpacklib'
                    return x
        cls.LOG.warning("No base class found for {}".format(klass.__name__))
        return Component

    @classmethod
    def get_my_bases(cls, klass, skip_self=True, skip_schema=True, skip_base=True):
        """Return base classes of given class minus implicitly inherited"""
        bases = cls.get_base_classes(klass, skip_self, skip_schema, skip_base)
        # remove any bases that already implicitly inherited
        for base in bases:
            metas = cls.get_base_classes(base, skip_self, skip_schema, skip_base)
            bases = [x for x in bases if x not in metas]
        return bases

    @classmethod
    def get_base_classes(cls, klass, skip_self=False, skip_schema=True, skip_base=True):
        bases = []
        for base in getattr(klass, '__mro__', []):
            if not hasattr(base, '_relations'):
                continue
            if len(base._relations) == 0:
                continue
            if skip_base and 'ZenModel' in base.__module__:
                continue
            if skip_schema and 'schema' in base.__module__:
                continue
            if skip_self and base == klass:
                continue
            if base not in bases:
                bases.append(base)
        return bases

    @classmethod
    def get_base_names(cls, klass, skip_self=False, skip_schema=True, skip_base=True):
        return [x.__name__ for x in cls.get_base_classes(klass, skip_self, skip_schema, skip_base)]

    @classmethod
    def use_rel(cls, klass, relname):
        """Return True if this class relations should be dumped"""
        rel_sparm = RelationshipSchemaSpecParams.fromClass(klass, relname)

        if not RelationshipSchemaSpec.valid_orientation(rel_sparm.left_type, rel_sparm.right_type):
            return False

        local_class = rel_sparm.get_module_class(rel_sparm.left_class)
        local_classname = klass.__name__

        remote_class = rel_sparm.get_module_class(rel_sparm.right_class)
        remote_classname = remote_class.__name__

        # need to check that relation is bi-directional between classes and/or their bases
        if remote_classname not in cls.get_base_names(remote_class) and local_classname not in cls.get_base_names(local_class):
            return False

        return True
