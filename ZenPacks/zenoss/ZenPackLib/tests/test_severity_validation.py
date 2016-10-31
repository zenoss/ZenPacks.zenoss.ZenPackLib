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

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase

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
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
"""

class TestValidSeverity(BaseTestCase):
    """Test color input validation"""

    def test_valid_color(self):
        ''''''
        loaded = yaml.load(YAML_DOC, Loader=Loader)
        dumped = yaml.dump(loaded, Dumper=Dumper)

        self.assertEquals(dumped, EXPECTED,
                        'YAML severity validation test failed, got: \n{}'.format(dumped))

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
