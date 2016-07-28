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
    This is designed to test whether or not a relation added to a 
    zenpacklib.Device subclass wipes out other relations added to 
    Products.ZenModel.Device (ZEN-24108)
"""

# stdlib Imports
import os
import unittest
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')

from .ZPLTestHarness import ZPLTestHarness

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


class TestZen24018(unittest.TestCase):

    """Specs test suite."""
    zps = []

    def setUp(self):
        fdir = '%s/data/yaml' % os.path.dirname(__file__)
        self.base_device_file = '%s/%s' % (fdir, 'zen-24018-1.yaml')
        self.device_subclass_file = '%s/%s' % (fdir, 'zen-24018-2.yaml')
        self.subclass_relation_file = '%s/%s' % (fdir, 'zen-24018-3.yaml')


    def test_inherited_relations(self):
        device_subclass_zp = ZPLTestHarness(self.device_subclass_file)
        base_device_zp = ZPLTestHarness(self.base_device_file)
        subclass_relation_zp = ZPLTestHarness(self.subclass_relation_file)

        from Products.ZenModel.Device import Device as ZenDevice
        from ZenPacks.zenoss.ZPLDevice.BaseDevice import BaseDevice
        from ZenPacks.zenoss.ZPLDevice.Device import Device
        from ZenPacks.zenoss.ZPLDevice.ClusterDevice import ClusterDevice

        # all ZenModel.Device subclasses should have this relation
        for x in [ZenDevice, BaseDevice, Device, ClusterDevice]:
            # should be True
            self.assertTrue(self.has_relation(ZenDevice, 'basicDeviceComponents'),
                            '%s is missing relation: basicDeviceComponents' % x.__name__)

        # these should have subClassComponents
        for x in [Device, ClusterDevice]:
            self.assertTrue(self.has_relation(ZenDevice, 'subClassComponents'),
                            '%s is missing relation: subClassComponents' % x.__name__)

        # these should not have subClassComponents
        for x in [ZenDevice, BaseDevice]:
            self.assertTrue(self.has_relation(ZenDevice, 'subClassComponents'),
                            '%s is missing relation: subClassComponents' % x.__name__)

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
