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
from .RRDThresholdSpecParams import RRDThresholdSpecParams
from .RRDDatasourceSpecParams import RRDDatasourceSpecParams
from .GraphDefinitionSpecParams import GraphDefinitionSpecParams
from ..spec.RRDTemplateSpec import RRDTemplateSpec


class RRDTemplateSpecParams(SpecParams, RRDTemplateSpec):
    def __init__(self, deviceclass_spec, name, thresholds=None, datasources=None, graphs=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

        self.thresholds = self.specs_from_param(
            RRDThresholdSpecParams, 'thresholds', thresholds, zplog=self.LOG)

        self.datasources = self.specs_from_param(
            RRDDatasourceSpecParams, 'datasources', datasources, zplog=self.LOG)

        self.graphs = self.specs_from_param(
            GraphDefinitionSpecParams, 'graphs', graphs, zplog=self.LOG)

    @classmethod
    def fromObject(cls, template):
        self = super(RRDTemplateSpecParams, cls).fromObject(template)

        template = aq_base(template)

        self.thresholds = {x.id: RRDThresholdSpecParams.fromObject(x) for x in template.thresholds()}
        self.datasources = {x.id: RRDDatasourceSpecParams.fromObject(x) for x in template.datasources()}
        self.graphs = {x.id: GraphDefinitionSpecParams.fromObject(x) for x in template.graphDefs()}

        return self
