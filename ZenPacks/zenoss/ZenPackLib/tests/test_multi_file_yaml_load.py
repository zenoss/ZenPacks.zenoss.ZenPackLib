#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Multi-YAML import load

Tests YAML loading from multiple files

"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib

classes:
  DeviceIndexedComponent:
    base: [zenpacklib.Component]
    properties:
      basic:
        label: Basic
      device_idx:
        label: Device Indexed
        index_type: field
        index_scope: device
        default: blah
  GlobalIndexedComponent:
    base: [zenpacklib.Component]
    properties:
      basic:
        label: Basic
      global_idx:
        label: Global Indexed
        index_type: field
        index_scope: global
        default: blah
  GlobalAndDeviceIndexedComponent:
    base: [zenpacklib.Component]
    properties:
      basic:
        label: Basic
      global_idx:
        label: Global Indexed
        index_type: field
        index_scope: global
        default: blah
      device_idx:
        label: Device Indexed
        index_type: field
        index_scope: device
        default: blah
"""


class TestCatalogScope(BaseTestCase):
    """Test catalog creation for specs"""
    Z = ZPLTestHarness(YAML_DOC)

    def test_catalog_specs(self):
        ''''''
        data = {'DeviceIndexedComponent': {'device'},
                'GlobalIndexedComponent': {'global'},
                'GlobalAndDeviceIndexedComponent': {'device', 'global'},
                }
        for name, expected in data.items():
            actual = self.get_scope(name)
            self.assertEqual(actual, expected, 'Expected catalog scope {}, got {} for {}'.format(expected, actual, name))

    def get_scope(self, name):
        ob = self.Z.build_ob(name)
        return ob.get_catalog_scopes(name)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogScope))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
