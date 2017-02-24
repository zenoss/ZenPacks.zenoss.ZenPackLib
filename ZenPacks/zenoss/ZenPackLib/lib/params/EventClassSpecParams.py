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
    def new(cls, eventclass, description='', transform='', remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        self.path = eventclass
        self.description = description
        self.transform = transform
        self.remove = remove
        return self

    @classmethod
    def fromObject(cls, eventclass, zenpack=None, remove=True):
        self = super(EventClassSpecParams, cls).fromObject(eventclass)
        self.remove = remove
        eventclass = aq_base(eventclass)

        self.path = eventclass.getOrganizerName()

        mappings = self.get_sorted_objects(eventclass.instances(), 'id')

        if zenpack:
            mappings = [x for x in mappings if x in zenpack.packables()]

        self.mappings = EventClassMappingSpecParams.get_ordered_params(mappings, 'id')

        return self
