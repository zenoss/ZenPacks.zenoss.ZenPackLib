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
            RRDThresholdSpecParams, 'thresholds', thresholds, log=self.LOG)

        self.datasources = self.specs_from_param(
            RRDDatasourceSpecParams, 'datasources', datasources, log=self.LOG)

        self.graphs = self.specs_from_param(
            GraphDefinitionSpecParams, 'graphs', graphs, log=self.LOG)

    @classmethod
    def fromObject(cls, template):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        template = aq_base(template)

        # Weed out any values that are the same as they would by by default.
        # We do this by instantiating a "blank" template and comparing
        # to it.
        sample_template = template.__class__(template.id)

        for propname in ('targetPythonClass', 'description',):
            if hasattr(sample_template, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_template, propname))
            if getattr(template, propname, None) != getattr(sample_template, propname, None):
                setattr(self, propname, getattr(template, propname, None))

        self.thresholds = {x.id: RRDThresholdSpecParams.fromObject(x) for x in template.thresholds()}
        self.datasources = {x.id: RRDDatasourceSpecParams.fromObject(x) for x in template.datasources()}
        self.graphs = {x.id: GraphDefinitionSpecParams.fromObject(x) for x in template.graphDefs()}

        return self

