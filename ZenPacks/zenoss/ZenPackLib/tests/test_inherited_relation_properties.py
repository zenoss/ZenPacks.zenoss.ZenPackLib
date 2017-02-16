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
    This is designed to test whether or not a relation added to a 
    zenpacklib.Device subclass wipes out other relations added to 
    Products.ZenModel.Device (ZEN-24108)
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """
name: ZenPacks.zenoss.OpenStackInfrastructure
zProperties:
  DEFAULTS:
    category: OpenStack
class_relationships:
- Endpoint(components) 1:MC OpenstackComponent
- OrgComponent(childOrgs) 1:M (parentOrg)OrgComponent

classes:
  Endpoint:
    base: [zenpacklib.Device]
    meta_type: OpenStackInfrastructureEndpoint
    label: OpenStack Endpoint
  OpenstackComponent:
    base: [zenpacklib.Component]
    relationships:
      endpoint:
        grid_display: true
        label: Endpoint
  OrgComponent:
    base: [OpenstackComponent]
    relationships:
      childOrgs:
        label: Children
        order: 1.1
        label_width: 60
        content_width: 60
      parentOrg:
        label: Parent Region
        order: 1.0
        label_width: 60
        content_width: 60
  AvailabilityZone:
    base: [OrgComponent]
    meta_type: OpenStackInfrastructureAvailabilityZone
    label: Availability Zone
    order: 2
    relationships:
      parentOrg:
        label: Parent
      childOrgs:
        grid_display: false
        details_display: false
"""


class TestInheritedRelationProperties(ZPLTestBase):
    """Test fix for ZEN-23763

       specifying properties (display, label, etc) on an inherited relationship
    """
    yaml_doc = YAML_DOC

    def test_inherited_relation_display(self):
        comp = self.z.cfg.classes.get('OpenstackComponent')
        org = self.z.cfg.classes.get('OrgComponent')
        az = self.z.cfg.classes.get('AvailabilityZone')

        self.property_value(comp, 'endpoint', 'grid_display', True)
        self.property_value(comp, 'endpoint', 'label', 'Endpoint')
        self.property_value(org, 'endpoint', 'grid_display', True)
        self.property_value(org, 'endpoint', 'label', 'Endpoint')
        self.property_value(az, 'endpoint', 'grid_display', True)
        self.property_value(az, 'endpoint', 'label', 'Endpoint')

        self.property_value(org, 'parentOrg', 'grid_display', True)
        self.property_value(org, 'parentOrg', 'label', 'Parent Region')
        self.property_value(org, 'parentOrg', 'label_width', 60)

        self.property_value(az, 'parentOrg', 'grid_display', True)
        self.property_value(az, 'parentOrg', 'label', 'Parent')
        self.property_value(az, 'parentOrg', 'label_width', 60)

        self.property_value(org, 'childOrgs', 'grid_display', True)
        self.property_value(org, 'childOrgs', 'label', 'Children')
        self.property_value(org, 'childOrgs', 'label_width', 60)

        self.property_value(az, 'childOrgs', 'grid_display', False)
        self.property_value(az, 'childOrgs', 'label', 'Children')
        self.property_value(az, 'childOrgs', 'label_width', 60)

    def property_value(self, spec, rel_name, attr_name, expected):
        rel = spec.relationships.get(rel_name)
        actual = getattr(rel, attr_name, None)
        self.assertEquals(expected, actual,
                          '{} has unexpected value for "{}", expected: {}, actual: {}'.format(
                          spec.name, rel_name, expected, actual)
                          )

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInheritedRelationProperties))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
