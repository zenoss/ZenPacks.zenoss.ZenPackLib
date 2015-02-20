##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""ZPLTest1 health monitoring."""

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
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

# Constants
SOURCETYPE = 'ZPLTest1 Health'


class HealthDataSource(PythonDataSource):

    """ZPLTest1 health datasource type."""

    sourcetype = SOURCETYPE
    sourcetypes = (SOURCETYPE,)

    # PythonDataSource
    plugin_classname = '.'.join((__name__, 'HealthDataSourcePlugin'))

    # Defaults for PythonDataSource user-facing properties.
    cycletime = '${here/zZPLTest1HealthInterval}'


class IHealthDataSourceInfo(IRRDDataSourceInfo):

    """ZPLTest1 health datasource API Info interface."""

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))


class HealthDataSourceInfo(RRDDataSourceInfo):

    """ZPLTest1 health datasource API Info adapter factory."""

    implements(IHealthDataSourceInfo)
    adapts(HealthDataSource)

    testable = False
    cycletime = ProxyProperty('cycletime')


class HealthDataSourcePlugin(PythonDataSourcePlugin):
    pass
