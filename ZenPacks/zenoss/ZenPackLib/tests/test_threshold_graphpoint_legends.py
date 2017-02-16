#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" 
    Test Threshold GraphPoint legend and coloring (ZEN-24904)
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase

YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Devices:
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
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
          b:
            type: MinMaxThreshold
            dsnames: [A_A]
          c:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Test:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
                thresholdLegends:
                  a:
                    legend: test_a
                    color: 234234
                  b:
                    legend: test_b
                  c:
                    color: AAAAAA
"""

EXPECTED = {'A': {'color': '', 'legend': '${graphPoint/id}'},
            'a': {'color': '234234', 'legend': 'test_a'},
            'b': {'color': '', 'legend': 'test_b'},
            'c': {'color': 'AAAAAA', 'legend': '${graphPoint/id}'}}


class TestThresholdGraphPointLegends(ZPLTestBase):
    """Test Threshold GraphPoint legend and coloring"""

    yaml_doc = YAML_DOC

    def test_threshold_graphpoint(self):
        ''''''
        tspec = self.z.cfg.device_classes.get('/Devices').templates.get('TEST')
        # template based on original spec
        template = tspec.create(self.dmd, False)
        g = template.graphDefs()[0]
        actual = {}
        for gp in g.graphPoints():
            actual[gp.id] = {'legend': gp.legend, 'color': gp.color}
        self.assertEqual(actual, EXPECTED,
                         'Threshold GraphPoint legend/color testing failed, '\
                         'expected {} got {}'.format(EXPECTED, actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestThresholdGraphPointLegends))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()

