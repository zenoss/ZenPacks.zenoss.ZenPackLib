##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .helpers.ZenPackLibLog import DEFAULTLOG


FACET_BLACKLIST = (
    'dependencies',
    'dependents',
    'maintenanceWindows',
    'pack',
    'productClass',
    )


### functions to determine conditional imports elsewhere


def yaml_installed():
    '''Return True if Impact is installed'''
    try:
        import yaml
        import yaml.constructor
    except ImportError:
        DEFAULTLOG.critical('PyYAML is required but not installed. Run "easy_install PyYAML" or "pip install PyYAML"')
        pass
    else:
        return True
    return False


def impact_installed():
    '''Return True if Impact is installed'''
    try:
        from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
        from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider
    except ImportError:
        DEFAULTLOG.info('Impact is not installed and some functionality dependent on it will be disabled')
        pass
    else:
        return True
    return False


def dynamicview_installed():
    '''Return True if DynamicView is installed'''
    try:
        from ZenPacks.zenoss.DynamicView import BaseRelation, BaseGroup, TAG_ALL
        from ZenPacks.zenoss.DynamicView.interfaces import IRelatable, IRelationsProvider, IGroupMappingProvider
        from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable, BaseRelationsProvider
    except ImportError:
        DEFAULTLOG.info('DynamicView is not installed and some functionality dependent on it will be disabled')
        pass
    else:
        return True
    return False


def has_metricfacade():
    '''return True if metricfacade can be imported'''
    try:
        from Products.Zuul.facades import metricfacade
    except ImportError:
        DEFAULTLOG.info('MetricFacade is not available and some functionality dependent on it will be disabled')
        pass
    else:
        return True
    return False

