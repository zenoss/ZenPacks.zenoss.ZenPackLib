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
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('zen.zenpacklib.tests')

import Globals
from Products.ZenUtils.Utils import unused, binPath
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase


def get_cmd_output(cmd, vars):
    LOG.info(" ".join(cmd))
    env = dict(os.environ)
    env.update(vars)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         env=env)
    out, err = p.communicate()
    p.wait()
    return (p,out,err)

class TestInstall(BaseTestCase):

    zenpack_name = 'ZenPacks.zenoss.ZPLTest1'
    zenpack_path = os.path.join(os.path.dirname(__file__),
                                "data/zenpacks/ZenPacks.zenoss.ZPLTest1")
    disableLogging = False

    def test_install(self):
        """install the zenpack for the first time"""
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.run_cmd(cmd)

    def test_install_upgrade(self):
        """install it a second time unchanged"""
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.run_cmd(cmd)

    def test_install_upgrade_yaml(self):
        """
            install it a second time, with a different yaml file that simulates
            adding a new monitoring template
        """
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]
        out = self.run_cmd(cmd, vars={'ZPL_YAML_FILENAME': 'yes'})

    def test_remove_if_installed(self):
        " remove the installed zenpack"
        out = self.run_cmd([binPath('zenpack'), "--list"])
        if self.zenpack_name in out:
            out = self.run_cmd([binPath('zenpack'), "--remove", self.zenpack_name])

    def run_cmd(self, cmd, vars={}):
        """execute a command and assert success"""
        p,out,err = get_cmd_output(cmd, vars)
        LOG.debug("out=%s, err=%s", out, err)
        msg = 'Command "{}" failed with error:\n  {}'.format(cmd, err)
        self.assertIs(p.returncode, 0, msg)
        return out


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
