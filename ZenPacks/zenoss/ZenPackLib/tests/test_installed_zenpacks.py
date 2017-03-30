#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
"""Test this version of ZenPackLib against relevant installed ZenPacks"""
#
# import importlib
# import os
# from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness
# from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
# from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack
#
# class TestInstalledZenPacks(ZPLTestBase):
#     """Test this version of ZenPackLib against relevant installed ZenPacks"""
#
#     use_dmd = True
#
#     def test_installed_zenpacks(self):
#         for zenpack in self.z.dmd.ZenPackManager.packs():
#             if not isinstance(zenpack, ZenPack):
#                 continue
#
#             zenpack_module = importlib.import_module(zenpack.id)
#             cfg = getattr(zenpack_module, "CFG", None)
#             self.check_zenpack(ZPLTestHarness(cfg, verbose=False))
#
#     def check_zenpack(self, z):
#         self.assertTrue(z.check_properties(), "Property testing failed for {}".format(z.cfg.name))
#         self.assertTrue(z.check_cfg_relations(), "Relation testing failed for {}".format(z.cfg.name))
#         self.assertTrue(z.check_templates_vs_yaml(), "Template (YAML) testing failed for {}".format(z.cfg.name))
#         self.assertTrue(z.check_templates_vs_specs(), "Template (Spec) testing failed for {}".format(z.cfg.name))
#
# def test_suite():
#     """Return test suite for this module."""
#     from unittest import TestSuite, makeSuite
#     suite = TestSuite()
#     #suite.addTest(makeSuite(TestInstalledZenPacks))
#     return suite
#
# if __name__ == "__main__":
#     from zope.testrunner.runner import Runner
#     runner = Runner(found_suites=[test_suite()])
#     runner.run()
