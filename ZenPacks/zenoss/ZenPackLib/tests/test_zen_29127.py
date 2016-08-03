#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""extra_paths unit tests

This module tests zenpacklib 'extra_paths' and path reporters.

"""
# stdlib Imports
import os
import site
import tempfile
import traceback
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


YAML = """
name: ZenPacks.zenoss.SomeZenPack

class_relationships:
- BaseDevice 1:MC BaseComponent


classes:
  BaseDevice:
    base: [zenpacklib.Device]
    relationships:
      baseComponents: {}
      # this doesn't exist
      auxComponents: {}
      # These exist but aren't defined in this schema
      systems: {}
      deviceClass: {}

  BaseComponent:
    # Component Base Type
    base: [zenpacklib.Component]
    relationships:
      baseDevice: {}
      # this doesn't exist
      auxComponents: {}

  AuxComponent:
    # Component Base Type
    base: [zenpacklib.Component]
    relationships:
      # this exists but isn't defined in this schema
dependents: {}
"""


class TestZen21927(BaseTestCase):
    """Test removal of undefined relations"""

    def test_undefined_relations(self):
        ''''''
        with tempfile.NamedTemporaryFile() as f:
            f.write(YAML.strip())
            f.flush()
            try:
                cfg = zenpacklib.load_yaml(f.name)
            except:
                msg = traceback.format_exc(limit=0)
                self.fail(msg)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen21927))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()