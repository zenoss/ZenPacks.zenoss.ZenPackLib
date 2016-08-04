#!/usr/bin/env python

##############################################################################
# This program is part of zenpacklib, the ZenPack API.
# Copyright (C) 2013-2015  Zenoss, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
##############################################################################

"""zenpacklib - ZenPack API.

This module provides a single integration point for common ZenPacks.

"""

# PEP-396 version. (https://www.python.org/dev/peps/pep-0396/)
__version__ = "1.1.0dev"

# Must defer definition of TestCase. Otherwise it imports
# BaseTestCase which puts Zope into testing mode.
TestCase = None

import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

# ZenPacks use these to load their YAML files
from lib.helpers.utils import load_yaml, load_yaml_multi, load_yaml_dir

# these are the base classes for zenpacklib.Device, zenpacklib.Component, zenpacklib.HardwareComponent
from lib.base.Device import Device
from lib.base.Component import Component
from lib.base.HardwareComponent import HardwareComponent


if __name__ == '__main__':
    from lib.libexec.ZPLCommand import ZPLCommand

    script = ZPLCommand(version=__version__)
    script.run()
