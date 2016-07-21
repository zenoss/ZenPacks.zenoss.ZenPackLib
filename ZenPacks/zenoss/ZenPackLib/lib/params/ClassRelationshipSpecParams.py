from .SpecParams import SpecParams
from ..spec.ClassRelationshipSpec import ClassRelationshipSpec


class ClassRelationshipSpecParams(SpecParams, ClassRelationshipSpec):
    def __init__(self, class_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
