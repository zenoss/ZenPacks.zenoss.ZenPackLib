##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import importlib
from Acquisition import aq_base
from .SpecParams import SpecParams
from ..spec.RelationshipSchemaSpec import RelationshipSchemaSpec
from ..base.types import Relationship


class RelationshipSchemaSpecParams(SpecParams, RelationshipSchemaSpec):
    def __init__(self, class_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def find_schema_on_class(cls, klass, relname):
        for name, schema in getattr(klass, '_relations', []):
            if name == relname:
                return schema
        return None

    @classmethod
    def get_module_class(cls, modname):
        try:
            module = importlib.import_module(modname)
        except ImportError:
            # this might be patched to an existing class with full module & classpath
            modname = '.'.join(modname.split('.')[:-1])
            return cls.get_module_class(modname)
        classname = modname.split('.')[-1]
        return getattr(module, classname, None)

    @classmethod
    def fromObject(cls, ob, relname, zenpack='Unknown'):
        """Generate SpecParams from example object and list of properties"""
        self = object.__new__(cls)
        SpecParams.__init__(self)

        ob = aq_base(ob)

        local_schema = cls.find_schema_on_class(ob.__class__, relname)

        remote_modname = local_schema.remoteClass
        remote_class = cls.get_module_class(remote_modname)
        remote_classname = remote_class.__name__
        remote_name = local_schema.remoteName
        remote_schema = cls.find_schema_on_class(remote_class, remote_name)

        local_class = cls.get_module_class(remote_schema.remoteClass)
        local_classname = local_class.__name__
        local_modname = local_class.__module__
        local_name = relname

        remote_type = Relationship(local_schema.remoteType.__name__)
        local_type = Relationship(remote_schema.remoteType.__name__)

        self.left_rel = remote_type
        self.left_class = remote_modname

        if zenpack in remote_modname:
            self.left_class = remote_classname

        self.left_relname = remote_name
        self.left_type = local_type.name

        self.right_rel = local_type

        self.right_class = local_modname
        if zenpack in local_modname:
            self.right_class = local_classname

        self.right_relname = local_name
        self.right_type = remote_type.name
        return self

    @classmethod
    def fromClass(cls, klass, relname, zenpack='Unknown'):
        """Generate SpecParams from given class"""
        return cls.fromObject(klass('ob'), relname, zenpack)
