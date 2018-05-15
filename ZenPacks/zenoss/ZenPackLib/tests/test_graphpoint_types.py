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
    Test various GraphPoint types
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.GraphPoints
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
          b:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Test:
            graphpoints:
              A:
                dpName: A_A
                legend: Legend A
                color: BBBBBB
                lineType: AREA
                lineWidth: 2
                stacked: true
                format: "%7.2lf%s"
                rpn: 1024,*
                cFunc: LAST
              B:
                type: CommentGraphPoint
                text: Text Description
              C:
                type: ThresholdGraphPoint
                legend: Legend C
                threshId: b
              D:
                dpName: A_A
                limit: 100
                colorindex: 1
                
"""


class TestGraphPointTypes(ZPLBaseTestCase):
    """Test Threshold GraphPoint legend and coloring"""

    yaml_doc = YAML_DOC
    disableLogging = False
    build = True

    def get_graph_and_spec(self):
        config = self.configs.get('ZenPacks.zenoss.GraphPoints')
        cfg = config.get('cfg')
        dc_obs = config.get('objects').device_class_objects
        template = dc_obs.get('/Devices').get('templates').get('TEST')
        template_spec = cfg.device_classes.get('/Devices').templates.get('TEST')
        g = template.graphDefs.findObject('Test')
        g_spec = template_spec.graphs.get('Test')
        return g, g_spec

    def test_graphpoints(self):
        """Test that created object attributes match their specs"""
        g, g_spec = self.get_graph_and_spec()
        gp_a = g.graphPoints.findObject('A')
        gp_a_spec = g_spec.graphpoints.get('A')
        for x in ['legend', 'color', 'lineType', 'lineWidth',
            'stacked', 'format', 'rpn', 'cFunc']:
            self.is_equal(gp_a, gp_a_spec, x)

        gp_b = g.graphPoints.findObject('B')
        gp_b_spec = g_spec.graphpoints.get('B')
        self.is_equal(gp_b, gp_b_spec, 'text')

        gp_c = g.graphPoints.findObject('C')
        gp_c_spec = g_spec.graphpoints.get('C')
        self.is_equal(gp_c, gp_c_spec, 'legend')
        self.is_equal(gp_c, gp_c_spec, 'threshId')

    def test_A(self):
        g, g_spec = self.get_graph_and_spec()
        gp_a = g.graphPoints.findObject('A')
        gp_a_spec = g_spec.graphpoints.get('A')
        for x in ['legend', 'color', 'lineType', 'lineWidth',
            'stacked', 'format', 'rpn', 'cFunc']:
            self.is_equal(gp_a, gp_a_spec, x)

    def test_B(self):
        g, g_spec = self.get_graph_and_spec()
        gp_b = g.graphPoints.findObject('B')
        gp_b_spec = g_spec.graphpoints.get('B')
        self.is_equal(gp_b, gp_b_spec, 'text')

    def test_C(self):
        g, g_spec = self.get_graph_and_spec()
        gp_c = g.graphPoints.findObject('C')
        gp_c_spec = g_spec.graphpoints.get('C')
        self.is_equal(gp_c, gp_c_spec, 'legend')
        self.is_equal(gp_c, gp_c_spec, 'threshId')

    def test_D(self):
        g, g_spec = self.get_graph_and_spec()
        gp_d = g.graphPoints.findObject('D')
        gp_d_spec = g_spec.graphpoints.get('D')
        self.is_equal(gp_d, gp_d_spec, 'limit')
        self.assertEquals(gp_d.color, '0000ff',
            'GraphPoint {} attribute {} expected: {}, got: {}'.format(
            gp_d.id, 'color', '0000ff', gp_d.color))

    def is_equal(self, ob, spec, attribute):
        actual = getattr(ob, attribute)
        expected = getattr(spec, attribute, spec.extra_params.get(attribute))

        self.assertEquals(actual, expected,
            'GraphPoint {} attribute {} expected: {}, got: {}'.format(
            ob.id, attribute, expected, actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGraphPointTypes))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()

