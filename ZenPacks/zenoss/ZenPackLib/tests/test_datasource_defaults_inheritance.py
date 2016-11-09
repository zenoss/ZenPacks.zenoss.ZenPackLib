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
    datasource inheritance custom Datasource with DEFAULTS (ZEN-24083)
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


def aggregator_installed():
    """Return True if AggregatingDataSource is installed"""
    try:
        from ZenPacks.zenoss.CalculatedPerformance.datasources.AggregatingDataSource import AggregatingDataSource
    except ImportError:
        pass
    else:
        return True
    return False

YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Device:
    templates:
      TESTAGGFAIL:
        description: you should see that targetDatsource does not set
        datasources:
          # THESE defaults arent working so set manually below remove when fixed
          DEFAULTS:
            type: Datapoint Aggregator
            eventClass: /App/Zenoss
            component: "${here/id}"
            targetDataSource: ethernetcmascd_64
            targetDataPoint: ifHCOutOctets
            targetMethod: os.interfaces
          agg_out_octets:
            datapoints:
              aggifHCOutOctets:
                operation: sum
          agg_in_octets:
            targetDataPoint: aggifHCOutOctets
            datapoints:
              aggifHCInOctets:
                operation: sum
"""


class TestZen24083(BaseTestCase):
    """Test fix for ZEN-24083

       datasource inheritance custom Datasource with DEFAULTS
    """

    def test_datasource_inheritance(self):
        if aggregator_installed():
            z = ZPLTestHarness(YAML_DOC)
            z.connect()
            self.assertTrue(z.check_templates_vs_yaml(), "Template objects do not match YAML")
            self.assertTrue(z.check_templates_vs_specs(), "Template objects do not match Spec")
            # check properties on dummy template
            dcs = z.cfg.device_classes.get('/Device')
            tcs = dcs.templates.get('TESTAGGFAIL')
            t = tcs.create(z.dmd, False)
            for ds in t.datasources():
                # standard paramenter
                self.assertEquals(ds.component, '${here/id}', 'datasource property (component) was not inherited from DEFAULTS')
                # extraparams parameter
                self.assertEquals(ds.targetDataSource, 'ethernetcmascd_64', 'datasource property (targetDataSource) was not inherited from DEFAULTS')
                # test local override of DEFAULTS
                if ds.id == 'agg_in_octets':
                    self.assertEquals(ds.targetDataPoint, 'aggifHCOutOctets', 'datasource property (targetDataPoint) DEFAULTS override was not set')



def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen24083))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
