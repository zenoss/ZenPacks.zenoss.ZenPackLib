##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .Spec import Spec
from ..functions import LOG


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
            _source_location=None):
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
          :type transform: str
          :param example: debugging string to use in the regular expression ui testing.
          :type example: str
          :param explanation: Enter a textual description for matches for this event class mapping. Use in conjunction with the Resolution field.
          :type explanation: str
          :param resolution: Use the Resolution field to enter resolution instructions for clearing the event.
          :type resolution: str
          :param remove: Remove the Mapping when the ZenPack is removed
          :type remove: bool
        """
        super(EventClassMappingSpec, self).__init__(_source_location=_source_location)
        self.eventclass_spec = eventclass_spec
        self.name = name
        self.eventClassKey = eventClassKey
        self.sequence = sequence
        self.transform = transform
        self.rule = rule
        self.regex = regex
        self.example = example
        self.explanation = explanation
        self.resolution = resolution
        self.remove = remove

    def create(self, eventclass):
        mapping = eventclass.instances._getOb(eventclass.prepId(self.name), False)
        if not mapping:
            LOG.info('Creating mapping %s @ %s' % (self.name, self.eventclass_spec.path))
            mapping = eventclass.createInstance(self.name)
        _properties = ['eventClassKey', 'sequence', 'rule', 'regex',
                       'example', 'explanation', 'resolution', 'transform']
        for x in _properties:
            if getattr(mapping, x) != getattr(self, x):
                LOG.info('Setting %s on mapping %s @ %s' % (x, self.name, self.eventclass_spec.path))
                setattr(mapping, x, getattr(self, x, None))
