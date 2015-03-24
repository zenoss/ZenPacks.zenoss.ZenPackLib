#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Schema unit tests.

This is primarily testing that zenpacklib is functioning as desired. If
zenpacklib was already mature these kinds of tests would be in its
test suite instead of in the ZenPack's.

"""

import logging
import subprocess
import os
import re
import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('zen.zenpacklib.tests')

from Products.ZenTestCase.BaseTestCase import BaseTestCase


class TestCommands(BaseTestCase):

    zenpack_name = 'ZenPacks.zenoss.ZPLTest1'
    zenpack_path = os.path.join(os.path.dirname(__file__),
                                "data/zenpacks/ZenPacks.zenoss.ZPLTest1")
    zenpacklib_path = os.path.join(os.path.dirname(__file__),
                                   "../zenpacklib.py")
    yaml_path = os.path.join(zenpack_path, 'ZenPacks/zenoss/ZPLTest1/zenpack.yaml')

    disableLogging = False

    def afterSetUp(self):
        try:
            super(TestCommands, self).afterSetUp()
        except ImportError, e:
            self.assertFalse(
                e.message == 'No module named ZPLTest1',
                "ZPLTest1 zenpack is not installed.  You must install it before running this test:\n   zenpack --link --install=%s" % self.zenpack_path
            )

    def _smoke_command(self, *args):
        cmd = (self.zenpacklib_path,) + args
        cmdstr = " ".join(cmd)

        LOG.info("Running %s" % cmdstr)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        p.wait()
        LOG.debug("Stdout: %s\nStderr: %s", out, err)

        self.assertIs(p.returncode, 0,
                      'Error running %s: %s%s' % (cmdstr, err, out))

        if out is not None:
            self.assertNotIn("Error", out)
            self.assertNotIn("Error", out)
        if err is not None:
            self.assertNotIn("Traceback", err)
            self.assertNotIn("Traceback", err)

        return out

    def test_smoke_lint(self):
        self._smoke_command("lint", self.yaml_path)

    # Can't be tested with ZPLTest1, because that is already using YAML.
    # Need to build another small zenpack if we want to do that.
    # def test_smoke_py_to_yaml(self):
    #     self._smoke_command("py_to_yaml", self.zenpack_name)

    def test_smoke_dump_templates(self):
        self._smoke_command("dump_templates", self.zenpack_name)

    def test_smoke_class_diagram(self):
        self._smoke_command("class_diagram yuml", self.yaml_path)

    def test_version(self):
        output = self._smoke_command("version").strip()
        version_pattern = r'^\d+\.\d+\.\d+(dev)?$'
        match = re.match(version_pattern, output)
        self.assertTrue(
            match,
            "version output {!r} doesn't match /{}/"
            .format(output, version_pattern))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCommands))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
