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
    Test that export of Zope objects works as expected
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase
from ZenPacks.zenoss.ZenPackLib.lib.libexec.ZPLCommand import YAMLExporter

YAML_DOC = '''
name: ZenPacks.acme.Processes

device_classes:
  /ZPL/Test:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            parser: Nagios
            commandTemplate: echo OK|percent=100

process_class_organizers:
  /Widget:
    description: Organizer for Widget process classes
    process_classes:
      widget:
        description: Widget process class
        includeRegex: sbin\/widget
        excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
        replaceRegex: .*
        replacement: Widget

event_classes:
  /Status/Test:
    remove: false
    description: Test event class
    transform: "from ZenPacks.zenoss.CiscoMonitor import transforms\\ntransforms.status_handler(device, component, evt)"
    mappings:
      TestMapping:
        eventClassKey: TestMapping
        sequence:  10
        example: Test Mapping example
        explanation: This is a test for an example mapping
        resolution: This is the resolution for the test mapping
        remove: true
        regex: +.*
        transform: "from ZenPacks.zenoss.CiscoMonitor import transforms\\ntransforms.status_handler(device, component, evt)"
        rule: "component.id == id"
'''

T_YAML = '''name: ZenPacks.acme.Processes
device_classes:
  /ZPL/Test:
    templates:
      TestTemplate:
        datasources:
          ds0:
            type: COMMAND
            commandTemplate: echo OK|percent=100
            parser: Nagios
'''

EV_YAML = '''name: ZenPacks.acme.Processes
event_classes:
  /Status/Test:
    description: Test event class
    transform: |-
      from ZenPacks.zenoss.CiscoMonitor import transforms
      transforms.status_handler(device, component, evt)
    mappings:
      TestMapping:
        eventClassKey: TestMapping
        sequence: 10
        rule: component.id == id
        regex: +.*
        transform: |-
          from ZenPacks.zenoss.CiscoMonitor import transforms
          transforms.status_handler(device, component, evt)
        example: Test Mapping example
        explanation: This is a test for an example mapping
        resolution: This is the resolution for the test mapping
        remove: true
'''

EV_YAML_ZP = '''name: ZenPacks.acme.Processes
event_classes:
  /Status/Test:
    description: Test event class
    transform: |-
      from ZenPacks.zenoss.CiscoMonitor import transforms
      transforms.status_handler(device, component, evt)
    mappings:
      TestMapping:
        eventClassKey: TestMapping
        sequence: 10
        rule: component.id == id
        regex: +.*
        transform: |-
          from ZenPacks.zenoss.CiscoMonitor import transforms
          transforms.status_handler(device, component, evt)
        example: Test Mapping example
        explanation: This is a test for an example mapping
        resolution: This is the resolution for the test mapping
'''

PR_YAML = '''name: ZenPacks.acme.Processes
process_class_organizers:
  /Widget:
    process_classes:
      widget:
        description: Widget process class
        includeRegex: sbin\/widget
        excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
        replaceRegex: .*
        replacement: Widget
'''


class TestZopeObjectExport(ZPLBaseTestCase):
    """
    Test that export of Zope objects works as expected
    """
    yaml_doc = [YAML_DOC]

    def afterSetUp(self):
        super(TestZopeObjectExport, self).afterSetUp()
        config = self.configs.get('ZenPacks.acme.Processes')
        self.cfg = config.get('cfg')
        self.zenpack = config.get('zenpack')

    def test_export_process_classes(self):
        """Test export from ZPL-based ZenPacks"""
        process_classes = YAMLExporter.dump_process_classes(self.zenpack)
        diff = self.zenpack.get_yaml_diff(process_classes, PR_YAML)
        self.assertEquals(
            process_classes, PR_YAML,
            'Expected:\n{}\ngot:\n{}'.format(PR_YAML, diff))

    def test_export_process_classes_packable(self):
        """Test dumping from legacy ZenPacks with packables"""
        for psname, psspec in self.cfg.process_class_organizers.iteritems():
            porg = psspec.create(self.app.zport.dmd)
            try:
                self.zenpack.packables.addRelation(porg)
            except:
                pass
        process_classes = YAMLExporter.dump_process_classes(self.zenpack)
        diff = self.zenpack.get_yaml_diff(PR_YAML, process_classes)
        self.assertEquals(
            process_classes, PR_YAML,
            'Expected:\n{}\ngot:\n{}'.format(PR_YAML, diff))

    def test_export_event_classes(self):
        """Test export from ZPL-based ZenPacks"""
        event_classes = YAMLExporter.dump_event_classes(self.zenpack)
        diff = self.zenpack.get_yaml_diff(event_classes, EV_YAML)
        self.assertEquals(
            event_classes, EV_YAML,
            'Expected:\n{}\ngot:\n{}'.format(EV_YAML, diff))

    def test_export_event_classes_packable(self):
        """Test export from ZPL-based ZenPacks"""
        for ecname, ecspec in self.cfg.event_classes.iteritems():
            ecorg = ecspec.instantiate(self.app.zport.dmd)
            try:
                self.zenpack.packables.addRelation(ecorg)
            except:
                pass
        event_classes = YAMLExporter.dump_event_classes(self.zenpack)
        diff = self.zenpack.get_yaml_diff(event_classes, EV_YAML_ZP)
        self.assertEquals(
            event_classes, EV_YAML_ZP,
            'Expected:\n{}\ngot:\n{}'.format(EV_YAML_ZP, diff))

    def test_export_templates(self):
        """Test export from ZPL-based ZenPacks"""
        templates = YAMLExporter.dump_templates(self.zenpack)
        diff = self.zenpack.get_yaml_diff(templates, T_YAML)
        self.assertEquals(
             templates, T_YAML,
            'Expected:\n{}\ngot:\n{}'.format(T_YAML, diff))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeObjectExport))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
