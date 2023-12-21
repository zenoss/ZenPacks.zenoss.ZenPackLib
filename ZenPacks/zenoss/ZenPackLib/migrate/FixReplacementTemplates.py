##############################################################################
#
# Copyright (C) Zenoss, Inc. 2023, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging

from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration


LOG = logging.getLogger('zen.ZenPackLib.migrate')


class FixReplacementTemplates(ZenPackMigration):
    """
    Change from AristaBgpPeer plugin to AristaVrfBgpMap plugin
    """

    version = Version(1, 6, 0)

    def _migrateObject(self, obj):
            if obj.hasProperty('zDeviceTemplates'):
                objchanged = False
                availtempls = None
                templs = obj.zDeviceTemplates
                for templ in list(templs):
                    if templ.endswith('-replacement') or templ.endswith('-addition'):
                        if availtempls = None:
                            availtempls = [t.id for t in obj.getAvailableTemplates()]
                        base = templ.rsplit('-',1)[0]
                        if base in availtempls:
                            LOG.info("Removing template %s from %s.zDeviceTemplates", templ, obj.id)
                            templs.remove(templ)
                            if base not in templs:
                                LOG.info("Adding base template %s to %s.zDeviceTemplates", base, obj.id)
                                templs.append(base)
                        else:
                            LOG.warning("base template %s for template %s was not found, not migrating.", base, templ)
                            continue
                        objchanged = True
                if objchanged:
                    obj.setZenProperty('zCollectorPlugins', templs)

    def migrate(self, pack):
        LOG.info("fix zDeviceTemplates on /Devices and subclasses")

        )
        deviceClass = pack.dmd.Devices

        # Migrate zDeviceTemplates on Device Classes
        deviceClasses = [deviceClass]
        deviceClasses.extend(deviceClass.getSubOrganizers())
        for dc in deviceClasses:
            self._migrateObject(dc)
            for device in dc.devices():
                self._migrateObject(device)

