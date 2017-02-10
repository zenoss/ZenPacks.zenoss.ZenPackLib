##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec
from ..base.types import Severity


class RRDThresholdSpec(Spec):
    """RRDThresholdSpec"""

    def __init__(
            self,
            template_spec,
            name,
            type_='MinMaxThreshold',
            dsnames=[],
            eventClass=None,
            severity=None,
            enabled=None,
            extra_params=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create an RRDThreshold Specification

            :param type_: TODO
            :type type_: str
            :yaml_param type_: type
            :param dsnames: TODO
            :type dsnames: list(str)
            :param eventClass: TODO
            :type eventClass: str
            :param severity: TODO
            :type severity: Severity
            :param enabled: TODO
            :type enabled: bool
            :param extra_params: Additional parameters that may be used by subclasses of RRDDatasource
            :type extra_params: ExtraParams

        """
        super(RRDThresholdSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.name = name
        self.template_spec = template_spec
        self.dsnames = dsnames
        self.eventClass = eventClass
        Severity.LOG = self.LOG
        self.severity = Severity(severity)
        self.enabled = enabled
        self.type_ = type_
        if extra_params is None:
            self.extra_params = {}
        else:
            self.extra_params = extra_params

    def create(self, templatespec, template):
        if self.dsnames is None:
            raise ValueError("%s: threshold has no dsnames attribute", self)

        # Shorthand for datapoints that have the same name as their datasource.
        for i, dsname in enumerate(self.dsnames):
            if '_' not in dsname:
                self.dsnames[i] = '_'.join((dsname, dsname))

        threshold_types = dict((y, x) for x, y in template.getThresholdClasses())
        type_ = threshold_types.get(self.type_)
        if not type_:
            raise ValueError("'%s' is an invalid threshold type. Valid types: %s" %
                             (self.type_, ', '.join(threshold_types)))

        threshold = template.manage_addRRDThreshold(self.name, self.type_)
        self.speclog.debug("adding threshold")

        if self.dsnames is not None:
            threshold.dsnames = self.dsnames
        if self.eventClass is not None:
            threshold.eventClass = self.eventClass
        if self.severity is not None:
            threshold.severity = int(self.severity)
        if self.enabled is not None:
            threshold.enabled = self.enabled
        if self.extra_params:
            for param, value in self.extra_params.iteritems():
                if param in [x['id'] for x in threshold._properties]:
                    setattr(threshold, param, value)
                else:
                    raise ValueError("%s is not a valid property for threshold of type %s" % (param, type_))

