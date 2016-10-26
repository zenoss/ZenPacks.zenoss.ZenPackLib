##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .Spec import Spec
from Products.ZenModel.WinServiceClass import WinServiceClass

"""Process Class Specs"""


class WindowsServiceSpec(Spec):
    """Initialize a Process Set via Python at install time."""
    def __init__(
            self,
            zenpack_spec,
            name,
            description='',
            monitoredStartModes=None,
            remove=False,
            monitor=None,
            fail_severity=None,
            _source_location=None,
            zplog=None):
        """
          :param description: Description of Process Class Set
          :type description: str
          :param monitoredStartModes: list of monitored start modes
          :type monitoredStartModes: list(str)
          :param monitor: Enable Monitoring?
          :type monitor: bool
          :param fail_severity: Failure Event Severity
          :type fail_severity: bool
          :param remove: Remove Organizer on ZenPack removal
          :type remove: boolean
        """
        super(WindowsServiceSpec, self).__init__(_source_location=_source_location)
        self.klass_string = 'WindowsServiceClass'
        self.zenpack_spec = zenpack_spec
        self.name = name
        self.description = description
        if monitoredStartModes and not isinstance(monitoredStartModes, list):
            raise TypeError('Property monitoredStartModes on {} must be a list'.format(name))

        validStartModes = ['Auto', 'Manual', 'Disabled', 'Not Installed']
        for mode in monitoredStartModes:
            if mode not in validStartModes:
                raise TypeError('Property monitoredStartModes on {} contains an invalid start mode.'
                                "  It must be one or more of '{}'".format("', '".join(validStartModes)))
        self.monitoredStartModes = monitoredStartModes
        self.remove = remove
        if zplog:
            self.LOG = zplog
        self.monitor = monitor
        self.fail_severity = fail_severity

    def create(self, dmd, org):
        # get existing process class
        try:
            windows_service = org.getObjByPath(org.getPrimaryUrlPath() + "/serviceclasses/" + self.name)
        except Exception:
            windows_service = org.manage_addServiceClass(self.name)
            windows_service.__class__ = WinServiceClass

        bChanged = False

        monitoredStartModes = getattr(windows_service, 'monitoredStartModes', None)
        if monitoredStartModes != self.monitoredStartModes:
            bChanged = True
            monitoredStartModes = self.monitoredStartModes

        description = windows_service.description
        if description != self.description:
            bChanged = True
            description = self.description

        if bChanged:
            # If something changed, then update the class
            windows_service.manage_editServiceClass(
                monitoredStartModes=monitoredStartModes,
                description=description)
        if self.monitor is not None:
            windows_service.setZenProperty('zMonitor', self.monitor)

        if self.fail_severity is not None:
            windows_service.setZenProperty('zFailSeverity', self.fail_severity)

        # Flag this as a ZPL managed object, that is, one that should not be
        # exported to objects.xml  (contained objects will also be excluded)
        windows_service.zpl_managed = True
