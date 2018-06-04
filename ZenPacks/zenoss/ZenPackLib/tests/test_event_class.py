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
    Test Event Classes
"""

from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.EventClasses
event_classes:
  /Status/Test:
    remove: false
    description: Test event class
    transform: "from ZenPacks.zenoss.CiscoMonitor import transforms\\ntransforms.status_handler(device, component, evt)"
    zProperties:
      zFlappingThreshold: 6
    mappings:
      TestMapping:
        zProperties:
          zFlappingThreshold: 4
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


class TestEventClass(ZPLBaseTestCase):
    """Test Event Classes
    """
    yaml_doc = YAML_DOC
    build = True

    def test_event_classes(self):
        config = self.configs.get('ZenPacks.zenoss.EventClasses')
        cfg = config.get('cfg')
        reloaded = config.get('yaml_map')
        self.assertEquals(len(reloaded['event_classes']), len(cfg.event_classes))
        self.assertEquals(reloaded['event_classes'].keys()[0], cfg.event_classes.keys()[0])
        self.assertTrue('/Status/Test' in cfg.event_classes.keys())
        self.assertFalse(cfg.event_classes['/Status/Test'].remove)
        self.assertEquals(len(reloaded['event_classes']['/Status/Test']['mappings']),
                          len(cfg.event_classes['/Status/Test'].mappings))
        self.assertEquals(reloaded['event_classes']['/Status/Test']['mappings']['TestMapping']['sequence'],
                          cfg.event_classes['/Status/Test'].mappings['TestMapping'].sequence)

    def test_event_class_org(self):
        """Test that event class is created and properties are accurate"""
        config = self.configs.get('ZenPacks.zenoss.EventClasses')
        ec_objects = config.get('objects').event_class_objects
        ec_ob = ec_objects['/Status/Test']['ob']
        self.assertEquals(ec_ob.zFlappingThreshold, 6,
            '{} zProperty was not set correctly'.format(ec_ob.id))

    def test_event_class_mapping(self):
        """Test that event class is created and properties are accurate"""
        config = self.configs.get('ZenPacks.zenoss.EventClasses')
        ec_objects = config.get('objects').event_class_objects
        ec_ob = ec_objects['/Status/Test']['mappings']['TestMapping']
        self.assertEquals(ec_ob.zFlappingThreshold, 4,
            '{} zProperty was not set correctly'.format(ec_ob.id))


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
