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
    Test accurate detection of template modifications
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack
from ZenPacks.zenoss.ZenPackLib.lib.params.RRDTemplateSpecParams import RRDTemplateSpecParams
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Loader import Loader


YAML_DOC = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Server:
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
          memBuffer:
            type: SNMP
            datapoints:
              memBuffer:
                aliases: {memoryBuffered__bytes: '1024,*'}
            oid: .1.3.6.1.4.1.2021.4.14.0
          laLoadInt5:
            type: SNMP
            datapoints:
              laLoadInt5:
                aliases: {loadAverage5min: '100,/'}
            oid: 1.3.6.1.4.1.2021.10.1.5.2
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle:
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {cpu__pct: '__EVAL:str(len(here.hw.cpus())) + '',/,100,EXC,-,0,MAX'''}
            oid: 1.3.6.1.4.1.2021.11.53.0
          ssCpuRawSystem:
            type: SNMP
            datapoints:
              ssCpuRawSystem: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.52.0
          ssCpuRawWait:
            type: SNMP
            datapoints:
              ssCpuRawWait: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.54.0
          sysUpTime:
            type: SNMP
            datapoints:
              sysUpTime: GAUGE
            oid: 1.3.6.1.2.1.25.1.1.0
          memAvailSwap:
            type: SNMP
            datapoints:
              memAvailSwap: GAUGE
            oid: 1.3.6.1.4.1.2021.4.4.0
          memCached:
            type: SNMP
            datapoints:
              memCached:
                aliases: {memoryCached__bytes: '1024,*'}
            oid: .1.3.6.1.4.1.2021.4.15.0
          memAvailReal:
            type: SNMP
            datapoints:
              memAvailReal:
                aliases: {memoryAvailable__bytes: '1024,*'}
            oid: 1.3.6.1.4.1.2021.4.6.0
          ssCpuRawUser:
            type: SNMP
            datapoints:
              ssCpuRawUser: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.50.0
        graphs:
          Load Average 5 min:
            units: processes
            graphpoints:
              laLoadInt5:
                dpName: laLoadInt5_laLoadInt5
                lineType: AREA
                format: '%0.2lf'
                rpn: 100,/
          Free Memory:
            units: bytes
            miny: 0
            graphpoints:
              memAvailReal:
                dpName: memAvailReal_memAvailReal
                lineType: AREA
                rpn: 1024,*
          CPU Idle:
            units: percentage
            graphpoints:
              ssCpuRawIdle:
                dpName: ssCpuRawIdle_ssCpuRawIdle
                lineType: AREA
                format: '%0.1lf%%'
                includeThresholds: true
          Free Swap:
            units: KBytes
            miny: 0
            graphpoints:
              memAvailSwap:
                dpName: memAvailSwap_memAvailSwap
                lineType: AREA
                format: '%0.2lf'
          CPU Utilization:
            units: percentage
            graphpoints:
              ssCpuRawSystem:
                dpName: ssCpuRawSystem_ssCpuRawSystem
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
              ssCpuRawWait:
                dpName: ssCpuRawWait_ssCpuRawWait
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
              ssCpuRawUser:
                dpName: ssCpuRawUser_ssCpuRawUser
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
          Load Average:
            units: load
            graphpoints:
              laLoadInt5:
                dpName: laLoadInt5_laLoadInt5
                lineType: AREA
                format: '%0.2lf'
                rpn: 100,/
