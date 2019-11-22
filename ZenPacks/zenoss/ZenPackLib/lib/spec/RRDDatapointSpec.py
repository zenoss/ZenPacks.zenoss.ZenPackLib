##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import re
from .Spec import Spec
from Products.ZenModel.RRDDataPoint import RRDDataPoint


class RRDDatapointSpec(Spec):
    """RRDDatapointSpec"""

    def __init__(
            self,
            datasource_spec,
            name,
            type_=None,
            rrdtype=None,
            createCmd=None,
            isrow=None,
            rrdmin=None,
            rrdmax=None,
            description=None,
            aliases=None,
            shorthand=None,
            extra_params=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create an RRDDatapoint Specification
        
        :param type_: TODO
        :type type_: str
        :yaml_param type_: type
        :param rrdtype: TODO
        :type rrdtype: str
        :param createCmd: TODO
        :type createCmd: str
        :param isrow: TODO
        :type isrow: bool
        :param rrdmin: TODO
        :type rrdmin: int
        :param rrdmax: TODO
        :type rrdmax: int
        :param description: TODO
        :type description: str
        :param aliases: TODO
        :type aliases: dict(str)
        :param extra_params: Additional parameters that may be used by subclasses of RRDDatapoint
        :type extra_params: ExtraParams

        """
        super(RRDDatapointSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.datasource_spec = datasource_spec
        self.name = name

        self.type_ = type_
        self.rrdtype = rrdtype
        self.createCmd = createCmd
        self.isrow = isrow
        self.rrdmin = rrdmin
        self.rrdmax = rrdmax
        self.description = description
        if extra_params is None:
            self.extra_params = {}
        elif isinstance(extra_params, dict):
            self.extra_params = extra_params

        self.aliases = aliases

        self.shorthand = shorthand

    def __eq__(self, other):
        if self.shorthand:
            # when shorthand syntax is in use, the other values are not relevant
            return super(RRDDatapointSpec, self).__eq__(other, ignore_params=['rrdtype', 'rrdmin', 'rrdmax'])
        else:
            return super(RRDDatapointSpec, self).__eq__(other)

    @property
    def shorthand(self):
        return self._shorthand

    @shorthand.setter
    def shorthand(self, value):
        """Either set local values from shorthand or shorthand from values"""
        self._shorthand = value
        # update local variables from shorthand
        if value:
            # set the rrdtype from shorthand
            try:
                rrd_type = value.upper().split('_')[0]
                self.rrdtype = rrd_type
                # this can happen if shorthand contains an invalid rrdtype
                if rrd_type not in self.rrdtype:
                    self._shorthand = value.replace(rrd_type, self.rrdtype)
            except Exception as e:
                self.LOG.warning('No rrdtype was derived from shorthand: {} ({})'.format(self._shorthand, e))

            # set rrdmin if provided
            min_match = re.search(r'MIN_(\d+)', value, re.IGNORECASE)
            if min_match:
                rrdmin = min_match.group(1)
                self.rrdmin = rrdmin

            # set rrdmax if provided
            max_match = re.search(r'MAX_(\d+)', value, re.IGNORECASE)
            if max_match:
                rrdmax = max_match.group(1)
                self.rrdmax = rrdmax

            # set the alias tag if used
            if value.upper().split('_')[-1] == 'ALIAS':
                self.aliases = self.name

        # otherwise build the shorthand if no other properties are found
        else:
            if self.use_shorthand():
                self._shorthand = self.rrdtype
                if self.rrdmin is not None:
                    self._shorthand += '_MIN_{}'.format(str(self.rrdmin))
                if self.rrdmax is not None:
                    self._shorthand += '_MAX_{}'.format(self.rrdmax)
                if self.aliases:
                    self._shorthand += '_ALIAS'

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, value):
        if not hasattr(self, '_aliases'):
            self._aliases = {}
        if value is not None:
            if isinstance(value, dict):
                # if we receive a dict, then it overrides since it could have come from
                self._aliases.update(value)
            elif isinstance(value, str):
                self.LOG.debug('setting default alias for {}'.format(value))
                self._aliases[value] = None
            else:
                raise ValueError("aliases must be specified as a dict or string (got {})".format(value))
        # ensure that alias keys do not exceed 31 characters in length
        aliases = {}
        for k, v, in self._aliases.items():
            if len(k) > 31:
                self.LOG.warning("alias character length limit exceeded 31: {}, truncating".format(k))
            aliases[k[:31]] = v
        self._aliases = aliases

    @property
    def rrdtype(self):
        return self._rrdtype

    @rrdtype.setter
    def rrdtype(self, value):
        valid_types = ['GAUGE', 'DERIVE', 'COUNTER', 'ABSOLUTE']
        if not value:
            value = 'GAUGE'
        if str(value).upper() not in valid_types:
            self.LOG.warning('Invalid rrdtype: {}, using GAUGE instead'.format(value.upper()))
            value = 'GAUGE'
        self._rrdtype = value

    @property
    def rrdmin(self):
        return self._rrdmin

    @rrdmin.setter
    def rrdmin(self, value):
        if value is not None:
            try:
                value = int(value)
            except Exception as e:
                self.LOG.warning('Invalid rrdmin: {} ({})'.format(value, e))
        self._rrdmin = value

    @property
    def rrdmax(self):
        return self._rrdmax

    @rrdmax.setter
    def rrdmax(self, value):
        if value is not None:
            try:
                value = int(value)
            except Exception as e:
                self.LOG.warning('Invalid rrdmax: {} ({})'.format(value, e))
        self._rrdmax = value

    def using_default_alias(self):
        """Return True if one alias exists with default datapoint name"""
        # default is for alias name to match datapoint name and
        # for it to be the only entry
        if self.name in self.aliases and len(self.aliases) == 1:
            return True
        return False

    def use_shorthand(self):
        """return True if shorthand should be used"""
        # only use shorthand if none of these properties are set
        disqualifiers = ['description', 'createCmd', 'isrow', 'description', 'extra_params']
        if [x for x in disqualifiers if hasattr(self, x) and getattr(self, x, None)]:
            return False
        # do not use shorthand if multiple, non-default aliases are in use
        if self.aliases and not self.using_default_alias():
            return False
        return True

    def get_datapoint_classes(self, dmd, datasource_spec):
        """Return dictionary of datapoint classes"""
        return dict([(dp.__name__, dp)
            for dp in datasource_spec.template_spec.getDataPointClasses(dmd)])

    def create(self, dmd, datasource_spec, datasource):
        # let the datasource create the datapoint if it's not overridden here
        if self.type_ is None:
            datapoint = datasource.manage_addRRDDataPoint(self.name)
        # otherwise we look for the subclass and use our own method instead
        else:
            dp_classes = self.get_datapoint_classes(dmd, datasource_spec)
            dp_class = dp_classes.get(self.type_, RRDDataPoint)
            datapoint = dp_class(self.name)
            datasource.datapoints._setObject(datapoint.id, datapoint)
            datapoint = datasource.datapoints._getOb(datapoint.id)

        type_ = datapoint.__class__.__name__
        self.speclog.debug("adding datapoint of type {}".format(type_))

        if self.rrdtype is not None:
            datapoint.rrdtype = self.rrdtype
        if self.createCmd is not None:
            datapoint.createCmd = self.createCmd
        if self.isrow is not None:
            datapoint.isrow = self.isrow
        if self.rrdmin is not None:
            datapoint.rrdmin = str(self.rrdmin)
        if self.rrdmax is not None:
            datapoint.rrdmax = str(self.rrdmax)
        if self.description is not None:
            datapoint.description = self.description
        if self.extra_params:
            for param, value in self.extra_params.iteritems():
                if param in [x['id'] for x in datapoint._properties]:
                    setattr(datapoint, param, value)
                else:
                    raise ValueError("%s is not a valid property for datapoint of type %s" % (param, type_))

        self.speclog.debug("adding {} aliases".format(len(self.aliases)))
        for alias_id, formula in self.aliases.items():
            datapoint.addAlias(alias_id, formula)
            self.speclog.debug("adding alias".format(alias_id))
            self.speclog.debug("formula = {}".format(formula))
