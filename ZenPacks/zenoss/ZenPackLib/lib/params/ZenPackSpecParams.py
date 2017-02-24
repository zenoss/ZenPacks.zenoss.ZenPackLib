##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import inspect
import importlib
from Acquisition import aq_base
from Products.ZenModel.ManagedEntity import ManagedEntity
from .SpecParams import SpecParams
from .ZPropertySpecParams import ZPropertySpecParams
from .ClassSpecParams import ClassSpecParams
from .RelationshipSchemaSpecParams import RelationshipSchemaSpecParams
from .DeviceClassSpecParams import DeviceClassSpecParams
from .EventClassSpecParams import EventClassSpecParams
from .ProcessClassOrganizerSpecParams import ProcessClassOrganizerSpecParams
from ..spec.ZenPackSpec import ZenPackSpec
from collections import OrderedDict

class ZenPackSpecParams(SpecParams, ZenPackSpec):
    def __init__(self,
                 name,
                 zProperties=None,
                 class_relationships=None,
                 classes=None,
                 device_classes=None,
                 event_classes=None,
                 process_class_organizers=None,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.id_prefix = name.replace(".", "_")

        self.zProperties = self.specs_from_param(
            ZPropertySpecParams, 'zProperties', zProperties, leave_defaults=True, zplog=self.LOG)

        self.classes = self.specs_from_param(
            ClassSpecParams, 'classes', classes, leave_defaults=True, zplog=self.LOG)

        self.class_relationships = class_relationships

        self.device_classes = self.specs_from_param(
            DeviceClassSpecParams, 'device_classes', device_classes, leave_defaults=True, zplog=self.LOG)

        self.event_classes = self.specs_from_param(
            EventClassSpecParams, 'event_classes', event_classes, leave_defaults=True, zplog=self.LOG)

        self.process_class_organizers = self.specs_from_param(
            ProcessClassOrganizerSpecParams, 'process_class_organizers', process_class_organizers, leave_defaults=True, zplog=self.LOG)

    @classmethod
    def fromObject(cls, ob,
                   all=True,
                   zproperties=False,
                   classes=False,
                   class_relationships=False,
                   device_classes=False,
                   event_classes=False,
                   process_classes=False,
                   get_templates=True,
                   get_zprops=True):

        self = super(ZenPackSpecParams, cls).fromObject(ob)

        ob = aq_base(ob)
        self.name = ob.id

        # import the ZenPack module
        zp = importlib.import_module(self.name)

        zp_cls = zp.ZenPack

        # zproperties
        if all or zproperties:
            self.zProperties = {x[0]: ZPropertySpecParams.fromTuple(x) for x in zp_cls.packZProperties}
            if hasattr(zp_cls, "packZProperties_data"):
                for k, v in zp_cls.packZProperties_data.items():
                    self.zProperties[k].label = v.get('label', '')
                    self.zProperties[k].description = v.get('description', '')

        # classes and class relationships
        self.classes = {}
        self.class_relationships = []

        # do not process Device / ManagedEntity Relations
        ignore_rels = [x[0] for x in ManagedEntity._relations]
        # iterate through modules of ZP
        for k, v in zp.__dict__.items():
            if k in ['schema', 'zenpacklib']:
                continue
            if inspect.ismodule(v):
                for i, j in v.__dict__.items():
                    if not inspect.isclass(j):
                        continue
                    if not issubclass(j, ManagedEntity):
                        continue
                    if all or classes:
                        self.classes[j.__name__] = ClassSpecParams.fromClass(j)
                    if all or class_relationships:
                        relnames = [x[0] for x in j._relations if x[0] not in ignore_rels]
                        for relname in relnames:
                            if ClassSpecParams.use_rel(j, relname):
                                relspecparam = RelationshipSchemaSpecParams.fromClass(j, relname, self.name)
                                if relspecparam not in self.class_relationships:
                                    self.class_relationships.append(relspecparam)

        # if relation is M:M, then we want to avoid duplicates
        for i, rel_i in enumerate(self.class_relationships):
            if not ('ToMany' == rel_i.left_type == rel_i.right_type):
                continue
            for j in range(i):
                rel_j = self.class_relationships[j]
                if not ('ToMany' == rel_j.left_type == rel_j.right_type):
                    continue
                if rel_i.left_class == rel_j.right_class and rel_i.right_class == rel_j.left_class:
                    self.class_relationships.remove(rel_j)

        if all or class_relationships:
            self.class_relationships.sort(key=lambda x: x.left_class)

        self.device_classes = OrderedDict()

        if all or device_classes:
            d_classes = {x for x in ob.packables() if x.meta_type == 'DeviceClass'}
            t_classes = {x.deviceClass() for x in ob.packables() if x.meta_type == 'RRDTemplate'}
            all_classes = d_classes.union(t_classes)
            self.device_classes = DeviceClassSpecParams.get_ordered_params(all_classes, 'getOrganizerName', is_method=True, zenpack=ob, get_templates=get_templates, get_zprops=get_zprops)

            # t_classes = {x.deviceClass() for x in ob.packables() if x.meta_type == 'RRDTemplate'}
            # self.device_classes.update(DeviceClassSpecParams.get_ordered_params(t_classes, 'getOrganizerName', is_method=True, zenpack=ob, get_templates=templates, get_zprops=get_zprops))

#         # device classes/templates
#         if all or templates:
#             d_classes = {x.deviceClass() for x in ob.packables() if x.meta_type == 'RRDTemplate'}
#             self.device_classes.update(DeviceClassSpecParams.get_ordered_params(d_classes, 'getOrganizerName', is_method=True, zenpack=ob, get_templates=templates, get_zprops=get_zprops))

        # event classes
        if all or event_classes:
            e_classes = list({x for x in ob.packables() if x.meta_type == 'EventClass'})
            e_inst_classes = list({x for x in ob.packables() if x.meta_type == 'EventClassInst'})
            self.event_classes = EventClassSpecParams.get_ordered_params(e_classes, 'getOrganizerName', is_method=True, zenpack=ob)

            e_inst_classes = list({x.eventClass() for x in ob.packables() if x.meta_type == 'EventClassInst'})
            self.event_classes.update(EventClassSpecParams.get_ordered_params(e_inst_classes, 'getOrganizerName', is_method=True, zenpack=ob, remove=False))

        # process class organizers
        if all or process_classes:
            p_classes = {x for x in ob.packables() if x.meta_type == 'OSProcessOrganizer'}
            self.process_class_organizers = ProcessClassOrganizerSpecParams.get_ordered_params(p_classes, 'getOrganizerName', is_method=True, zenpack=ob)

            p_inst_classes = list({x.osProcessOrganizer() for x in ob.packables() if x.meta_type == 'OSProcessClass'})
            self.process_class_organizers.update(ProcessClassOrganizerSpecParams.get_ordered_params(p_inst_classes, 'getOrganizerName', is_method=True, zenpack=ob, remove=False))

        return self


