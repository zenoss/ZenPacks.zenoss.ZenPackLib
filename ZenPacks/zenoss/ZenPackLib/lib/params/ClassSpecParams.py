##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .SpecParams import SpecParams
from .ClassPropertySpecParams import ClassPropertySpecParams
from .ClassRelationshipSpecParams import ClassRelationshipSpecParams
from ..spec.ClassSpec import ClassSpec


class ClassSpecParams(SpecParams, ClassSpec):
    def __init__(self, zenpack_spec, name, base=None, properties=None, relationships=None, monitoring_templates=[], **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

        if isinstance(base, (tuple, list, set)):
            self.base = tuple(base)
        else:
            self.base = (base,)

        if isinstance(monitoring_templates, (tuple, list, set)):
            self.monitoring_templates = list(monitoring_templates)
        else:
            self.monitoring_templates = [monitoring_templates]

        self.properties = self.specs_from_param(
            ClassPropertySpecParams, 'properties', properties, leave_defaults=True, zplog=self.LOG)

        self.relationships = self.specs_from_param(
            ClassRelationshipSpecParams, 'relationships', relationships, leave_defaults=True, zplog=self.LOG)
