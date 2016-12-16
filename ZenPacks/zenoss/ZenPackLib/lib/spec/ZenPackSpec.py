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
import inspect
import operator
import types
from Products.Five import zcml
from Products.ZenUtils.Utils import monkeypatch
from Products.Zuul.routers.device import DeviceRouter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewlet
from zope.browser.interfaces import IBrowserView
from Products.ZenUI3.browser.interfaces import IMainSnippetManager
from Products.ZenModel.interfaces import IExpandedLinkProvider
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
from .RelationshipSchemaSpec import RelationshipSchemaSpec
from .ZPropertySpec import ZPropertySpec
from .EventClassSpec import EventClassSpec
from .ProcessClassOrganizerSpec import ProcessClassOrganizerSpec
from .LinkProviderSpec import LinkProviderSpec
from ..links import DeviceLinkProvider

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

    _zenpack_class = None
    _ordered_classes = None
    _device_js_snippet = None
    _dynamicview_nav_js_snippet = None
    _zenpack_module = None
    imported_classes = {}

    def __init__(
            self,
            name,
            zProperties=None,
            classes=None,
            class_relationships=None,
            device_classes=None,
            event_classes=None,
            process_class_organizers=None,
            link_providers=None,
            _source_location=None,
            zplog=None):
        """
            Create a ZenPack Specification

            :param name: Full name of the ZenPack (ZenPacks.zenoss.MyZenPack)
            :type name: str
            :param zProperties: zProperty Specs
            :type zProperties: SpecsParameter(ZPropertySpec)
            :param classes: Class Specs
            :type classes: SpecsParameter(ClassSpec)
            :param class_relationships: Class Relationship Specs
            :type class_relationships: list(RelationshipSchemaSpec)
            :yaml_block_style class_relationships: True
            :param device_classes: DeviceClass Specs
            :type device_classes: SpecsParameter(DeviceClassSpec)
            :param event_classes: EventClass Specs
            :type event_classes: SpecsParameter(EventClassSpec)
            :param process_class_organizers: Process Class Specs
            :type process_class_organizers: SpecsParameter(ProcessClassOrganizerSpec)
            :param link_providers: Link Provider Specs
            :type link_providers: SpecsParameter(LinkProviderSpec)
        """
        super(ZenPackSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.name = name
        self.LOG.debug("------ {} ------".format(self.name))
        self.id_prefix = name.replace(".", "_")

        self.NEW_COMPONENT_TYPES = []
        self.NEW_RELATIONS = collections.defaultdict(list)

        # zProperties
        self.zProperties = self.specs_from_param(
            ZPropertySpec, 'zProperties', zProperties, zplog=self.LOG)

        # Classes
        self.classes = self.specs_from_param(ClassSpec, 'classes', classes, zplog=self.LOG)
        # deal with float order parameters if they exist
        self.normalize_child_order(self.classes.values())

        # update properties from ancestor classes
        self.plumb_properties()

        # Class Relationship Schema
        self.class_relationships = []
        if class_relationships:
            if not isinstance(class_relationships, list):
                raise ValueError("class_relationships must be a list, not a %s" % type(class_relationships))
            for rel in class_relationships:
                rel['zplog'] = self.LOG
                self.class_relationships.append(RelationshipSchemaSpec(self, **rel))

        # update relationships for ClassSpec child classes
        for rel in self.class_relationships:
            rel.update_children()

        # update relations on imported classes
        self.plumb_relations()

        # Device Classes
        self.device_classes = self.specs_from_param(
            DeviceClassSpec, 'device_classes', device_classes, zplog=self.LOG)

        # Event Classes
        self.event_classes = self.specs_from_param(
            EventClassSpec, 'event_classes', event_classes)

        # Process Classes
        self.process_class_organizers = self.specs_from_param(
            ProcessClassOrganizerSpec, 'process_class_organizers', process_class_organizers)

        # Link Providers
        self.link_providers = self.specs_from_param(
            LinkProviderSpec, 'link_providers', link_providers, zplog=self.LOG)

        # The parameters from which this zenpackspec was originally
        # instantiated.
        from ..params.ZenPackSpecParams import ZenPackSpecParams
        self.specparams = ZenPackSpecParams(
            name,
            zProperties=zProperties,
            classes=classes,
            class_relationships=self.class_relationships,
            device_classes=device_classes,
            event_classes=event_classes,
            process_class_organizers=process_class_organizers,
            zplog=self.LOG)

    def plumb_properties(self):
        """
            Plumb class properties by ancestors first
        """
        for class_ in self.classes.values():
            for name in class_.get_base_specs():
                spec = self.classes.get(name)
                spec.update_inherited_property_parameters()
            class_.update_inherited_property_parameters()

    def plumb_relations(self):
        """
            Plumb class relations by ancestors first
        """
        for class_ in self.classes.values():
            for name in class_.get_base_specs():
                spec = self.classes.get(name)
                spec.update_inherited_relation_parameters()
                spec.plumb_class_relations()
            class_.update_inherited_relation_parameters()
            class_.plumb_class_relations()

    @property
    def ordered_classes(self):
        """Return ordered list of ClassSpec instances."""
        if not self._ordered_classes:
            self._ordered_classes = sorted(self.classes.values(), key=operator.attrgetter('order'))
        return self._ordered_classes

    def create(self):
        """Implement specification."""
        self.create_zenpack_class()

        for spec in self.zProperties.itervalues():
            spec.create()

        for spec in self.classes.itervalues():
            schema = spec.model_schema_class

        for spec in self.classes.itervalues():
            spec.create_registered()

        self.create_product_names()
        self.create_ordered_component_tree()
        self.create_global_js_snippet()
        self.create_device_js_snippet()
        self.register_browser_resources()
        self.apply_platform_patches()
        self.register_link_providers()

    def register_link_providers(self):
        if not self.link_providers:
            return

        # register for base Device type
        GSM.registerSubscriptionAdapter(
            DeviceLinkProvider,
            required=(Device,),
            provided=IExpandedLinkProvider)

        for key, provider in self.link_providers.iteritems():
            class_name = provider.link_class.split('.')
            try:
                module = importlib.import_module('.'.join(class_name[:-1]))
                klass = getattr(module, class_name[-1:][0], None)
            except (ImportError, AttributeError, IndexError):
                self.LOG.warn('Problem attempting to find and load link_class '
                              '{} for provider {}.'.format(provider.link_class, key))
            if Device not in inspect.getmro(klass):
                # if class is not derived from base Device, register it
                GSM.registerSubscriptionAdapter(
                    DeviceLinkProvider,
                    required=(klass,),
                    provided=IExpandedLinkProvider)

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
            x.meta_type: x.scaled_order
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
        if not self._device_js_snippet:
            self._device_js_snippet = self.get_device_js_snippet()
        return self._device_js_snippet

    def get_device_js_snippet(self):
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
        if not self._dynamicview_nav_js_snippet:
            self._dynamicview_nav_js_snippet = self.create_dynamicview_nav_js_snippet()
        return self._dynamicview_nav_js_snippet

    def create_dynamicview_nav_js_snippet(self):
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
                    cases='\n            '.join(
                        "case '{}': return true;".format(x)
                        for x in service_view_metatypes))
        else:
            return ""

    @property
    def zenpack_module(self):
        """Return ZenPack module."""
        if not self._zenpack_module:
            self._zenpack_module = importlib.import_module(self.name)
        return self._zenpack_module

    @property
    def zenpack_class(self):
        """Return ZenPack class."""
        if not self._zenpack_class:
            self._zenpack_class = self.create_zenpack_class()
        return self._zenpack_class

    def create_zenpack_class(self):
        """Create ZenPack class."""
        packZProperties = [
            x.packZProperties for x in self.zProperties.itervalues()]

        attributes = {
            'packZProperties': packZProperties
            }
        attributes['zenpack_spec'] = self
        attributes['device_classes'] = self.device_classes
        attributes['event_classes'] = self.event_classes
        attributes['process_class_organizers'] = self.process_class_organizers
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
