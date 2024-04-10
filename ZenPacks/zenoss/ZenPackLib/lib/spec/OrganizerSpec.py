##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from .Spec import Spec

RESERVED_CLASSES = set(['Status', 'App', 'Cmd', 'Perf',
                        'Heartbeat', 'Unknown', 'Change', 'Processes',
                        'Services', 'WinService', 'IpService',
                        'Devices', 'Server'])


class OrganizerSpec(Spec):
    """Abstract base for organizer specifications.

    Subclasses:

    * DeviceClassSpec
    * EventClassSpec
    * ProcessClassOrganizerSpec

    """

    def __init__(
            self,
            zenpack_spec,
            path,
            description='',
            zProperties=None,
            create=True,
            remove=False,
            reset=True,
            _source_location=None,
            zplog=None):
        """Create an Organizer specification."""
        super(OrganizerSpec, self).__init__(_source_location=_source_location)

        if zplog:
            self.LOG = zplog

        self.zenpack_spec = zenpack_spec
        self.path = path.lstrip("/")
        self.description = description

        if zProperties is None:
            self.zProperties = {}
        else:
            self.zProperties = zProperties

        self.create = bool(create)
        self.remove = bool(remove)
        self.reset = bool(reset)

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

    def set_zpl_managed(self, dmd):
        """
        zpl_managed was not set on device classes prior to 2.1.0
        so we set it now so that ZP uninstalls will work correctly
        """
        org_obj = self.get_organizer(dmd)
        if org_obj:
            if self.create and not hasattr(org_obj, 'zpl_managed'):
                org_obj.zpl_managed = True

    def create_organizer(self, dmd):
        """Return organizer whether existing or new"""
        org_obj = self.get_organizer(dmd)
        if org_obj:
            if self.reset:
                self.set_zproperties(dmd)
        else:
            if self.create:
                org_obj = self.get_root(dmd).createOrganizer(self.path)
                self.set_zproperties(dmd)
        self.set_zpl_managed(dmd)
        return org_obj

    def set_zproperties(self, dmd):
        """Set zProperties on a given Organizer according to the Spec"""
        org_obj = self.get_organizer(dmd)
        for zprop, value in self.zProperties.iteritems():
            if org_obj.getPropertyType(zprop) is None and org_obj.getProperty(zprop) is None:
                self.LOG.error(
                    "Unable to set zProperty %s on %s (undefined zProperty)",
                    zprop, self.path)
            else:
                self.LOG.debug(
                    "Setting zProperty %s to %r on %s (was %r)",
                    zprop, value, self.path, getattr(org_obj, zprop, ''))

                # We want to explicitly set the value even if it's the same as
                # what's being acquired. This is why aq_base is required.
                aq_base(org_obj).setZenProperty(zprop, value)

    def remove_organizer(self, dmd, zenpack=None):
        # also double-check that we do not remove anything important like /Status or Processes
        if self.path.lstrip('/') in RESERVED_CLASSES:
            self.LOG.debug("Not removing reserved organizer %s", self.path)
            return False

        org_obj = self.get_organizer(dmd)
        if not org_obj:
            self.LOG.info("Not removing nonexistent organzier %s", self.path)
            return False

        if zenpack:
            # Anything left in packables will be removed the platform.
            try:
                zenpack.packables.removeRelation(org_obj)
            except Exception:
                # The organizer wasn't in packables.
                pass

        self.set_zpl_managed(dmd)
        # make sure the organizer is zpl_managed before we try and delete it
        if self.remove and getattr(org_obj, 'zpl_managed', False):
            self.get_root(dmd).manage_deleteOrganizer(org_obj.getDmdKey())
            self.LOG.info('Removing {} {}'.format(org_obj.__class__.__name__, self.path))
            return True

    def remove_subs(self, dmd, map_name, remove_name):
        """Remove subclasses within an organizer
        Used for event classes, process classes, windows services
        The specs should use path to describe the organizer name/path
        For subclasses, use klass_string for the class type name
        Also be sure to set zpl_managed in the specs
        """
        org_obj = self.get_organizer(dmd)
        if not org_obj:
            return

        remove_func = getattr(org_obj, remove_name, None)
        if not remove_func:
            return

        for name, spec in getattr(self, map_name, {}).items():
            if not spec.remove:
                continue

            preppedId = org_obj.prepId(name)
            # make sure object is zpl managed
            try:
                obj = org_obj.findObject(preppedId)
            # skip this suborganizer as it has been removed previously
            except AttributeError:
                self.LOG.info('Skipping {} suborganizer remove as it has been removed previously.'.format(name))
                continue

            if getattr(obj, 'zpl_managed', False):
                self.LOG.info('Removing {} {} @ {}'.format(spec.klass_string, name, self.path))
                remove_func(preppedId)

    def remove_organizer_or_subs(self, dmd, map_name, remove_name, zenpack=None):
        """Remove the organizer or subclasses within an organizer
        """
        org_removed = self.remove_organizer(dmd, zenpack)
        if not org_removed:
            self.remove_subs(dmd, map_name, remove_name)
