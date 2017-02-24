##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import re
from .Spec import Spec
from ..base.types import Severity

"""Process Class Specs"""


class ProcessClassSpec(Spec):
    """Initialize a Process Set via Python at install time."""
    def __init__(
            self,
            porg_spec,
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
            _source_location=None,
            zplog=None):
        """
          :param description: Description of Process Class Set
          :type description: str
          :param includeRegex: Processes to include
          :type includeRegex: str
          :param excludeRegex: Processes to exclude
          :type excludeRegex: str
          :param replaceRegex: Replace command line text, regex
          :type replaceRegex: str
          :param replacement: Text to show instead of command line
          :type replacement: str
          :param monitor: Enable Monitoring?
          :type monitor: bool
          :param alert_on_restart: Send Event on Restart?
          :type alert_on_restart: bool
          :param fail_severity: Failure Event Severity (0-5)
          :type fail_severity: Severity
          :param modeler_lock: Lock Process Components, should be one of 0 (UNLOCKED), 1 (DELETE_LOCKED), 2 (UPDATE_LOCKED)
          :type modeler_lock: int
          :param send_event_when_blocked: Send and event when action is blocked?
          :type send_event_when_blocked: bool
          :param remove: Remove Organizer on ZenPack removal
          :type remove: boolean
        """
        super(ProcessClassSpec, self).__init__(_source_location=_source_location)
        self.klass_string = 'OSProcessClass'
        self.porg_spec = porg_spec
        self.name = name
        self.description = description
        self.remove = remove
        if zplog:
            self.LOG = zplog
        try:
            re.compile(includeRegex)
        except re.error as e:
            raise Exception("includeRegex {} will not compile: {}".format(includeRegex), e)
        self.includeRegex = includeRegex

        try:
            re.compile(excludeRegex)
        except re.error as e:
            raise Exception("excludeRegex {} will not compile: {}".format(excludeRegex), e)
        self.excludeRegex = excludeRegex

        try:
            re.compile(replaceRegex)
        except re.error as e:
            raise Exception("replaceRegex {} will not compile: {}".format(replaceRegex), e)
        self.replaceRegex = replaceRegex

        self.replacement = replacement
        self.monitor = monitor
        self.alert_on_restart = alert_on_restart
        Severity.LOG = self.LOG
        self.fail_severity = Severity(fail_severity)
        self.modeler_lock = modeler_lock
        self.send_event_when_blocked = send_event_when_blocked

    def create(self, dmd, porg, addToZenPack=True):
        # get existing process class
        process_class = None
        for pc in porg.osProcessClasses():
            if pc.id == self.name:
                process_class = pc
                break

        if not process_class:
            process_class = porg.manage_addOSProcessClass(self.name)

        bChanged = False
        includeRegex = process_class.includeRegex
        if process_class.includeRegex != self.includeRegex:
            bChanged = True
            includeRegex = self.includeRegex

        excludeRegex = process_class.excludeRegex
        if process_class.excludeRegex != self.excludeRegex:
            bChanged = True
            excludeRegex = self.excludeRegex

        replaceRegex = process_class.replaceRegex
        if process_class.replaceRegex != self.replaceRegex:
            bChanged = True
            replaceRegex = self.replaceRegex

        replacement = process_class.replacement
        if process_class.replacement != self.replacement:
            bChanged = True
            replacement = self.replacement

        description = process_class.description
        if process_class.description != self.description:
            bChanged = True
            description = self.description

        if bChanged:
            # If something changed, then update the class
            process_class.manage_editOSProcessClass(
                includeRegex=includeRegex,
                excludeRegex=excludeRegex,
                replaceRegex=replaceRegex,
                replacement=replacement,
                description=description)
        if self.monitor is not None:
            process_class.setZenProperty('zMonitor', self.monitor)

        if self.alert_on_restart is not None:
            process_class.setZenProperty('zAlertOnRestart', self.alert_on_restart)

        if self.fail_severity is not None:
            process_class.setZenProperty('zFailSeverity', int(self.fail_severity))

        if self.modeler_lock is not None:
            process_class.setZenProperty('zModelerLock', self.modeler_lock)

        if self.send_event_when_blocked is not None:
            process_class.setZenProperty('zSendEventWhenBlockedFlag', self.send_event_when_blocked)

        # Flag this as a ZPL managed object, that is, one that should not be
        # exported to objects.xml  (contained objects will also be excluded)
        process_class.zpl_managed = True

        return self.return_or_add_to_zenpack(process_class, self.porg_spec.zenpack_spec.name, addToZenPack)
