#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Command unit tests.

This module tests command line usage of zenpacklib.py.

"""
import logging
import os
import re
import shutil
import Globals
from Products.ZenUtils.Utils import unused, binPath

unused(Globals)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('zen.zenpacklib.tests')


from ZenPacks.zenoss.ZenPackLib.tests.BaseTestCommand import BaseTestCommand

from ZenPacks.zenoss.ZenPackLib.tests.test_install import TestInstall, get_cmd_output


class TestCommands(BaseTestCommand):

    zenpack_name = TestInstall.zenpack_name
    zenpack_path = TestInstall.zenpack_path
    yaml_path = os.path.join(zenpack_path, 'ZenPacks/zenoss/ZPLTest1/zenpack.yaml')

    disableLogging = False

    def afterSetUp(self):
        try:
            super(TestCommands, self).afterSetUp()
        except ImportError, e:
            self.assertFalse(
                e.message == 'No module named ZPLTest1',
                "ZPLTest1 zenpack is not installed.  You must install it before running this test:\n   zenpack --link --install=%s" % self.zenpack_path
            )

    def test_smoke_lint(self):
        self._smoke_command("--lint", self.yaml_path)

    # Can't be tested with ZPLTest1, because that is already using YAML.
    # Need to build another small zenpack if we want to do that.
    # def test_smoke_py_to_yaml(self):
    #     self._smoke_command("py_to_yaml", self.zenpack_name)

    def test_smoke_dump_templates(self):
        self._smoke_command("--dump-templates", 'ZenPacks.zenoss.DnsMonitor')

    def test_smoke_class_diagram(self):
        self._smoke_command("--diagram", self.yaml_path)

    def test_create(self):
        zenpack_name = "ZenPacks.test.ZPLTestCreate"

        # Cleanup from any failed previous tests.
        shutil.rmtree(zenpack_name, ignore_errors=True)

        output = self._smoke_command("--create", zenpack_name)

        # Test that output describes what's being created.
        expected_terms = (
            "setup.py", "MANIFEST.in", "zenpack.yaml")

        for expected_term in expected_terms:
            self.assertIn(expected_term, output)

        # Test that expected directories and files were created.
        expected_directories = (
            "",
            "ZenPacks",
            "ZenPacks/test",
            "ZenPacks/test/ZPLTestCreate",
            )

        for expected_directory in expected_directories:
            self.assertTrue(
                os.path.isdir(os.path.join(zenpack_name, expected_directory)),
                "{!r} directory not created".format(expected_directory))

        expected_files = (
            "setup.py",
            "MANIFEST.in",
            "ZenPacks/__init__.py",
            "ZenPacks/test/__init__.py",
            "ZenPacks/test/ZPLTestCreate/__init__.py",
            "ZenPacks/test/ZPLTestCreate/zenpack.yaml",
            )

        for expected_file in expected_files:
            self.assertTrue(
                os.path.isfile(os.path.join(zenpack_name, expected_file)),
                "{!r} file not created".format(expected_file))

        # Cleanup created directory.
        shutil.rmtree(zenpack_name, ignore_errors=True)

    def test_version(self):
        output = self._smoke_command("--version").strip()
        version_pattern = r'^\d+\.\d+\.\d+(dev)?$'
        match = re.match(version_pattern, output)
        self.assertTrue(
            match,
            "version output {!r} doesn't match /{}/"
            .format(output, version_pattern))

    def test_a_install(self):
        """install the zenpack for the first time"""
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.run_cmd(cmd)

    def test_z_remove(self):
        " remove the installed zenpack"
        out = self.run_cmd([binPath('zenpack'), "--list"])
        if self.zenpack_name in out:
            out = self.run_cmd([binPath('zenpack'), "--remove", self.zenpack_name])

    def run_cmd(self, cmd, vars={}):
        """execute a command and assert success"""
        p, out, err = get_cmd_output(cmd, vars)
        LOG.debug("out=%s, err=%s", out, err)
        msg = 'Command "{}" failed with error:\n  {}'.format(cmd, err)
        self.assertIs(p.returncode, 0, msg)
        return out

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCommands))
    return suite


if __name__ == "__main__":

    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
