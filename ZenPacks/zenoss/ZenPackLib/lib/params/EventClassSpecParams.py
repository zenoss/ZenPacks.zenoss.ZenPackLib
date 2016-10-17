##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .SpecParams import SpecParams
from .EventClassMappingSpecParams import EventClassMappingSpecParams
from ..spec.EventClassSpec import EventClassSpec


class EventClassSpecParams(SpecParams, EventClassSpec):
    def __init__(self, zenpack_spec, path, description='', transform='', mappings=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.path = path
        self.description = description
        self.transform = transform
        self.mappings = self.specs_from_param(
            EventClassMappingSpecParams, 'mappings', mappings)

    @classmethod
    def new(cls, eventclass, description='', transform='', create=False, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        self.path = eventclass
        self.description = description
        self.transform = transform
        self.create = create
        self.remove = remove
        return self

    @classmethod
    def fromObject(cls, eventclass, create=False, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)

        self.description = eventclass.description
        self.transform = eventclass.transform
        self.create = create
        self.remove = remove
        self.mappings = {x.id: EventClassMappingSpecParams.fromObject(x) for x in eventclass.instances()}
        return self
