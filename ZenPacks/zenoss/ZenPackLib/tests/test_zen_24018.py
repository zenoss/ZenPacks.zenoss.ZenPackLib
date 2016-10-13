#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test fix for ZEN-24108
    Device relations between ZPL-based ZenPacks overwrite inherited Device relations
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


RELATION_YAML = """
name: ZenPacks.zenoss.ZenPackLib
classes:
  BasicDeviceComponent:
    base: [zenpacklib.Component]
    properties:
      something:
        label: Something
  SubClassComponent:
    base: [zenpacklib.Component]

class_relationships:
  - Products.ZenModel.Device.Device 1:MC BasicDeviceComponent
  - ZenPacks.zenoss.ZPLDevice.NormDevice.NormDevice 1:MC SubClassComponent
"""


SUBCLASS_YAML = """
name: ZenPacks.zenoss.ZPLDevice
classes:
  BaseDevice:
    base: [zenpacklib.Device]
  NormDevice:
    base: [BaseDevice]
  ClusterDevice:
    base: [NormDevice]
"""


device_subclass_zp = ZPLTestHarness(SUBCLASS_YAML)
subclass_relation_zp = ZPLTestHarness(RELATION_YAML)

from Products.ZenModel.Device import Device as ZenDevice
from ZenPacks.zenoss.ZPLDevice.BaseDevice import BaseDevice
from ZenPacks.zenoss.ZPLDevice.NormDevice import NormDevice
from ZenPacks.zenoss.ZPLDevice.ClusterDevice import ClusterDevice


class TestZen24018(BaseTestCase):
    """Test fix for ZEN-24108

       Device relations between ZPL-based ZenPacks overwrite inherited Device relations
    """

    def test_inherited_relations(self):

        # all ZenModel.Device subclasses should have this relation
        for x in [ZenDevice, BaseDevice, NormDevice, ClusterDevice]:
            # should be True
            self.assertTrue(self.has_relation(x, 'basicDeviceComponents'),
                            '%s is missing relation: basicDeviceComponents' % x.__name__)

        # these should have subClassComponents
        for x in [NormDevice, ClusterDevice]:
            self.assertTrue(self.has_relation(x, 'subClassComponents'),
                            '%s is missing relation: subClassComponents' % x.__name__)

        # these should not have subClassComponents
        for x in [ZenDevice, BaseDevice]:
            self.assertFalse(self.has_relation(x, 'subClassComponents'),
                            '%s has unneeded relation: subClassComponents' % x.__name__)

    def has_relation(self, cls, relname):
        if relname in dict(cls._relations).keys():
            return True
        return False


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen24018))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
