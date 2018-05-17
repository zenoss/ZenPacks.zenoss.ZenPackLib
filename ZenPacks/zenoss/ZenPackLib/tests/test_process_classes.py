#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test Process Classes
    process_classes:

"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """name: ZenPacks.zenoss.Processes
process_class_organizers:
  Test:
    description: Description of the Process Class Organizer
    zProperties:
      zMonitor: false
    process_classes:
      foo:
        description: Description of the foo Process Class
        includeRegex: sbin\/foo
        replaceRegex: ".*"
        replacement: Foo Process Class
        excludeRegex: \\b(vim|tail|grep|tar|cat|bash)\\b
        zProperties:
          zMonitor: true
      bar:
        description: Description of the bar Process Class
        includeRegex: sbin\/bar
        excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
        replaceRegex: .*
        replacement: Bar Process Class
        alert_on_restart: false
        fail_severity: 3
        modeler_lock: 0
        send_event_when_blocked: true
"""


class TestProcessClass(ZPLBaseTestCase):
    """Test Process Classes
    """
    yaml_doc = YAML_DOC
    build = True

    def test_process_classes(self):
        config = self.configs.get('ZenPacks.zenoss.Processes')
        exported = config.get('yaml_map')
        organizers = config.get('cfg').process_class_organizers
        self.assertEquals(len(exported['process_class_organizers']), 1)
        self.assertEquals(len(exported['process_class_organizers']), len(organizers))
        self.assertEquals(exported['process_class_organizers'].keys()[0], organizers.keys()[0])
        self.assertTrue('Test' in organizers.keys())
        self.assertEquals(organizers['Test'].description, "Description of the Process Class Organizer")

        cfg_process_classes = organizers['Test'].process_classes

        self.assertIsNotNone(cfg_process_classes)
        self.assertEquals(len(cfg_process_classes), 2)
        self.assertEquals(cfg_process_classes['foo'].includeRegex, 'sbin\/foo')
        self.assertEquals(cfg_process_classes['foo'].excludeRegex, '\\b(vim|tail|grep|tar|cat|bash)\\b')
        self.assertEquals(cfg_process_classes['foo'].replaceRegex, '.*')
        self.assertEquals(cfg_process_classes['foo'].replacement, 'Foo Process Class')

        self.assertEquals(cfg_process_classes['bar'].excludeRegex, "\x08(vim|tail|grep|tar|cat|bash)\x08")
        self.assertFalse(cfg_process_classes['bar'].alert_on_restart)
        self.assertTrue(cfg_process_classes['bar'].send_event_when_blocked)
        self.assertEquals(cfg_process_classes['bar'].fail_severity, 3)
        self.assertEquals(cfg_process_classes['bar'].modeler_lock, 0)

    def test_process_class_org(self):
        """Test that process class is created and properties are accurate"""
        config = self.configs.get('ZenPacks.zenoss.Processes')
        objects = config.get('objects').process_class_objects
        ob = objects['Test']['ob']
        self.assertEquals(ob.zMonitor, False,
            '{} zProperty was not set correctly'.format(ob.id))

    def test_process_class_mapping(self):
        """Test that event process is created and properties are accurate"""
        config = self.configs.get('ZenPacks.zenoss.Processes')
        objects = config.get('objects').process_class_objects
        foo_ob = objects['Test']['classes']['foo']
        bar_ob = objects['Test']['classes']['bar']
        self.assertEquals(foo_ob.zMonitor, True,
            '{} zProperty was not set correctly'.format(foo_ob.id))
        self.assertEquals(bar_ob.zMonitor, False,
            '{} zProperty was not set correctly'.format(bar_ob.id))


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
