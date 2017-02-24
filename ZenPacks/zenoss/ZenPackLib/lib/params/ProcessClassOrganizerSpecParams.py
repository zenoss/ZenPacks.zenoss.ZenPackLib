##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from .SpecParams import SpecParams
from .ProcessClassSpecParams import ProcessClassSpecParams
from ..spec.ProcessClassOrganizerSpec import ProcessClassOrganizerSpec


class ProcessClassOrganizerSpecParams(SpecParams, ProcessClassOrganizerSpec):
    def __init__(self, zenpack_spec, path, description='', process_classes=None, remove=False, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.path = path
        self.description = description
        self.remove = remove
        self.process_classes = self.specs_from_param(
            ProcessClassSpecParams, 'process_classes', process_classes)

    @classmethod
    def fromObject(cls, processclass, zenpack=None, remove=True):
        self = super(ProcessClassOrganizerSpecParams, cls).fromObject(processclass)
        self.remove = remove
        processclass = aq_base(processclass)

        self.path = processclass.getOrganizerName()

        p_classes = processclass.osProcessClasses()

        if zenpack:
            p_classes = [x for x in p_classes if x in zenpack.packables()]

        self.process_classes = ProcessClassSpecParams.get_ordered_params(p_classes, 'id')

        return self

    @classmethod
    def new(cls, processclass, description='', remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        self.path = processclass
        self.description = description
        self.remove = remove
        return self

