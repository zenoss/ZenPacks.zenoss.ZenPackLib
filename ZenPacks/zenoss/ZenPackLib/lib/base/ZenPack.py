import os
import sys
from lxml import etree
import yaml
import logging

from Products.ZenModel.ZenPack import ZenPack
from ..helpers.Dumper import Dumper
from ..functions import LOG
from ..params.RRDTemplateSpecParams import RRDTemplateSpecParams


class ZenPack(ZenPack):
    """
    ZenPack loader that handles custom installation and removal tasks.
    """
    LOG = LOG

    def __init__(self, *args, **kwargs):
        super(ZenPack, self).__init__(*args, **kwargs)
        self.LOG = kwargs.get('log', LOG)
        # Emable logging to stderr if the user sets the ZPL_LOG_ENABLE environment
        # variable to this zenpack's name.   (defaults to 'DEBUG', but
        # user may choose a different level with ZPL_LOG_LEVEL.
        if self.id in os.environ.get('ZPL_LOG_ENABLE', ''):
            levelName = os.environ.get('ZPL_LOG_LEVEL', 'DEBUG').upper()
            logLevel = getattr(logging, levelName)

            if logLevel:
                # Reconfigure the logger to ensure it goes to stderr for the
                # selected level or above.
                self.LOG.propagate = False
                self.LOG.setLevel(logLevel)
                h = logging.StreamHandler(sys.stderr)
                h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
                self.LOG.addHandler(h)
            else:
                self.LOG.error("Unrecognized ZPL_LOG_LEVEL '%s'" %
                          os.environ.get('ZPL_LOG_LEVEL'))

    # NEW_COMPONENT_TYPES AND NEW_RELATIONS will be monkeypatched in
    # via zenpacklib when this class is instantiated.

    def _buildDeviceRelations(self):
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()

    def install(self, app):
        self.createZProperties(app)

        # create device classes and set zProperties on them
        for dcname, dcspec in self.device_classes.iteritems():
            if dcspec.create:
                try:
                    self.dmd.Devices.getOrganizer(dcspec.path)
                except KeyError:
                    self.LOG.info('Creating DeviceClass %s' % dcspec.path)
                    app.dmd.Devices.createOrganizer(dcspec.path)

            dcObject = self.dmd.Devices.getOrganizer(dcspec.path)
            for zprop, value in dcspec.zProperties.iteritems():
                if dcObject.getPropertyType(zprop) is None:
                    self.LOG.error("Unable to set zProperty %s on %s (undefined zProperty)", zprop, dcspec.path)
                    continue
                self.LOG.info('Setting zProperty %s on %s' % (zprop, dcspec.path))
                dcObject.setZenProperty(zprop, value)

        # Load objects.xml now
        super(ZenPack, self).install(app)
        if self.NEW_COMPONENT_TYPES:
            self.LOG.info('Adding %s relationships to existing devices' % self.id)
            self._buildDeviceRelations()

        # load monitoring templates
        for dcname, dcspec in self.device_classes.iteritems():
            for mtname, mtspec in dcspec.templates.iteritems():
                mtspec.create(self.dmd)

    def remove(self, app, leaveObjects=False):
        if self._v_specparams is None:
            return

        from Products.Zuul.interfaces import ICatalogTool
        if leaveObjects:
            # Check whether the ZPL-managed monitoring templates have
            # been modified by the user.  If so, those changes will
            # be lost during the upgrade.
            #
            # Ideally, I would inspect self.packables() to find these
            # objects, but we do not have access to that relationship
            # at this point in the process.
            for dcname, dcspec in self._v_specparams.device_classes.iteritems():
                try:
                    deviceclass = self.dmd.Devices.getOrganizer(dcname)
                except KeyError:
                    # DeviceClass.getOrganizer() can raise a KeyError if the
                    # organizer doesn't exist.
                    deviceclass = None

                if deviceclass is None:
                    self.LOG.warning(
                        "DeviceClass %s has been removed at some point "
                        "after the %s ZenPack was installed.  It will be "
                        "reinstated if this ZenPack is upgraded or reinstalled",
                        dcname, self.id)
                    continue

                for orig_mtname, orig_mtspec in dcspec.templates.iteritems():
                    try:
                        template = deviceclass.rrdTemplates._getOb(orig_mtname)
                    except AttributeError:
                        template = None

                    if template is None:
                        self.LOG.warning(
                            "Monitoring template %s/%s has been removed at some point "
                            "after the %s ZenPack was installed.  It will be "
                            "reinstated if this ZenPack is upgraded or reinstalled",
                            dcname, orig_mtname, self.id)
                        continue

                    installed = RRDTemplateSpecParams.fromObject(template)

                    if installed != orig_mtspec:
                        import time
                        import difflib

                        lines_installed = [x + '\n' for x in yaml.dump(installed, Dumper=Dumper).split('\n')]
                        lines_orig_mtspec = [x + '\n' for x in yaml.dump(orig_mtspec, Dumper=Dumper).split('\n')]
                        diff = ''.join(difflib.unified_diff(lines_orig_mtspec, lines_installed))

                        newname = "{}-upgrade-{}".format(orig_mtname, int(time.time()))
                        self.LOG.error(
                            "Monitoring template %s/%s has been modified "
                            "since the %s ZenPack was installed.  These local "
                            "changes will be lost as this ZenPack is upgraded "
                            "or reinstalled.   Existing template will be "
                            "renamed to '%s'.  Please review and reconcile "
                            "local changes:\n%s",
                            dcname, orig_mtname, self.id, newname, diff)

                        deviceclass.rrdTemplates.manage_renameObject(template.id, newname)

        else:
            dc = app.Devices
            for catalog in self.GLOBAL_CATALOGS:
                catObj = getattr(dc, catalog, None)
                if catObj:
                    self.LOG.info('Removing Catalog %s' % catalog)
                    dc._delObject(catalog)

            if self.NEW_COMPONENT_TYPES:
                self.LOG.info('Removing %s components' % self.id)
                cat = ICatalogTool(app.zport.dmd)
                for brain in cat.search(types=self.NEW_COMPONENT_TYPES):
                    try:
                        component = brain.getObject()
                    except Exception as e:
                        self.LOG.error("Trying to remove non-existent object %s", e)
                        continue
                    else:
                        component.getPrimaryParent()._delObject(component.id)

                # Remove our Device relations additions.
                from Products.ZenUtils.Utils import importClass
                for device_module_id in self.NEW_RELATIONS:
                    Device = importClass(device_module_id)
                    Device._relations = tuple([x for x in Device._relations
                                               if x[0] not in self.NEW_RELATIONS[device_module_id]])

                self.LOG.info('Removing %s relationships from existing devices.' % self.id)
                self._buildDeviceRelations()

            for dcname, dcspec in self.device_classes.iteritems():
                if dcspec.remove:
                    organizerPath = '/Devices/' + dcspec.path.lstrip('/')
                    try:
                        app.dmd.Devices.getOrganizer(organizerPath)
                    except KeyError:
                        self.LOG.warning('Unable to remove DeviceClass %s (not found)' % dcspec.path)
                        continue

                    self.LOG.info('Removing DeviceClass %s' % dcspec.path)
                    app.dmd.Devices.manage_deleteOrganizer(organizerPath)

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def manage_exportPack(self, download="no", REQUEST=None):
        """Export ZenPack to $ZENHOME/export directory.

        Postprocess the generated xml files to remove references to ZPL-managed
        objects.
        """
        from Products.ZenModel.ZenPackLoader import findFiles

        result = super(ZenPack, self).manage_exportPack(
            download=download,
            REQUEST=REQUEST)

        for filename in findFiles(self, 'objects', lambda f: f.endswith('.xml')):
            self.filter_xml(filename)

        return result

    def filter_xml(self, filename):
        pruned = 0
        try:
            tree = etree.parse(filename)

            path = []
            context = etree.iterwalk(tree, events=('start', 'end'))
            for action, elem in context:
                if elem.tag == 'object':
                    if action == 'start':
                        path.append(elem.attrib.get('id'))

                    elif action == 'end':
                        obj_path = '/'.join(path)
                        try:
                            obj = self.dmd.getObjByPath(obj_path)
                            if getattr(obj, 'zpl_managed', False):
                                self.LOG.debug("Removing %s from %s", obj_path, filename)
                                pruned += 1

                                # if there's a comment before it with the
                                # primary path of the object, remove that first.
                                prev = elem.getprevious()
                                if '<!-- ' + repr(tuple('/'.join(path).split('/'))) + ' -->' == repr(prev):
                                    elem.getparent().remove(prev)

                                # Remove the ZPL-managed object
                                elem.getparent().remove(elem)

                        except Exception:
                            self.LOG.warning("Unable to postprocess %s in %s", obj_path, filename)

                        path.pop()

                if elem.tag == 'tomanycont':
                    if action == 'start':
                        path.append(elem.attrib.get('id'))
                    elif action == 'end':
                        path.pop()

            if len(tree.getroot()) == 0:
                self.LOG.info("Removing %s", filename)
                os.remove(filename)
            elif pruned:
                self.LOG.info("Pruning %d objects from %s", pruned, filename)
                with open(filename, 'w') as f:
                    f.write(etree.tostring(tree))
            else:
                self.LOG.debug("Leaving %s unchanged", filename)

        except Exception, e:
            self.LOG.error("Unable to postprocess %s: %s", filename, e)
