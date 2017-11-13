##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016-2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..base.types import multiline
from .OrganizerSpecParams import OrganizerSpecParams
from .EventClassMappingSpecParams import EventClassMappingSpecParams
from ..spec.EventClassSpec import EventClassSpec


class EventClassSpecParams(OrganizerSpecParams, EventClassSpec):
    def __init__(self, zenpack_spec, path, description='', transform='', mappings=None, **kwargs):
        OrganizerSpecParams.__init__(self, zenpack_spec, path, **kwargs)
        self.description = description
        self.transform = multiline(transform)
        self.mappings = self.specs_from_param(
            EventClassMappingSpecParams, 'mappings', mappings)

    @classmethod
    def new(cls, eventclass, description='', transform='', remove=False):
        self = object.__new__(cls)
        OrganizerSpecParams.__init__(self)

        self.path = eventclass
        self.description = description
        self.transform = multiline(transform)
        self.remove = remove
        return self

    @classmethod
    def fromObject(cls, eventclass, remove=False):
        self = object.__new__(cls)
        OrganizerSpecParams.__init__(self)

        self.description = eventclass.description
        self.transform = multiline(eventclass.transform)
        self.remove = remove
        self.mappings = {x.id: EventClassMappingSpecParams.fromObject(x) for x in eventclass.instances()}
        return self
