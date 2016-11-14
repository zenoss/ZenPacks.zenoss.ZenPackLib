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
    Test the proper handling of inherited ClassSpec properties 
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
name: ZenPacks.zenoss.BasicZenPack
class_relationships:
- BasicDevice 1:MC BasicComponent
classes:
  BasicDevice:
    base: [zenpacklib.Device]
  BasicComponent:
    base: [zenpacklib.Component]
    properties:
      hello_world:
        label: Hello World
        api_only: true
        api_backendtype: method
        grid_display: true
  SubComponent:
    base: [BasicComponent]
    properties:
      DEFAULTS:
        grid_display: false
      sub_test:
        label: SubComponent Test 
  AuxComponent:
    base: [SubComponent]
    properties:
      aux_test:
        label: AuxComponent Test
      hello_world:
        label: Aux Hello
"""


class TestInheritedProperties(BaseTestCase):
    """
        Test the proper handling of inherited ClassSpec properties 
    """

    def test_inherited_properties_display(self):
        z = ZPLTestHarness(YAML_DOC)

        base = z.cfg.classes.get('BasicComponent')
        sub = z.cfg.classes.get('SubComponent')
        aux = z.cfg.classes.get('AuxComponent')

        # make sure the expected properties exist
        self.properties_exist(base, ['hello_world'])
        self.properties_exist(sub, ['sub_test', 'hello_world'])
        self.properties_exist(aux, ['aux_test', 'hello_world', 'sub_test'])

        self.property_value(base, 'hello_world', 'label', 'Hello World')
        self.property_value(sub, 'hello_world', 'label', 'Hello World')
        self.property_value(aux, 'hello_world', 'label', 'Aux Hello')

        self.property_value(base, 'hello_world', 'api_only', True)
        self.property_value(sub, 'hello_world', 'api_only', True)
        self.property_value(aux, 'hello_world', 'api_only', True)

        self.property_value(base, 'hello_world', 'api_backendtype', 'method')
        self.property_value(sub, 'hello_world', 'api_backendtype', 'method')
        self.property_value(aux, 'hello_world', 'api_backendtype', 'method')

        self.property_value(base, 'hello_world', 'grid_display', True)
        self.property_value(sub, 'hello_world', 'grid_display', False)
        self.property_value(aux, 'hello_world', 'grid_display', False)

        self.property_value(sub, 'sub_test', 'grid_display', False)
        self.property_value(aux, 'sub_test', 'grid_display', False)

        self.property_value(sub, 'sub_test', 'label', 'SubComponent Test')
        self.property_value(aux, 'sub_test', 'label', 'SubComponent Test')

        self.property_value(aux, 'aux_test', 'grid_display', True)


    def property_value(self, spec, prop_name, attr_name, expected):
        prop = spec.properties.get(prop_name)
        actual = getattr(prop, attr_name, None)
        self.assertEquals(expected, actual,
                          '{} has unexpected value for "{}", expected: {}, actual: {}'.format(
                          spec.name, prop_name, expected, actual)
                          )

    def properties_exist(self, spec, expected):
        """confirm expected properties exist"""
        actual = spec.properties.keys()
        self.assertEquals(expected,
                          actual,
                          '{} properties expected: {}, actual: {}'.format(spec.name,
                                                                          expected,
                                                                          actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInheritedProperties))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
