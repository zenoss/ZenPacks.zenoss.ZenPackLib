#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Install unit tests.

This module tests ZenPack install, upgrade and remove.

"""
import os
from Products.ZenUtils.Utils import binPath
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestCommand


class TestInstall(ZPLTestCommand):
    """Test installation, upgrade, and removal of Example ZenPack"""
    zenpack_name = 'ZenPacks.zenoss.ZPLTest1'
    zenpack_path = os.path.join(os.path.dirname(__file__),
                                "data/zenpacks/ZenPacks.zenoss.ZPLTest1")

    def test_install(self):
        """install the zenpack for the first time"""
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.get_cmd_success(cmd)

    def test_install_upgrade(self):
        """install it a second time unchanged"""
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.get_cmd_success(cmd)

    def test_install_upgrade_yaml(self):
        """
            install it a second time, with a different yaml file that simulates
            adding a new monitoring template
        """
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.get_cmd_success(cmd, vars={'ZPL_YAML_FILENAME': 'yes'})

    def test_remove_if_installed(self):
        " remove the installed zenpack"
        out = self.get_cmd_success([binPath('zenpack'), "--list"])
        if self.zenpack_name in out:
            out = self.get_cmd_success([binPath('zenpack'), "--remove", self.zenpack_name])


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
