#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Function unit tests.

This module tests "public" zenpacklib functions.

"""

# stdlib Imports
import os
import unittest
import site

# Zenoss Imports
import Globals
from Products.ZenUtils.Utils import unused

unused(Globals)

# zenpacklib Imports
site.addsitedir(os.path.join(os.path.dirname(__file__), '..'))
from ZenPacks.zenoss.ZenPackLib import zenpacklib


class TestFunctions(unittest.TestCase):

    """Functions test suite."""

    def test_relationships_from_yuml_blank_lines(self):
        """Test that YUML containing empty lines can be parsed."""
        yuml = '\n'.join((
            "",
            "[MyDevice]++-[MyComponentA]",
            "[MyDevice]++-[MyComponentB]",
            "    ",
            "[MyComponentA]*-.-*[MyComponentB]"
            "",
            ))

        classes = zenpacklib.relationships_from_yuml(yuml)

        self.assertEquals(
            len(classes), 3,
            "{} classes found in YUML instead of 3".format(len(classes)))

        expected_classes = [{
            'left_class': 'MyDevice',
            'left_relname': 'myComponentAs',
            'left_type': 'ToManyCont',
            'right_class': 'MyComponentA',
            'right_relname': 'myDevice',
            'right_type': 'ToOne',
        }, {
            'left_class': 'MyDevice',
            'left_relname': 'myComponentBs',
            'left_type': 'ToManyCont',
            'right_class': 'MyComponentB',
            'right_relname': 'myDevice',
            'right_type': 'ToOne',
        }, {
            'left_class': 'MyComponentA',
            'left_relname': 'myComponentBs',
            'left_type': 'ToMany',
            'right_class': 'MyComponentB',
            'right_relname': 'myComponentAs',
            'right_type': 'ToMany',
        }]

        self.assertEquals(classes, expected_classes)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
