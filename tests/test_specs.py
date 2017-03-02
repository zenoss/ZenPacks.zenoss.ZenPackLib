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

This module tests zenpacklib "Specs". These are the intermediate step
between YAML and Zenoss functionality.

"""

# stdlib Imports
import os
import unittest
import site
import tempfile

# Zenoss Imports
import Globals  # noqa

# zenpacklib Imports
site.addsitedir(os.path.join(os.path.dirname(__file__), '..'))
import zenpacklib

LINUX_YAML = """
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


EXPECTED_SUBCOMPONENT_VIEW = """
Zenoss.nav.appendTo('Component', [{
    id: 'ZenPacks_zenpacklib_TestLinuxStorage_subcomponent_view',
    text: _t('Dynamic View'),
    xtype: 'dynamicview',
    relationshipFilter: 'impacted_by',
    viewName: 'service_view',
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'Application': return true; case 'Linux': return true;
            default: return false;
        }
    }
}]);
"""


def spec_from_string(s):
    with tempfile.NamedTemporaryFile() as f:
        f.write(s.strip())
        f.flush()
        return zenpacklib.load_yaml(f.name)


class TestSpecs(unittest.TestCase):

    """Specs test suite."""

    def test_DynamicViewComponentNav(self):
        zenpack = spec_from_string(LINUX_YAML)

        # dynamicview_nav_js_snippet is only used internally by zenpacklib, but
        # it should match exactly and be an easier test to make.
        self.assertMultiLineEqual(
            zenpack.dynamicview_nav_js_snippet.strip(),
            EXPECTED_SUBCOMPONENT_VIEW.strip())

        # device_js_snippet is actually used to create the JavaScript snippet,
        # and should contain our subcomponent_view among many other things.
        self.assertIn(
            EXPECTED_SUBCOMPONENT_VIEW.strip(),
            zenpack.device_js_snippet.strip())


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSpecs))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
