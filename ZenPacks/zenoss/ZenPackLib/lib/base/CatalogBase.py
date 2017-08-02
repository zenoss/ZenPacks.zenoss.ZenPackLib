##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016-2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenUtils.Search import makeFieldIndex, makeKeywordIndex
from Products.ZenUtils.Utils import prepId

from ..functions import catalog_search
from ..helpers.ZenPackLibLog import DEFAULTLOG
from ..utils import has_modelindex


HAS_MODELINDEX = has_modelindex()


class CatalogBase(object):
    """Abstract base class that implements cataloging properties."""

    _device_catalogs = {}
    _global_catalogs = {}
    LOG = DEFAULTLOG

    # Searching ##############################################################

    def device_search(self, name, *args, **kwargs):
        """Return iterable of brains from named catalog that match."""
        return catalog_search(self, name, *args, **kwargs)

    # Method alias for backwards compatibility.
    search = device_search

    @classmethod
    def global_search(cls, dmd, name=None, *args, **kwargs):
        """Return iterable of brains from named catalog that match."""
        name = "{}_{}".format(
            cls.zenpack_name.replace(".", "_"),
            name or cls.__name__)

        return catalog_search(dmd.Devices, name, *args, **kwargs)

    # Method alias for backwards compatibility.
    class_search = global_search

    # Catalog Lookup #########################################################

    def get_all_catalogs(self):
        """Return list of device and global catalogs for this object."""
        catalogs = self.get_device_catalogs()

        try:
            dmd = self.getDmd()
        except Exception:
            pass
        else:
            catalogs.extend(self.get_global_catalogs(dmd))

        return catalogs

    def get_device_catalogs(self):
        """Return list of device catalogs for this object."""
        return [self.get_device_catalog(x) for x in self._device_catalogs]

    @classmethod
    def get_global_catalogs(cls, dmd):
        """Return list of global catalogs for this class."""
        return [cls.get_global_catalog(dmd, x) for x in cls._global_catalogs]

    def get_device_catalog(self, name):
        """Return device catalog by name."""
        catalog = getattr(
            self.device(),
            "{}Search".format(name),
            None)

        if catalog:
            return catalog
        else:
            return self.create_device_catalog(name)

    @classmethod
    def get_global_catalog(cls, dmd, name):
        """Return global catalog by name."""
        catalog = getattr(
            dmd.Devices,
            "{}_{}Search".format(cls.zenpack_name.replace('.', '_'), name),
            None)

        if catalog:
            return catalog
        else:
            return cls.create_global_catalog(dmd, name)

    # Catalog Creation and Maintenance #######################################

    def create_device_catalog(self, name):
        indexes = self._device_catalogs.get(name)
        if indexes:
            # Create an id index in all device catalogs.
            expanded_indexes = {'id': 'field'}
            expanded_indexes.update(indexes)
            return self.create_catalog(
                context=self.device(),
                name='{}Search'.format(name),
                indexes=expanded_indexes,
                classname='{0}.{1}.{1}'.format(self.zenpack_name, name))

    @classmethod
    def create_global_catalog(cls, dmd, name):
        context = dmd.Devices

        catalog_name = "{zenpack_name}_{name}Search".format(
            zenpack_name=cls.zenpack_name.replace('.', '_'),
            name=name)

        catalog = getattr(context, catalog_name, None)
        if catalog is not None:
            return catalog

        indexes = cls._global_catalogs.get(name)
        if not indexes:
            return

        # Create id and device indexes in all global catalogs.
        expanded_indexes = {'id': 'field', 'device_id': 'field'}
        expanded_indexes.update(indexes)

        classname = "{0}.{1}.{1}".format(cls.zenpack_name, name)

        if HAS_MODELINDEX:
            setattr(
                context,
                catalog_name,
                LegacyCatalogAdapter(
                    context=dmd,
                    zcatalog_name=catalog_name,
                    objectImplements=[classname],
                    fields=expanded_indexes.keys()))

            return context._getOb(catalog_name)
        else:
            return cls.create_catalog(
                context=context,
                name=catalog_name,
                indexes=expanded_indexes,
                classname=classname)

    @staticmethod
    def create_catalog(context, name, indexes, classname):
        """Return catalog. Create it first if necessary."""
        zcatalog = getattr(context, name, None)
        if not zcatalog:
            from Products.ZCatalog.ZCatalog import manage_addZCatalog
            manage_addZCatalog(context, name, name)
            zcatalog = context._getOb(name)

        if CatalogBase.create_catalog_indexes(zcatalog, indexes):
            CatalogBase.reindex_catalog(context, zcatalog, classname)

        return zcatalog

    @staticmethod
    def create_catalog_indexes(zcatalog, indexes):
        """Return True if zcatalog indexes were changed."""
        from Products.ZCatalog.Catalog import CatalogError

        changed = False
        catalog = zcatalog._catalog
        index_factories = {
            'field': makeFieldIndex,
            'keyword': makeKeywordIndex,
            }

        for index_name, index_type in indexes.iteritems():
            index_factory = index_factories.get(
                index_type.lower(),
                makeFieldIndex)

            try:
                catalog.addIndex(index_name, index_factory(index_name))
                catalog.addColumn(index_name)
            except CatalogError:
                # Index already exists.
                pass
            else:
                changed = True

        return changed

    @classmethod
    def reindex_catalog(cls, context, zcatalog, classname):
        from Products.Zuul.interfaces import ICatalogTool

        for result in ICatalogTool(context).search(types=(classname,)):
            try:
                obj = result.getObject()
            except Exception as e:
                cls.LOG.warning("failed to index non-existent object: %s", e)
            else:
                zcatalog.catalog_object(obj, obj.getPrimaryId())

    # Indexing and Unindexing ################################################

    def index_object(self, idxs=None):
        """Index in all configured catalogs."""
        for catalog in self.get_all_catalogs():
            if catalog:
                catalog.catalog_object(self, self.getPrimaryId())

    def unindex_object(self):
        """Unindex from all configured catalogs."""
        for catalog in self.get_all_catalogs():
            if catalog:
                catalog.uncatalog_object(self.getPrimaryId())

    def device_id(self):
        """Return associated device id, or empty string if n/a.
        Required for inclusion in zenpacklib global catalogs.
        """
        try:
            device = self.device()
            return device.id
        except Exception:
            return ''


