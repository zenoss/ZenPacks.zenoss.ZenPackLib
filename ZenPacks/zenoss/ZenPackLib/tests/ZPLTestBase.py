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
    Basic Unit test utilizing ZPLTestHarness
"""
import io
import yaml
import os
import subprocess
import traceback
import logging

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
from Products.ZenTestCase.BaseTestCase import BaseTestCase
unused(Globals)

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness
from ZenPacks.zenoss.ZenPackLib.lib.helpers.WarningLoader import WarningLoader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.ZenPackLibLog import ZPLOG


class ZPLTestBase(BaseTestCase):
    """BaseTestCase class with ZPLTestHarness support"""
    log = logging.getLogger("ZenPackLib.test")
    yaml_doc = '''name: ZenPacks.zenoss.ZenPackLib'''
    use_dmd = False
    disableLogging = True

    def afterSetUp(self):
        super(ZPLTestBase, self).afterSetUp()
        # for a list of docs, iterate through
        if isinstance(self.yaml_doc, list):
            counter = 0
            for y_d in self.yaml_doc:
                if counter == 0:
                    try:
                        self.z = ZPLTestHarness(y_d)
                    except Exception:
                        self.fail(traceback.format_exc(limit=0))
                else:
                    try:
                        setattr(self, 'z_{}'.format(counter), ZPLTestHarness(y_d))
                    except Exception:
                        self.fail(traceback.format_exc(limit=0))
                counter += 1
        else:
            try:
                self.z = ZPLTestHarness(self.yaml_doc)
            except Exception:
                self.fail(traceback.format_exc(limit=0))
            if self.use_dmd:
                self.z.connect()

    def tearDown(self):
        if isinstance(self.yaml_doc, list):
            counter = 1
            for y_d in self.yaml_doc:
                z = getattr(self, 'z_{}'.format(counter), None)
                if z:
                    z.disconnect()
                counter += 1

        self.z.disconnect()


class ZPLTestCommand(ZPLTestBase):
    """Add support for command line testing"""

    log = logging.getLogger("ZenPackLib.test.command")
    log.setLevel(logging.INFO)
    disableLogging = False
    zenpacklib_path = os.path.join(os.path.dirname(__file__), "../zenpacklib.py")

    def _zenpacklib_cmd(self, *args):
        """test output of zenpacklib.py"""
        cmd = ('python', self.zenpacklib_path,) + args
        cmdstr = " ".join(cmd)

        self.log.info("Running %s" % cmdstr)
        p, out, err = self.get_cmd_output(cmd)

        self.log.debug("Stdout: %s\nStderr: %s", out, err)

        self.assertIs(p.returncode, 0,
                      'Error running %s: %s%s' % (cmdstr, err, out))

        if out is not None:
            self.assertNotIn("Error", out)
            self.assertNotIn("Error", out)
        if err is not None:
            self.assertNotIn("Traceback", err)
            self.assertNotIn("Traceback", err)

        return out

    def get_cmd_success(self, cmd, vars={}):
        """execute a command and assert success"""
        p, out, err = self.get_cmd_output(cmd, vars)
        self.log.debug("out=%s, err=%s", out, err)
        msg = 'Command "{}" failed with error:\n  {}'.format(cmd, err)
        self.assertIs(p.returncode, 0, msg)
        return out

    @classmethod
    def get_cmd_output(cls, cmd, vars={}):
        """execute a command and return the output"""
        cls.log.info(" ".join(cmd))
        env = dict(os.environ)
        env.update(vars)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        p.wait()
        return (p, out, err)

# Using this ZenPackSpec name for logging-type tests
LOG = ZPLOG.add_log('ZenPacks.zenoss.TestLogging')
LOG.propagate = False


class WarningLoader(WarningLoader):
    LOG = LOG


class LogCapture(object):
    """"""
    def start_capture(self):
        self.buffer = io.StringIO()
        WarningLoader.LOG.setLevel(logging.WARNING)
        self.handler = logging.StreamHandler(self.buffer)
        self.handler.setFormatter(logging.Formatter(u'[%(levelname)s] %(message)s'))
        WarningLoader.LOG.addHandler(self.handler)

    def stop_capture(self):
        WarningLoader.LOG.removeHandler(self.handler)
        self.handler.flush()
        self.buffer.flush()
        return self.buffer.getvalue()

    def test_yaml(self, yaml_doc):
        self.start_capture()
        cfg = yaml.load(yaml_doc, Loader=WarningLoader)
        logs = self.stop_capture()
        return str(logs)
