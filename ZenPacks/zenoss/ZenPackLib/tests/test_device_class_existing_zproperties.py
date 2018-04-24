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
    Test that device classes can optionally have their zProperties reset (ZPS-810)
"""

from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.DeviceClasses

device_classes:
  /Server:
    zProperties:
      zSnmpMonitorIgnore: False
    reset: true
"""


class TestZPropertyReset(ZPLBaseTestCase):
    """
    Test that device classes can be removed (ZEN-18134)
    """

    yaml_doc = YAML_DOC
    build = False

    def test_device_class(self):
        config = self.configs.get('ZenPacks.zenoss.DeviceClasses')
        cfg = config.get('cfg')
        zenpack = cfg._zenpack_class(self.app)

        # create the device class
        for dcname, dcspec in cfg.device_classes.items():
            zenpack.create_device_class(self.app, dcspec)
            # verify that it was created
            dc = self.device_class_exists(dcspec.path)
            self.assertTrue(dc,
                'Device class {} does not exist'.format(dcspec.path))

        for dcname, dcspec in cfg.device_classes.iteritems():
            if dcspec.reset:
                zenpack.set_zproperties(self.app, dc, dcspec)
            self.assertFalse(getattr(dc, 'zSnmpMonitorIgnore'),
                'Device class {} zProperty was not set correctly'.format(dcspec.path))

    def device_class_exists(self, path):
        try:
            ob = self.dmd.Devices.getOrganizer(path)
            return ob
        except KeyError:
            return


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZPropertyReset))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
