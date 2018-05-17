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
    Test that device classes can optionally have their zProperties reset (ZPS-810)
"""

from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.Organizers

device_classes:
  /Server:
    description: Basic Server Organizer
    zProperties:
      zSnmpMonitorIgnore: true
    create: true
    reset: true
    remove: true
  /Server/NewDevices:
    description: Basic Server Organizer
    zProperties:
      zSnmpMonitorIgnore: true
    create: true
    reset: true
    remove: true

event_classes:
  /Organizer/Mappings:
    description: Basic Event Organizer with Mappings
    create: true
    reset: true
    remove: false
    mappings:
      TestRemove:
        eventClassKey: TestRemove
        remove: true
      TestRemain:
        eventClassKey: TestRemain
        remove: false
  /Organizer/Status:
    description: Basic Event Organizer
    zProperties:
      zFlappingThreshold: 6
    create: true
    reset: true
    remove: true
  /Status:
    description: Basic Event Organizer
    zProperties:
      zFlappingThreshold: 6
    create: true
    reset: true
    remove: true

process_class_organizers:
  /Test:
    description: Basic Process Organizer
    zProperties:
      zAlertOnRestart: false
    create: true
    reset: true
    remove: true
  /TestClasses:
    description: Basic Process Organizer
    zProperties:
      zAlertOnRestart: false
    create: true
    reset: true
    remove: false
    process_classes:
      remove:
        description: Description of the foo Process Class
        includeRegex: sbin\/foo
        replaceRegex: ".*"
        replacement: Foo Process Class
        excludeRegex: \\b(vim|tail|grep|tar|cat|bash)\\b
        remove: true
      remain:
        description: Description of the bar Process Class
        includeRegex: sbin\/bar
        excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
        replaceRegex: .*
        replacement: Bar Process Class
        monitor: true
        alert_on_restart: false
        fail_severity: 3
        modeler_lock: 0
        send_event_when_blocked: true
        remove: false
"""


