##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenUtils.Search import makeFieldIndex, makeKeywordIndex
from ..functions import catalog_search
from ..helpers.ZenPackLibLog import DEFAULTLOG


class CatalogBase(object):
    """Base class that implements cataloging a property"""

    # By Default there is no default catalog created.
    _catalogs = {}
    LOG = DEFAULTLOG

    def search(self, name, *args, **kwargs):
        """
        Return iterable of matching brains in named catalog.
        'name' is the catalog name (typically the name of a class)
        """
        return catalog_search(self, name, *args, **kwargs)

    @classmethod
    def class_search(cls, dmd, name, *args, **kwargs):
        """
        Return iterable of matching brains in named catalog.
        'name' is the catalog name (typically the name of a class)
        """

        name = cls.__module__.replace('.', '_')
        return catalog_search(dmd.Devices, name, *args, **kwargs)

    @classmethod
    def get_catalog_name(cls, name, scope):
        if scope == 'device':
            return '{}Search'.format(name)
        else:
            name = cls.__module__.replace('.', '_')
            return '{}Search'.format(name)

    @classmethod
    def class_get_catalog(cls, dmd, name, scope, create=True):
        """Return catalog by name."""
        spec = cls._get_catalog_spec(name)
        if not spec:
            return

        if scope == 'device':
            raise ValueError("device scoped catalogs are only available from device or component objects, not classes")
        else:
            try:
                return getattr(dmd.Devices, cls.get_catalog_name(name, scope))
            except AttributeError:
                if create:
                    return cls._class_create_catalog(dmd, name, 'global')
        return

    def get_catalog(self, name, scope, create=True):
        """Return catalog by name."""

        spec = self._get_catalog_spec(name)
        if not spec:
            return

        if scope == 'device':
            try:
                return getattr(self.device(), self.get_catalog_name(name, scope))
            except AttributeError:
                if create:
                    return self._create_catalog(name, 'device')
        else:
            try:
                return getattr(self.dmd.Devices, self.get_catalog_name(name, scope))
            except AttributeError:
                if create:
                    return self._create_catalog(name, 'global')
        return

    @classmethod
    def get_catalog_scopes(cls, name):
        """Return catalog scopes by name."""
        spec = cls._get_catalog_spec(name)
        if not spec:
            return set()

        scopes = [spec['indexes'][x].get('scope', 'device') for x in spec['indexes']]
        if 'both' in scopes:
            scopes = [x for x in scopes if x != 'both']
            scopes.append('device')
            scopes.append('global')
        return set(scopes)

    @classmethod
    def class_get_catalogs(cls, dmd, whiteList=None):
        """Return all catalogs for this class."""

        catalogs = []
        for name in cls._catalogs:
            for scope in cls.get_catalog_scopes(name):
                if scope == 'device':
                    # device scoped catalogs are not available at the class level
                    continue

                if not whiteList:
                    catalogs.append(cls.class_get_catalog(dmd, name, scope))
                else:
                    if scope in whiteList:
                        catalogs.append(cls.class_get_catalog(dmd, name, scope, create=False))
        return catalogs

    def get_catalogs(self, whiteList=None):
        """Return all catalogs for this class."""
        catalogs = []
        for name in self._catalogs:
            for scope in self.get_catalog_scopes(name):
                if not whiteList:
                    catalogs.append(self.get_catalog(name, scope))
                else:
                    if scope in whiteList:
                        catalogs.append(self.get_catalog(name, scope, create=False))
        return catalogs

    @classmethod
    def _get_catalog_spec(cls, name):
        if not hasattr(cls, '_catalogs'):
            cls.LOG.error("{} has no catalogs defined".format(cls))
            return

        spec = cls._catalogs.get(name)
        if not spec:
            cls.LOG.error("{} catalog definition is missing".format(name))
            return

        if not isinstance(spec, dict):
            cls.LOG.error("{} catalog definition is not a dict".format(name))
            return

        if not spec.get('indexes'):
            cls.LOG.error("{} catalog definition has no indexes".format(name))
            return

        return spec

    @classmethod
    def _class_create_catalog(cls, dmd, name, scope='device'):
        """Create and return catalog defined by name."""
        from Products.ZCatalog.ZCatalog import manage_addZCatalog

        spec = cls._get_catalog_spec(name)
        if not spec:
            return

        if scope == 'device':
            raise ValueError("device scoped catalogs may only be created from the device or component object, not classes")
        else:
            catalog_name = cls.get_catalog_name(name, scope)
            deviceClass = dmd.Devices

            if not hasattr(deviceClass, catalog_name):
                manage_addZCatalog(deviceClass, catalog_name, catalog_name)

            zcatalog = deviceClass._getOb(catalog_name)

        cls._create_indexes(zcatalog, spec)
        return zcatalog

    def _create_catalog(self, name, scope='device'):
        """Create and return catalog defined by name."""
        from Products.ZCatalog.ZCatalog import manage_addZCatalog

        spec = self._get_catalog_spec(name)
        if not spec:
            return

        if scope == 'device':
            catalog_name = self.get_catalog_name(name, scope)

            device = self.device()
            if not hasattr(device, catalog_name):
                manage_addZCatalog(device, catalog_name, catalog_name)

            zcatalog = device._getOb(catalog_name)
        else:
            catalog_name = self.get_catalog_name(name, scope)
            deviceClass = self.dmd.Devices

            if not hasattr(deviceClass, catalog_name):
                manage_addZCatalog(deviceClass, catalog_name, catalog_name)

            zcatalog = deviceClass._getOb(catalog_name)

        self._create_indexes(zcatalog, spec)
        return zcatalog

    @classmethod
    def _create_indexes(cls, zcatalog, spec):
        from Products.ZCatalog.Catalog import CatalogError
        from Products.Zuul.interfaces import ICatalogTool
        catalog = zcatalog._catalog

        # I think this is the original intent for setting classname, not sure why it would fail
        try:
            classname = '{}.{}'.format(cls.__module__, cls.__class__.__name__)
        except Exception:
            classname = 'Products.ZenModel.DeviceComponent.DeviceComponent'

        for propname, propdata in spec['indexes'].items():
            index_type = propdata.get('type')
            if not index_type:
                cls.LOG.error("{} index has no type".format(propname))
                return

            index_factory = {
                'field': makeFieldIndex,
                'keyword': makeKeywordIndex,
                }.get(index_type.lower())

            if not index_factory:
                cls.LOG.error("{} is not a valid index type".format(index_type))
                return

            try:
                catalog.addIndex(propname, index_factory(propname))
                catalog.addColumn(propname)
            except CatalogError:
                # Index already exists.
                pass
            else:
                # the device if it's a device scoped catalog, or dmd.Devices
                # if it's a global scoped catalog.
                context = zcatalog.getParentNode()

                # reindex all objects of this type so they are added to the
                # catalog.
                results = ICatalogTool(context).search(types=(classname,))
                for result in results:
                    try:
                        new_obj = result.getObject()
                    except Exception as e:
                        cls.LOG.error("Trying to index non-existent object {}".format(e))
                        continue
                    else:
                        if hasattr(new_obj, 'index_object'):
                            new_obj.index_object()

    def index_object(self, idxs=None):
        """Index in all configured catalogs."""
        for catalog in self.get_catalogs():
            if catalog:
                catalog.catalog_object(self, self.getPrimaryId())

    def unindex_object(self):
        """Unindex from all configured catalogs."""
        for catalog in self.get_catalogs():
            if catalog:
                catalog.uncatalog_object(self.getPrimaryId())

