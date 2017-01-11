#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Color format validation YAML dump/load

"""
# zenpacklib Imports
import yaml
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Loader import Loader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
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

EXPECTED = """name: ZenPacks.zenoss.ZenPackLib
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

class TestValidInput(BaseTestCase):
    """Test color input validation"""

    def test_valid_color(self):
        ''''''
        loaded = yaml.load(YAML_DOC, Loader=Loader)
        dumped = yaml.dump(loaded, Dumper=Dumper)


        self.assertEquals(dumped, EXPECTED,
                        'YAML Color validation test failed')


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
