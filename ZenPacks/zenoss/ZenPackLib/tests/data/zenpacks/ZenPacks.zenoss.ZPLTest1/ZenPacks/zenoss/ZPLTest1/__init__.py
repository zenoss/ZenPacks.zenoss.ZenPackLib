##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
from ZenPacks.zenoss.ZenPackLib import zenpacklib

if 'ZPL_YAML_FILENAME' in os.environ:
    YAML = os.path.join(os.path.dirname(__file__), 'zenpack2.yaml')
else:
    YAML = os.path.join(os.path.dirname(__file__), 'zenpack.yaml')

CFG = zenpacklib.load_yaml(YAML)
