#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Schema unit tests.

This is primarily testing that zenpacklib is functioning as desired. If
zenpacklib was already mature these kinds of tests would be in its
test suite instead of in the ZenPack's.

"""

import Globals
from Products.ZenUtils.Utils import unused, binPath
from Products.ZenTestCase.BaseTestCase import BaseTestCase

unused(Globals)

import os
import subprocess


class TestInstall(BaseTestCase):

    zenpack_name = 'ZenPacks.zenoss.ZPLTest1'
    zenpack_path = os.path.join(os.path.dirname(__file__),
                                "data/zenpacks/ZenPacks.zenoss.ZPLTest1")
    disableLogging = False

    def setUp(self):
        cmd = [binPath('zenpack'), "--list"]
        print " ".join(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()

        self.assertIs(p.returncode, 0,
                      'Error listing installed zenpacks: %s' % err)

        if self.zenpack_name in out:
            cmd = [binPath('zenpack'), "--remove", self.zenpack_name]

            print " ".join(cmd)
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = p.communicate()
            p.wait()

            self.assertIs(p.returncode, 0,
                          'Error removing %s zenpack: %s' % (self.zenpack_name, err))

    def test_install(self):
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]

        print " ".join(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()

        self.assertIs(p.returncode, 0,
                      'Error installing %s zenpack: %s' % (self.zenpack_name, err))

    def test_upgrade(self):
        cmd = [binPath('zenpack'), "--link", "--install", self.zenpack_path]

        print " ".join(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()

        self.assertIs(p.returncode, 0,
                      'Error installing %s zenpack: %s' % (self.zenpack_path, err))

        # install it a second time.  Basically a do-nothign upgrade.

        print " ".join(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()

        self.assertIs(p.returncode, 0,
                      'Error upgrading %s zenpack: %s' % (self.zenpack_name, err))

        pass

    def test_uninstall(self):
        cmd = [binPath('zenpack'), "--remove", self.zenpack_name]

        print " ".join(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()

        self.assertIs(p.returncode, 0,
                      'Error removing %s zenpack: %s' % (self.zenpack_name, err))


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
