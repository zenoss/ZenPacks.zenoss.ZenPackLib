##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from .SpecParams import SpecParams
from .RRDTemplateSpecParams import RRDTemplateSpecParams
from .ZPropertySpecParams import ZPropertySpecParams

from ..spec.DeviceClassSpec import DeviceClassSpec


class DeviceClassSpecParams(SpecParams, DeviceClassSpec):
    def __init__(self, zenpack_spec, path, zProperties=None, templates=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.path = path
        self.zProperties = zProperties
        self.templates = self.specs_from_param(
            RRDTemplateSpecParams, 'templates', templates, zplog=self.LOG)

    @classmethod
    def fromObject(cls, deviceclass, zenpack=None, get_templates=True, get_zprops=True):
        self = super(DeviceClassSpecParams, cls).fromObject(deviceclass)

        deviceclass = aq_base(deviceclass)

        self.path = deviceclass.getOrganizerName().lstrip('/')

        if get_zprops:
            # if this is set locally
            if 'devtypes' in deviceclass.__dict__ and deviceclass in zenpack.packables():
                if deviceclass.devtypes:
                    entry = deviceclass.devtypes[0]
                    self.description = entry[0]
                    self.protocol = entry[1]

            zprops = [x for x in deviceclass.zenPropertyIds(all=False) if deviceclass.isLocal(x)]
            self.zProperties = {x: getattr(deviceclass, x) for x in zprops}

        if get_templates:
            templates = deviceclass.rrdTemplates()
            if zenpack:
                templates = [x for x in templates if x in zenpack.packables()]

            self.templates = RRDTemplateSpecParams.get_ordered_params(templates, 'id', reorder=False)

        return self
