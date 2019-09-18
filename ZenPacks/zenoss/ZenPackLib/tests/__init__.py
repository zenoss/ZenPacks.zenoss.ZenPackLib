##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
""" 
    Basic classes used for unit testing
"""
import yaml
import unittest
import difflib
import zope.component
from zope.event import notify
from zope.traversing.adapters import DefaultTraversable
from transaction._transaction import Transaction

# Zenoss Imports
import Globals 
import Products.ZenTestCase
from Products.Five import zcml
from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.Zuul.catalog.events import IndexingEvent
from Products.ZenUtils.Utils import unused
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenTestCase.BaseTestCase import ZenossTestCaseLayer
unused(Globals)

from ZenPacks.zenoss.ZenPackLib.lib.helpers.loaders import OrderedLoader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper
from ZenPacks.zenoss.ZenPackLib.lib.helpers.ZenPackLibLog import (
    ZenPackLibLog, 
    DEFAULTLOG
)
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import load_yaml_single
from ZenPacks.zenoss.ZenPackLib.tests.utils import (
    LogCapture, 
    CommandMixin, 
    ClassObjectHelper
)

from ZenPacks.zenoss.ZenPackLib import zenpacklib
zenpacklib.enableTesting()


def get_layer_subclass(name, yaml_doc=None, tc_attributes=None, reset=True):
    """ Returns a named subclass of ZPLTestCaseLayer 
        which can then be used to hold unique layered test environments
    """
    return type(name, (object, ZPLTestCaseLayerBase,), 
        {'yaml_doc': yaml_doc, 'reset': reset, 'tc_attributes': tc_attributes})


