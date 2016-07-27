#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Keyword Tests
This test will use lint to load in example yaml with keywords used
"""
# stdlib Imports
import tempfile
import logging

# Zenoss Imports
import Globals  # noqa

from Products.ZenUtils.Utils import unused
from BaseTestCommand import BaseTestCommand

unused(Globals)
log = logging.getLogger('zen.zenpacklib.tests')

RESERVED_YAML = """name: ZenPacks.zenoss.Example
classes:
    ExampleDevice:
        base: [zenpacklib.Device]
        label: Example
        properties:
            uuid:
                label: UUID
            yield:
                label: Yield
    lambda:
        base: [zenpacklib.Component]
        label: Lambda
        properties:
            prop1:
                label: yield
device_classes:
    /Server/SSH:
        templates:
            breadCrumbs:
                description: Poorly named template
                datasources:
                    health:
                        type: COMMAND
                        parser: Nagios
                        commandTemplate: "echo OK|percent=100"
                        datapoints:
                          percent:
                            rrdtype: GAUGE
                            rrdmin: 0
                            rrdmax: 100
"""
NO_RESERVED_YAML = """name: ZenPacks.zenoss.Example
classes:
    ExampleDevice:
        base: [zenpacklib.Device]
        label: Example
        properties:
            prop1:
                label: Example Property
    ProperComponent:
        base: [zenpacklib.Component]
        label: Properly Named Component
        properties:
            prop1:
                label: Property One
"""


class TestKeywords(BaseTestCommand):

    def test_reserved_keywords(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(RESERVED_YAML.strip())
            f.flush()
            out = self._smoke_command('--lint', f.name).split('\n')
            log.debug('Lint results: {}'.format(out))
            self.assertEquals(5, len(out))
            self.assertIn("Found reserved keyword 'uuid'", out[0])
            self.assertIn("Found reserved keyword 'yield'", out[1])
            self.assertIn("Found reserved keyword 'lambda'", out[2])
            self.assertIn("Found reserved keyword 'breadCrumbs'", out[3])

            f.close()

    def test_no_reserved_keywords(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(NO_RESERVED_YAML.strip())
            f.flush()
            out = self._smoke_command('--lint', f.name)
            self.assertEquals('', out)
            f.close()


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestKeywords))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
runner.run()