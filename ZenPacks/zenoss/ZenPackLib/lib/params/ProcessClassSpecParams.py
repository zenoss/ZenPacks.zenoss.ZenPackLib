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
from ..spec.ProcessClassSpec import ProcessClassSpec


class ProcessClassSpecParams(SpecParams, ProcessClassSpec):
    def __init__(self,
                 zenpack_spec,
                 name,
                 description='',
                 remove=False,
                 includeRegex='',
                 excludeRegex='',
                 replaceRegex='',
                 replacement='',
                 monitor=None,
                 alert_on_restart=None,
                 fail_severity=None,
                 modeler_lock=None,
                 send_event_when_blocked=None,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.description = description
        self.remove = remove
        self.includeRegex = includeRegex
        self.excludeRegex = excludeRegex
        self.replaceRegex = replaceRegex
        self.replacement = replacement
        self.monitor = monitor
        self.alert_on_restart = alert_on_restart
        self.fail_severity = fail_severity
        self.modeler_lock = modeler_lock
        self.send_event_when_blocked = send_event_when_blocked

    @classmethod
    def fromObject(cls, processclass, remove=False):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        processclass = aq_base(processclass)

        _properties = ['description', 'includeRegex', 'excludeRegex',
                       'replacement', 'zMonitor', 'zAlertOnRestart',
                       'zFailSeverity', 'zModelerLock', 'zSendEventWhenBlockedFlag']

        for x in _properties:
            setattr(self, x, getattr(processclass, x, None))

        self.remove = remove
        return self
