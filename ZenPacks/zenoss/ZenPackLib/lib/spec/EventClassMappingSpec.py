##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..base.types import multiline
from .Spec import Spec


class EventClassMappingSpec(Spec):
    """Initialize a EventClassMapping via Python at install time."""
    def __init__(
            self,
            eventclass_spec,
            name,
            eventClassKey='',
            sequence=None,
            rule='',
            regex='',
            example='',
            transform='',
            explanation='',
            resolution='',
            remove=False,
            _source_location=None,
            zplog=None):
        """
          :param eventClassKey: Event Class Key ( whats the default key )
          :type eventClassKey: str
          :param sequence: Define the match priority. Lower is a higher priority
          :type sequence: int
          :param rule: a python expression to match an event
          :type rule: str
          :param regex: a regular expression to match an event
          :type regex: str
          :param transform: a python expression for transformation
          :type transform: multiline
          :param example: debugging string to use in the regular expression ui testing.
          :type example: multiline
          :param explanation: Enter a textual description for matches for this event class mapping. Use in conjunction with the Resolution field.
          :type explanation: multiline
          :param resolution: Use the Resolution field to enter resolution instructions for clearing the event.
          :type resolution: multiline
          :param remove: Remove the Mapping when the ZenPack is removed
          :type remove: bool
        """
        super(EventClassMappingSpec, self).__init__(_source_location=_source_location)
        self.klass_string = 'EventClassInst'
        self.eventclass_spec = eventclass_spec
        self.name = name
        self.eventClassKey = eventClassKey or name
        self.sequence = sequence
        self.transform = multiline(transform)
        self.rule = rule
        self.regex = regex
        self.example = multiline(example)
        self.explanation = multiline(explanation)
        self.resolution = multiline(resolution)
        self.remove = remove
        if zplog:
            self.LOG = zplog

    def create(self, eventclass):
        mapping = eventclass.instances._getOb(eventclass.prepId(self.name), False)
        if not mapping:
            mapping = eventclass.createInstance(self.name)
        _properties = ['eventClassKey', 'sequence', 'rule', 'regex',
                       'example', 'explanation', 'resolution', 'transform']
        for x in _properties:
            if getattr(mapping, x) != getattr(self, x):
                setattr(mapping, x, getattr(self, x, None))

        mapping.zpl_managed = True
        mapping.index_object()
