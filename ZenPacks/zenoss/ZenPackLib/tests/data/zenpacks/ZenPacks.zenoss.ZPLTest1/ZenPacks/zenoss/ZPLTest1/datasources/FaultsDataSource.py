##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""ZPLTest1 fault monitoring."""

import logging
LOG = logging.getLogger('zen.ZPLTest1')

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSource,
    PythonDataSourcePlugin,
    )

# Zope Imports
from zope.component import adapts
from zope.interface import implements

# Zenoss Imports
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo


# Constants
SOURCETYPE = 'ZPLTest1 Faults'


class FaultsDataSource(PythonDataSource):

    """ZPLTest1 faults datasource type."""

    sourcetype = SOURCETYPE
    sourcetypes = (SOURCETYPE,)

    # PythonDataSource
    plugin_classname = '.'.join((__name__, 'FaultsDataSourcePlugin'))


class IFaultsDataSourceInfo(IRRDDataSourceInfo):

    """ZPLTest1 datasource API Info interface."""


class FaultsDataSourceInfo(RRDDataSourceInfo):

    """CiscoAPIC datasource API Info adapter factory."""

    implements(IFaultsDataSourceInfo)
    adapts(FaultsDataSource)

    testable = False


class FaultsDataSourcePlugin(PythonDataSourcePlugin):
    pass
