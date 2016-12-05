##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec
from .RRDTemplateSpec import RRDTemplateSpec


class DeviceClassSpec(Spec):
    """Initialize a DeviceClass via Python at install time."""

    def __init__(
            self,
            zenpack_spec,
            path,
            create=True,
            zProperties=None,
            remove=False,
            templates=None,
            description=None,
            protocol=None,
            overwrite_plugins=False,
            _source_location=None,
            zplog=None):
        """
            Create a DeviceClass Specification

            :param create: Create the DeviceClass with ZenPack installation, if it does not exist?
            :type create: bool
            :param remove: Remove the DeviceClass when ZenPack is removed?
            :type remove: bool
            :param zProperties: zProperty values to set upon this DeviceClass
            :type zProperties: dict(str)
            :param templates: TODO
            :type templates: SpecsParameter(RRDTemplateSpec)
            :param description: Description used for registering devtype
            :type description: str
            :param protocol: Protocol to use for registered devtype
            :type protocol: str
            :param overwrite_plugins: Whether to overwrite or append any given modeler plugins 
            :type overwrite_plugins: bool
        """
        super(DeviceClassSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.zenpack_spec = zenpack_spec
        self.path = path.lstrip('/')
        self.create = bool(create)
        self.remove = bool(remove)
        self.description = description
        self.protocol = protocol
        self.overwrite_plugins = overwrite_plugins

        if zProperties is None:
            self.zProperties = {}
        else:
            self.zProperties = zProperties

        self.templates = self.specs_from_param(
            RRDTemplateSpec, 'templates', templates, zplog=self.LOG)
