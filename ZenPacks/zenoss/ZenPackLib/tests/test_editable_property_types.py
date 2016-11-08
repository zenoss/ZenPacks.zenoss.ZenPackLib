#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    This is designed to test whether or not ZenPack lib 
    sets editable class properties as strings regardless of type (ZEN-22057)
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness



YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
classes:
  SomeComponent:
    base: [zenpacklib.Component]
    label: SomeComponent
    properties:
      property_int:
        type: int
        editable: true
      property_bool:
        type: boolean
        editable: true
      property_float:
        type: float
        editable: true
      property_string:
        type: string
        editable: true
      property_lines:
        type: lines
        editable: true
"""


class TestZen22057(BaseTestCase):
    """Test fix for ZEN-22057
    """

    def test_inherited_relation_display(self):
        z = ZPLTestHarness(YAML_DOC)
        ob = z.build_ob('SomeComponent')
        for x in ['1', True, 1.0, 1]:
            # check integer
            ob.property_int = x
            self.check_type(ob.property_int, 1)
            # boolean check
            ob.property_bool = x
            self.check_type(ob.property_bool, True)
            # check float
            ob.property_float = x
            self.check_type(ob.property_float, 1.0)
            # check lines
            ob.property_lines = x
            self.check_type(ob.property_lines, [str(x)])
            # check string
            ob.property_string = x
            self.check_type(ob.property_string, str(x))

    def check_type(self, actual, expected):
        self.assertEquals(expected, actual,
            'Type check failed,  expected {} ({}), got {} ({})'.format(expected,
                                                                       type(expected).__name__,
                                                                       actual,
                                                                       type(actual).__name__))

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen22057))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
