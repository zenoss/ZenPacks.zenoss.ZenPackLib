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
    Ensure proper type handling for extra_params attribute overloading (ZEN-24079, ZEN-25315, ZEN-24083
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestMockZenPack
from Products.ZenModel.MinMaxThreshold import MinMaxThreshold
from Products.ZenModel.RRDDataSource import RRDDataSource


class CustomThreshold(MinMaxThreshold):
    """Mock Threshold for testing"""
    meta_type = "CustomThreshold"
    # Add default values for custom properties of this datasource.
    description = ''
    property_int = 100  # All data points must be violating the threshold
    _properties = MinMaxThreshold._properties + (
        {'id': 'description', 'type': 'string', 'mode': 'rw'},
        {'id': 'property_int', 'type': 'int', 'mode': 'rw'},
        {'id': 'property_bool', 'type': 'boolean', 'mode': 'rw'},
        {'id': 'property_float', 'type': 'float', 'mode': 'rw'},
        {'id': 'property_lines', 'type': 'lines', 'mode': 'rw'},
        )

class CustomDatasource(RRDDataSource):
    """Mock Datasource for testing"""
    sourcetypes = ('CustomDatasource',)
    sourcetype = sourcetypes[0]

    _properties = RRDDataSource._properties + (
        {'id': 'description', 'type': 'string', 'mode': 'rw'},
        {'id': 'property_int', 'type': 'int', 'mode': 'rw'},
        {'id': 'property_bool', 'type': 'boolean', 'mode': 'rw'},
        {'id': 'property_float', 'type': 'float', 'mode': 'rw'},
        {'id': 'property_lines', 'type': 'lines', 'mode': 'rw'},
        )

YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Devices:
    templates:
      TESTTEMPLATE:
        description: Testing that Duration threshold accepts integer values
        datasources:
          # THESE defaults arent working so set manually below remove when fixed
          DEFAULTS:
            type: CustomDatasource
            description: Default Description
            property_int: 100
            property_bool: true
            property_float: 10.0
          inheritedReading: 
            datapoints:
              inheritedReading: GAUGE
          currentReading:
            type: CustomDatasource
            datapoints:
              currentReading: {}
            description: Text Description
            property_int: 10
            property_bool: false
            property_float: 1.0
        thresholds:
          CustomThreshold:
            type: CustomThreshold
            dsnames: [currentReading_currentReading]
            description: Text Description
            property_int: 10
            property_bool: false
            property_float: 1.0
            
"""


class TestExtraParamsTypeHandling(ZPLTestMockZenPack):
    """
    """
    yaml_doc = YAML_DOC
    disableLogging = False

    def afterSetUp(self):
        super(TestExtraParamsTypeHandling, self).afterSetUp([CustomDatasource], [CustomThreshold])
        self.template = self.z.cfg.device_classes.get('/Devices').templates.get('TESTTEMPLATE').create(self.dmd, False)

    def test_inherited_defaults(self):
        """Test that inherited extra_params properties function correctly (ZEN-24083)"""
        for th in self.template.datasources():
            if th.id != "inheritedReading":
                continue
            self.assertEquals(th.description, 'Default Description', 'Datasource attribute '\
                              'inheritance mismatch, expected: {}, actual: {}'.format('Default Description',
                                                                                      th.description))
            self.assertEquals(th.property_int, 100, 'Datasource attribute '\
                              'inheritance mismatch, expected: {}, actual: {}'.format(100,
                                                                                      th.property_int))
            self.assertEquals(th.property_bool, True, 'Datasource attribute '\
                              'inheritance mismatch, expected: {}, actual: {}'.format(True,
                                                                                      th.property_bool))
            self.assertEquals(th.property_float, 10.0, 'Datasource attribute '\
                              'inheritance mismatch, expected: {}, actual: {}'.format(10.0,
                                                                                      th.property_float))

    def test_extra_params_datasources(self):
        """Test that datasource extra_params properties function correctly (ZEN-25315)"""
        # check properties on dummy template
        for th in self.template.datasources():
            self.assertTrue(isinstance(th.description, str),
                 '{} property ({}) should be str, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.description)))
            self.assertTrue(isinstance(th.property_int, int),
                 '{} property ({}) should be int, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_int)))
            self.assertTrue(isinstance(th.property_bool, int),
                 '{} property ({}) should be bool, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_bool)))
            self.assertTrue(isinstance(th.property_float, float),
                 '{} property ({}) should be float, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_float)))

    def test_extra_params_thresholds(self):
        """Test that threshold extra_params properties function correctly (ZEN-24079)"""
        for th in self.template.thresholds():
            self.assertTrue(isinstance(th.description, str),
                 '{} property ({}) should be str, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.description)))
            self.assertTrue(isinstance(th.property_int, int),
                 '{} property ({}) should be int, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_int)))
            self.assertTrue(isinstance(th.property_bool, int),
                 '{} property ({}) should be bool, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_bool)))
            self.assertTrue(isinstance(th.property_float, float),
                 '{} property ({}) should be float, got {}'.format(th.__class__.__name__,
                                                                 th.id,
                                                                 type(th.property_float)))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtraParamsTypeHandling))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
