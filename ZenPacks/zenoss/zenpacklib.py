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

import yaml

import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

from lib.functions import load_yaml, represent_spec, \
    represent_zenpackspec,  represent_relschemaspec, \
    construct_zenpackspec, relationships_from_yuml
from lib.helpers.Loader import Loader
from lib.helpers.Dumper import Dumper

# these are the base classes for zenpacklib.Device, zenpacklib.Component, zenpacklib.HardwareComponent
from lib.base.Device import Device
from lib.base.Component import Component
from lib.base.HardwareComponent import HardwareComponent


from lib.spec.ZenPackSpec import ZenPackSpec
from lib.spec.DeviceClassSpec import DeviceClassSpec
from lib.spec.ZPropertySpec import ZPropertySpec
from lib.spec.ClassSpec import ClassSpec
from lib.spec.ClassPropertySpec import ClassPropertySpec
from lib.spec.ClassRelationshipSpec import ClassRelationshipSpec
from lib.spec.RelationshipSchemaSpec import RelationshipSchemaSpec

from lib.params.ZenPackSpecParams import ZenPackSpecParams
from lib.params.DeviceClassSpecParams import DeviceClassSpecParams
from lib.params.ZPropertySpecParams import ZPropertySpecParams
from lib.params.ClassSpecParams import ClassSpecParams
from lib.params.ClassPropertySpecParams import ClassPropertySpecParams
from lib.params.ClassRelationshipSpecParams import ClassRelationshipSpecParams
from lib.params.RRDTemplateSpecParams import RRDTemplateSpecParams
from lib.params.RRDThresholdSpecParams import RRDThresholdSpecParams
from lib.params.RRDDatasourceSpecParams import RRDDatasourceSpecParams
from lib.params.RRDDatapointSpecParams import RRDDatapointSpecParams
from lib.params.GraphDefinitionSpecParams import GraphDefinitionSpecParams
from lib.params.GraphPointSpecParams import GraphPointSpecParams

Dumper.add_representer(ZenPackSpec, represent_zenpackspec)
Dumper.add_representer(DeviceClassSpec, represent_spec)
Dumper.add_representer(ZPropertySpec, represent_spec)
Dumper.add_representer(ClassSpec, represent_spec)
Dumper.add_representer(ClassPropertySpec, represent_spec)
Dumper.add_representer(ClassRelationshipSpec, represent_spec)
Dumper.add_representer(RelationshipSchemaSpec, represent_relschemaspec)
Loader.add_constructor(u'!ZenPackSpec', construct_zenpackspec)

yaml.add_path_resolver(u'!ZenPackSpec', [], Loader=Loader)

Dumper.add_representer(ZenPackSpecParams, represent_zenpackspec)
Dumper.add_representer(DeviceClassSpecParams, represent_spec)
Dumper.add_representer(ZPropertySpecParams, represent_spec)
Dumper.add_representer(ClassSpecParams, represent_spec)
Dumper.add_representer(ClassPropertySpecParams, represent_spec)
Dumper.add_representer(ClassRelationshipSpecParams, represent_spec)
Dumper.add_representer(RRDTemplateSpecParams, represent_spec)
Dumper.add_representer(RRDThresholdSpecParams, represent_spec)
Dumper.add_representer(RRDDatasourceSpecParams, represent_spec)
Dumper.add_representer(RRDDatapointSpecParams, represent_spec)
Dumper.add_representer(GraphDefinitionSpecParams, represent_spec)
Dumper.add_representer(GraphPointSpecParams, represent_spec)


if __name__ == '__main__':
    from lib.libexec.ZPLCommand import ZPLCommand

    script = ZPLCommand(version=__version__)
    script.run()
