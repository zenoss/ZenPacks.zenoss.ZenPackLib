##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from .Spec import Spec
from .EventClassMappingSpec import EventClassMappingSpec
from ..functions import LOG


class EventClassSpec(Spec):
    """Initialize a EventClass via Python at install time."""
    def __init__(
            self,
            zenpack_spec,
            path,
            description='',
            transform='',
            create=True,
            remove=False,
            mappings=None,
            _source_location=None):
        """
          :param create: Create the EventClass with ZenPack installation, if it does not exist?
          :type create: bool
          :param remove: Remove the EventClass when ZenPack is removed?
          :type remove: bool
          :param description: Description of the EventClass
          :type description: str
          :param transform: EventClass Transformation
          :type transform: str
          :param mappings: TODO
          :type mappings: SpecsParameter(EventClassMappingSpec)
        """
        super(EventClassSpec, self).__init__(_source_location=_source_location)
        self.zenpack_spec = zenpack_spec
        self.path = path
        self.description = description
        self.transform = transform
        self.create = bool(create)
        self.remove = bool(remove)
        self.mappings = self.specs_from_param(
            EventClassMappingSpec, 'mappings', mappings)

    def instantiate(self, dmd):
        if self.create:
            try:
                dmd.Events.getOrganizer(self.path)
            except KeyError:
                LOG.info('Creating EventClass {}'.format(self.path))
                dmd.Events.createOrganizer(self.path)
        ecObject = dmd.Events.getOrganizer(self.path)
        if self.description != '':
            if not ecObject.description == self.description:
                LOG.info('Setting description on {}'.format(self.path))
                ecObject.description = self.description
        if self.transform != '':
            if not ecObject.transform == self.transform:
                LOG.info('Setting transform on {}'.format(self.path))
                ecObject.transform = self.transform
        # Flag this as a ZPL managed object, that is, one that should not be
        # exported to objects.xml  (contained objects will also be excluded)
        ecObject.zpl_managed = True
        for mapping_id, mapping_spec in self.mappings.items():
            mapping_spec.create(ecObject)
