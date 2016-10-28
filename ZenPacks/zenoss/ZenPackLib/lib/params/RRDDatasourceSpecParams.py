##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from collections import OrderedDict
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
    def fromObject(cls, datasource):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        datasource = aq_base(datasource)

        # Weed out any values that are the same as they would by by default.
        # We do this by instantiating a "blank" datapoint and comparing
        # to it.
        sample_ds = datasource.__class__(datasource.id)

        self.sourcetype = datasource.sourcetype
        for propname in ('enabled', 'component', 'eventClass', 'eventKey',
                         'severity', 'commandTemplate'):
            if hasattr(sample_ds, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_ds, propname))
            if getattr(datasource, propname, None) != getattr(sample_ds, propname, None):
                setattr(self, propname, getattr(datasource, propname, None))

        self.extra_params = OrderedDict()
        for propname in [x['id'] for x in datasource._properties]:
            if propname not in self.init_params:
                if getattr(datasource, propname, None) != getattr(sample_ds, propname, None):
                    self.extra_params[propname] = getattr(datasource, propname, None)

        self.datapoints = {x.id: RRDDatapointSpecParams.fromObject(x) for x in datasource.datapoints()}

        return self