"""

YAML_CHANGED = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Server:
    templates:
      Device:
        description: Net-SNMP template for late vintage unix device.  Has CPU threshold.
        thresholds:
          CPU Utilization:
            dsnames: [ssCpuRawIdle_ssCpuRawIdle]
            eventClass: /Perf/CPU
            minval: '3'
            escalateCount: 7
        datasources:
          memBuffer:
            type: SNMP
            datapoints:
              memBuffer:
                aliases: {memoryBuffered__bytes: '1024,*'}
            oid: .1.3.6.1.4.1.2021.4.14.0
          laLoadInt5:
            type: SNMP
            datapoints:
              laLoadInt5:
                aliases: {loadAverage5min: '100,/'}
            oid: 1.3.6.1.4.1.2021.10.1.5.2
          ssCpuRawIdle:
            type: SNMP
            datapoints:
              ssCpuRawIdle:
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {cpu__pct: '__EVAL:str(len(here.hw.cpus())) + '',/,100,EXC,-,0,MAX'''}
            oid: 1.3.6.1.4.1.2021.11.53.0
          ssCpuRawSystem:
            type: SNMP
            datapoints:
              ssCpuRawSystem: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.52.0
          ssCpuRawWait:
            type: SNMP
            datapoints:
              ssCpuRawWait: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.54.0
          sysUpTime:
            type: SNMP
            datapoints:
              sysUpTime: GAUGE
            oid: 1.3.6.1.2.1.25.1.1.0
          memAvailSwap:
            type: SNMP
            datapoints:
              memAvailSwap: GAUGE
            oid: 1.3.6.1.4.1.2021.4.4.0
          memCached:
            type: SNMP
            datapoints:
              memCached:
                aliases: {memoryCached__bytes: '1024,*'}
            oid: .1.3.6.1.4.1.2021.4.15.0
          memAvailReal:
            type: SNMP
            datapoints:
              memAvailReal:
                aliases: {memoryAvailable__bytes: '1024,*'}
            oid: 1.3.6.1.4.1.2021.4.6.0
          ssCpuRawUser:
            type: SNMP
            datapoints:
              ssCpuRawUser: DERIVE_MIN_0
            oid: 1.3.6.1.4.1.2021.11.50.0
        graphs:
          Load Average 5 min:
            units: processes
            graphpoints:
              laLoadInt5:
                dpName: laLoadInt5_laLoadInt5
                lineType: AREA
                format: '%0.2lf'
                rpn: 100,/
          Free Memory:
            units: bytes
            miny: 0
            graphpoints:
              memAvailReal:
                dpName: memAvailReal_memAvailReal
                lineType: AREA
                rpn: 1024,*
          CPU Idle:
            units: percentage
            graphpoints:
              ssCpuRawIdle:
                dpName: ssCpuRawIdle_ssCpuRawIdle
                lineType: AREA
                format: '%0.1lf%%'
                includeThresholds: true
          Free Swap:
            units: KBytes
            miny: 0
            graphpoints:
              memAvailSwap:
                dpName: memAvailSwap_memAvailSwap
                lineType: AREA
                format: '%0.2lf'
          CPU Utilization:
            units: percentage
            graphpoints:
              ssCpuRawSystem:
                dpName: ssCpuRawSystem_ssCpuRawSystem
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
              ssCpuRawWait:
                dpName: ssCpuRawWait_ssCpuRawWait
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
              ssCpuRawUser:
                dpName: ssCpuRawUser_ssCpuRawUser
                lineType: AREA
                stacked: true
                format: '%0.1lf%%'
          Load Average:
            units: load
            graphpoints:
              laLoadInt5:
                dpName: laLoadInt5_laLoadInt5
                format: '%0.2lf'
                rpn: 100,/
"""

DIFF = "--- \n+++ \n@@ -4,8 +4,8 @@\n   CPU Utilization:\n     dsnames: [ssCpuRawIdle_ssCpuRawIdle]\n     eventClass: /Perf/CPU\n-    minval: '2'\n-    escalateCount: 5\n+    minval: '3'\n+    escalateCount: 7\n datasources:\n   memBuffer:\n     type: SNMP\n@@ -113,7 +113,6 @@\n     graphpoints:\n       laLoadInt5:\n         dpName: laLoadInt5_laLoadInt5\n-        lineType: AREA\n         format: '%0.2lf'\n         rpn: 100,/\n \n"

class TestTemplateModified(BaseTestCase):
    """
    Test installed vs spec template changes
    """

    def test_modified(self):
        self.get_result(YAML_DOC, YAML_DOC)
        self.get_result(YAML_DOC, YAML_CHANGED, DIFF)

    def get_result(self, orig_doc, new_doc, expected=None):
        z_orig = ZPLTestHarness(orig_doc)
        z_new = ZPLTestHarness(new_doc)
        z_orig.connect()
        z_new.connect()
        zenpack = ZenPack(z_new.dmd)
        # original template spec
        orig_tspec = z_orig.cfg.device_classes.get('/Server').templates.get('Device')
        # template based on original spec
        orig_template = orig_tspec.create(z_orig.dmd, False)
        # new temlate spec
        new_tspec = z_new.cfg.device_classes.get('/Server').templates.get('Device')
        diff = zenpack.template_changed(z_new, orig_template, new_tspec)
        self.assertEquals(diff, expected, 'Expected:\n{}\ngot:\n{}'.format(expected, diff))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateModified))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