class ZPLBaseTestCase(BaseTestCase):
    """ Unit test base class with functionality for loading 
        YAML files and creating related dmd objects used by 
        tests
    """
    # As in BaseTestCase, the default behavior is to disable
    # all logging from within a unit test.  To enable it,
    # set disableLogging = False in your subclass.  This is
    # recommended during active development, but is too noisy
    # to leave as the default.
    LOG = DEFAULTLOG
    disableLogging = True
    # set disableLogging to True to use
    capture = LogCapture()
    command = CommandMixin()
    yaml_doc = None
    configs = None
    build = False
    # tc_attributes can be a dictionary containing additional info for testing
    tc_attributes = None

    def afterSetUp(self):
        ZenPackLibLog.enable_log_stderr(self.LOG)
        super(ZPLBaseTestCase, self).afterSetUp()

        # BaseTestCast.afterSetUp already hides transaction.commit. So we also
        # need to hide transaction.abort.
        self._transaction_abort = Transaction.abort
        Transaction.abort = lambda *x: None
        
        self.update_tc_attributes()
        self.initialize(self.yaml_doc)
        # Not included with BaseTestCase. Needed to test that UI
        # components have been properly registered.
        from Products.Five import zcml
        import Products.ZenUI3
        zcml.load_config('configure.zcml', Products.ZenUI3)

        import Products.ZenEvents
        zcml.load_config('meta.zcml', Products.ZenEvents)

        try:
            import ZenPacks.zenoss.DynamicView
            zcml.load_config('configure.zcml', ZenPacks.zenoss.DynamicView)
        except ImportError:
            pass

        try:
            import Products.Jobber
            zcml.load_config('meta.zcml', Products.Jobber)
        except ImportError:
            pass

        try:
            import ZenPacks.zenoss.Impact
            zcml.load_config('meta.zcml', ZenPacks.zenoss.Impact)
            zcml.load_config('configure.zcml', ZenPacks.zenoss.Impact)
        except ImportError:
            pass

    def beforeTearDown(self):
        super(ZPLBaseTestCase, self).beforeTearDown()
        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort

    def _close(self):
        """ If the exception occurs during setUp, beforeTearDown is not called,
            so we also need to restore abort here as well
        """
        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort
        super(ZPLBaseTestCase, self)._close()

    def get_zenpacklib_cmd(self, *args):
        """test output of zenpacklib.py"""
        cmd, p, out, err = self.command.zenpacklib_cmd_output(*args)
        self.assertIs(p.returncode, 0,
                      'Error running %s: %s%s' % (cmd, err, out))

        if out is not None:
            self.assertNotIn("Error", out)
            self.assertNotIn("Error", out)
        if err is not None:
            self.assertNotIn("Traceback", err)
            self.assertNotIn("Traceback", err)

        return out

    def get_cmd_success(self, cmd, vars=None):
        """execute a command and assert success"""
        cmd, p, out, err = self.command.get_cmd_output(cmd, vars)
        self.LOG.debug("out=%s, err=%s", out, err)
        msg = 'Command "{}" failed with error:\n  {}'.format(cmd, err)
        self.assertIs(p.returncode, 0, msg)
        return out

    def update_tc_attributes(self):
        """Set additional attributes"""
        if isinstance(self.tc_attributes, dict):
            for k, v in self.tc_attributes.iteritems():
                setattr(self, k, v)

    def install_zenpack(self, cfg):
        """Install ZenPack given name and optional class.
    
        This is far from a full installation. The ZenPack object is
        instantiated and added to ZenPackManager. This is mainly useful to
        make modeler plugins and datasource types available for loading.
        """
        zenpack = cfg.zenpack_class(cfg.name)
        zenpack.eggPack = True
        self.dmd.ZenPackManager.packs._setObject(zenpack.id, zenpack)

        def getThresholdClasses():
            return getattr(self, 'thresholds', [])

        def getDataSourceClasses():
            return getattr(self, 'datasources', [])
        
        zenpack.getThresholdClasses = getThresholdClasses
        zenpack.getDataSourceClasses = getDataSourceClasses
        return self.dmd.ZenPackManager.packs._getOb(zenpack.id)

    def get_config(self, yaml_doc):
        """Load a YAML document and return a dictionary describing it"""
        cfg = zenpacklib.load_yaml(yaml_doc,
            verbose=not self.disableLogging, level=10)
        cfg.test_setup()
        
        return {'cfg': cfg,
                'schema': cfg.zenpack_module.schema,
                'yaml_map': load_yaml_single(
                    yaml_doc, loader=OrderedLoader),
                'yaml_dump': yaml.dump(cfg, Dumper=Dumper),
                'yaml_from_specparams': yaml.dump(
                    cfg.specparams, Dumper=Dumper),
                'zenpack_module': cfg.zenpack_module,
                'zenpack_module_name': cfg.name,
                'zenpack': self.install_zenpack(cfg),
                'objects': ClassObjectHelper(self.dmd, cfg, self.build),
                }

    def initialize(self, yaml_doc):
        """Create and store a config representing a loaded YAML
        and related DMD objects"""
        if not yaml_doc:
            return
        if self.configs is None:
            self.configs = {}
        if isinstance(yaml_doc, list):
            for y in yaml_doc:
                self.initialize(y)
        else:
            config = self.get_config(yaml_doc)
            cfg = config.get('cfg')
            self.configs[cfg.name] = config
            self.install_zenpack(cfg)

    def get_device_class_objects(self, zp_name):
        """Return device classes for a given ZenPack name"""
        ob_helper = self.configs.get(zp_name, {}).get('objects')
        return ob_helper.device_class_objects
    
    def get_device_class_templates(self, zp_name, dc_name):
        """Return templates for a given ZenPack and device class name"""
        dc_objects = self.get_device_class_objects(zp_name)
        return {t_name: t_ob for t_name, t_ob in 
            dc_objects.get(
            dc_name, {}).get('templates', {}).items()}

    def get_diff(self, expected, actual):
        """Return diff between YAML files"""
        lines_expected = [x + '\n' for x in expected.split('\n')]
        lines_actual = [x + '\n' for x in actual.split('\n')]
        return ''.join(difflib.unified_diff(lines_expected, lines_actual))


