#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Severity format validation YAML dump/load

"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Device:
    templates:
      TEST:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          A:
            type: MinMaxThreshold
            dsnames: [A_A]
            severity: 3
          B:
            type: MinMaxThreshold
            dsnames: [A_A]
            severity: Warning
          C:
            type: MinMaxThreshold
            dsnames: [A_A]
            severity: warning
          D:
            type: MinMaxThreshold
            dsnames: [A_A]
            severity: NotSure
          E:
            type: MinMaxThreshold
            dsnames: [A_A]
"""


EXPECTED = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Device:
    templates:
      TEST:
        thresholds:
          A:
            dsnames: [A_A]
            severity: 3
          B:
            dsnames: [A_A]
            severity: Warning
          C:
            dsnames: [A_A]
            severity: warning
          D:
            dsnames: [A_A]
            severity: NotSure
          E:
            dsnames: [A_A]
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: GAUGE
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
"""


class TestValidSeverity(ZPLTestBase):
    """Test severity input validation"""

    yaml_doc = YAML_DOC

    def test_valid_severity(self):
        self.assertEquals(self.z.exported_yaml, EXPECTED,
                        'YAML severity validation test failed, got: \n{}'.format(self.z.exported_yaml))

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestValidSeverity))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
