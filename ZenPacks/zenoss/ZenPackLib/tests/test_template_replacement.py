#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = '''
name: ZenPacks.zenoss.ZPL.Test

class_relationships:
  - TestDevice 1:MC TestComponent

classes:
  TestDevice:
    base: [zenpacklib.Device]
  TestComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [TestTemplate]

device_classes:
  /ZPL/Test:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"

      TestTemplate-replacement:
        datasources:
          ds1:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"

      TestTemplate-addition:
        datasources:
          ds2:
            type: COMMAND
            parser: Nagios
            commandTemplate: "echo OK|percent=100"
'''


class TestTemplateReplacement(ZPLTestBase):
    """Ensure getRRDTemplates returns the expected output."""

    yaml_doc = YAML_DOC

    def _get_templates(self):
        device_class = self.z.cfg.device_classes.get('/ZPL/Test')
        return {
            tname: tspec.create(self.dmd, False)
            for tname, tspec in device_class.templates.iteritems()}

    def _test_replacement(self, obj, templates):
        self.assertListEqual(
            ['TestTemplate-replacement', 'TestTemplate-addition'],
            [tpl.titleOrId() for tpl in obj.getRRDTemplates()])

        del templates['TestTemplate-replacement']

        self.assertListEqual(
            ['TestTemplate', 'TestTemplate-addition'],
            [tpl.titleOrId() for tpl in obj.getRRDTemplates()])

        del templates['TestTemplate-addition']

        self.assertListEqual(
            ['TestTemplate'],
            [tpl.titleOrId() for tpl in obj.getRRDTemplates()])

    def test_device_replacement(self):
        templates = self._get_templates()

        def getRRDTemplateByName(name):
            return templates.get(name)

        obj = self.z.zp.TestDevice.TestDevice('test_device_1')
        obj.setZenProperty('zDeviceTemplates', ['TestTemplate'])
        obj.getRRDTemplateByName = getRRDTemplateByName

        self._test_replacement(obj, templates)

    def test_component_replacement(self):
        templates = self._get_templates()

        def getRRDTemplateByName(name):
            return templates.get(name)

        obj = self.z.zp.TestComponent.TestComponent('test_component_1')
        obj.getRRDTemplateByName = getRRDTemplateByName

        self._test_replacement(obj, templates)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateReplacement))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
