import re
from .Spec import Spec

class RRDDatapointSpec(Spec):

    """TODO."""

    def __init__(
            self,
            datasource_spec,
            name,
            rrdtype=None,
            createCmd=None,
            isrow=None,
            rrdmin=None,
            rrdmax=None,
            description=None,
            aliases=None,
            shorthand=None,
            extra_params=None,
            _source_location=None
            ):
        """
        Create an RRDDatapoint Specification

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

        self.datasource_spec = datasource_spec
        self.name = name

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

        if aliases is None:
            self.aliases = {}
        elif isinstance(aliases, dict):
            self.aliases = aliases
        else:
            raise ValueError("aliases must be specified as a dict")

        if shorthand:
            if 'DERIVE' in shorthand.upper():
                self.rrdtype = 'DERIVE'

            min_match = re.search(r'MIN_(\d+)', shorthand, re.IGNORECASE)
            if min_match:
                rrdmin = min_match.group(1)
                self.rrdmin = rrdmin

            max_match = re.search(r'MAX_(\d+)', shorthand, re.IGNORECASE)
            if max_match:
                rrdmax = max_match.group(1)
                self.rrdmax = rrdmax

    def __eq__(self, other):
        if self.shorthand:
            # when shorthand syntax is in use, the other values are not relevant
            return super(RRDDatapointSpec, self).__eq__(other, ignore_params=['rrdtype', 'rrdmin', 'rrdmax'])
        else:
            return super(RRDDatapointSpec, self).__eq__(other)

    def create(self, datasource_spec, datasource):
        datapoint = datasource.manage_addRRDDataPoint(self.name)
        type_ = datapoint.__class__.__name__
        self.speclog.debug("adding datapoint of type %s" % type_)

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

