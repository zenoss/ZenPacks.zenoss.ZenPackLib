##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import zope.schema
from zope.component import adapts
from zope.interface import implements, providedBy
from Products.Zuul.form.interfaces import IFormBuilder
from Products.Zuul.interfaces import IInfo
from Products.Zuul.infos.component import ComponentFormBuilder as BaseComponentFormBuilder
from ..helpers.ZenPackLibLog import DEFAULTLOG


class ComponentFormBuilder(BaseComponentFormBuilder):

    """Base class for all custom FormBuilders.

    Adds support for renderers in the Component Details form.

    """

    implements(IFormBuilder)
    adapts(IInfo)
    LOG = DEFAULTLOG

    def render(self, **kwargs):
        rendered = super(ComponentFormBuilder, self).render(kwargs)
        self.zpl_decorate(rendered)
        return rendered

    def zpl_decorate(self, item):
        if 'items' in item:
            for item in item['items']:
                self.zpl_decorate(item)
            return

        if 'xtype' in item and 'name' in item and item['xtype'] != 'linkfield':
            if item['name'] in self.renderer:
                renderer = self.renderer[item['name']]

                if renderer:
                    item['xtype'] = 'ZPL_{zenpack_id_prefix}_RenderableDisplayField'.format(
                        zenpack_id_prefix=self.zenpack_id_prefix)
                    item['renderer'] = renderer

    def fields(self, fieldFilter=None):
        """ override to ensure fields are inherited properly"""
        d = {}

        iface_fields = []
        for iface in providedBy(self.context):
            f = zope.schema.getFields(iface)
            if f:
                iface_fields.append(f)
        # reverse so that subclasses processed last
        iface_fields.reverse()

        for f in iface_fields:
            def _filter(item):
                include = True
                if fieldFilter:
                    key=item[0]
                    include = fieldFilter(key)
                else:
                    include = bool(item)
                return include
            for k,v in filter(_filter, f.iteritems()):
                c = self._dict(v)
                c['name'] = k
                value =  getattr(self.context, k, None)
                c['value'] = value() if callable(value) else value
                if c['xtype'] in ('autoformcombo', 'itemselector'):
                    c['values'] = self.vocabulary(v)
                d[k] = c
        return d
