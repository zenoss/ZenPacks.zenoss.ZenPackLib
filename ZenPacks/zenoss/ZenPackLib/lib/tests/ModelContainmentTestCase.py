##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import importlib
from ..helpers.ZenPackLibLog import ZenPackLibLog, DEFAULTLOG
from Products.ZenTestCase.BaseTestCase import BaseTestCase

"""Enable test mode. Only call from code under tests/.

If this is called from production code it will cause all Zope
clients to start in test mode. Which isn't useful for anything but
unit testing.

"""

class ModelContainmentTestCase(BaseTestCase):
    '''
    This Test Case walks the implementing ZenPacks' Relationship Map,
    validating that each component is contained only once.
    ZenPacks with example implementations of test_containment_model.py:
        vSphere - 4.0.4 or higher
        Nutanix - 1.1.0 or higher
        EMC.base - 2.2.0 or higher
        NetAppMonitor - 4.0.1 or higher
    '''
    LOG = DEFAULTLOG
    disableLogging = True
    zenpack_module_name = None

    def set_caller(self, module_name):
        """Set name of calling ZenPack"""
        self.zenpack_module_name = module_name

    def get_caller(self):
        """Return name of calling ZenPack"""
        import inspect
        frm = inspect.stack()[-1]
        file_name = inspect.getabsfile(frm[0])
        first_part = file_name[file_name.find('ZenPacks.'):]
        zp_name = first_part[:first_part.find('/')]
        return zp_name

    def afterSetUp(self):
        ZenPackLibLog.enable_log_stderr(self.LOG)
        super(ModelContainmentTestCase, self).afterSetUp()

        self.zenpack_module = None
        self.class_relationships = []
        self.log = self.LOG

        if not hasattr(self, 'zenpack_module_name') or self.zenpack_module_name is None:
            self.zenpack_module_name = self.get_caller()
        if not self.zenpack_module_name:
            return

        try:
            self.zenpack_module = importlib.import_module(self.zenpack_module_name)
        except Exception as e:
            self.LOG.exception("Unable to load zenpack named '{}' - is it installed? ({})".format(self.zenpack_module_name, e))
        if not self.zenpack_module:
            return

        zenpackspec = getattr(self.zenpack_module, 'CFG', None)
        if zenpackspec:
            zenpackspec.test_setup()
            self.class_relationships = zenpackspec.class_relationships
        else:
            self.LOG.exception("name {!r} is not defined".format( '.'.join((self.zenpack_module_name, 'CFG')) ))

    def get_relationship_maps(self):
        if self.class_relationships:
            return self.class_relationships
        return []

    def check_containment_model(self):
        class_relationships = self.get_relationship_maps()

        # Iterate Class Relationships
        self.assertIsNotNone(class_relationships)
        self.assertTrue(isinstance(class_relationships, list))
        containment_list = []
        for rel in class_relationships:
            name = getattr(rel, 'left_relname', '')
            type = getattr(rel, 'left_type', '')
            if type == 'ToManyCont':
                self.assertFalse(name in containment_list)
                containment_list.append(name)
