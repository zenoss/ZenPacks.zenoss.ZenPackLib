#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Color format validation YAML dump/load

"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack

YAML_DOC = """
name: ZenPacks.zenoss.Color
device_classes:
  /Server:
    templates:
      TEST:
        datasources:
          test:
            datapoints:
              a: GAUGE
              b: GAUGE
              c: GAUGE
        graphs:
          Graph:
            graphpoints:
              A:
                dpName: test_a
                color: 007700
              A2:
                dpName: test_a
                color: '007700'
              B:
                dpName: test_b
                color: FF3300
              C:
                dpName: test_c
                color: 0000BB
              D:
                dpName: test_c
                color: 000
              E:
                dpName: test_c
                color: JJJ0020
              F:
                dpName: test_c
"""

EXPECTED = """name: ZenPacks.zenoss.Color
device_classes:
  /Server:
    templates:
      TEST:
        datasources:
          test:
            datapoints:
              a: GAUGE
              b: GAUGE
              c: GAUGE
        graphs:
          Graph:
            graphpoints:
              A:
                dpName: test_a
                color: '007700'
              A2:
                dpName: test_a
                color: '007700'
              B:
                dpName: test_b
                color: FF3300
              C:
                dpName: test_c
                color: 0000BB
              D:
                dpName: test_c
                color: '000000'
              E:
                dpName: test_c
                color: FFF002
              F:
                dpName: test_c
"""


class TestValidInput(ZPLBaseTestCase):
    """Test color input validation"""
    yaml_doc = YAML_DOC

    def test_valid_color(self):
        ''''''
        config = self.configs.get('ZenPacks.zenoss.Color')
        yaml_param = config.get('yaml_from_specparams')
        yaml_spec = config.get('yaml_dump')

        diff = ZenPack.get_yaml_diff(EXPECTED, yaml_spec)
        self.assertEquals(yaml_spec, EXPECTED,
                        'YAML Color validation test failed:\n{}'.format(diff))

        diff = ZenPack.get_yaml_diff(yaml_param, yaml_spec)

        self.assertEquals(yaml_spec, yaml_param,
                        'YAML Color validation test failed:\n{}'.format(diff))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestValidInput))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
