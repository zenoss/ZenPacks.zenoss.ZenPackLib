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
from ..spec.EventClassMappingSpec import EventClassMappingSpec


class EventClassMappingSpecParams(SpecParams, EventClassMappingSpec):
    def __init__(self,
                 eventclass_spec,
                 name,
                 eventClassKey='',
                 sequence='',
                 rule='',
                 regex='',
                 example='',
                 explanation='',
                 resolution='',
                 transform='',
                 remove='',
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.eventClassKey = eventClassKey
        self.sequence = sequence
        self.rule = rule
        self.regex = regex
        self.example = example
        self.explanation = explanation
        self.resolution = resolution
        self.transform = transform
        self.remove = remove

    @classmethod
    def fromObject(cls, mapping, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        mapping = aq_base(mapping)

        _properties = ['eventClassKey', 'sequence', 'rule', 'regex',
                       'example', 'explanation', 'resolution', 'transform']
        for x in _properties:
            setattr(self, x, getattr(mapping, x, None))

        self.remove = remove
        return self