if HAS_MODELINDEX:
    from Products.Zuul.catalog.interfaces import IModelCatalogTool
    from Products.Zuul.catalog.legacy import (
        LegacyCatalogAdapter as BaseLegacyCatalogAdapter,
        LegacyFieldsTranslator,
        LegacyFieldTranslation,
    )

    from Products.Zuul.catalog.model_catalog_tool_helper import (
        ModelCatalogToolGenericHelper,
    )

    class LegacyCatalogAdapter(BaseLegacyCatalogAdapter):
        def __init__(
                self,
                context,
                zcatalog_name=None,
                objectImplements=None,
                fields=None):
            """Initialize LegacyCatalogAdapter."""
            super(LegacyCatalogAdapter, self).__init__(
                context,
                zcatalog_name=zcatalog_name)

            self.id = prepId(zcatalog_name)
            self.objectImplements = objectImplements
            self.fields = fields

        def _get_model_catalog(self):
            return ModelCatalogToolGenericHelper(
                IModelCatalogTool(self.context),
                objectImplements=[self.objectImplements],
                fields=self.fields)

        def _get_translator(self):
            translator = LegacyFieldsTranslator()
            translator.add_translations([
                LegacyFieldTranslation(old=x, new=x)
                for x in self.fields])

            return translator

        def catalog_object(self, *args, **kwargs):
            return

        def uncatalog_object(self, *args, **kwargs):
            return
