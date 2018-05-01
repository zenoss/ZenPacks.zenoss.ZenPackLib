##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016-2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .OrganizerSpecParams import OrganizerSpecParams
from .ProcessClassSpecParams import ProcessClassSpecParams
from ..spec.ProcessClassOrganizerSpec import ProcessClassOrganizerSpec


class ProcessClassOrganizerSpecParams(OrganizerSpecParams, ProcessClassOrganizerSpec):

    def __init__(self, zenpack_spec, path, description='', zProperties=None, process_classes=None, remove=False, **kwargs):
        OrganizerSpecParams.__init__(self, zenpack_spec, path, zProperties, **kwargs)
        self.description = description
        self.remove = remove
        self.process_classes = self.specs_from_param(
            ProcessClassSpecParams, 'process_classes', process_classes)

    @classmethod
    def fromObject(cls, processclass, remove=False):
        self = object.__new__(cls)
        OrganizerSpecParams.__init__(self)

        self.description = processclass.description
        self.remove = remove
        self.process_classes = {x.id: ProcessClassSpecParams.fromObject(x) for x in processclass.osProcessClasses()}
        return self

    @classmethod
    def new(cls, processclass, description='', remove=False):
        self = object.__new__(cls)
        OrganizerSpecParams.__init__(self)

        self.path = processclass
        self.description = description
        self.remove = remove
        return self
