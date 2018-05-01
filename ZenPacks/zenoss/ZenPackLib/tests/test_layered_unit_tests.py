#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
"""
    Verify that layered unit testing works as expected
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLLayeredTestCase, get_layer_subclass


YAML_DOC_1 = '''
name: ZenPacks.zenoss.ZPL.Test1
class_relationships:
  - TestDevice 1:MC TestComponent
classes:
  TestDevice:
    base: [zenpacklib.Device]
  TestComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [TestTemplate]
device_classes:
  /Test1:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"
'''

YAML_DOC_2 = '''
name: ZenPacks.zenoss.ZPL.Test2
class_relationships:
  - TestDevice 1:MC TestComponent
classes:
  TestDevice:
    base: [zenpacklib.Device]
  TestComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [TestTemplate]
device_classes:
  /Test2:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"
'''

YAML_DOC_3 = '''
name: ZenPacks.zenoss.ZPL.Test3
class_relationships:
  - TestDevice 1:MC TestComponent
classes:
  TestDevice:
    base: [zenpacklib.Device]
  TestComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [TestTemplate]
device_classes:
  /Test3:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"
'''


class TestLayeredTestShared1(ZPLLayeredTestCase):
    """Ensure that Layered test environment is shared only when needed"""
    layer = get_layer_subclass('SharedLayer', YAML_DOC_1, False)
    
    def test_zps_installed(self):
        installed = [p.id for p in self.dmd.ZenPackManager.packs()]
        self.assertListEqual(['ZenPacks.zenoss.ZPL.Test1'], installed)
        
    def test_configs(self):
        keys = self.configs.keys()
        self.assertListEqual(['ZenPacks.zenoss.ZPL.Test1'], keys)


class TestLayeredTestShared2(ZPLLayeredTestCase):
    """Ensure that Layered test environment is shared only when needed"""
    layer = type('SharedLayer2', (TestLayeredTestShared1.layer,), {'yaml_doc': YAML_DOC_2, 'reset': False})

    def test_zps_installed(self):
        installed = [p.id for p in self.dmd.ZenPackManager.packs()]
        installed.sort()
        self.assertListEqual(['ZenPacks.zenoss.ZPL.Test1', 'ZenPacks.zenoss.ZPL.Test2'], installed)

    def test_configs(self):
        keys = self.configs.keys()
        keys.sort()
        self.assertListEqual(['ZenPacks.zenoss.ZPL.Test1', 'ZenPacks.zenoss.ZPL.Test2'], keys)


class TestLayeredTestStandalone(ZPLLayeredTestCase):
    """Ensure that Layered test environment is shared only when needed"""
    layer = get_layer_subclass('StandaloneLayer', YAML_DOC_3)

    def test_zps_installed(self):
        installed = [p.id for p in self.dmd.ZenPackManager.packs()]
        self.assertListEqual(installed, ['ZenPacks.zenoss.ZPL.Test3'])
        
    def test_configs(self):
        keys = self.configs.keys()
        self.assertListEqual(keys, ['ZenPacks.zenoss.ZPL.Test3'])



def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLayeredTestShared1))
    suite.addTest(makeSuite(TestLayeredTestShared2))
    suite.addTest(makeSuite(TestLayeredTestStandalone))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
