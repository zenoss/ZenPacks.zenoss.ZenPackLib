#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Test Catalog Scope (ZEN-18269)
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


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


class TestCatalogScope(ZPLTestBase):
    """Test catalog creation for specs"""

    yaml_doc = YAML_DOC

    def test_catalog_specs(self):
        ''''''
        data = {'DeviceIndexedComponent': ['device_idx'],
                'GlobalIndexedComponent': ['global_idx'],
                'GlobalAndDeviceIndexedComponent': ['device_idx', 'global_idx'],
                }
        for name, expected in data.items():
            actual = self.get_scope(name)

            self.assertEqual(actual, expected, 'Expected catalog scope {}, got {} for {}'.format(expected, actual, name))

    def get_scope(self, name):
        ob = self.z.build_ob(name)
        return ob._device_catalogs.get(name, {}).keys() + ob._global_catalogs.get(name, {}).keys()


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
