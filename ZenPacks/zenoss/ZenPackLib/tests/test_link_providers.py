#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test link providers
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness

unused(Globals)


LINK_PROVIDER_YAML = """
name: ZenPacks.zenoss.ZenPackLib
link_providers:
    Cluster Node:
        global_search: false
        link_class: ZenPacks.zenoss.Microsoft.Windows.Device.Device
        catalog: device
        queries:
            - id:clusterhostdevices
    Cluster:
        link_class: ZenPacks.zenoss.Microsoft.Windows.Device.Device
        queries:
            - id:clusterdevices
        device_class: /Server/Microsoft/Cluster
"""

EXPECTED_YAML = {
    'link_providers': {
        'Cluster': {
            'device_class': '/Server/Microsoft/Cluster',
            'link_class': 'ZenPacks.zenoss.Microsoft.Windows.Device.Device',
            'queries': ['id:clusterdevices']
        },
        'Cluster Node': {
            'global_search': False,
            'catalog': 'device',
            'link_class': 'ZenPacks.zenoss.Microsoft.Windows.Device.Device',
            'queries': ['id:clusterhostdevices']
        }
    },
    'name': 'ZenPacks.zenoss.ZenPackLib'
}

link_provider_zp = ZPLTestHarness(LINK_PROVIDER_YAML)


class TestLinkProviders(BaseTestCase):
    """Test Event Classes
    """

    def test_link_providers(self):
        self.maxDiff = None
        self.assertEquals(len(link_provider_zp.yaml['link_providers']), len(link_provider_zp.cfg.link_providers))
        self.assertEquals(EXPECTED_YAML, link_provider_zp.yaml)
        link_providers = link_provider_zp.cfg.link_providers
        self.assertFalse(link_providers['Cluster'].global_search)
        self.assertEquals(link_providers['Cluster'].link_class, 'ZenPacks.zenoss.Microsoft.Windows.Device.Device')
        self.assertEquals(link_providers['Cluster'].catalog, 'device')
        self.assertEquals(link_providers['Cluster'].queries, {'id': 'clusterdevices'})
        self.assertIsNone(link_providers['Cluster Node'].device_class)
        self.assertEquals(link_providers['Cluster Node'].catalog, 'device')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLinkProviders))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