class TestOrganizerSpecs(ZPLBaseTestCase):
    """
    Test that Organizers can use zProperties and other attributes
    
        - test org creation
            - with create true and false
        - test zproperty setting
            - with reset true and false
        - test org removal
            - with remove tru and false
        - test removal of mappings/processes
    """

    yaml_doc = YAML_DOC

    def afterSetUp(self):
        super(TestOrganizerSpecs, self).afterSetUp()
        config = self.configs.get('ZenPacks.zenoss.Organizers')
        self.cfg = config.get('cfg')

    def test_process_classes(self):
        """Test that process class mappings are removed (or not) as intended"""
        spec = self.cfg.process_class_organizers.get('/TestClasses')
        name = spec.__class__.__name__

        # create the organizer and mappings
        init_org = spec.create_organizer(self.dmd)
        # import pdb ; pdb.set_trace()
        # 2 mappings should exist
        self.assertEquals(len(init_org.osProcessClasses()), 2,
            '{} {} is missing process class mappings'.format(name, spec.path))

        # remove it
        spec.remove_organizer(self.dmd)
        # organizer should still exist
        org = spec.get_organizer(self.dmd)

        # this mapping should remain
        self.assertTrue(org.osProcessClasses.findObject('remain'),
            '{} {} process class mapping should not have been removed'.format(
            name, spec.path))

        # this one should be removed
        gone = None
        try:
            gone = org.osProcessClasses.findObject('remove')
        except AttributeError:
            pass
        self.assertIsNone(gone,
                '{} {} mapping should have been removed'.format(name, spec.path))

        # one mapping should remain
        self.assertEquals(len(org.osProcessClasses()), 1,
            '{} {} should only have one mapping left'.format(name, spec.path))

    def test_event_mappings(self):
        """Test that event class mappings are removed (or not) as intended"""
        spec = self.cfg.event_classes.get('/Organizer/Mappings')
        name = spec.__class__.__name__

        # create the organizer and mappings
        init_org = spec.create_organizer(self.dmd)
        # 2 mappings should exist
        self.assertEquals(len(init_org.instances()), 2,
            '{} {} is missing event class mappings'.format(name, spec.path))

        # remove it
        spec.remove_organizer(self.dmd)
        # organizer should still exist
        org = spec.get_organizer(self.dmd)

        # this mapping should remain
        self.assertTrue(org.instances.findObject('TestRemain'),
            '{} {} event class mapping should not have been removed'.format(
            name, spec.path))

        # this one should be removed
        gone = None
        try:
            gone = org.instances.findObject('TestRemove')
        except AttributeError:
            pass
        self.assertIsNone(gone,
                '{} {} mapping should have been removed'.format(name, spec.path))

        # one mapping should remain
        self.assertEquals(len(org.instances()), 1,
            '{} {} should only have one mapping left'.format(name, spec.path))

    def test_device_class(self):
        """Test that device class is created and zProperties set"""
        self.get_organizer_results(
            self.cfg.device_classes.get('/Server/NewDevices'),
            'zSnmpMonitorIgnore', False)

    def test_device_class_reserved(self):
        """Test that device class is created and zProperties set"""
        self.get_organizer_results(
            self.cfg.device_classes.get('/Server'),
            'zSnmpMonitorIgnore', False, True)

    def test_event_class(self):
        """Test that event class is created and zProperties set"""
        self.get_organizer_results(
            self.cfg.event_classes.get('/Organizer/Status'),
            'zFlappingThreshold', 5)

    def test_event_class_reserved(self):
        """Test that event class is created and zProperties set"""
        self.get_organizer_results(
            self.cfg.event_classes.get('/Status'),
            'zFlappingThreshold', 5, True)

    def test_process_class_organizers(self):
        """Test that process class is created and zProperties set"""
        self.get_organizer_results(
            self.cfg.process_class_organizers.get('/Test'),
            'zAlertOnRestart', True)

    def get_organizer_results(self, spec, zproperty, new_val, reserved=False):
        """Test that device class is created and zProperties set"""

        name = spec.__class__.__name__

        default_val = spec.zProperties.get(zproperty)

        #  class should not be created if create is False
        spec.create = False
        org = spec.create_organizer(self.app.zport.dmd)
        self.assertIsNone(org,
            '{} {} should not have been created'.format(name, spec.path))

        # it should be created if create is True
        spec.create = True
        org = spec.create_organizer(self.dmd)
        self.assertTrue(org,
            '{} {} should have been created'.format(name, spec.path))
        self.assertEquals(getattr(org, zproperty), default_val,
            '{} {} zProperty was not set correctly'.format(name, spec.path))

        # Since reset is true, the zproperty should change
        spec.zProperties[zproperty] = new_val
        org = spec.create_organizer(self.dmd)
        self.assertEquals(getattr(org, zproperty), new_val,
            '{} {} zProperty was not set correctly'.format(name, spec.path))

        # with reset false, zproperty should stay the same
        spec.reset = False
        # test reset of zProperties
        spec.zProperties[zproperty] = default_val
        org = spec.create_organizer(self.dmd)
        self.assertEquals(getattr(org, zproperty), new_val,
            '{} {} zProperty was not set correctly'.format(name, spec.path))

        # test device class removal
        spec.remove = False
        removed = spec.remove_organizer(self.dmd)
        self.assertFalse(removed,
            ' {} {} should not have been removed'.format(name, spec.path))
        org = spec.get_organizer(self.dmd)
        self.assertTrue(org,
            '{} {} should not have been removed'.format(name, spec.path))

        spec.remove = True
        # test device class removal
        removed = spec.remove_organizer(self.dmd)
        org = spec.get_organizer(self.dmd)
        if reserved:
            self.assertFalse(removed,
                '{} {} should not have been removed'.format(name, spec.path))
            self.assertTrue(org,
                '{} {} should not have been removed'.format(name, spec.path))
        else:
            self.assertTrue(removed,
                '{} {} should have been removed'.format(name, spec.path))
            self.assertIsNone(org,
                '{} {} should have been removed'.format(name, spec.path))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrganizerSpecs))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
