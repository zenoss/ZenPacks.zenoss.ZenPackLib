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
    Verify that "escalateCount" property works correctly (ZEN-22840)
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Devices:
    templates:
      Device:
        description: Net-SNMP template for late vintage unix device.  Has CPU threshold.
        thresholds:
          CPU Utilization:
            dsnames: [ssCpuRawIdle_ssCpuRawIdle]
            eventClass: /Perf/CPU
            minval: '2'
            escalateCount: 5
        datasources:
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle:
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {cpu__pct: '__EVAL:str(len(here.hw.cpus())) + '',/,100,EXC,-,0,MAX'''}
            oid: 1.3.6.1.4.1.2021.11.53.0

"""


class TestEscalateCount(ZPLTestBase):
    """Test for ZEN-22840
       Verify that "escalateCount" property works correctly
    """

    yaml_doc = YAML_DOC

    def test_escalate_count(self):
        deviceclass = self.z.cfg.device_classes.get('/Devices')
        template = deviceclass.templates.get('Device')
        t = template.create(self.dmd, False)
        th = t.thresholds.findObjectsById('CPU Utilization')[0]
        self.assertEquals(th.escalateCount, 5,
                          'Escalate Count expected {} ({}), got {} ({})'.format(5, 'int',
                                                                                th.escalateCount,
                                                                                type(th.escalateCount).__name__))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEscalateCount))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
