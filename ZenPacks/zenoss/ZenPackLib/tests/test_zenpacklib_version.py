#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
"""Test that this version of ZenPackLib displays correct version"""

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib import zenpacklib

class TestInstalledZenPackLibVersion(ZPLTestBase):
    """Test this version of ZenPackLib against relevant installed ZenPacks"""

    use_dmd = True

    def test_installed_zenpacks(self):
        packs = self.z.dmd.ZenPackManager.packs.findObjectsById('ZenPacks.zenoss.ZenPackLib')
        if packs:
            pack = packs[0]
            expected = pack.version
            actual = zenpacklib.__version__
            self.assertEquals(expected, actual, "ZenPackLib version mismatch in zenpacklib.py.  Expected {}, actual {}".format(expected, actual))

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstalledZenPackLibVersion))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
