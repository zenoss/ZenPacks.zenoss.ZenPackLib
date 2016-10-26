##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .SpecParams import SpecParams
from .WindowsServiceSpecParams import WindowsServiceSpecParams
from ..spec.WindowsServiceOrganizerSpec import WindowsServiceOrganizerSpec


class WindowsServiceOrganizerSpecParams(SpecParams, WindowsServiceOrganizerSpec):
    def __init__(self,
                 zenpack_spec,
                 path,
                 description='',
                 windows_services=None,
                 monitor=None,
                 fail_severity=None,
                 remove=False,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.path = path
        self.description = description
        self.remove = remove
        self.monitor = monitor
        self.fail_severity = fail_severity
        self.windows_services = self.specs_from_param(
            WindowsServiceSpecParams, 'windows_services', windows_services)

    @classmethod
    def fromObject(cls, windowsservice, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)

        self.description = windowsservice.description
        self.remove = remove
        self.windows_services = {x.id: WindowsServiceSpecParams.fromObject(x) for x in windowsservice.serviceclasses()}
        return self

    @classmethod
    def new(cls, processclass, description='', remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        self.path = processclass
        self.description = description
        self.remove = remove
        return self
