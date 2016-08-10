from .SpecParams import SpecParams
from .RRDTemplateSpecParams import RRDTemplateSpecParams
from ..spec.DeviceClassSpec import DeviceClassSpec


class DeviceClassSpecParams(SpecParams, DeviceClassSpec):
    def __init__(self, zenpack_spec, path, zProperties=None, templates=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.path = path
        self.zProperties = zProperties
        self.templates = self.specs_from_param(
            RRDTemplateSpecParams, 'templates', templates, log=self.LOG)
