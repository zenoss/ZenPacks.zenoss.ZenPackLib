##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .SpecParams import SpecParams
from ..spec.ProcessClassSpec import ProcessClassSpec


class ProcessClassSpecParams(SpecParams, ProcessClassSpec):
    def __init__(self,
                 zenpack_spec,
                 name,
                 description='',
                 include_processes='',
                 exclude_processes='',
                 replace_text='',
                 with_text='',
                 monitor=None,
                 alert_on_restart=None,
                 fail_severity=None,
                 modeler_lock=None,
                 send_event_when_blocked=None,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.include_processes = include_processes
        self.exclude_processes = exclude_processes
        self.replace_text = replace_text
        self.with_text = with_text
        self.monitor = monitor
        self.alert_on_restart = alert_on_restart
        self.fail_severity = fail_severity
        self.modeler_lock = modeler_lock
        self.send_event_when_blocked = send_event_when_blocked
