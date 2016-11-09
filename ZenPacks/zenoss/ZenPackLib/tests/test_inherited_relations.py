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
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib



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
        grid_display: True
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
      childOrgs:
        grid_display: True
        details_display: False
"""


class TestZen23763(BaseTestCase):
    """Test fix for ZEN-23763

       specifying properties (display, label, etc) on an inherited relationship
    """

    def test_inherited_relation_display(self):
        CFG = zenpacklib.load_yaml(YAML_DOC)
        rel = CFG.classes.get('AvailabilityZone').relationships.get('parentOrg')
        self.assertEquals(rel.label, 'Parent Region', 'Inherited relation label failed')
        rel = CFG.classes.get('AvailabilityZone').relationships.get('endpoint')
        self.assertEquals(rel.grid_display, True, 'Inherited relation grid_display failed')
        rel = CFG.classes.get('AvailabilityZone').relationships.get('childOrgs')
        self.assertEquals(rel.grid_display, True, 'Inherited relation grid_display failed')

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen23763))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
