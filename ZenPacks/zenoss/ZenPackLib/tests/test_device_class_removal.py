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

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib

device_classes:
  /Server/ZenPackLib:
    zProperties:
      zSnmpMonitorIgnore: False
    remove: true
"""


class TestDeviceClassRemoval(ZPLTestBase):
    """
    Test that device classes can be removed (ZEN-18134)
    """

    yaml_doc = YAML_DOC

    def test_device_class(self):
        # instantiate the ZenPack class
        zenpack = ZenPack(self.app)

        # create the device class
        for dcname, dcspec in self.z.cfg.device_classes.items():
            zenpack.create_device_class(self.app, dcspec)
            # verify that it was created
            self.assertTrue(self.device_class_exists(dcspec.path),
                            'Device class {} was not created'.format(dcspec.path))

        for dcname, dcspec in self.z.cfg.device_classes.iteritems():
            if dcspec.remove:
                zenpack.remove_device_class(self.app, dcspec)
                # verify that it was removed
                self.assertFalse(self.device_class_exists(dcspec.path),
                                'Device class {} was not removed'.format(dcspec.path))

    def device_class_exists(self, path):
        try:
            self.dmd.Devices.getOrganizer(path)
            return True
        except KeyError:
            return False

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeviceClassRemoval))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
