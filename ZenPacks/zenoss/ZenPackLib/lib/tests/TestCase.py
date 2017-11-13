##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import importlib
import inspect
from ..helpers.ZenPackLibLog import ZenPackLibLog, DEFAULTLOG


"""Enable test mode. Only call from code under tests/.

If this is called from production code it will cause all Zope
clients to start in test mode. Which isn't useful for anything but
unit testing.

"""

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from transaction._transaction import Transaction

class TestCase(BaseTestCase):

    # As in BaseTestCase, the default behavior is to disable
    # all logging from within a unit test.  To enable it,
    # set disableLogging = False in your subclass.  This is
    # recommended during active development, but is too noisy
    # to leave as the default.
    LOG = DEFAULTLOG

    disableLogging = True
    zenpack_module_name = None

    def get_caller(self):
        """Return name of calling ZenPack"""
        frm = inspect.stack()[-1]
        file_name = inspect.getabsfile(frm[0])
        first_part = file_name[file_name.find('ZenPacks.'):]
        zp_name = first_part[:first_part.find('/')]
        return zp_name

    def afterSetUp(self):
        ZenPackLibLog.enable_log_stderr(self.LOG)
        super(TestCase, self).afterSetUp()
        # Not included with BaseTestCase. Needed to test that UI
        # components have been properly registered.
        from Products.Five import zcml
        import Products.ZenUI3
        zcml.load_config('configure.zcml', Products.ZenUI3)

        if not hasattr(self, 'zenpack_module_name') or self.zenpack_module_name is None:
            self.zenpack_module_name = self.get_caller()

        try:
            zenpack_module = importlib.import_module(self.zenpack_module_name)
        except Exception as e:
            self.LOG.exception("Unable to load zenpack named '{}' - is it installed? ({})".format(self.zenpack_module_name, e))
            raise

        zenpackspec = getattr(zenpack_module, 'CFG', None)
        if not zenpackspec:
            raise NameError(
                "name {!r} is not defined"
                .format('.'.join((self.zenpack_module_name, 'CFG'))))

        zenpackspec.test_setup()

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

        try:
            zcml.load_config('configure.zcml', zenpack_module)
        except IOError:
            pass

        # BaseTestCast.afterSetUp already hides transaction.commit. So we also
        # need to hide transaction.abort.
        self._transaction_abort = Transaction.abort
        Transaction.abort = lambda *x: None

    def beforeTearDown(self):
        super(TestCase, self).beforeTearDown()

        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort

    # If the exception occurs during setUp, beforeTearDown is not called,
    # so we also need to restore abort here as well:
    def _close(self):
        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort

        super(TestCase, self)._close()
