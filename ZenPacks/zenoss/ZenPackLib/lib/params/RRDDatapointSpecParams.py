##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import StringIO
from Acquisition import aq_base
from collections import OrderedDict
from ..spec.RRDDatapointSpec import RRDDatapointSpec
from .SpecParams import SpecParams


class RRDDatapointSpecParams(SpecParams, RRDDatapointSpec):
    def __init__(self, datasource_spec, name, shorthand=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.shorthand = shorthand

    @classmethod
    def fromObject(cls, datapoint):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        datapoint = aq_base(datapoint)
        sample_dp = datapoint.__class__(datapoint.id)

        for propname in ('name', 'rrdtype', 'createCmd', 'isrow', 'rrdmin',
                         'rrdmax', 'description',):
            if hasattr(sample_dp, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_dp, propname))
            if getattr(datapoint, propname, None) != getattr(sample_dp, propname, None):
                setattr(self, propname, getattr(datapoint, propname, None))

        if self.rrdmin is not None and self.rrdmin != '':
            self.rrdmin = int(self.rrdmin)
        if self.rrdmax is not None and self.rrdmax != '':
            self.rrdmax = int(self.rrdmax)

        self.aliases = {x.id: x.formula for x in datapoint.aliases()}

        self.extra_params = OrderedDict()
        for propname in [x['id'] for x in datapoint._properties]:
            if propname not in self.init_params:
                if getattr(datapoint, propname, None) != getattr(sample_dp, propname, None):
                    self.extra_params[propname] = getattr(datapoint, propname, None)

        # Shorthand support.  The use of the shorthand field takes
        # over all other attributes.  So we can only use it when the rest of
        # the attributes have default values.   This gets tricky if
        # RRDDatapoint has been subclassed, since we don't know what
        # the defaults are, necessarily.
        #
        # To do this, we actually instantiate a sample datapoint
        # using only the shorthand values, and see if the result
        # ends up being effectively the same as what we have.

        shorthand_props = {}
        shorthand = []
        self.shorthand = None
        if datapoint.rrdtype in ('GAUGE', 'DERIVE'):
            shorthand.append(datapoint.rrdtype)
            shorthand_props['rrdtype'] = datapoint.rrdtype

            if datapoint.rrdmin:
                shorthand.append('MIN_%d' % int(datapoint.rrdmin))
                shorthand_props['rrdmin'] = datapoint.rrdmin

            if datapoint.rrdmax:
                shorthand.append('MAX_%d' % int(datapoint.rrdmax))
                shorthand_props['rrdmax'] = datapoint.rrdmax

            if shorthand:
                for prop in shorthand_props:
                    setattr(sample_dp, prop, shorthand_props[prop])

                # Compare the current datapoint with the results
                # of constructing one from the shorthand syntax.
                #
                # The comparison is based on the objects.xml-style
                # xml representation, because it seems like that's really
                # the bottom line.  If they end up the same in there, then
                # I am certain that they are equivalent.

                io = StringIO.StringIO()
                datapoint.exportXml(io)
                dp_xml = io.getvalue()
                io.close()

                io = StringIO.StringIO()
                # these won't get set on the sample dp
                sample_dp.aliases = datapoint.aliases
                sample_dp._zendoc = datapoint._zendoc

                sample_dp.exportXml(io)
                sample_dp_xml = io.getvalue()
                io.close()

                # Identical, so set the shorthand.  This will cause
                # all other properties to be ignored during
                # serialization to yaml.
                if dp_xml == sample_dp_xml:
                    self.shorthand = '_'.join(shorthand)

        return self

