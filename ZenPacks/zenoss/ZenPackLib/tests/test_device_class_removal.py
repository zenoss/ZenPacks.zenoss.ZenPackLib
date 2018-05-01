#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test that device classes can be removed (ZEN-18134)
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.DeviceClasses

device_classes:
  /Server/ZenPackLib:
    zProperties:
      zSnmpMonitorIgnore: False
    remove: true
"""


class TestDeviceClassRemoval(ZPLBaseTestCase):
    """
    Test that device classes can be removed (ZEN-18134)
    """

    yaml_doc = YAML_DOC
    build = False

    def test_device_class(self):
        config = self.configs.get('ZenPacks.zenoss.DeviceClasses')
        cfg = config.get('cfg')

        # create the device class
        for dcname, dcspec in cfg.device_classes.items():
            dcspec.create_organizer(self.dmd)
            # verify that it was created
            self.assertTrue(self.device_class_exists(dcspec.path),
                            'Device class {} was not created'.format(dcspec.path))

        for dcname, dcspec in cfg.device_classes.iteritems():
            if dcspec.remove:
                dcspec.remove_organizer(self.dmd)
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
