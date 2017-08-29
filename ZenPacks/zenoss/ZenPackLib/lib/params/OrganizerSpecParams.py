##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016-2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .SpecParams import SpecParams
from ..spec.OrganizerSpec import OrganizerSpec


class OrganizerSpecParams(SpecParams, OrganizerSpec):
    def __init__(self, zenpack_spec=None, path='', **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.zenpack_spec = zenpack_spec
        self.path = path.lstrip("/")
