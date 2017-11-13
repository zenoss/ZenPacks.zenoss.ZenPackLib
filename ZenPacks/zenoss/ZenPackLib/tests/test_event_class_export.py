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

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import compare_zenpackspecs

YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
event_classes:
  /Status/Test:
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

EXPECTED = """name: ZenPacks.zenoss.ZenPackLib
event_classes:
  /Status/Test:
    description: Test event class
    transform: |-
      from ZenPacks.zenoss.CiscoMonitor import transforms
      transforms.status_handler(device, component, evt)
    mappings:
      TestMapping:
        eventClassKey: TestMapping
        sequence: 10
        rule: component.id == id
        regex: +.*
        transform: |-
          from ZenPacks.zenoss.CiscoMonitor import transforms
          transforms.status_handler(device, component, evt)
        example: Test Mapping example
        explanation: This is a test for an example mapping
        resolution: This is the resolution for the test mapping
        remove: true
"""


class TestEventClass(ZPLTestBase):
    """Test Event Classes
    """
    yaml_doc = YAML_DOC

    def test_exported_multiline(self):
        self.assertEquals(self.z.exported_yaml,
                          EXPECTED,
                          'Multi-line export differs from expected:\n{}\ngot:\n{}'.format(
                                                                  EXPECTED,
                                                                  self.z.exported_yaml))


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
