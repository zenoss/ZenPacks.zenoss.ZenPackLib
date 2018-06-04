##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from .OrganizerSpec import OrganizerSpec
from .RRDTemplateSpec import RRDTemplateSpec


class DeviceClassSpec(OrganizerSpec):
    """Initialize a DeviceClass via Python at install time."""

    def __init__(
            self,
            zenpack_spec,
            path,
            description=None,
            zProperties=None,
            create=True,
            remove=False,
            reset=False,
            protocol=None,
            templates=None,
            _source_location=None,
            zplog=None):
        """
            Create a DeviceClass Specification

            :param description: Description used for registering devtype
            :type description: str
            :param zProperties: zProperty values to set upon this DeviceClass
            :type zProperties: dict(str)
            :param create: Create the DeviceClass with ZenPack installation, if it does not exist?
            :type create: bool
            :param remove: Remove the DeviceClass when ZenPack is removed?
            :type remove: bool
            :param reset:  If True, reset any zProperties that differ from given
            :type reset: bool
            :param protocol: Protocol to use for registered devtype
            :type protocol: str
            :param templates: TODO
            :type templates: SpecsParameter(RRDTemplateSpec)
        """
        super(DeviceClassSpec, self).__init__(
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

        self.protocol = protocol

        self.templates = self.specs_from_param(
            RRDTemplateSpec, 'templates', templates, zplog=self.LOG)

    def get_root(self, dmd):
        """Return the root object for this organizer."""
        return dmd.Devices

    def create_organizer(self, dmd):
        """Return existing or new device class organizer"""
        dc_org = super(DeviceClassSpec, self).create_organizer(dmd)
        if not dc_org:
            return
        self.register_devtype(dc_org)
        return dc_org

    def register_devtype(self, dc_org):
        """Register devtype for device class organizer"""
        if self.description and self.protocol:
            self.LOG.debug(
                "Registering devtype for %s: %s (%s)",
                self.path,
                self.protocol,
                self.description)
            try:
                # We want to explicitly set the value even if it's the same as
                # what's being acquired. This is why aq_base is required.
                aq_base(dc_org).register_devtype(
                    self.description,
                    self.protocol)
            except Exception as e:
                self.LOG.warn(
                    "Error registering devtype for %s: %s (%s)",
                    self.path,
                    self.protocol,
                    e)
