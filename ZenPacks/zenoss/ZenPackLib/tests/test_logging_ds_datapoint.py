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
    Check DataPoint consistency (ZEN-19461)
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


# should be OK
GOOD_YAML = """
name: ZenPacks.zenoss.TestLogging
device_classes:
  /Devices:
    templates:
      Device:
        thresholds:
          CPU Utilization:
            dsnames: [ssCpuRawIdle_ssCpuRawIdle]
        datasources:
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.53.0
        graphs:
          CPU Idle:
            units: percentage
            graphpoints:
              ssCpuRawIdle:
                dpName: ssCpuRawIdle_ssCpuRawIdle
"""

# threshold/graph point has bad datapoints
INVALID_POINTS = """
name: ZenPacks.zenoss.TestLogging
device_classes:
  /Devices:
    templates:
      Device:
        thresholds:
          CPU Utilization:
            dsnames: [ssCpuRawIdle_ssCpuRawIdle, badReference_badReference]
        datasources:
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.53.0
        graphs:
          CPU Idle:
            units: percentage
            graphpoints:
              ssCpuRawIdle:
                dpName: ssCpuRawIdle_ssCpuRawIdle
              badGraphPoint:
                dpName: badReference_badReference
"""

# graph point has no valid datapoint
NO_VALID_POINTS = """
name: ZenPacks.zenoss.TestLogging
device_classes:
  /Devices:
    templates:
      Device:
        thresholds:
          CPU Utilization:
            dsnames: []
        datasources:
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.53.0
        graphs:
          CPU Idle:
            units: percentage
            graphpoints:
              ssCpuRawIdle:
                dpName: null
"""


class TestLoggingDatasourceDatapoint(ZPLBaseTestCase):
    """"""
    disableLogging = False

    def test_good_yaml(self):
        actual = self.capture.test_yaml(GOOD_YAML)
        self.assertEquals(actual, '', 'Datapoint validation failed:\n  {}'.format(actual))

    def test_invalid_yaml(self):
        expected = '[WARNING] Threshold CPU Utilization has invalid datapoints: badReference_badReference\n' \
            '[WARNING] Graph Point badGraphPoint has no valid datapoints\n'\
            '[WARNING] Graph Point badGraphPoint has invalid datapoints: badReference_badReference\n'
        actual = self.capture.test_yaml(INVALID_POINTS)
        self.assertEquals(actual, expected, 'Datapoint validation failed:\n  {}'.format(actual))

    def test_no_valid_yaml(self):
        expected = '[WARNING] Threshold CPU Utilization has no valid datapoints\n'\
        '[WARNING] Graph Point ssCpuRawIdle has no valid datapoints\n'\
        '[WARNING] Graph Point ssCpuRawIdle has invalid datapoints: null_null\n'
        actual = self.capture.test_yaml(NO_VALID_POINTS)
        self.assertEquals(actual, expected, 'Datapoint validation failed:\n  {}'.format(actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLoggingDatasourceDatapoint))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
