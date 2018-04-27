##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..base.types import multiline
from .OrganizerSpec import OrganizerSpec
from .EventClassMappingSpec import EventClassMappingSpec


class EventClassSpec(OrganizerSpec):
    """Initialize a EventClass via Python at install time."""

    def __init__(
            self,
            zenpack_spec,
            path,
            description='',
            transform='',
            remove=False,
            mappings=None,
            _source_location=None,
            zplog=None):
        """
          :param remove: Remove the EventClass when ZenPack is removed?
          :type remove: bool
          :param description: Description of the EventClass
          :type description: str
          :param transform: EventClass Transformation
          :type transform: multiline
          :param mappings: TODO
          :type mappings: SpecsParameter(EventClassMappingSpec)
        """
        super(EventClassSpec, self).__init__(
            zenpack_spec,
            path,
            _source_location=_source_location)

        if zplog:
            self.LOG = zplog

        self.description = description
        self.transform = multiline(transform)
        self.remove = bool(remove)
        self.mappings = self.specs_from_param(
            EventClassMappingSpec, 'mappings', mappings, zplog=self.LOG)

    def instantiate(self, dmd):
        ecObject = self.get_organizer(dmd)
        if not ecObject:
            ecObject = dmd.Events.createOrganizer(self.path)
            ecObject.zpl_managed = True

        if self.description != '':
            if not ecObject.description == self.description:
                self.LOG.debug('Description of Event Class {} has changed from'
                               ' {} to {}'.format(self.path,
                                                  ecObject.description,
                                                  self.description))
                ecObject.description = self.description
        if self.transform != '':
            if not ecObject.transform == self.transform:
                self.LOG.debug('Transform for Event Class {} has changed from'
                               '\n{}\n to \n{}'.format(self.path,
                                                       ecObject.transform,
                                                       self.transform))
                ecObject.transform = self.transform

        for mapping_id, mapping_spec in self.mappings.items():
            mapping_spec.create(ecObject)
        return ecObject

    def get_root(self, dmd):
        """Return the root object for this organizer."""
        return dmd.Events
