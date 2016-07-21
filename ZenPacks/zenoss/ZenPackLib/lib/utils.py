import logging
LOG = logging.getLogger('zen.zenpacklib')
# Suppresses "No handlers could be found for logger" errors if logging
# hasn't been configured.
if len(LOG.handlers) == 0:
    LOG.addHandler(logging.NullHandler())


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
        print "YAML not installed"
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
        pass
    else:
        return True
    return False
