##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..spec.Spec import Spec
from ..helpers.ZenPackLibLog import DEFAULTLOG


class SpecParams(object):
    """SpecParams"""

    LOG = DEFAULTLOG

    def __init__(self, **kwargs):
        # Initialize with default values
        self.LOG = kwargs.get('zplog', DEFAULTLOG)

        params = self.__class__.init_params()
        for param in params:
            if 'default' in params[param]:
                setattr(self, param, params[param]['default'])

        # Overlay any named parameters
        self.__dict__.update(kwargs)

    @classmethod
    def init_params(cls):
        # Pull over the params for the underlying Spec class,
        # correcting nested Specs to SpecsParams instead.
        try:
            spec_base = [x for x in cls.__bases__ if issubclass(x, Spec)][0]
        except Exception:
            raise Exception("Spec Base Not Found for %s" % cls.__name__)

        params = spec_base.init_params()
        for p in params:
            params[p]['type'] = params[p]['type'].replace("Spec)", "SpecParams)")

        return params