##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products import Zuul
from zenoss.protocols.protobufs.zep_pb2 import (
    STATUS_NEW, STATUS_ACKNOWLEDGED,
    SEVERITY_CRITICAL,
    )
from .ModelBase import ModelBase


class DeviceBase(ModelBase):

    """First superclass for zenpacklib types created by DeviceTypeFactory.

    Contains attributes that should be standard on all ZenPack Device
    types.

    """

    def getStatus(self, statusclass=None, **kwargs):
        """Return status number for this device.

        The status number is the number of critical events associated
        with this device. This includes only events tagger with the
        device's UUID, and not events affecting components of the
        device.

        None is returned when the device's status is unknown because it
        isn't being monitored, or because there was an error retrieving
        its events.

        By default any critical severity event that is in either the new or
        acknowledged state in the event class that set in zStatusEventClass
        (if we don't have this property, use /Status/* class instead)
        property and is tagged with the device's UUID indicates that the
        device is down. An alternate event class (statusclass) can be
        provided, which is what would be done by the device's
        getPingStatus and getSnmpStatus methods.

        """
        if not self.monitorDevice():
            return None

        if statusclass is None:
            statusclass = getattr(self, 'zStatusEventClass', '/Status/*')

        zep = Zuul.getFacade("zep", self.dmd)
        try:
            event_filter = zep.createEventFilter(
                tags=[self.getUUID()],
                element_sub_identifier=[""],
                severity=[SEVERITY_CRITICAL],
                status=[STATUS_NEW, STATUS_ACKNOWLEDGED],
                event_class=filter(None, [statusclass]))

            result = zep.getEventSummaries(0, filter=event_filter, limit=0)
        except Exception:
            return None

        return int(result['total'])

    def getRRDTemplates(self):
        """Return list of templates to bind to this device.

        Support user-defined *-replacement and *-addition monitoring
        templates that can replace or augment the standard templates.

        """
        templates = []

        for template in super(ModelBase, self).getRRDTemplates():
            template_name = template.titleOrId()

            if template_name.endswith('-replacement') or \
                    template_name.endswith('-addition'):
                continue

            replacement = self.getRRDTemplateByName(
                '{}-replacement'.format(template_name))

            if replacement and replacement not in templates:
                templates.append(replacement)
                self.setZenProperty(
                    'zDeviceTemplates',
                    self.zDeviceTemplates + [replacement.titleOrId()])
            else:
                templates.append(template)

            addition = self.getRRDTemplateByName(
                '{}-addition'.format(template_name))

            if addition and addition not in templates:
                templates.append(addition)
                self.setZenProperty(
                    'zDeviceTemplates',
                    self.zDeviceTemplates + [addition.titleOrId()])

        return templates

    def getAvailableTemplates(self):
        """
        Returns all available templates for this device

        Support user-defined *-replacement monitoring templates
        that can replace or augment the standard templates.

        """
        templates = super(ModelBase, self).getAvailableTemplates()
        # Filter out any templates that have been 'replaced'
        filteredTemplates = list(templates)
        for t in templates:
            tName = t.titleOrId()
            if tName.endswith("-replacement"):
                tReplacedName = tName.replace('-replacement', '')
                tReplaced = self.getRRDTemplateByName(tReplacedName)
                if tReplaced:
                    filteredTemplates.remove(tReplaced)
        return filteredTemplates

