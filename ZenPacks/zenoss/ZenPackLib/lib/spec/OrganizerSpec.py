##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .Spec import Spec


class OrganizerSpec(Spec):
    """Abstract base for organizer specifications.

    Subclasses:

    * DeviceClassSpec
    * EventClassSpec
    * ProcessClassOrganizerSpec

    """

    def __init__(self, zenpack_spec, path, _source_location=None, zplog=None):
        """Create an Organizer specification."""
        super(OrganizerSpec, self).__init__(_source_location=_source_location)

        if zplog:
            self.LOG = zplog

        self.zenpack_spec = zenpack_spec
        self.path = path.lstrip("/")

    def get_root(self, dmd):
        """Return the root for this organizer.

        Must be overridden by subclasses. DeviceClassSpec, for example, would
        return dmd.Devices.

        """
        raise NotImplementedError

    def get_organizer(self, dmd):
        """Return organizer object for this specification or None."""
        try:
            organizer = self.get_root(dmd).getOrganizer(self.path)
        except KeyError:
            return
        else:
            # Guard against acquisition returning us the wrong organizer.
            if organizer.getOrganizerName().lstrip("/") == self.path:
                return organizer
