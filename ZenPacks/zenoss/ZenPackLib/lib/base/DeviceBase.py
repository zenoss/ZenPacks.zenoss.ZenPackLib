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

    def getStatus(self, statusclass="/Status/*", **kwargs):
        """Return status number for this device.

        The status number is the number of critical events associated
        with this device. This includes only events tagger with the
        device's UUID, and not events affecting components of the
        device.

        None is returned when the device's status is unknown because it
        isn't being monitored, or because there was an error retrieving
        its events.

        This method is overridden here to provide a simpler default
        meaning for "down". By default any critical severity event that
        is in either the new or acknowledged state in the /Status event
        class and is tagged with the device's UUID indicates that the
        device is down. An alternate event class (statusclass) can be
        provided, which is what would be done by the device's
        getPingStatus and getSnmpStatus methods.

        A key different between this methods behavior vs. that of the
        Device.getStatus method it overrides is that warning and error
        events are not considered as affecting the device's status.

        """
        if not self.monitorDevice():
            return None

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
