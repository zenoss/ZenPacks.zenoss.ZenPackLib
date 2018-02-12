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
from ZenPacks.zenoss.ZenPackLib.lib.helpers.loaders import WarningLoader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.ZenPackLibLog import ZPLOG

RUN_TESTS = False
if os.getenv('RUN_BROKEN_TESTS'):
    RUN_TESTS = True
else:
    print "Set RUN_BROKEN_TESTS environment variable to enable unit testing"


class ZPLTestBase(BaseTestCase):
    """BaseTestCase class with ZPLTestHarness support"""
    log = logging.getLogger("ZenPackLib.test")
    yaml_doc = '''name: ZenPacks.zenoss.ZenPackLib'''
    disableLogging = True
    z = None

    def setUp(self):
        if not RUN_TESTS:
            msg = (
                "Skipping {} because environment "
                "variable RUN_BROKEN_TESTS is unset"
                ).format(self.__class__.__name__)
            self.skipTest(msg)
        super(ZPLTestBase, self).setUp()

    def afterSetUp(self):
        super(ZPLTestBase, self).afterSetUp()
        self.load_yaml(self.yaml_doc)

    def load_yaml(self, yaml_doc):
        """"""
        self.z = None
        # for a list of docs, iterate through
        if isinstance(yaml_doc, list):
            counter = 0
            for y_d in yaml_doc:
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
                self.z = ZPLTestHarness(yaml_doc)
            except Exception:
                self.fail(traceback.format_exc(limit=0))

    def install_zpl_zenpack(self, z):
        """install loaded YAML-based zenpack"""
        zenpack = z.cfg.zenpack_class(z.cfg.name)
        zenpack.eggPack = True
        self.dmd.ZenPackManager.packs._setObject(zenpack.id, zenpack)


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

    def get_cmd_success(self, cmd, vars=None):
        """execute a command and assert success"""
        if vars is None:
            vars = {}
        p, out, err = self.get_cmd_output(cmd, vars)
        self.log.debug("out=%s, err=%s", out, err)
        msg = 'Command "{}" failed with error:\n  {}'.format(cmd, err)
        self.assertIs(p.returncode, 0, msg)
        return out

    @classmethod
    def get_cmd_output(cls, cmd, vars=None):
        """execute a command and return the output"""
        if vars is None:
            vars = {}
        cls.log.info(" ".join(cmd))
        env = dict(os.environ)
        env.update(vars)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        p.wait()
        return (p, out, err)


class ZPLTestMockZenPack(ZPLTestBase):
    """BaseTestCase class with ZPLTestHarness support"""
    log = logging.getLogger("ZenPackLib.test")
    yaml_doc = '''name: ZenPacks.zenoss.ZenPackLib'''
    zenpack_name = 'ZenPacks.zenoss.MockZenPack'
    disableLogging = True

    def afterSetUp(self, datasources=None, thresholds=None):
        super(ZPLTestMockZenPack, self).afterSetUp()
        if self.z:
            self.zenpack_name = self.z.zp.__name__
        if datasources is None:
            datasources = []
        if thresholds is None:
            thresholds = []
        self.zenpack = MockZenPack(self.dmd, self.zenpack_name, datasources=datasources, thresholds=thresholds)


class MockZenPack(object):
    ''''''
    def __init__(self, dmd, name, datasources=None, thresholds=None):
        self.dmd = dmd
        self.name = name
        if datasources is None:
            datasources = []
        if thresholds is None:
            thresholds = []
        self.datasources = datasources
        self.thresholds = thresholds
        self.install_zenpack()

    def install_zenpack(self, override_classes=True):
        """Install ZenPack given name and optional class.
    
        This is far from a full installation. The ZenPack object is
        instantiated and added to ZenPackManager. This is mainly useful to
        make modeler plugins and datasource types available for loading.
    
        """
        from Products.ZenModel.ZenPack import ZenPack as DefaultZenPack
        klass = DefaultZenPack
        self.zenpack = klass(self.name)
        self.zenpack.eggPack = True
        self.dmd.ZenPackManager.packs._setObject(self.zenpack.id, self.zenpack)
        if override_classes:
            self.override_get_classes()

    def override_get_classes(self):
        """"""
        def getThresholdClasses():
            return self.thresholds

        def getDataSourceClasses():
            return self.datasources

        self.zenpack.getThresholdClasses = getThresholdClasses
        self.zenpack.getDataSourceClasses = getDataSourceClasses


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
