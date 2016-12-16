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
from ..spec.RRDDatasourceSpec import RRDDatasourceSpec
from .RRDDatapointSpecParams import RRDDatapointSpecParams

class RRDDatasourceSpecParams(SpecParams, RRDDatasourceSpec):
    def __init__(self, template_spec, name, datapoints=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

        self.datapoints = self.specs_from_param(
            RRDDatapointSpecParams, 'datapoints', datapoints, zplog=self.LOG)

    @classmethod
    def fromObject(cls, ob):
        self = super(RRDDatasourceSpecParams, cls).fromObject(ob)

        ob = aq_base(ob)

        self.datapoints = {x.id: RRDDatapointSpecParams.fromObject(x) for x in ob.datapoints()}

        return self
