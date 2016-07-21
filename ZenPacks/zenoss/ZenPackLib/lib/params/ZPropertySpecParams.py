from .SpecParams import SpecParams
from ..spec.ZPropertySpec import ZPropertySpec

class ZPropertySpecParams(SpecParams, ZPropertySpec):
    def __init__(self, zenpack_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

