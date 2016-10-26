##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .Spec import Spec
from .WindowsServiceSpec import WindowsServiceSpec
from Products.ZenModel.ServiceOrganizer import manage_addServiceOrganizer


class WindowsServiceOrganizerSpec(Spec):
    """Initialize a Windows Service via Python at install time."""
    def __init__(
            self,
            zenpack_spec,
            path,
            description='',
            remove=False,
            monitor=None,
            fail_severity=None,
            windows_services=None,
            _source_location=None,
            zplog=None):
        """
          :param description: Description of Windows Service Organizer
          :type description: str
          :param windows_services: Windows Service specs
          :type windows_services: SpecsParameter(WindowsServiceSpec)
          :param remove: Remove Organizer on ZenPack removal
          :type remove: boolean
          :param monitor: Enable Monitoring?
          :type monitor: boolean
          :param fail_severity: Failure Event Severity
          :type fail_severity: int
        """
        self.path = path
        self.description = description
        self.remove = remove
        self.monitor = monitor
        self.fail_severity = fail_severity
        self.windows_services = self.specs_from_param(
            WindowsServiceSpec, 'windows_services', windows_services, zplog=self.LOG)

    def create(self, dmd):
        # get/create windows service organizer
        bCreated = False
        try:
            org = dmd.Services.getOrganizer(self.path)
            bCreated = getattr(org, 'zpl_managed', False)
        except KeyError:
            path = '/'
            root = None
            for name in self.path.split('/'):
                if name:
                    path += name
                    try:
                        root = dmd.Services.getOrganizer(path)
                    except KeyError:
                        manage_addServiceOrganizer(root, name)
            org = dmd.Services.getOrganizer(self.path)
            bCreated = True

        if org.description != self.description:
            org.description = self.description

        if self.monitor is not None:
            org.setZenProperty('zMonitor', self.monitor)

        if self.fail_severity is not None:
            org.setZenProperty('zFailSeverity', self.fail_severity)
        # Flag this as a ZPL managed object, that is, one that should not be
        # exported to objects.xml  (contained objects will also be excluded)
        # only if we created it
        org.zpl_managed = bCreated
        for windows_service_id, windows_service_spec in self.windows_services.items():
            windows_service_spec.create(dmd, org)