class InitializerTestCase(ZPLBaseTestCase):
    """The environment created by this TestCase 
    is accessible via the 'tc' attribute of ZPLTestLayerBase
    """
    def test_nothing(self):
        pass


class ZPLLayeredTestCase(unittest.TestCase):
    """ Base Class for ZenPackLib unit tests that use layering 
        to provide a shared environment betweeen unit tests.
        
        Testing in this fashion can reduce overall testing time 
        by removing repeat setup and teardowns of the shared environment 
        that would otherwise occur between tests. 
        
        Subclassing "layer" from another unit test can provide access 
        to that unit tests's dmd
        (see test_layered_unit_tests.py script)
    """
    LOG = DEFAULTLOG
    layer = None
    disableLogging = True
    yaml_doc = None

    def setUp(self):
        super(ZPLLayeredTestCase, self).setUp()
        # Pull down the shared environment from the layer
        self.tc = self.layer.tc
        self.dmd = self.tc.dmd
        self.configs = self.tc.configs


class ZPLTestCaseLayerBase(ZenossTestCaseLayer):
    """ TestCaseLayer that sets up environment shared between test cases.  
        This is done by assigning the "tc" attribute which 
        points to a dummy InitializerTestCase.  
        
        The InitializerTestCase instance then hosts the dmd 
        (and associated machinery), which can then be shared between 
        ZPLLayeredTestCase (unittest.TestCase) instances
        
        Note: This will only get run *once* across all layers.  If you want
        something to be invoked for each layer, put it in
        ZPLTestCaseLayer.setUp() instead
    """
    LOG = DEFAULTLOG
    yaml_doc = None
    configs = None
    tc = None
    tc_attributes = None
    reset = True
    device = None
    mapper = None

    @classmethod
    def setUp(cls):
        zope.component.testing.setUp(cls)
        zope.component.provideAdapter(DefaultTraversable, (None,))
        zcml.load_config('testing-noevent.zcml', Products.ZenTestCase)
        # Silly trickery here.
        # We create a single TestCase, and share the environment that it creates
        # across all our ZPLLayeredTestCase (which we have inheriting 
        # from unittest.TestCase instead)
        if not cls.tc or cls.reset:
            cls.tc = InitializerTestCase("test_nothing")
            if isinstance(cls.tc_attributes, dict):
                for k, v in cls.tc_attributes.iteritems():
                    setattr(cls.tc, k, v)
            cls.tc.setUp()
            cls.tc.dmd.REQUEST = None

        if cls.yaml_doc:
            cls.load_yaml()

        try:
            from Products.ZenTestCase.BaseTestCase import (
                init_model_catalog_for_tests)
            init_model_catalog_for_tests()
        except ImportError:
            pass

        cls.mapper = ApplyDataMap()

    @classmethod
    def load_yaml(cls):
        """Load a YAML file and update stored configs"""
        cls.tc.initialize(cls.yaml_doc)
        if cls.configs is None:
            cls.configs = {}
        cls.configs.update(cls.tc.configs)

    @classmethod
    def createDevice(cls, name, devclass):
        cls.device = cls.tc.dmd.Devices.findDevice(name)
        if cls.device:
            cls.device.deleteDevice()
        cls.device = devclass.createInstance(name)

    @classmethod
    def apply_maps(cls, datamaps):
        """Return device with datamaps applied"""
        [cls.mapper._applyDataMap(cls.device, datamap) for datamap in datamaps]
        cls.device.index_object()
        notify(IndexingEvent(cls.device))
        for component in cls.device.getDeviceComponentsNoIndexGen():
            component.index_object()
            notify(IndexingEvent(component))

    @classmethod
    def tearDown(cls):
        if hasattr(cls.tc, '_transaction_abort'):
            Transaction.abort = cls.tc._transaction_abort
        if cls.device:
            cls.device.deleteDevice()
  
