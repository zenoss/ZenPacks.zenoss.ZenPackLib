#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Test subcomponent_nav_js_snippet

    Validate fix for ZEN-25847
        ZPL creating doubled number of subpanels for same-named relations

"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


YAML_DOC = """name: ZenPacks.zenoss.SubComponentNav
class_relationships:
  - ComputeResource(resourcePools) 1:M (owner)ResourcePool
  - Endpoint 1:MC Datacenter
  - Endpoint(vms) 1:MC VirtualMachine
  - Datacenter 1:MC ComputeResource
  - Datacenter 1:MC ResourcePool
  - Datacenter(vms) 1:M VirtualMachine
  - ResourcePool(childResourcePools) 1:M (parentResourcePool)ResourcePool
  - ResourcePool(vms) 1:M VirtualMachine
classes:
  Endpoint:
    base: [zenpacklib.Device]
  BaseEntity:
    base: [zenpacklib.Component]
  BaseComponent:
    base: [BaseEntity]
  ResourcePool:
    base: [BaseComponent]
    meta_type: vResourcePool
    label: Resource Pool
    extra_paths:
      - ['(parentResourcePool)+']
    relationships:
      datacenter:
        order: 1.1
        label_width: 125
      owner:
        label: Owner
        order: 1.2
        label_width: 125
      vms:
        grid_display: false
        details_display: false
      parentResourcePool:
        grid_display: false
        label: "Parent Resource Pool"
      childResourcePools:
        grid_display: false
        label: "Child Resource Pools"
  VirtualApp:
    base: [ResourcePool]
    meta_type: vVirtualApp
    label: vApp
    relationships:
      owner:
        grid_display: false
      parentResourcePool:
        grid_display: false
        label: "Parent vApp"
      childResourcePools:
        grid_display: false
        label: "Child vApps"
  ComputeResource:
    base: [BaseComponent]
    filter_hide_from: [Datacenter]
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      resourcePools:
        grid_display: false
  Datacenter:
    base: [BaseComponent]
    relationships:
      vms:
        order: 1.5
        label_width: 65
      computeResources:
        grid_display: false
        details_display: false
      resourcePools:
        grid_display: false
  VirtualMachine:
    base: [BaseComponent]
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      resourcePool:
        order: 1.2
"""

expected_rp = "Zenoss.nav.appendTo('Component', [{\n    id: 'component_vresourcepool_child_resource_pools',\n    text: _t('Child Resource Pools'),\n    xtype: 'vResourcePoolPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vResourcePool': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vResourcePoolPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\nZenoss.nav.appendTo('Component', [{\n    id: 'component_vresourcepool_resource_pools',\n    text: _t('Resource Pools'),\n    xtype: 'vResourcePoolPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'Datacenter': return true;\n            case 'ComputeResource': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vResourcePoolPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\n"

expected_va = "Zenoss.nav.appendTo('Component', [{\n    id: 'component_vvirtualapp_child_vapps',\n    text: _t('Child vApps'),\n    xtype: 'vVirtualAppPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vVirtualApp': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vVirtualAppPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\nZenoss.nav.appendTo('Component', [{\n    id: 'component_vvirtualapp_vapps',\n    text: _t('vApps'),\n    xtype: 'vVirtualAppPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'Datacenter': return true;\n            case 'ComputeResource': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vVirtualAppPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\n"



class TestSubComponentNavJS(ZPLBaseTestCase):
    """Test catalog creation for specs"""

    yaml_doc = YAML_DOC
    build = True
    def afterSetUp(self):
        super(TestSubComponentNavJS, self).afterSetUp()
        config = self.configs.get('ZenPacks.zenoss.SubComponentNav')
        self.objects = config.get('objects').class_objects
        
    def test_nav_js(self):
        ''''''
        self.get_test_result('ResourcePool', expected_rp)
        self.get_test_result('VirtualApp', expected_va)
        self.get_test_result('ComputeResource', '')

    def get_test_result(self, name, expected_js):
        cls = self.objects.get(name).get('spec')
        actual_js = cls.subcomponent_nav_js_snippet
        self.assertEquals(actual_js,
                          expected_js,
                          'Unexpected subcomponent_nav_js_snippet for {}, got: {}'.format(id,
                                                                  self.get_diff(expected_js, actual_js)))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubComponentNavJS))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
