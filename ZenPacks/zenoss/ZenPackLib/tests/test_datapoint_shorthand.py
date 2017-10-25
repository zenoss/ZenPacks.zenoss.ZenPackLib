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

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


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
                aliases: {dp_gauge_map_alias: null}
              dp_gauge_map_descr:
                rrdtype: GAUGE
                description: Some kind of thing
              dp_gauge_map_extra:
                rrdtype: GAUGE
                extra_property: true
              dp_unknown: UNKNOWNTYPE
              dp_aliased: DERIVE_MIN_0_ALIAS
              dp_aliased_2: 
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {dp_aliased_2: null}
              dp_aliased_3: 
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {dp_aliased_alt: null}
              dp_aliased_4: 
                rrdtype: COUNTER
                rrdmin: 0
                rrdmax: 100
                aliases: {dp_aliased_4: null}
              dp_aliased_5: 
                rrdtype: RAW
                rrdmin: 0
                rrdmax: 100
                aliases: {dp_aliased_5: null}
              dp_aliased_6: 
                rrdtype: ABSOLUTE
                rrdmin: 0
                rrdmax: 100
                aliases: {dp_aliased_6: null}
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
              dp_gauge: GAUGE
              dp_counter_map: COUNTER
              dp_gauge_map_alias: GAUGE_ALIAS
              dp_gauge_map_descr:
                rrdtype: GAUGE
                description: Some kind of thing
              dp_gauge_map_extra:
                rrdtype: GAUGE
                extra_property: true
              dp_unknown: GAUGE
              dp_aliased: DERIVE_MIN_0_ALIAS
              dp_aliased_2: DERIVE_MIN_0_ALIAS
              dp_aliased_3:
                rrdtype: DERIVE
                rrdmin: 0
                aliases: {dp_aliased_alt: null}
              dp_aliased_4: COUNTER_MIN_0_MAX_100_ALIAS
              dp_aliased_5: RAW_MIN_0_MAX_100_ALIAS
              dp_aliased_6: ABSOLUTE_MIN_0_MAX_100_ALIAS
            oid: 1.3.6.1.4.1.2021.10.1.5.2
"""

class TestDatapointShorthand(ZPLTestBase):
    """Test DataPointSpec shorthand handling"""

    yaml_doc = YAML_DOC

    def test_datapoint_shorthand(self):
        ''''''
        diff = self.z.get_diff(EXPECTED, self.z.exported_yaml)
        self.assertEqual(self.z.exported_yaml,
                         EXPECTED,
                         'Datapoint shorthand unexpected difference between expected and actual:\n{}'.format(diff))


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
