#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Test removal of undefined relations"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


YAML_DOC = """
name: ZenPacks.zenoss.TestLogging

classes:
  BaseDevice:
    base: [zenpacklib.Device]
    relationships:
      baseComponents: {}
      # this doesn't exist
      auxComponents: {}
      # These exist but aren't defined in this schema
      systems: {}
      deviceClass: {}
  BaseComponent:
    # Component Base Type
    base: [zenpacklib.Component]
    relationships:
      baseDevice: {}
      # this doesn't exist
      auxComponents: {}
  AuxComponent:
    # Component Base Type
    base: [zenpacklib.Component]
    relationships:
      # this exists but isn't defined in this schema
      dependents: {}

class_relationships:
- BaseDevice 1:MC BaseComponent
"""


EXPECTED = """[ERROR] Removing invalid display config for relationship auxComponents from  ZenPacks.zenoss.TestLogging.BaseDevice
[ERROR] Removing invalid display config for relationship systems from  ZenPacks.zenoss.TestLogging.BaseDevice
[ERROR] Removing invalid display config for relationship deviceClass from  ZenPacks.zenoss.TestLogging.BaseDevice
[ERROR] Removing invalid display config for relationship auxComponents from  ZenPacks.zenoss.TestLogging.BaseComponent
[ERROR] Removing invalid display config for relationship dependents from  ZenPacks.zenoss.TestLogging.AuxComponent
"""

class TestLoggingRelationsRemoval(ZPLBaseTestCase):
    disableLogging = False

    def test_undefined_relation_removal(self):
        actual = self.capture.test_yaml(YAML_DOC)
        self.assertEquals(actual, EXPECTED, 'Undefined relations removal testing failed:\n  {}'.format(actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLoggingRelationsRemoval))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
