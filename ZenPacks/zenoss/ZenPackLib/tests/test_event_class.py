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
    Test Event Classes
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness

unused(Globals)


EVENT_CLASS_YAML = """
name: ZenPacks.zenoss.ZenPackLib
event_classes:
  /Status/Test:
    create: true
    remove: false
    description: Test event class
    transform: "from ZenPacks.zenoss.CiscoMonitor import transforms\\ntransforms.status_handler(device, component, evt)"
    mappings:
      TestMapping:
        eventClassKey: TestMapping
        sequence:  10
        example: Test Mapping example
        explanation: This is a test for an example mapping
        resolution: This is the resolution for the test mapping
        remove: true
        regex: +.*
        transform: "from ZenPacks.zenoss.CiscoMonitor import transforms\\ntransforms.status_handler(device, component, evt)"
        rule: "component.id == id"
"""


event_class_zp = ZPLTestHarness(EVENT_CLASS_YAML)


class TestEventClass(BaseTestCase):
    """Test Event Classes
    """

    def test_event_classes(self):
        self.assertEquals(len(event_class_zp.yaml['event_classes']), len(event_class_zp.cfg.event_classes))
        self.assertEquals(event_class_zp.yaml['event_classes'].keys()[0], event_class_zp.cfg.event_classes.keys()[0])
        self.assertTrue('/Status/Test' in event_class_zp.cfg.event_classes.keys())
        self.assertTrue(event_class_zp.yaml['event_classes']['/Status/Test']['create'])
        self.assertTrue(event_class_zp.cfg.event_classes['/Status/Test'].create)
        self.assertFalse(event_class_zp.yaml['event_classes']['/Status/Test']['remove'])
        self.assertFalse(event_class_zp.cfg.event_classes['/Status/Test'].remove)
        self.assertEquals(len(event_class_zp.yaml['event_classes']['/Status/Test']['mappings']),
                          len(event_class_zp.cfg.event_classes['/Status/Test'].mappings))
        self.assertEquals(event_class_zp.yaml['event_classes']['/Status/Test']['mappings']['TestMapping']['sequence'],
                          event_class_zp.cfg.event_classes['/Status/Test'].mappings['TestMapping'].sequence)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEventClass))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
