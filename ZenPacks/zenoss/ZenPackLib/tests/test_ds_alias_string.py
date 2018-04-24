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
    Test fix for ZEN-19486
    not entering dict of aliases in datapoint results in broken zenpack
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


YAML_DOC = """name: ZenPacks.zenoss.GOODAlias
device_classes:
  /Server:
    templates:
      Device:
        datasources:
          laLoadInt5:
            type: SNMP
            datapoints:
              laLoadInt5:
                aliases: {loadAverage5min: null}
            oid: 1.3.6.1.4.1.2021.10.1.5.2
"""

BAD_DOC = """name: ZenPacks.zenoss.BADAlias
device_classes:
  /Server:
    templates:
      Device:
        datasources:
          laLoadInt5:
            type: SNMP
            datapoints:
              laLoadInt5:
                aliases: loadAverage5min
            oid: 1.3.6.1.4.1.2021.10.1.5.2
"""


class TestDatapointAliasAsString(ZPLBaseTestCase):
    """Test fix for ZEN-19486"""

    def afterSetUp(self):
        super(TestDatapointAliasAsString, self).afterSetUp()
        self.initialize(YAML_DOC)
        self.initialize(BAD_DOC)

    def test_datapoint_aliases(self):
        ''''''
        good_cfg = self.configs.get('ZenPacks.zenoss.GOODAlias').get('cfg')
        bad_cfg = self.configs.get('ZenPacks.zenoss.BADAlias').get('cfg')
        dp_dict = self.get_alias(good_cfg)
        dp_str = self.get_alias(bad_cfg)
        self.assertEqual(dp_dict.aliases, dp_str.aliases, 'Datapoint aliases {} and {} do not match'.format(
                                                        dp_dict.aliases, dp_str.aliases))

    def get_alias(self, cfg):
        dcspec = cfg.device_classes.get('/Server')
        tspec = dcspec.templates.get('Device')
        return tspec.datasources.get('laLoadInt5').datapoints.get('laLoadInt5')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDatapointAliasAsString))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
