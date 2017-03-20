##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .OrganizerSpecParams import OrganizerSpecParams
from .RRDTemplateSpecParams import RRDTemplateSpecParams
from ..spec.DeviceClassSpec import DeviceClassSpec


class DeviceClassSpecParams(OrganizerSpecParams, DeviceClassSpec):
    def __init__(self, zenpack_spec, path, zProperties=None, templates=None, **kwargs):
        OrganizerSpecParams.__init__(self, zenpack_spec, path, **kwargs)
        self.zProperties = zProperties
        self.templates = self.specs_from_param(
            RRDTemplateSpecParams, 'templates', templates, zplog=self.LOG)
