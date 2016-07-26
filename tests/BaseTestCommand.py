#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Command unit tests.

This module tests command line usage of zenpacklib.py.

"""

import logging
import subprocess
import os
import Globals
from Products.ZenUtils.Utils import unused
from Products.ZenTestCase.BaseTestCase import BaseTestCase

unused(Globals)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('zen.zenpacklib.tests')


class BaseTestCommand(BaseTestCase):

    zenpacklib_path = os.path.join(os.path.dirname(__file__),
                                   "../zenpacklib.py")

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
