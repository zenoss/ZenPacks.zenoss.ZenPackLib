from .SpecParams import SpecParams
from ..spec.ClassPropertySpec import ClassPropertySpec


class ClassPropertySpecParams(SpecParams, ClassPropertySpec):
    def __init__(self, class_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
