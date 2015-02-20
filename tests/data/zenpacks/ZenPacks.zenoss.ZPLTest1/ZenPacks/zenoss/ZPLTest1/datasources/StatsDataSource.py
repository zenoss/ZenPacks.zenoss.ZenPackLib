##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""ZPLTest1 statistics monitoring."""

# Logging
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
SOURCETYPE = 'ZPLTest1 Stats'

# For cases where we can't figure out a better cycletime from the name.
DEFAULT_CYCLETIME = 300


class StatsDataSource(PythonDataSource):

    """Datasource used to define ZPLTest1 stats requests."""

    sourcetype = SOURCETYPE
    sourcetypes = (SOURCETYPE,)

    # RRDDataSource
    component = '${here/id}'
    cycletime = DEFAULT_CYCLETIME
    eventClass = '/Ignore'

    # PythonDataSource
    plugin_classname = '.'.join((__name__, 'StatsDataSourcePlugin'))

    # StatsDataSource
    classname = '${here/apic_classname}'
    base_dn = ''
    object_dn = '${here/apic_dn}'
    statistic = '${here/id}'
    granularity = '5min'

    _properties = PythonDataSource._properties + (
        {'id': 'classname', 'type': 'string'},
        {'id': 'base_dn', 'type': 'string'},
        {'id': 'object_dn', 'type': 'string'},
        {'id': 'statistic', 'type': 'string'},
        {'id': 'granularity', 'type': 'string'},
        )

    def getDescription(self):
        """Return a short string that represents this datasource."""
        return "{}/{} ({})".format(
            self.classname,
            self.statistic,
            self.granularity)


class IStatsDataSourceInfo(IRRDDataSourceInfo):

    """API Info interface for StatsDataSource."""

    classname = schema.TextLine(
        group=_t(u'ZPLTest1'),
        title=_t(u'Object Class'))

    base_dn = schema.TextLine(
        group=_t(u'ZPLTest1'),
        title=_t(u'Base DN'))

    object_dn = schema.TextLine(
        group=_t(u'ZPLTest1'),
        title=_t(u'Object DN'))

    statistic = schema.TextLine(
        group=_t(u'ZPLTest1'),
        title=_t(u'Statistic Name'))

    granularity = schema.TextLine(
        group=_t(u'ZPLTest1'),
        title=_t(u'Collection Granularity'))


class StatsDataSourceInfo(RRDDataSourceInfo):

    """ZPLTest1 stats datasource API Info adapter factory."""

    implements(IStatsDataSourceInfo)
    adapts(StatsDataSource)

    testable = False

    classname = ProxyProperty('classname')
    base_dn = ProxyProperty('base_dn')
    object_dn = ProxyProperty('object_dn')
    statistic = ProxyProperty('statistic')
    granularity = ProxyProperty('granularity')


class StatsDataSourcePlugin(PythonDataSourcePlugin):
    pass

