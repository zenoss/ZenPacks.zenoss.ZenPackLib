##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
import Globals
import sys
import logging
LOG = logging.getLogger('zen.ZenPackLib')

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused, zenPath
from .lib.utils import yaml_installed

unused(Globals)
#
#
class ZenPack(ZenPackBase):
    '''ZenPack'''

    def install(self, dmd):
        if yaml_installed():
            ZenPackBase.install(self, dmd)
            self.check_permissions()
            self.create_symlink()
        else:
            sys.exit(1)

    def remove(self, dmd, leaveObjects=False):
        if not leaveObjects:
            pass
        self.remove_symlink()
        ZenPackBase.remove(self, dmd, leaveObjects=leaveObjects)

    def check_permissions(self):
        basedir = os.path.dirname(__file__)
        shell_path = os.path.join(basedir, "bin/zenpacklib")
        py_path = os.path.join(basedir, 'zenpacklib.py')
        for x in [shell_path, py_path]:
            LOG.info('Setting permissions on {}'.format(x))
            os.chmod(x, 0755)

    def create_symlink(self):
        '''create symlink'''
        source_path = os.path.join(os.path.dirname(__file__), "bin/zenpacklib")
        dest_path = zenPath('bin', 'zenpacklib')
        LOG.info('Creating symlink {}'.format(dest_path))
        os.system('ln -sf "%s" "%s"' % (source_path, dest_path))
        os.system('chmod 0755 %s' % dest_path)

    def remove_symlink(self):
        '''remove symlink'''
        dest_path = zenPath('bin', 'zenpacklib')
        os.system('rm -f "%s"' % dest_path)
        LOG.info('Removing symlink {}'.format(dest_path))


# Patch last to avoid import recursion problems.
from ZenPacks.zenoss.ZenPackLib import patches
