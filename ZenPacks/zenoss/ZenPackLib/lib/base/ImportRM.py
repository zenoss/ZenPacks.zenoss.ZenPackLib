from Products.ZenRelations.ImportRM import SpoofedOptions, NoLoginImportRM
from xml.sax.handler import ContentHandler
from collections import OrderedDict

import os
from lxml import etree

from Products.ZenModel.DmdBuilder import DmdBuilder
from Products.ZenModel.ZentinelPortal import PortalGenerator
from Testing import ZopeTestCase

# import yaml
# import difflib
# import time
# import sys
# import Globals

# from Acquisition import aq_base
# from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
# from ..helpers.Dumper import Dumper


# setup the Products needed for the Zenoss test instance
ZopeTestCase.installProduct('ZenModel', 1)
ZopeTestCase.installProduct('ZCatalog', 1)
ZopeTestCase.installProduct('OFolder', 1)
ZopeTestCase.installProduct('ManagableIndex', 1)
ZopeTestCase.installProduct('AdvancedQuery', 1)
ZopeTestCase.installProduct('ZCTextIndex', 1)
ZopeTestCase.installProduct('CMFCore', 1)
ZopeTestCase.installProduct('CMFDefault', 1)
ZopeTestCase.installProduct('MailHost', 1)
ZopeTestCase.installProduct('Transience', 1)
ZopeTestCase.installProduct('ZenRelations', 1)

class ImportRM(NoLoginImportRM):
    '''Class override of ImportRM with additional
        ZPL-related functionality for use when upgrading
        from legacy Zenpacks
    '''
#
#     def loadObjectFromXML(self, xmlfile=''):
#         super(ImportRM, self).loadObjectFromXML(xmlfile)
#         return self.objstack
#     def __init__(self):
#         self.app = ZopeTestCase.ZopeTestCase.app
#         super(ImportRM, self).__init__(self.app)
#
#         gen = PortalGenerator()
#         if hasattr(self.app, 'zport'):
#             self.app._delObject('zport', suppress_events=True)
#         gen.create(self.app, 'zport', True)
#         # builder params:
#         # portal, cvthost, evtuser, evtpass, evtdb,
#         #    smtphost, smtpport, pagecommand
#         builder = DmdBuilder(self.app.zport, 'localhost', 'zenoss', 'zenoss',
#                             'events', 3306, 'localhost', '25',
#                              '$ZENHOME/bin/zensnpp localhost 444 $RECIPIENT')
#         builder.build()
#         self.dmd = builder.dmd

    def get_xml_objects(self, xmlfile=''):
        '''Return objects that would be loaded from objects.xml'''

        objects = {'device_classes': OrderedDict(),
                   'event_classes': OrderedDict(),
                   }
        obs = self.loadObjectFromXML(xmlfile)
        for ob in obs:
            if ob.id == 'dmd':
                continue
            # device classes
            elif ob.id == 'rrdTemplates':
                path = '/'.join([x for x in ob.getPrimaryPath() if x not in ['zport', 'dmd', 'Devices', 'rrdTemplates']])
                if path not in objects['device_classes']:
                    objects['device_classes'][path] = OrderedDict()
                for rrd in ob():
                    objects['device_classes'][path][rrd.id] = rrd
            elif ob.__class__.__name__ == 'EventClass':
                path = '/'.join([x for x in ob.getPrimaryPath() if x not in ['zport', 'dmd', 'Events']])
                if path not in objects['device_classes']:
                    objects['event_classes'][path] = ob
        return objects

    def filter_xml(self, filename):
        pruned = 0
        try:
            tree = etree.parse(filename)

            path = []
            context = etree.iterwalk(tree, events=('start', 'end'))
            for action, elem in context:
                if elem.tag == 'object':
                    if action == 'start':
                        path.append(elem.attrib.get('id'))

                    elif action == 'end':
                        obj_path = '/'.join(path)
                        try:
                            obj = self.dmd.getObjByPath(obj_path)
                            if getattr(obj, 'zpl_managed', False):
                                self.LOG.debug("Removing {} from {}".format(obj_path, filename))
                                pruned += 1

                                # if there's a comment before it with the
                                # primary path of the object, remove that first.
                                prev = elem.getprevious()
                                if '<!-- ' + repr(tuple('/'.join(path).split('/'))) + ' -->' == repr(prev):
                                    elem.getparent().remove(prev)

                                # Remove the ZPL-managed object
                                elem.getparent().remove(elem)

                        except Exception:
                            self.LOG.warning("Unable to postprocess {} in {}".format(obj_path, filename))

                        path.pop()

                if elem.tag == 'tomanycont':
                    if action == 'start':
                        path.append(elem.attrib.get('id'))
                    elif action == 'end':
                        path.pop()

            if len(tree.getroot()) == 0:
                self.LOG.info("Removing {}".format(filename))
                os.remove(filename)
            elif pruned:
                self.LOG.info("Pruning {} objects from {}".format(pruned, filename))
                with open(filename, 'w') as f:
                    f.write(etree.tostring(tree))
            else:
                self.LOG.debug("Leaving {} unchanged".format(filename))

        except Exception, e:
            self.LOG.error("Unable to postprocess {}: {}".format(filename, e))

if __name__ == '__main__':
    im = ImportRM()
    im.loadDatabase()
