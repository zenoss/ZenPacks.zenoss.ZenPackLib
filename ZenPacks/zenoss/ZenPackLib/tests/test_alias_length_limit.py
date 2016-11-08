#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" 
    Test fix for ZEN-17950
    Enforce alias length limit in ZenPackLib
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


YAML_DOC = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Server:
    templates:
      TEST:
        datasources:
          dsname:
            type: SNMP
            datapoints:
              dpname26:
                aliases: {abcdefghijklmnopqrstuvwxyz: null}
              dpname52:
                aliases: {abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz: null}
              dpname26str:
                aliases: abcdefghijklmnopqrstuvwxyz
              dpname52str:
                aliases: abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
            oid: 1.3.6.1.4.1.2021.10.1.5.2
"""


class Test17950(BaseTestCase):
    """Test fix for ZEN-17950"""

    def test_datapoint_alias_length(self):
        ''''''
        z = ZPLTestHarness(YAML_DOC)
        ds_spec = z.cfg.device_classes.get('/Server').templates.get('TEST').datasources.get('dsname')
        for dp_name, dp_spec in ds_spec.datapoints.items():
            for k in dp_spec.aliases.keys():
                self.assertTrue(len(k) <= 31, 'Datapoint alias key too long: {} ({})'.format(k, len(k)))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test17950))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
