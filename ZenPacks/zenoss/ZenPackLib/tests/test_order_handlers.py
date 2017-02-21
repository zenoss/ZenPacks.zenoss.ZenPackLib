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
    Validate handling, normalization, and scaling of order parameter across Specs
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = '''name: ZenPacks.zenoss.ZenPackLib
class_relationships:
- BasicDevice 1:MC BasicComponent
- SubComponent M:M AuxComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    properties:
        a: {}
        b: {}
        c: {}
  BasicComponent:
    base: [zenpacklib.Component]
    properties:
        a: {}
        b: {}
  SubComponent:
    base: [BasicComponent]
    relationships:
        auxComponents: {}
        basicDevice: {}
  AuxComponent:
    base: [SubComponent]
    properties:
        a: {}
        b: {}
'''

YAML_DOC_INT = '''name: ZenPacks.zenoss.ZenPackLib
class_relationships:
- BasicDevice 1:MC BasicComponent
- SubComponent M:M AuxComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    properties:
        a:
            order: 1
        b:
            order: 2
        c:
            order: 3
  BasicComponent:
    base: [zenpacklib.Component]
    order: 1
    properties:
        a:
            order: 1
        b:
            order: 2
  SubComponent:
    base: [BasicComponent]
    order: 2
    relationships:
        auxComponents:
            order: 1
        basicDevice:
            order: 2
  AuxComponent:
    base: [SubComponent]
    order: 3
    properties:
        a:
            order: 2
        b:
            order: 1
'''

YAML_DOC_FLOAT = '''name: ZenPacks.zenoss.ZenPackLib
class_relationships:
- BasicDevice 1:MC BasicComponent
- SubComponent M:M AuxComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    properties:
        a:
            order: 1.5
        b:
            order: 1.6
        c:
            order: 1.7
  BasicComponent:
    base: [zenpacklib.Component]
    order: 1.1
    properties:
        a:
            order: 1.3
        b:
            order: 1.0
  SubComponent:
    base: [BasicComponent]
    order: 1.2
    relationships:
        auxComponents:
            order: 50.5
        basicDevice:
            order: 3.3
  AuxComponent:
    base: [SubComponent]
    order: 1.3
    properties:
        a:
            order: 1.2
        b:
            order: 1.1
'''

EXPECTED_INT = {'AuxComponent': {'relationships': {'basicDevice': {'scaled': 3.02, 'order': 2}, 'auxComponents': {'scaled': 6.01, 'order': 1}, 'subComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 5.03, 'properties': {'a': {'scaled': 4.02, 'order': 2}, 'b': {'scaled': 4.01, 'order': 1}}, 'order': 3}, 'BasicComponent': {'relationships': {'basicDevice': {'scaled': 4.0, 'order': 100}}, 'scaled': 5.01, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 1}, 'BasicDevice': {'relationships': {'basicComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 6.0, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'c': {'scaled': 4.03, 'order': 3}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 100}, 'SubComponent': {'relationships': {'basicDevice': {'scaled': 3.02, 'order': 2}, 'auxComponents': {'scaled': 6.01, 'order': 1}}, 'scaled': 5.02, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 2}}

EXPECTED_FLOAT = {'AuxComponent': {'relationships': {'basicDevice': {'scaled': 3.01, 'order': 1}, 'auxComponents': {'scaled': 6.02, 'order': 2}, 'subComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 5.03, 'properties': {'a': {'scaled': 4.02, 'order': 2}, 'b': {'scaled': 4.01, 'order': 1}}, 'order': 3}, 'BasicComponent': {'relationships': {'basicDevice': {'scaled': 4.0, 'order': 100}}, 'scaled': 5.01, 'properties': {'a': {'scaled': 4.02, 'order': 2}, 'b': {'scaled': 4.01, 'order': 1}}, 'order': 1}, 'BasicDevice': {'relationships': {'basicComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 5.04, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'c': {'scaled': 4.03, 'order': 3}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 4}, 'SubComponent': {'relationships': {'basicDevice': {'scaled': 3.01, 'order': 1}, 'auxComponents': {'scaled': 6.02, 'order': 2}}, 'scaled': 5.02, 'properties': {'a': {'scaled': 4.02, 'order': 2}, 'b': {'scaled': 4.01, 'order': 1}}, 'order': 2}}

EXPECTED_DEFAULT = {'AuxComponent': {'relationships': {'basicDevice': {'scaled': 3.02, 'order': 2}, 'auxComponents': {'scaled': 6.01, 'order': 1}, 'subComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 5.04, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 4}, 'BasicComponent': {'relationships': {'basicDevice': {'scaled': 4.0, 'order': 100}}, 'scaled': 5.02, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 2}, 'BasicDevice': {'relationships': {'basicComponents': {'scaled': 7.0, 'order': 100}}, 'scaled': 5.01, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'c': {'scaled': 4.03, 'order': 3}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 1}, 'SubComponent': {'relationships': {'basicDevice': {'scaled': 3.02, 'order': 2}, 'auxComponents': {'scaled': 6.01, 'order': 1}}, 'scaled': 5.03, 'properties': {'a': {'scaled': 4.01, 'order': 1}, 'b': {'scaled': 4.02, 'order': 2}}, 'order': 3}}


class TestOrderHandlers(ZPLTestBase):
    """
        Validate handling, normalization, and scaling of order parameter across Specs
    """

    yaml_doc = [YAML_DOC, YAML_DOC_INT, YAML_DOC_FLOAT]

    def test_order_as_default(self):
        """Test handling of default order assignment"""
        self.assertEquals(EXPECTED_DEFAULT, self.get_order_data(self.z),
                          'Order parameter handling (default) failed validation')

    def test_order_as_float(self):
        """Test handling of legacy float order assignment"""
        self.assertEquals(EXPECTED_FLOAT, self.get_order_data(self.z_2),
                          'Order parameter handling (float) failed validation')

    def test_order_as_integer(self):
        """test ZPl 2.0 normal order"""
        self.assertEquals(EXPECTED_INT, self.get_order_data(self.z_1),
                          'Order parameter handling (integer) failed validation')

    def get_order_data(self, z):
        data = {}
        for spec in z.cfg.classes.values():
            data[spec.name] = {'properties': {}, 'relationships': {}, 'order': spec.order, 'scaled': spec.scaled_order}
            for p_spec in spec.properties.values():
                data[spec.name]['properties'][p_spec.name] = {'order': p_spec.order, 'scaled': p_spec.scaled_order}
            for r_spec in spec.relationships.values():
                data[spec.name]['relationships'][r_spec.name] = {'order': r_spec.order, 'scaled': r_spec.scaled_order}
        return data


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrderHandlers))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
