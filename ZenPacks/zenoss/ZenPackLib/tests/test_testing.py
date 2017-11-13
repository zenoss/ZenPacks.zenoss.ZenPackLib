##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import ZenPacks.zenoss.ZenPackLib
from ZenPacks.zenoss.ZenPackLib import zenpacklib
from ZenPacks.zenoss.ZenPackLib.lib.tests.TestCase import TestCase as LibTestCase
from ZenPacks.zenoss.ZenPackLib.lib.spec.ZenPackSpec import ZenPackSpec

zenpacklib.enableTesting()


class TestTestCase(zenpacklib.TestCase):
    def afterSetUp(self):
        ZenPacks.zenoss.ZenPackLib.CFG = ZenPackSpec("ZenPacks.zenoss.ZenPackLib")
        super(TestTestCase, self).afterSetUp()

    def beforeTearDown(self):
        del(ZenPacks.zenoss.ZenPackLib.CFG)

    def test_nothing(self):
        self.assertTrue(True)


class TestLibTestCase(LibTestCase):
    zenpack_module_name = "ZenPacks.zenoss.ZenPackLib"

    def afterSetUp(self):
        ZenPacks.zenoss.ZenPackLib.CFG = ZenPackSpec("ZenPacks.zenoss.ZenPackLib")
        super(TestLibTestCase, self).afterSetUp()

    def beforeTearDown(self):
        del(ZenPacks.zenoss.ZenPackLib.CFG)

    def test_nothing(self):
        self.assertTrue(True)
