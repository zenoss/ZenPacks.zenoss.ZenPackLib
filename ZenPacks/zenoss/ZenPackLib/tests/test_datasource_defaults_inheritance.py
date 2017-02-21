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

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """
name: ZenPacks.zenoss.CalculatedPerformance
device_classes:
  /Devices:
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


class TestDatasourceInheritance(ZPLTestBase):
    """Test fix for ZEN-24083

       datasource inheritance custom Datasource with DEFAULTS
    """
    yaml_doc = YAML_DOC
    use_dmd = True
    disableLogging = False

    def test_datasource_inheritance(self):
        if self.z.zenpack_installed():
            self.assertTrue(self.z.check_templates_vs_yaml(), "Template objects do not match YAML")
            self.assertTrue(self.z.check_templates_vs_specs(), "Template objects do not match Spec")
            # check properties on dummy template
            dcs = self.z.cfg.device_classes.get('/Devices')
            tcs = dcs.templates.get('TESTAGGFAIL')
            t = tcs.create(self.z.dmd, False)
            for ds in t.datasources():
                # standard paramenter
                self.assertEquals(ds.component, '${here/id}', 'datasource property (component) was not inherited from DEFAULTS')
                # extraparams parameter
                self.assertEquals(ds.targetDataSource, 'ethernetcmascd_64', 'datasource property (targetDataSource) was not inherited from DEFAULTS')
                # test local override of DEFAULTS
                if ds.id == 'agg_in_octets':
                    self.assertEquals(ds.targetDataPoint, 'aggifHCOutOctets', 'datasource property (targetDataPoint) DEFAULTS override was not set')
        else:
            self.log.warn('Skipping test_integer_threshold since ZenPacks.zenoss.CalculatedPerformance not installed.')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDatasourceInheritance))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
