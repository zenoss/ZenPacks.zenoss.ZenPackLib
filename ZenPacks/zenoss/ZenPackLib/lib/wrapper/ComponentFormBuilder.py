##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from zope.component import adapts
from zope.interface import implements
from Products.Zuul.form.interfaces import IFormBuilder
from Products.Zuul.interfaces import IInfo
from Products.Zuul.infos.component import ComponentFormBuilder as BaseComponentFormBuilder


class ComponentFormBuilder(BaseComponentFormBuilder):

    """Base class for all custom FormBuilders.

    Adds support for renderers in the Component Details form.

    """

    implements(IFormBuilder)
    adapts(IInfo)

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

