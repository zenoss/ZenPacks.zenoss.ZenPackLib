##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
import collections
import importlib
import operator
import types
from Products.Five import zcml
from Products.Zuul.decorators import memoize
from Products.ZenUtils.Utils import monkeypatch, importClass
from Products.Zuul.routers.device import DeviceRouter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewlet
from zope.browser.interfaces import IBrowserView
from Products.ZenUI3.browser.interfaces import IMainSnippetManager
from Products.ZenUI3.utils.javascript import JavaScriptSnippet
from ..utils import dynamicview_installed
from ..functions import get_symbol_name, get_zenpack_path
from ..resources.templates import JS_LINK_FROM_GRID
from ..gsm import get_gsm
from ..base.Device import Device
from ..base.ZenPack import ZenPack
from .Spec import Spec
from .ClassSpec import ClassSpec
from .DeviceClassSpec import DeviceClassSpec
from .ClassRelationshipSpec import ClassRelationshipSpec
from .RelationshipSchemaSpec import RelationshipSchemaSpec
from .ZPropertySpec import ZPropertySpec
from .EventClassSpec import EventClassSpec

DYNAMICVIEW_INSTALLED = dynamicview_installed()

GSM = get_gsm()


class ZenPackSpec(Spec):

    """Representation of a ZenPack's desired configuration.

    Intended to be used to build a ZenPack declaratively as in the
    following example in a ZenPack's __init__.py:

    ##### PRE-YAML style
        from . import zenpacklib

        CFG = zenpacklib.ZenPackSpec(
            name=__name__,

            zProperties={
                'zCiscoAPICHost': {
                    'category': 'Cisco APIC',
                    'type': 'string',
                },
                'zCiscoAPICPort': {
                    'category': 'Cisco APIC',
                    'default': '80',
                },
            },

            classes={
                'APIC': {
                    'base': zenpacklib.Device,
                },
                'FabricPod': {
                    'meta_type': 'Cisco APIC Fabric Pod',
                    'base': zenpacklib.Component,
                },
                'FvTenant': {
                    'meta_type': 'Cisco APIC Tenant',
                    'base': zenpacklib.Component,
                },
            },

            class_relationships=zenpacklib.relationships_from_yuml((
                "[APIC]++-[FabricPod]",
                "[APIC]++-[FvTenant]",
            ))
        )

        CFG.create()
    #####
    """

    def __init__(
            self,
            name,
            zProperties=None,
            classes=None,
            class_relationships=None,
            device_classes=None,
            event_classes=None,
            _source_location=None,
            zplog=None):
        """
            Create a ZenPack Specification

            :param name: Full name of the ZenPack (ZenPacks.zenoss.MyZenPack)
            :type name: str
            :param zProperties: zProperty Specs
            :type zProperties: SpecsParameter(ZPropertySpec)
            :param class_relationships: Class Relationship Specs
            :type class_relationships: list(RelationshipSchemaSpec)
            :yaml_block_style class_relationships: True
            :param device_classes: DeviceClass Specs
            :type device_classes: SpecsParameter(DeviceClassSpec)
            :param event_classes: EventClass Specs
            :type event_classes: SpecsParameter(EventClassSpec)
            :param classes: Class Specs
            :type classes: SpecsParameter(ClassSpec)
        """
        super(ZenPackSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        # The parameters from which this zenpackspec was originally
        # instantiated.
        from ..params.ZenPackSpecParams import ZenPackSpecParams
        self.specparams = ZenPackSpecParams(
            name,
            zProperties=zProperties,
            classes=classes,
            class_relationships=class_relationships,
            device_classes=device_classes,
            event_classes=event_classes,
            zplog=self.LOG)
        self.name = name
        self.LOG.debug("------ {} ------".format(self.name))
        self.id_prefix = name.replace(".", "_")

        self.NEW_COMPONENT_TYPES = []
        self.NEW_RELATIONS = collections.defaultdict(list)

        # zProperties
        self.zProperties = self.specs_from_param(
            ZPropertySpec, 'zProperties', zProperties, zplog=self.LOG)

        # Class Relationship Schema
        self.class_relationships = []
        if class_relationships:
            if not isinstance(class_relationships, list):
                raise ValueError("class_relationships must be a list, not a %s" % type(class_relationships))
            for rel in class_relationships:
                rel['zplog'] = self.LOG
                self.class_relationships.append(RelationshipSchemaSpec(self, **rel))

        # Classes
        self.classes = self.specs_from_param(ClassSpec, 'classes', classes, zplog=self.LOG)

        self.imported_classes = {}

        # Import any external classes referred to in the schema
        for rel in self.class_relationships:
            for relschema in (rel.left_schema, rel.right_schema):
                className = relschema.remoteClass
                if '.' in className and className.split('.')[-1] not in self.classes:
                    module = ".".join(className.split('.')[0:-1])
                    try:
                        kls = importClass(module)
                        self.imported_classes[className] = kls
                    except ImportError:
                        pass

        # Class Relationships
        if classes:
            for classname, classdata in classes.iteritems():
                if 'relationships' not in classdata:
                    classdata['relationships'] = []

                relationships = classdata['relationships']
                for relationship in relationships:
                    # We do not allow the schema to be specified directly.
                    if 'schema' in relationships[relationship]:
                        raise ValueError("Class '%s': 'schema' may not be defined or modified in an individual class's relationship.  Use the zenpack's class_relationships instead." % classname)

        def find_relation_in_bases(bases, relname):
            '''return inherited relationship spec'''
            for base in bases:
                base_cls = self.classes.get(base)
                if relname in base_cls.relationships:
                    return base_cls.relationships.get(relname)
            return None

        def get_bases(cls, bases=[]):
            '''find all available base classes for this class'''
            for base in cls.bases:
                base_cls = self.classes.get(base)
                if not base_cls:
                    continue
                if base not in bases:
                    bases.append(base)
                bases = get_bases(base_cls, bases)
            return bases

        for class_ in self.classes.values():
            # list of all base classes for this class
            bases = get_bases(class_, bases=[])
            # Link the appropriate predefined (class_relationships) schema into place on this class's relationships list.
            for rel in self.class_relationships:
                # handle both directions
                for direction in ['left', 'right']:
                    target_class = getattr(rel, '%s_class' % direction)
                    target_relname = getattr(rel, '%s_relname' % direction)
                    target_schema = getattr(rel, '%s_schema' % direction)
                    # these are directly specified for the class in yaml
                    if class_.name == target_class:
                        if target_relname not in class_.relationships:
                            class_.relationships[target_relname] = ClassRelationshipSpec(class_, target_relname)
                        if not class_.relationships[target_relname].schema:
                            class_.relationships[target_relname].schema = target_schema
                    # look for relations inherited from base classes
                    # go through these in order
                    else:
                        # these are in order from nearest to farthest
                        for base in bases:
                            if target_class == base:
                                # see if we have an existing relspec
                                found_rel = find_relation_in_bases(bases, target_relname)
                                # we need to inherit in this case
                                if found_rel:
                                    if target_relname not in class_.relationships:
                                        class_.relationships[target_relname] = found_rel
                                    if not class_.relationships[target_relname].schema:
                                        class_.relationships[target_relname].schema = target_schema
                                    continue

        for class_ in self.classes.values():
            # Plumb _relations
            for relname, relationship in class_.relationships.iteritems():
                if not relationship.schema:
                    self.LOG.error("Removing invalid display config for relationship {} from  {}.{}".format(relname, self.name, class_.name))
                    class_.relationships.pop(relname)
                    continue

                if relationship.schema.remoteClass in self.imported_classes.keys():
                    remoteClass = relationship.schema.remoteClass  # Products.ZenModel.Device.Device
                    relname = relationship.schema.remoteName  # coolingFans
                    modname = relationship.class_.model_class.__module__  # ZenPacks.zenoss.HP.Proliant.CoolingFan
                    className = relationship.class_.model_class.__name__  # CoolingFan
                    remoteClassObj = self.imported_classes[remoteClass]  # Device_obj
                    remoteType = relationship.schema.remoteType  # ToManyCont
                    localType = relationship.schema.__class__  # ToOne
                    remote_relname = relationship.zenrelations_tuple[0]  # products_zenmodel_device_device

                    if relname not in (x[0] for x in remoteClassObj._relations):
                        rel = ((relname, remoteType(localType, modname, remote_relname)),)
                        # do this differently if it's on a ZPL-based class
                        if hasattr(remoteClassObj, '_v_local_relations'):
                            remoteClassObj._v_local_relations += rel
                        else:
                            remoteClassObj._relations += rel

                    remote_module_id = remoteClassObj.__module__
                    if relname not in self.NEW_RELATIONS[remote_module_id]:
                        self.NEW_RELATIONS[remote_module_id].append(relname)

                    component_type = '.'.join((modname, className))
                    if component_type not in self.NEW_COMPONENT_TYPES:
                        self.NEW_COMPONENT_TYPES.append(component_type)

        # Device Classes
        self.device_classes = self.specs_from_param(
            DeviceClassSpec, 'device_classes', device_classes, zplog=self.LOG)

        # Event Classes
        self.event_classes = self.specs_from_param(
            EventClassSpec, 'event_classes', event_classes)

    @property
    def ordered_classes(self):
        """Return ordered list of ClassSpec instances."""
        return sorted(self.classes.values(), key=operator.attrgetter('order'))

    def create(self):
        """Implement specification."""
        self.create_zenpack_class()

        for spec in self.zProperties.itervalues():
            spec.create()

        # try to avoid import errors on class overrides
        # by creating specs first
        for spec in self.classes.itervalues():
            spec.create_schema_classes()

        for spec in self.classes.itervalues():
            spec.create_zenpack_classes()
            spec.create_registered()

        self.create_product_names()
        self.create_ordered_component_tree()
        self.create_global_js_snippet()
        self.create_device_js_snippet()
        self.register_browser_resources()
        self.apply_platform_patches()

    def create_product_names(self):
        """Add all classes to ZenPack's productNames list.

        This allows zenchkschema to verify the relationship schemas
        created by create().

        """
        productNames = getattr(self.zenpack_module, 'productNames', [])
        self.zenpack_module.productNames = list(
            set(list(self.classes.iterkeys()) + list(productNames)))

    def create_ordered_component_tree(self):
        """Monkeypatch DeviceRouter.getComponentTree to order components."""
        device_meta_types = {
            x.meta_type
            for x in self.classes.itervalues()
            if x.is_device}

        order = {
            x.meta_type: float(x.order)
            for x in self.classes.itervalues()}

        def getComponentTree(self, uid=None, id=None, **kwargs):
            # We do our own sorting.
            kwargs.pop('sorting_dict', None)

            # original is injected by monkeypatch.
            result = original(self, uid=uid, id=id, **kwargs)

            # Only change the order for custom device types.
            meta_type = self._getFacade().getInfo(uid=uid).meta_type
            if meta_type not in device_meta_types:
                return result

            return sorted(result, key=lambda x: order.get(x['id'], 100.0))

        monkeypatch(DeviceRouter)(getComponentTree)

    def register_browser_resources(self):
        """Register browser resources if they exist."""
        zenpack_path = get_zenpack_path(self.name)
        if not zenpack_path:
            return

        resource_path = os.path.join(zenpack_path, 'resources')
        if not os.path.isdir(resource_path):
            return

        directives = []
        directives.append(
            '<resourceDirectory name="{name}" directory="{directory}"/>'
            .format(
                name=self.name,
                directory=resource_path))

        def get_directive(name, for_, weight):
            path = os.path.join(resource_path, '{}.js'.format(name))
            if not os.path.isfile(path):
                return

            return (
                '<viewlet'
                '    name="js-{zenpack_name}-{name}"'
                '    paths="/++resource++{zenpack_name}/{name}.js"'
                '    for="{for_}"'
                '    weight="{weight}"'
                '    manager="Products.ZenUI3.browser.interfaces.IJavaScriptSrcManager"'
                '    class="Products.ZenUI3.browser.javascript.JavaScriptSrcBundleViewlet"'
                '    permission="zope.Public"'
                '    />'
                .format(
                    name=name,
                    for_=for_,
                    weight=weight,
                    zenpack_name=self.name))

        directives.append(get_directive('global', '*', 20))

        for spec in self.ordered_classes:
            if spec.is_device:
                for_ = get_symbol_name(self.name, spec.name, spec.name)

                directives.append(get_directive('device', for_, 21))
                directives.append(get_directive(spec.name, for_, 22))

        # Eliminate None items from list of directives.
        directives = tuple(x for x in directives if x)

        if directives:
            zcml.load_string(
                '<configure xmlns="http://namespaces.zope.org/browser">'
                '<include package="Products.Five" file="meta.zcml"/>'
                '<include package="Products.Five.viewlet" file="meta.zcml"/>'
                '{directives}'
                '</configure>'
                .format(
                    name=self.name,
                    directory=resource_path,
                    directives=''.join(directives)))

    def apply_platform_patches(self):
        """Apply necessary patches to platform code."""
        self.apply_zen21467_patch()

    def apply_zen21467_patch(self):
        """Patch cause of ZEN-21467 issue.

        The problem is that zenpacklib sets string property values to unicode
        strings instead of regular strings. There's a platform bug that
        prevents unicode values from being serialized to be used by zenjmx.
        This means that JMX datasources won't work without this patch.

        """
        try:
            from Products.ZenHub.XmlRpcService import XmlRpcService
            if types.UnicodeType not in XmlRpcService.PRIMITIVES:
                XmlRpcService.PRIMITIVES.append(types.UnicodeType)
        except Exception:
            # The above may become wrong in future platform versions.
            pass

    def create_js_snippet(self, name, snippet, classes=None):
        """Create, register and return JavaScript snippet for given classes."""
        if isinstance(classes, (list, tuple)):
            classes = tuple(classes)
        else:
            classes = (classes,)

        def snippet_method(self):
            return snippet

        attributes = {
            '__allow_access_to_unprotected_subobjects__': True,
            'weight': 20,
            'snippet': snippet_method,
            }

        snippet_class = self.create_class(
            get_symbol_name(self.name),
            get_symbol_name(self.name, 'schema'),
            name,
            (JavaScriptSnippet,),
            attributes)

        try:
            target_name = 'global' if classes[0] is None else 'device'
        except Exception:
            target_name = 'global'

        for klass in classes:
            GSM.registerAdapter(
                snippet_class,
                (klass,) + (IDefaultBrowserLayer, IBrowserView, IMainSnippetManager),
                IViewlet,
                'js-snippet-{name}-{target_name}'
                .format(
                    name=self.name,
                    target_name=target_name))

        return snippet_class

    def create_global_js_snippet(self):
        """Create and register global JavaScript snippet."""
        snippets = []
        for spec in self.ordered_classes:
            snippets.append(spec.global_js_snippet)

        snippet = (
            "(function(){{\n"
            "var ZC = Ext.ns('Zenoss.component');\n"
            "{snippets}"
            "}})();\n"
            .format(
                snippets=''.join(snippets)))

        return self.create_js_snippet('global', snippet)

    def create_device_js_snippet(self):
        """Register device JavaScript snippet."""
        snippet = self.device_js_snippet
        if not snippet:
            return

        device_classes = [
            x.model_class
            for x in self.classes.itervalues()
            if Device in x.resolved_bases]

        # Add imported device objects
        for kls in self.imported_classes.itervalues():
            if 'deviceClass' in [x[0] for x in kls._relations]:
                device_classes.append(kls)

        return self.create_js_snippet(
            'device', snippet, classes=device_classes)

    @property
    def device_js_snippet(self):
        """Return device JavaScript snippet for ZenPack."""
        snippets = []
        for spec in self.ordered_classes:
            snippets.append(spec.device_js_snippet)

        # One DynamicView navigation snippet for all classes.
        snippets.append(self.dynamicview_nav_js_snippet)

        # Don't register the snippet if there's nothing in it.
        if not [x for x in snippets if x]:
            return ""

        link_code = JS_LINK_FROM_GRID.replace('{zenpack_id_prefix}', self.id_prefix)
        return (
            "(function(){{\n"
            "var ZC = Ext.ns('Zenoss.component');\n"
            "{link_code}\n"
            "{snippets}"
            "}})();\n"
            .format(
                link_code=link_code,
                snippets=''.join(snippets)))

    @property
    def dynamicview_nav_js_snippet(self):
        if not DYNAMICVIEW_INSTALLED:
            return ""

        service_view_metatypes = set()
        for kls in self.ordered_classes:
            # Currently only supporting service_view.
            if 'service_view' in (kls.dynamicview_views or []):
                service_view_metatypes.add(kls.meta_type)

        if service_view_metatypes:
            return (
                "Zenoss.nav.appendTo('Component', [{{\n"
                "    id: 'subcomponent_view',\n"
                "    text: _t('Dynamic View'),\n"
                "    xtype: 'dynamicview',\n"
                "    relationshipFilter: 'impacted_by',\n"
                "    viewName: 'service_view',\n"
                "    filterNav: function(navpanel) {{\n"
                "        switch (navpanel.refOwner.componentType) {{\n"
                "            {cases}\n"
                "            default: return false;\n"
                "        }}\n"
                "    }}\n"
                "}}]);\n"
                ).format(
                    cases=' '.join(
                        "case '{}': return true;".format(x)
                        for x in service_view_metatypes))
        else:
            return ""

    @property
    def zenpack_module(self):
        """Return ZenPack module."""
        return importlib.import_module(self.name)

    @property
    def zenpack_class(self):
        """Return ZenPack class."""
        return self.create_zenpack_class()

    @memoize
    def create_zenpack_class(self):
        """Create ZenPack class."""
        packZProperties = [
            x.packZProperties for x in self.zProperties.itervalues()]

        attributes = {
            'packZProperties': packZProperties
            }

        attributes['device_classes'] = self.device_classes
        attributes['event_classes'] = self.event_classes
        attributes['_v_specparams'] = self.specparams
        attributes['NEW_COMPONENT_TYPES'] = self.NEW_COMPONENT_TYPES
        attributes['NEW_RELATIONS'] = self.NEW_RELATIONS
        attributes['GLOBAL_CATALOGS'] = []
        global_catalog_classes = {}
        for (class_, class_spec) in self.classes.items():
            for (p, property_spec) in class_spec.properties.items():
                if property_spec.index_scope in ('both', 'global'):
                    global_catalog_classes[class_] = True
                    continue
        for class_ in global_catalog_classes:
            catalog = ".".join([self.name, class_]).replace(".", "_")
            attributes['GLOBAL_CATALOGS'].append('{}Search'.format(catalog))

        cls = self.create_class(get_symbol_name(self.name),
                            get_symbol_name(self.name, 'schema'),
                            'ZenPack',
                            (ZenPack,),
                            attributes)
        return cls

    def test_setup(self):
        """Execute from a test suite's afterSetUp method.

        Our test layer appears to wipe out adapter registrations. We
        call this again after the layer has been setup so that
        programatically-registered adapters are in place for testing.

        """
        for spec in self.classes.itervalues():
            spec.test_setup()

        self.create_global_js_snippet()
        self.create_device_js_snippet()
