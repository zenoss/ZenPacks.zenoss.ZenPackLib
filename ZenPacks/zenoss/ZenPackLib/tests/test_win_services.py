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
    Test Event Classes
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness

unused(Globals)


WIN_SERVICE_YAML = """
name: ZenPacks.zenoss.ZenPackLib
windows_service_organizers:
  /WinService/Autos:
    description: Test Windows Service Organizer
    windows_services:
      ALG:
        description: ALG Service
        monitoredStartModes: ['Auto']
        monitor: true
        fail_severity: 3
        remove: true
      BFE:
        description: BFE Service
        monitoredStartModes: ['Auto']
  /WinService/AutosOrManuals:
    description: monitor auto or manual start
    monitor: true
    windows_services:
      ALG:
        description: ALG Service
        monitoredStartModes: ['Auto', 'Manual']
        fail_severity: 3
        remove: true
      BFE:
        description: BFE Service
        monitoredStartModes: ['Auto', 'Manual']
"""


win_service_zp = ZPLTestHarness(WIN_SERVICE_YAML)


class TestWinService(BaseTestCase):
    """Test Windows Service Classes
    """

    def test_event_classes(self):
        self.assertEquals(len(win_service_zp.yaml['windows_service_organizers']), len(win_service_zp.cfg.windows_service_organizers))
        self.assertEquals(len(win_service_zp.yaml['windows_service_organizers']), 2)
        self.assertTrue('/WinService/Autos' in win_service_zp.cfg.windows_service_organizers.keys())
        self.assertFalse(win_service_zp.cfg.windows_service_organizers['/WinService/Autos'].remove)
        self.assertEquals(len(win_service_zp.yaml['windows_service_organizers']['/WinService/Autos']['windows_services']),
                          len(win_service_zp.cfg.windows_service_organizers['/WinService/Autos'].windows_services))
        self.assertEquals(win_service_zp.yaml['windows_service_organizers']['/WinService/Autos']['windows_services']['ALG']['monitoredStartModes'],
                          win_service_zp.cfg.windows_service_organizers['/WinService/Autos'].windows_services['ALG'].monitoredStartModes)
        self.assertEquals(win_service_zp.cfg.windows_service_organizers['/WinService/AutosOrManuals'].windows_services['ALG'].monitoredStartModes,
                          ['Auto', 'Manual'])
        self.assertTrue(win_service_zp.cfg.windows_service_organizers['/WinService/AutosOrManuals'].monitor)
        self.assertEquals(win_service_zp.cfg.windows_service_organizers['/WinService/AutosOrManuals'].windows_services['ALG'].fail_severity, 3)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWinService))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
