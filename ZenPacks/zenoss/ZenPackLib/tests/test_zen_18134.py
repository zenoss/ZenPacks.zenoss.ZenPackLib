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
    Test that device classes can be removed (ZEN-18134)
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib

device_classes:
  /Server/ZenPackLib:
    zProperties:
      zSnmpMonitorIgnore: False
    remove: true
"""


class TestZen18134(BaseTestCase):
    """
    Test that device classes can be removed (ZEN-18134)
    """
    z = ZPLTestHarness(YAML_DOC)

    def test_device_class(self):
        self.z.connect()

        # instantiate the ZenPack class
        zenpack = ZenPack(self.z.dmd)

        # create the device class
        for dcname, dcspec in self.z.cfg.device_classes.items():
            dc = zenpack.create_device_class(self.z, dcspec)
            # verify that it was created
            self.assertTrue(self.device_class_exists(dcspec.path),
                            'Device class {} was not created'.format(dcspec.path))

        for dcname, dcspec in self.z.cfg.device_classes.iteritems():
            if dcspec.remove:
                zenpack.remove_device_class(self.z, dcspec)
                # verify that it was removed
                self.assertFalse(self.device_class_exists(dcspec.path),
                                'Device class {} was not removed'.format(dcspec.path))

    def device_class_exists(self, path):
        try:
            self.z.dmd.Devices.getOrganizer(path)
            return True
        except KeyError:
            return False

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen18134))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
