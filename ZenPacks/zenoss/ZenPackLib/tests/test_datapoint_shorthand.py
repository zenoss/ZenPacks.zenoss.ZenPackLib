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
    Test DataPointSpec shorthand handling
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


YAML_DOC = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Server:
    templates:
      TEST:
        datasources:
          datasource:
            type: SNMP
            datapoints:
              dp_gauge: GAUGE
              dp_counter_map:
                rrdtype: COUNTER
              dp_gauge_map_alias:
                rrdtype: GAUGE
                aliases: {dp_gauge_map: null}
              dp_gauge_map_descr:
                rrdtype: GAUGE
                description: Some kind of thing
              dp_gauge_map_extra:
                rrdtype: GAUGE
                extra_property: true
              dp_unknown: UNKNOWNTYPE
            oid: 1.3.6.1.4.1.2021.10.1.5.2
            
"""

EXPECTED = """name: ZenPacks.zenoss.ZenPackLib
device_classes:
  /Server:
    templates:
      TEST:
        datasources:
          datasource:
            type: SNMP
            datapoints:
              dp_counter_map: COUNTER
              dp_gauge: GAUGE
              dp_gauge_map_alias:
                rrdtype: GAUGE
                aliases: {dp_gauge_map: null}
              dp_gauge_map_descr:
                rrdtype: GAUGE
                description: Some kind of thing
              dp_gauge_map_extra:
                rrdtype: GAUGE
                extra_property: true
              dp_unknown: GAUGE
            oid: 1.3.6.1.4.1.2021.10.1.5.2
"""

class TestDatapointShorthand(BaseTestCase):
    """Test DataPointSpec shorthand handling"""

    def test_datapoint_shorthand(self):
        ''''''
        z = ZPLTestHarness(YAML_DOC)
        self.assertEqual(z.exported_yaml, EXPECTED,
                         'Datapoint shorthand expected {} got {}'.format(EXPECTED,
                                                                         z.exported_yaml))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDatapointShorthand))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
