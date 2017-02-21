#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Spec unit tests.

This module tests zenpacklib  DynamicView functionality

"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib.lib.utils import dynamicview_installed


YAML_DOC = """
name: ZenPacks.zenpacklib.TestLinuxStorage

classes:
  DEFAULTS:
    dynamicview_views: []

  Linux:
    base: [zenpacklib.Device]
    dynamicview_views: [service_view]

  Process: {}

  Application:
    dynamicview_views: [service_view]

  PhysicalVolumeTarget: {}
  MountableDevice: {}

  PhysicalVolume:
    dynamicview_views: [linux_lvm_view]

  VolumeGroup:
    dynamicview_views: [linux_lvm_view]

  FileSystem:
    dynamicview_views: [linux_lvm_view]

  Disk:
    base: [zenpacklib.Component, PhysicalVolumeTarget]
    dynamicview_views: [linux_lvm_view]

  Partition:
    base: [zenpacklib.Component, PhysicalVolumeTarget, MountableDevice]
    dynamicview_views: [linux_lvm_view]

  LogicalVolume:
    base: [zenpacklib.Component, MountableDevice]
    dynamicview_views: [linux_lvm_view]

  SnapshotVolume:
    base: [zenpacklib.Component, LogicalVolume]
    dynamicview_views: [linux_lvm_view]

class_relationships:
  - Linux 1:MC Disk
  - Linux 1:MC PhysicalVolume
  - Linux 1:MC VolumeGroup
  - Linux 1:MC FileSystem
  - Linux 1:MC Application
  - Disk 1:MC Partition
  - VolumeGroup 1:MC LogicalVolume
  - LogicalVolume 1:MC SnapshotVolume
  - PhysicalVolume 1:1 PhysicalVolumeTarget
  - FileSystem 1:1 MountableDevice
  - VolumeGroup 1:M PhysicalVolume
  - Application M:M FileSystem
"""


EXPECTED_SUBCOMPONENT_VIEW = "Zenoss.nav.appendTo('Component', [{\n    id: 'subcomponent_view',\n    text: _t('Dynamic View'),\n    xtype: 'dynamicview',\n    relationshipFilter: 'impacted_by',\n    viewName: 'service_view',\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'Application': return true;\n            case 'Linux': return true;\n            default: return false;\n        }\n    }\n}]);"


class TestDynamicViewComponentNav(ZPLTestBase):
    """Specs test suite."""

    yaml_doc = YAML_DOC
    disableLogging = False

    def test_dynamic_view_nav_js(self):
        if dynamicview_installed():
            # dynamicview_nav_js_snippet is only used internally by zenpacklib, but
            # it should match exactly and be an easier test to make.
            self.assertMultiLineEqual(
                self.z.cfg.dynamicview_nav_js_snippet.strip(),
                EXPECTED_SUBCOMPONENT_VIEW.strip())

            # device_js_snippet is actually used to create the JavaScript snippet,
            # and should contain our subcomponent_view among many other things.
            self.assertIn(
                EXPECTED_SUBCOMPONENT_VIEW.strip(),
                self.z.cfg.device_js_snippet.strip())
        else:
            self.log.warn("Skipping TestDynamicViewComponentNav since ZenPacks.zenoss.DynamicView not installed")


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDynamicViewComponentNav))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
