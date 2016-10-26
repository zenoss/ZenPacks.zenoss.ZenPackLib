##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Acquisition import aq_base

from .SpecParams import SpecParams
from ..spec.WindowsServiceSpec import WindowsServiceSpec


class WindowsServiceSpecParams(SpecParams, WindowsServiceSpec):
    def __init__(self,
                 zenpack_spec,
                 name,
                 description='',
                 monitoredStartModes=None,
                 remove=False,
                 monitor=None,
                 fail_severity=None,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.description = description
        self.monitoredStartModes = monitoredStartModes
        self.remove = remove
        self.monitor = monitor
        self.fail_severity = fail_severity

    @classmethod
    def fromObject(cls, windowsservice, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        windowsservice = aq_base(windowsservice)

        _properties = ['description', 'monitoredStartModes',
                       'zMonitor', 'zFailSeverity']

        for x in _properties:
            setattr(self, x, getattr(windowsservice, x, None))

        self.remove = remove
        return self
