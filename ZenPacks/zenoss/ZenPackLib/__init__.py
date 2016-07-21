# Nothing is required in this __init__.py, but it is an excellent place to do
# many things in a ZenPack.
#
# The example below which is commented out by default creates a custom subclass
# of the ZenPack class. This allows you to define custom installation and
# removal routines for your ZenPack. If you don't need this kind of flexibility
# you should leave the section commented out and let the standard ZenPack
# class be used.
#
# Code included in the global scope of this file will be executed at startup
# in any Zope client. This includes Zope itself (the web interface) and zenhub.
# This makes this the perfect place to alter lower-level stock behavior
# through monkey-patching.
import os
import Globals

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused, zenPath

unused(Globals)
#
#
class ZenPack(ZenPackBase):
    '''ZenPack'''

    def install(self, dmd):
        ZenPackBase.install(self, dmd)
        self.create_symlink()


    def remove(self, dmd, leaveObjects=False):
        if not leaveObjects:

            pass
        self.remove_symlink()
        ZenPackBase.remove(self, dmd, leaveObjects=leaveObjects)

    def create_symlink(self):
        '''create symlink'''
        source_path = os.path.join(os.path.dirname(__file__), "bin/zenpacklib")
        dest_path = zenPath('bin', 'zenpacklib')
        os.system('ln -sf "%s" "%s"' % (source_path, dest_path))
        os.system('chmod 0755 %s' % dest_path)

    def remove_symlink(self):
        '''remove symlink'''
        dest_path = zenPath('bin', 'zenpacklib')
        os.system('rm -f "%s"' % dest_path)