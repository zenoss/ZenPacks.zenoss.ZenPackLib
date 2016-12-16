##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .SpecParams import SpecParams
from ..spec.RRDThresholdSpec import RRDThresholdSpec


class RRDThresholdSpecParams(SpecParams, RRDThresholdSpec):
    def __init__(self, template_spec, name, foo=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
