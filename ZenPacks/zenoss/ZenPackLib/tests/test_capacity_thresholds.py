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
    Verify that Capacity Thresholds are handled whether or not Capacity ZenPack is installed
"""

from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase
import ZenPacks.zenoss.ZenPackLib.lib.spec.RRDTemplateSpec

YAML_DOC = """
name: ZenPacks.zenoss.UsesCapacityThresholds
device_classes:
  /Devices:
    templates:
      Template:
        datasources:
          stats:
            type: SNMP
            oid: 1.3.6.1.4.1.2021.10.1.5.2
            datapoints:
              used: GAUGE
              total: GAUGE
        thresholds:
          storage_capacity:
            type: CapacityThreshold
            eventClass: /Capacity/Storage
            dsnames: [stats_used, stats_total]
            capacity_type: storage
            total_expression: stats_used
            used_expression: stats_total
            pct_threshold: 99.0
"""


class TestCapacityThresholds(ZPLBaseTestCase):
    """ Test that custom datasource/threshold class attributes are handled correctly"""

    yaml_doc = YAML_DOC

    def test_without_capacity(self):
        """Verify that thresholds are removed if Capacity ZenPack is not installed"""
        ZenPacks.zenoss.ZenPackLib.lib.spec.RRDTemplateSpec.CAPACITY_INSTALLED = False
        num_thresholds = self.get_num_thresholds()
        self.assertEqual(
            num_thresholds, 0,
            'Expected {} capacity threshold, got {}'.format(0, num_thresholds)),

    def test_with_capacity(self):
        """Verify that thresholds are removed if Capacity ZenPack is installed"""
        ZenPacks.zenoss.ZenPackLib.lib.spec.RRDTemplateSpec.CAPACITY_INSTALLED = True
        num_thresholds = self.get_num_thresholds()
        self.assertEqual(
            num_thresholds, 1,
            'Expected {} capacity threshold, got {}'.format(1, num_thresholds)),

    def get_num_thresholds(self):
        self.initialize(self.yaml_doc)
        config = self.configs.get('ZenPacks.zenoss.UsesCapacityThresholds')
        cfg = config.get('cfg')
        thresholds = cfg.device_classes.get(
            '/Devices').templates.get('Template').thresholds
        return len(thresholds.keys())


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCapacityThresholds))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
