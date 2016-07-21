from ..spec.Spec import Spec


class SpecParams(object):
    def __init__(self, **kwargs):
        # Initialize with default values
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