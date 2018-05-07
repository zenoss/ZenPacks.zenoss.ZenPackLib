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
            zProperties=None,
            create=True,
            remove=False,
            reset=True,
            transform='',
            mappings=None,
            _source_location=None,
            zplog=None):
        """
            Create an Event Class Organizer Specification
            
            :param description: Description of Event Class Organizer
            :type description: str
            :param zProperties: zProperty values to set upon this Organizer
            :type zProperties: dict(str)
            :param create: Create the Event Class Organizer with ZenPack installation, if it does not exist?
            :type create: bool
            :param remove: Remove the Event Class Organizer when ZenPack is removed?
            :type remove: bool
            :param reset:  If True, reset any zProperties that differ from given
            :type reset: bool
            :param transform: EventClass Transformation
            :type transform: multiline
            :param mappings: TODO
            :type mappings: SpecsParameter(EventClassMappingSpec)
        """
        super(EventClassSpec, self).__init__(
            zenpack_spec,
            path,
            description,
            zProperties,
            create,
            remove,
            reset,
            _source_location=_source_location)

        if zplog:
            self.LOG = zplog

        self.transform = multiline(transform)

        self.mappings = self.specs_from_param(
            EventClassMappingSpec, 'mappings', mappings, zplog=self.LOG)

    def create_organizer(self, dmd):
        """Return existing or new event class organizer"""
        ec_org = super(EventClassSpec, self).create_organizer(dmd)
        if not ec_org:
            return

        if self.description != '' and self.description != ec_org.description:
            self.LOG.debug('Description of Event Class {} has changed from'
                ' {} to {}'.format(self.path,
                ec_org.description, self.description))

            ec_org.ec_org = self.description

        if self.transform != '' and self.transform != ec_org.transform:
            self.LOG.debug(
                'Transform for Event Class {} has changed from'
                '\n{}\n to \n{}'.format(self.path,
                ec_org.transform, self.transform))

            ec_org.transform = self.transform

        for mapping_id, mapping_spec in self.mappings.items():
            mapping_spec.create(ec_org)

        return ec_org

    def get_root(self, dmd):
        """Return the root object for this organizer."""
        return dmd.Events

    def remove_organizer(self, dmd, zenpack=None):
        """Remove the organizer or subclasses within an organizer
        """
        org_removed = super(EventClassSpec, self).remove_organizer(dmd, zenpack)
        if not org_removed:
            self.remove_subs(dmd, 'mappings', 'removeInstances')
        return org_removed
