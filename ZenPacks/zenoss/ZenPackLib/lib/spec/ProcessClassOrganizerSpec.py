##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .OrganizerSpec import OrganizerSpec
from .ProcessClassSpec import ProcessClassSpec


class ProcessClassOrganizerSpec(OrganizerSpec):
    """Initialize a Process Set via Python at install time."""

    def __init__(
            self,
            zenpack_spec,
            path,
            description='',
            zProperties=None,
            create=True,
            remove=False,
            reset=True,
            process_classes=None,
            _source_location=None,
            zplog=None):
        """
            Create a Process Class Organizer Specification
            
            :param description: Description of Process Class Organizer
            :type description: str
            :param zProperties: zProperty values to set upon this Organizer
            :type zProperties: dict(str)
            :param create: Create the Process Class Organizer with ZenPack installation, if it does not exist?
            :type create: bool
            :param remove: Remove the Process Class Organizer when ZenPack is removed?
            :type remove: bool
            :param reset:  If True, reset any zProperties that differ from given
            :type reset: bool
            :param process_classes: Process Class specs
            :type process_classes: SpecsParameter(ProcessClassSpec)
        """
        super(ProcessClassOrganizerSpec, self).__init__(
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

        self.process_classes = self.specs_from_param(
            ProcessClassSpec, 'process_classes', process_classes, zplog=self.LOG)

    def create_organizer(self, dmd):
        """Return existing or new process class organizer"""
        ps_org = super(ProcessClassOrganizerSpec, self).create_organizer(dmd)
        if not ps_org:
            return

        if self.description != '' and self.description != ps_org.description:
            ps_org.description = self.description

        for process_class_id, process_class_spec in self.process_classes.items():
            process_class_spec.create(dmd, ps_org)
        return ps_org

    def get_root(self, dmd):
        """Return the root object for this organizer."""
        return dmd.Processes

    def remove_organizer(self, dmd, zenpack=None):
        """Remove the organizer or subclasses within an organizer
        """
        org_removed = super(ProcessClassOrganizerSpec, self).remove_organizer(dmd, zenpack)
        if not org_removed:
            self.remove_subs(dmd, 'process_classes', 'removeOSProcessClasses')
        return org_removed
