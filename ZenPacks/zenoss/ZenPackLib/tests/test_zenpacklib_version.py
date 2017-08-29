#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015-2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
"""Test that this version of ZenPackLib displays correct version"""

import os
import re

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib import zenpacklib


class TestInstalledZenPackLibVersion(ZPLTestBase):
    """Test this version of ZenPackLib against relevant installed ZenPacks"""

    def get_version(self):
        '''extract the ZenPack version from setup.py'''

        def get_path():
            # develop mode
            dev_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'setup.py')
            if os.path.exists(dev_path):
                return dev_path
            # egg mode
            egg_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'EGG-INFO', 'PKG-INFO')
            if os.path.exists(egg_path):
                return egg_path

        path = get_path()
        if not path:
            return

        data = None
        with open(path) as setup_file:
            data = setup_file.readlines()
        if data:
            for line in data:
                if 'VERSION' in line:
                    return line.split('=')[-1].strip().replace('"', '')
                else:
                    try:
                        tag, value = line.split(':')
                        if tag == 'Version':
                            # In cases, when the version contains a build info suffix,
                            # we check whether the version starts with Major.Minor.Revision format
                            # and return just the appropriate part.
                            match = re.match(r'(?P<version>\d+\.\d+\.\d+)', value.strip())
                            if match:
                                return match.group('version')
                    except:
                        continue
        return None

    def test_zenpacklib_version(self):
        """test that setup.py VERSION matches zenpacklib __version__"""
        expected = self.get_version()
        actual = zenpacklib.__version__
        self.assertEquals(expected, actual, "ZenPackLib version mismatch in zenpacklib.py.  Expected {}, actual {}".format(expected, actual))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstalledZenPackLibVersion))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
