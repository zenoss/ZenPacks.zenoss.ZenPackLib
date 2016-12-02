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
    Test that modeler plugins are appended or replaced (ZEN-24901) 
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
      zCollectorPlugins:
        - zenoss.snmp.DeviceMap
        - snmp.bigip.DeviceMap
"""


class TestCollectorPlugins(BaseTestCase):
    """
    Test that modeler plugins are appended or replaced
    """

    def test_device_class_plugins(self):
        path = '/Server/ZenPackLib'
        dummy_plugin = 'dummy.plugin'
        z = ZPLTestHarness(YAML_DOC)
        z.connect()

        # instantiate the ZenPack class
        zenpack = ZenPack(z.dmd)

        # create device class
        dcObject = z.dmd.Devices.createOrganizer(path)
        # add our preexisting plugin
        dcObject.setZenProperty('zCollectorPlugins', [dummy_plugin])

        self.assertTrue(len(dcObject.zCollectorPlugins) == 1, 'device class not created properly')

        # create/update existing like install would
        dcspec = z.cfg.device_classes.get(path)
        dc = zenpack.create_device_class(z, dcspec)

        # verify that dummy plugin still exists
        self.assertTrue(dummy_plugin in dc.zCollectorPlugins, 'zCollectorPlugins not updated properly after update')
        # verify that count is now 3
        self.assertTrue(len(dc.zCollectorPlugins) == 3, 'zCollectorPlugins not updated properly after update')

        # test "removal"
        zenpack.remove_device_class(z, dcspec)

        # verify that dummy plugin still exists
        self.assertTrue(dummy_plugin in dcObject.zCollectorPlugins, 'zCollectorPlugins not updated properly after removal')
        # verify that count is now 3
        self.assertTrue(len(dcObject.zCollectorPlugins) == 1, 'zCollectorPlugins not updated properly after removal')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCollectorPlugins))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
