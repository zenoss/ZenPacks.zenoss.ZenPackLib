##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import zenpacklib
import os

if 'ZPL_YAML_FILENAME' in os.environ:
    CFG = zenpacklib.load_yaml(os.environ['ZPL_YAML_FILENAME'])
else:
    CFG = zenpacklib.load_yaml()
