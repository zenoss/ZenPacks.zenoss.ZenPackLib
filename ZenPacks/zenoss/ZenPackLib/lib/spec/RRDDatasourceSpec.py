##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec
from .RRDDatapointSpec import RRDDatapointSpec
from ..base.types import Severity

class RRDDatasourceSpec(Spec):
    """RRDDatasourceSpec"""

    def __init__(
            self,
            template_spec,
            name,
            sourcetype=None,
            enabled=True,
            component=None,
            eventClass=None,
            eventKey=None,
            severity=None,
            commandTemplate=None,
            datapoints=None,
            extra_params=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create an RRDDatasource Specification

            :param sourcetype: TODO
            :type sourcetype: str
            :yaml_param sourcetype: type
            :param enabled: TODO
            :type enabled: bool
            :param component: TODO
            :type component: str
            :param eventClass: TODO
            :type eventClass: str
            :param eventKey: TODO
            :type eventKey: str
            :param severity: TODO
            :type severity: Severity
            :param commandTemplate: TODO
            :type commandTemplate: str
            :param datapoints: TODO
            :type datapoints: SpecsParameter(RRDDatapointSpec)
            :param extra_params: Additional parameters that may be used by subclasses of RRDDatasource
            :type extra_params: ExtraParams

        """
        super(RRDDatasourceSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.template_spec = template_spec
        self.name = name
        self.sourcetype = sourcetype
        self.enabled = enabled
        self.component = component
        self.eventClass = eventClass
        self.eventKey = eventKey
        Severity.LOG = self.LOG
        self.severity = Severity(severity)
        self.commandTemplate = commandTemplate
        if extra_params is None:
            self.extra_params = {}
        else:
            self.extra_params = extra_params

        self.datapoints = self.specs_from_param(
            RRDDatapointSpec, 'datapoints', datapoints, zplog=self.LOG)

    def create(self, templatespec, template):
        datasource_types = dict(template.getDataSourceOptions())

        if not self.sourcetype:
            raise ValueError('No type for %s/%s. Valid types: %s' % (
                             template.id, self.name, ', '.join(datasource_types)))

        type_ = datasource_types.get(self.sourcetype)
        if not type_:
            raise ValueError("%s is an invalid datasource type. Valid types: %s" % (
                             self.sourcetype, ', '.join(datasource_types)))

        datasource = template.manage_addRRDDataSource(self.name, type_)
        self.speclog.debug("adding datasource")

        if self.enabled is not None:
            datasource.enabled = self.enabled
        if self.component is not None:
            datasource.component = self.component
        if self.eventClass is not None:
            datasource.eventClass = self.eventClass
        if self.eventKey is not None:
            datasource.eventKey = self.eventKey
        if self.severity:
            datasource.severity = int(self.severity)
        if self.commandTemplate is not None:
            datasource.commandTemplate = self.commandTemplate

        if self.extra_params:
            for param, value in self.extra_params.iteritems():
                if param in [x['id'] for x in datasource._properties]:
                    # handle an ui test error that expects the oid value to be a string
                    # this is to workaround a ui bug known in 4.5 and 5.0.3
                    if type_ == 'BasicDataSource.SNMP' and param == 'oid':
                        setattr(datasource, param, str(value))
                    else:
                        setattr(datasource, param, value)
                else:
                    raise ValueError("%s is not a valid property for datasource of type %s" % (param, type_))

        self.speclog.debug("adding {} datapoints".format(len(self.datapoints)))
        for datapoint_id, datapoint_spec in self.datapoints.items():
            datapoint_spec.create(self, datasource)
