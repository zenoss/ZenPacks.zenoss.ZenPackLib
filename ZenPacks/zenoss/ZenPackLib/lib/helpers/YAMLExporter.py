##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import yaml
import collections
from ..params.ZenPackSpecParams import ZenPackSpecParams
from ..params.RRDTemplateSpecParams import RRDTemplateSpecParams
from ..params.EventClassSpecParams import EventClassSpecParams
from ..params.EventClassMappingSpecParams import EventClassMappingSpecParams
from ..params.ProcessClassOrganizerSpecParams import ProcessClassOrganizerSpecParams
from .Dumper import Dumper


class YAMLExporter(object):
    """
        Class containing methods for exporting 
        existing ZenPack objects to YAML
    """

    @staticmethod
    def dump_templates(zenpack):
        """Return YAML export of RRD Templates"""
        zenpack_name = zenpack.id
        templates = YAMLExporter.get_template_specparams(zenpack)
        if not templates:
            for dc_name, dc_sp in zenpack._v_specparams.device_classes.items():
                templates.update({dc_name: dc_sp.templates})

        if templates:
            zpsp = ZenPackSpecParams(
                zenpack_name,
                device_classes={x: {} for x in templates})
            for dc_name in templates:
                zpsp.device_classes[dc_name].templates = templates[dc_name]

            return yaml.dump(zpsp, Dumper=Dumper)

    @staticmethod
    def dump_event_classes(zenpack):
        """Return YAML export of Event Classes"""
        eventclasses = YAMLExporter.get_event_class_specparams(zenpack)
        if not eventclasses:
            eventclasses.update(zenpack._v_specparams.event_classes)
        zenpack_name = zenpack.id
        if eventclasses:
            zpsp = ZenPackSpecParams(zenpack_name,
                                     event_classes={x: {} for x in eventclasses})
            for ec_name in eventclasses:
                zpsp.event_classes[ec_name] = eventclasses[ec_name]
                zpsp.event_classes[ec_name].mappings = eventclasses[ec_name].mappings

            return yaml.dump(zpsp, Dumper=Dumper)

    @staticmethod
    def dump_process_classes(zenpack):
        """Return YAML export of Process Classes"""
        processclasses = YAMLExporter.get_process_class_specparams(zenpack)
        if not processclasses:
            processclasses.update(zenpack._v_specparams.process_class_organizers)
        zenpack_name = zenpack.id
        if processclasses:
            zpsp = ZenPackSpecParams(zenpack_name,
                                     process_class_organizers={x: {} for x in processclasses})
            for pc_name in processclasses:
                zpsp.process_class_organizers[pc_name].process_classes = processclasses[pc_name].process_classes

            return yaml.dump(zpsp, Dumper=Dumper)

    @staticmethod
    def get_template_specparams(zenpack):
        """Return dictionary of Template SpecParams"""
        specs = collections.defaultdict(dict)

        dc_packables = YAMLExporter.get_packables(
            zenpack, 'DeviceClass')
        rrd_packables = YAMLExporter.get_packables(
            zenpack, 'RRDTemplate')

        for template in set(
            [x.getAllRRDTemplates() for x in dc_packables] + rrd_packables):
            deviceClass = template.deviceClass()
            if deviceClass:
                dc_name = deviceClass.getOrganizerName()
                specs[dc_name][template.id] = RRDTemplateSpecParams.fromObject(template)
        return specs

    @staticmethod
    def get_event_class_specparams(zenpack):
        """Return dictionary of EventClass SpecParams"""
        ec_packables = YAMLExporter.get_packables(
            zenpack, 'EventClass')

        eventclasses = YAMLExporter.get_organizer_specparams(
            ec_packables, EventClassSpecParams)

        # get list of instances associated with event classes not already seen
        inst_packables = YAMLExporter.get_packables(
                zenpack, 'EventClassInst')

        # list of unique event classes
        inst_evs = list({x.eventClass() for x in inst_packables
            if x.eventClass().getDmdKey() not in eventclasses})

        for ev in inst_evs:
            ec_name = ev.getDmdKey()
            ev_spec = EventClassSpecParams.new(ec_name, remove=False)
            ev_instances = [x for x in ev.instances() if x in zenpack.packables()]
            ev_spec.mappings = { x.id: EventClassMappingSpecParams.fromObject(x) for x in ev_instances }
            eventclasses[ec_name] = ev_spec

        return eventclasses

    @staticmethod
    def get_process_class_specparams(zenpack):
        """Return dictionary of EventClass SpecParams"""
        from_packables = YAMLExporter.get_packables(
            zenpack, 'OSProcessOrganizer')
        return YAMLExporter.get_organizer_specparams(
            from_packables, ProcessClassOrganizerSpecParams)

    @staticmethod
    def get_organizer_specparams(organizers, specparam_cls):
        """Return organizer_related specparams"""
        output = collections.defaultdict(dict)
        for org in organizers:
            name = org.getDmdKey()
            # electing not to set remove=True here to avoid unwanted deletions
            output[name] = specparam_cls.fromObject(org)
            for sub_org in org.getSubOrganizers():
                name = sub_org.getDmdKey()
                output[name] = specparam_cls.fromObject(sub_org, remove=False)
        return output

    @staticmethod
    def get_packables(zenpack, meta_type):
        """Return objects of a given meta_type from a ZenPack's packables"""
        return [x for x in zenpack.packables()
            if x.meta_type == meta_type]
