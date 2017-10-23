##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..base.types import multiline
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
        self.example = multiline(example)
        self.explanation = multiline(explanation)
        self.resolution = multiline(resolution)
        self.transform = multiline(transform)
        self.remove = remove

    @classmethod
    def fromObject(cls, mapping, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        mapping = aq_base(mapping)

        for x in ['eventClassKey', 'sequence', 'rule', 'regex']:
            setattr(self, x, getattr(mapping, x, None))

        self.example = multiline(mapping.example)
        self.explanation = multiline(mapping.explanation)
        self.resolution = multiline(mapping.resolution)
        self.transform = multiline(mapping.transform)
        self.remove = remove
        return self
