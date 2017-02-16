#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test Process Classes
    process_classes:

"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """name: ZenPacks.zenoss.Processes
process_class_organizers:
  Test:
    description: Description of the Process Class Organizer
    process_classes:
      foo:
        description: Description of the foo Process Class
        includeRegex: sbin\/foo
        replaceRegex: ".*"
        replacement: Foo Process Class
        excludeRegex: \\b(vim|tail|grep|tar|cat|bash)\\b
      bar:
        description: Description of the bar Process Class
        includeRegex: sbin\/bar
        excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
        replaceRegex: .*
        replacement: Bar Process Class
        monitor: true
        alert_on_restart: false
        fail_severity: 3
        modeler_lock: 0
        send_event_when_blocked: true
"""


class TestProcessClass(ZPLTestBase):
    """Test Process Classes
    """
    yaml_doc = YAML_DOC

    def test_process_classes(self):
        self.assertEquals(len(self.z.yaml['process_class_organizers']), 1)
        self.assertEquals(len(self.z.yaml['process_class_organizers']), len(self.z.cfg.process_class_organizers))
        self.assertEquals(self.z.yaml['process_class_organizers'].keys()[0], self.z.cfg.process_class_organizers.keys()[0])
        self.assertTrue('Test' in self.z.cfg.process_class_organizers.keys())
        self.assertEquals(self.z.cfg.process_class_organizers['Test'].description, "Description of the Process Class Organizer")

        cfg_process_classes = self.z.cfg.process_class_organizers['Test'].process_classes

        self.assertIsNotNone(cfg_process_classes)

        self.assertEquals(len(cfg_process_classes), 2)
        self.assertEquals(cfg_process_classes['foo'].includeRegex, 'sbin\/foo')
        self.assertEquals(cfg_process_classes['foo'].excludeRegex, '\\b(vim|tail|grep|tar|cat|bash)\\b')
        self.assertEquals(cfg_process_classes['foo'].replaceRegex, '.*')
        self.assertEquals(cfg_process_classes['foo'].replacement, 'Foo Process Class')

        self.assertEquals(cfg_process_classes['bar'].excludeRegex, "\x08(vim|tail|grep|tar|cat|bash)\x08")
        self.assertTrue(cfg_process_classes['bar'].monitor)
        self.assertFalse(cfg_process_classes['bar'].alert_on_restart)
        self.assertTrue(cfg_process_classes['bar'].send_event_when_blocked)
        self.assertEquals(cfg_process_classes['bar'].fail_severity, 3)
        self.assertEquals(cfg_process_classes['bar'].modeler_lock, 0)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProcessClass))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
