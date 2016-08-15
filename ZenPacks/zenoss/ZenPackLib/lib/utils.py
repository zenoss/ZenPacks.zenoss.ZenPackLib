from .helpers.ZenPackLibLog import ZenPackLibLog
from .functions import LOG


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
        LOG.critical('PyYAML is required but not installed. Run "easy_install PyYAML" or "pip install PyYAML"')
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
        LOG.info('Impact is not installed and some functionality dependent on it will be disabled')
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
        LOG.info('DynamicView is not installed and some functionality dependent on it will be disabled')
        pass
    else:
        return True
    return False


def has_metricfacade():
    '''return True if metricfacade can be imported'''
    try:
        from Products.Zuul.facades import metricfacade
    except ImportError:
        LOG.info('MetricFacade is not available and some functionality dependent on it will be disabled')
        pass
    else:
        return True
    return False

