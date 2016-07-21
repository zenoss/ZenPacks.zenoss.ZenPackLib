from .SpecParams import SpecParams
from .ZPropertySpecParams import ZPropertySpecParams
from .ClassSpecParams import ClassSpecParams
from .DeviceClassSpecParams import DeviceClassSpecParams
from ..spec.RelationshipSchemaSpec import RelationshipSchemaSpec
from ..spec.ZenPackSpec import ZenPackSpec


class ZenPackSpecParams(SpecParams, ZenPackSpec):
    def __init__(self, name, zProperties=None, class_relationships=None, classes=None, device_classes=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

        self.zProperties = self.specs_from_param(
            ZPropertySpecParams, 'zProperties', zProperties, leave_defaults=True)

        self.class_relationships = []
        if class_relationships:
            if not isinstance(class_relationships, list):
                raise ValueError("class_relationships must be a list, not a %s" % type(class_relationships))

            for rel in class_relationships:
                self.class_relationships.append(RelationshipSchemaSpec(self, **rel))

        self.classes = self.specs_from_param(
            ClassSpecParams, 'classes', classes, leave_defaults=True)

        self.device_classes = self.specs_from_param(
            DeviceClassSpecParams, 'device_classes', device_classes, leave_defaults=True)


