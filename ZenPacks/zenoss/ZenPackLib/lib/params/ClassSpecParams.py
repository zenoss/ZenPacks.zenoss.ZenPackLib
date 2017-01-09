##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.Device import Device
from .SpecParams import SpecParams
from .ClassPropertySpecParams import ClassPropertySpecParams
from .ClassRelationshipSpecParams import ClassRelationshipSpecParams
from .RelationshipSchemaSpecParams import RelationshipSchemaSpecParams
from .ImpactTriggerSpecParams import ImpactTriggerSpecParams
from ..spec.RelationshipSchemaSpec import RelationshipSchemaSpec
from ..spec.ClassSpec import ClassSpec


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
    def fromObject(cls, ob):
        self = super(ClassSpecParams, cls).fromObject(ob)

        ob = aq_base(ob)

        self.name = ob.__class__.__name__

        bases = cls.get_my_bases(ob.__class__)
        self.base = tuple([x.__name__ if 'zenpacklib' not in x.__module__ else 'zenpacklib.{}'.format(x.__name__) for x in bases])

        ignore = [x['id'] for x in ManagedEntity._properties]
        props = [x for x in ob._properties if x['id']  not in ignore]
        self.properties = {x['id']: ClassPropertySpecParams.fromObject(x['id'], ob) for x in props}

        ignore = [x[0] for x in Device._relations]
        rels = [x for x in ob._relations if x[0] not in ignore]
        self.relationships = {x[0]: ClassRelationshipSpecParams.fromObject(x, ob) for x in rels}

        self.monitoring_templates = [t for t in list(getattr(ob, '_templates', [])) if t not in cls.get_base_names(ob.__class__)]
        return self

    @classmethod
    def fromClass(cls, klass):
        """Generate SpecParams from given class"""
        return cls.fromObject(klass('ob'))

    @classmethod
    def get_my_bases(cls, klass):
        """Return base classes of given class minus implicitly inherited"""
        bases = cls.get_base_classes(klass, skip_self=True)
        # remove any bases that already implicitly inherited
        for base in bases:
            metas = cls.get_base_classes(base, skip_self=True)
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
