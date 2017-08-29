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
            remove=False,
            process_classes=None,
            _source_location=None,
            zplog=None):
        """
          :param description: Description of Process Class Organizer
          :type description: str
          :param process_classes: Process Class specs
          :type process_classes: SpecsParameter(ProcessClassSpec)
          :param remove: Remove Organizer on ZenPack removal
          :type remove: boolean
        """
        super(ProcessClassOrganizerSpec, self).__init__(
            zenpack_spec,
            path,
            _source_location=_source_location)

        if zplog:
            self.LOG = zplog

        self.description = description
        self.remove = remove
        self.process_classes = self.specs_from_param(
            ProcessClassSpec, 'process_classes', process_classes, zplog=self.LOG)

    def create(self, dmd, addToZenPack=True):
        porg = self.get_organizer(dmd)
        if not porg:
            porg = dmd.Processes.createOrganizer(self.path)
            porg.zpl_managed = True

        # Set to false to facilitate testing without ZP installation.
        if addToZenPack:
             # Add this OSProcessOrganizer to the zenpack.
            porg.addToZenPack(pack=self.zenpack_spec.name)

        if porg.description != self.description:
            porg.description = self.description

        for process_class_id, process_class_spec in self.process_classes.items():
            process_class_spec.create(dmd, porg)

    def get_root(self, dmd):
        """Return the root object for this organizer."""
        return dmd.Processes
