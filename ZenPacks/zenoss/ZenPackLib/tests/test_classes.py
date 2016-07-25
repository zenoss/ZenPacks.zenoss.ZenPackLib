#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Spec unit tests.

This module tests zenpacklib "Specs". These are the intermediate step
between YAML and Zenoss functionality.

"""

# stdlib Imports
import os
import unittest
import site

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')

from .ZPLTestHarness import ZPLTestHarness

# Zenoss Imports
import Globals  # noqa


dynamicview_js = '''Zenoss.nav.appendTo('Component', [{
    id: 'subcomponent_view',
    text: _t('Dynamic View'),
    xtype: 'dynamicview',
    relationshipFilter: 'impacted_by',
    viewName: 'service_view',
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
'''

ibm_component = '''ZC.LogicalPartitionsPanel = Ext.extend(ZC.ZPL_ZenPacks_zenoss_IBM_Power_ComponentGridPanel, {    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'LogicalPartitions',
            autoExpandColumn: 'name',
            fields: [{name: 'uid'},{name: 'name'},{name: 'meta_type'},{name: 'class_label'},{name: 'status'},{name: 'severity'},{name: 'usesMonitorAttribute'},{name: 'monitame: 'locking'},{name: 'hmcserver'},{name: 'getManagedSystemStatusText'},{name: 'managedSystem'}],
            columns: [{id: 'severity',dataIndex: 'severity',header: _t('Events'),renderer: Zenoss.render.severity,width: 50},{id: 'name',dataIndex: 'name',header: _t('Name'r: Zenoss.render.zenpacklib_ZenPacks_zenoss_IBM_Power_entityLinkFromGrid},{id: 'HMCServer',dataIndex: 'hmcserver',header: _t('HMC Server'),width: 100,renderer: Zenoss.rendelib_ZenPacks_zenoss_IBM_Power_entityLinkFromGrid},{id: 'managedSystem',dataIndex: 'managedSystem',header: _t('Managed System'),width: 100,renderer: Zenoss.render.zenpacklib_zenoss_IBM_Power_entityLinkFromGrid},{id: 'getManagedSystemStatusText',dataIndex: 'getManagedSystemStatusText',header: _t('Managed System Status'),width: 130},{id: 'monitoIndex: 'monitored',header: _t('Monitored'),renderer: Zenoss.render.checkbox,width: 70},{id: 'locking',dataIndex: 'locking',header: _t('Locking'),renderer: Zenoss.render.locs,width: 65}]
        });
        ZC.LogicalPartitionsPanel.superclass.constructor.call(this, config);
    }
});
'''

class TestClasses(unittest.TestCase):

    """Specs test suite."""
    zps = []

    def setUp(self):
        fdir = '%s/data/yaml' % os.path.dirname(__file__)
        for f in os.listdir(fdir):
            if '.yaml' not in f:
                continue
        #for file in ['ms_windows.yaml', 'bigipmonitor.yaml', 'ibm_power.yaml', 'hp_proliant.yaml']:
            file = os.path.join(os.path.dirname(__file__), 'data/yaml/%s' % f)
            print "LOADING FILE: %s" % file
            log.info("loading file: %s" % file)
            self.zps.append(ZPLTestHarness(file))

    def test_ClassProperties(self):
        '''
        check that class properties follow the spec
        '''
        log.info("Checking Properties")
        for zp in self.zps:
            self.assertTrue(zp.check_properties(),"Test Failed")

    def test_ClassRelations(self):
        '''
        check that class relations follow the spec
        '''
        log.info("Checking relations")
        for zp in self.zps:
            self.assertTrue(zp.check_cfg_relations(),"Test Failed")

#     def test_DynamicViewComponentNav(self):
#         
#         for zp in self.zps:
#             # dynamicview_nav_js_snippet is only used internally by zenpacklib, but
#             # it should match exactly and be an easier test to make.
#             self.assertMultiLineEqual(
#                 zp.cfg.dynamicview_nav_js_snippet.strip(),
#                 dynamicview_js.strip())
# 
#             # device_js_snippet is actually used to create the JavaScript snippet,
#             # and should contain our subcomponent_view among many other things.
# #             self.assertIn(
# #                 EXPECTED_SUBCOMPONENT_VIEW.strip(),
# #                 zenpack.device_js_snippet.strip())


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestClasses))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
