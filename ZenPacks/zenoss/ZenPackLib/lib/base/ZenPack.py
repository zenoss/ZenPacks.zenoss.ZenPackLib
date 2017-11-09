##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
from lxml import etree
import yaml
import difflib
import time
import sys

from Acquisition import aq_base
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from ..helpers.Dumper import Dumper
from ..helpers.ZenPackLibLog import ZenPackLibLog, new_log
from Products.ZenEvents import ZenEventClasses

LOG = new_log('zpl.ZenPack')
LOG.setLevel('INFO')
ZenPackLibLog.enable_log_stderr(LOG)

# We need to make sure we aren't removing an important/default event,
# windows/ip service, or process class on ZenPack removal
RESERVED_CLASSES = set(['/Status', '/App', '/Cmd', '/Perf',
                        '/Heartbeat', '/Unknown', '/Change', 'Processes',
                        'Services', 'WinService', 'IpService'])

for x in dir(ZenEventClasses):
    y = getattr(ZenEventClasses, x)
    if isinstance(y, str):
        RESERVED_CLASSES.add(y)


class ZenPack(ZenPackBase):
    """
    ZenPack loader that handles custom installation and removal tasks.

    NEW_COMPONENT_TYPES AND NEW_RELATIONS will be monkeypatched in
    via zenpacklib when this class is instantiated.
    """
    LOG = LOG

    def __init__(self, *args, **kwargs):
        super(ZenPack, self).__init__(*args, **kwargs)

    def _buildDeviceRelations(self, app, batch=10):
        count = 0
        for d in app.zport.dmd.Devices.getSubDevicesGen():
            d.buildRelations()
            count += 1
            if count % batch == 0:
                sys.stderr.write('.')
        if count > batch:
            sys.stderr.write('\n')
        self.LOG.info('Finished adding {} relationships to existing devices'.format(self.id))

    def install(self, app):
        self.createZProperties(app)
        self.create_device_classes(app)

        # Load objects.xml now
        super(ZenPack, self).install(app)
        if self.NEW_COMPONENT_TYPES:
            self.LOG.info('Adding {} relationships to existing devices'.format(self.id))
            self._buildDeviceRelations(app)

        # load monitoring templates
        for dcname, dcspec in self.device_classes.iteritems():
            deviceclass = dcspec.get_organizer(app.zport.dmd)

            for mtname, mtspec in dcspec.templates.iteritems():
                mtspec.create(app.zport.dmd)

        # Load event classes
        for ecname, ecspec in self.event_classes.iteritems():
            ecspec.instantiate(app.zport.dmd)

        # Create Process Classes
        for psname, psspec in self.process_class_organizers.iteritems():
            psspec.create(app.zport.dmd)

    def remove(self, app, leaveObjects=False):
        if self._v_specparams is None:
            return

        from Products.Zuul.interfaces import ICatalogTool
        if leaveObjects:
            # Check whether the ZPL-managed monitoring templates have
            # been modified by the user.  If so, those changes will
            # be backed up now.
            for dcname, dcspec in self.device_classes.iteritems():
                dcspecparam = self._v_specparams.device_classes.get(dcname)
                deviceclass = dcspec.get_organizer(app.zport.dmd)
                if not deviceclass:
                    self.LOG.warning(
                        "DeviceClass {} has been removed at some point "
                        "after the {} ZenPack was installed.  It will be "
                        "reinstated if this ZenPack is upgraded or reinstalled".format(
                        dcname, self.id))
                    continue

                for orig_mtname, orig_mtspec in dcspec.templates.iteritems():
                    orig_mtspecparam = dcspecparam.templates.get(orig_mtname)
                    # attempt to find an existing template in zope
                    template = self.get_object(deviceclass, 'rrdTemplates', orig_mtname)
                    if template:
                        self.backup_user_changes(app, deviceclass, 'rrdTemplates',
                                                 orig_mtname, orig_mtspec, orig_mtspecparam)
                    else:
                        self.LOG.warning(
                            "Monitoring template {}/{} has been removed after installation "
                            "of the {} ZenPack.  It will be "
                            "reinstated if this ZenPack is upgraded or reinstalled".format(
                            dcname, orig_mtname, self.id))

        else:
            dc = app.Devices
            for catalog in self.GLOBAL_CATALOGS:
                catObj = getattr(dc, catalog, None)
                if catObj:
                    self.LOG.info('Removing Catalog {}'.format(catalog))
                    dc._delObject(catalog)

            if self.NEW_COMPONENT_TYPES:
                self.LOG.info('Removing {} components'.format(self.id))
                cat = ICatalogTool(app.zport.dmd)
                for brain in cat.search(types=self.NEW_COMPONENT_TYPES):
                    try:
                        component = brain.getObject()
                    except Exception as e:
                        self.LOG.error("Trying to remove non-existent object {}".format(e))
                        continue
                    else:
                        component.getPrimaryParent()._delObject(component.id)

                # Remove our Device relations additions.
                from Products.ZenUtils.Utils import importClass
                for device_module_id in self.NEW_RELATIONS:
                    Device = importClass(device_module_id)
                    Device._relations = tuple([x for x in Device._relations
                                               if x[0] not in self.NEW_RELATIONS[device_module_id]])

                self.LOG.info('Removing {} relationships from existing devices.'.format(self.id))
                self._buildDeviceRelations(app)

            for dcname, dcspec in self.device_classes.iteritems():
                if dcspec.remove:
                    self.remove_device_class(app, dcspec)

            # Remove EventClasses with remove flag set
            self.remove_organizer_or_subs(app.zport.dmd.Events,
                                          self.event_classes,
                                          'mappings',
                                          'removeInstances')
            # Remove Process Classes/Organizers with remove flag set
            self.remove_organizer_or_subs(app.zport.dmd.Processes,
                                          self.process_class_organizers,
                                          'process_classes',
                                          'removeOSProcessClasses')

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def backup_user_changes(self, app, parent, relname, object_id, spec, specparam):
        """
        Compare existing object to the reference spec generated object.  Report and 
        create a backup if they differ.
        """
        # check the difference between our candidate and the new spec
        # and back up the candidate if there is a difference
        object = self.get_object(parent, relname, object_id)
        diff = self.object_changed(app, object, spec, specparam)
        # if they differ, create a backup
        if diff:
            backup = self.get_or_create_backup(parent, relname, object_id)
            LOG.info("Existing object {}/{} differs from "
                     "the version provided by the {} ZenPack.  "
                     "The existing object will be "
                     "backed up to '{}'.  Please review and reconcile any "
                     "local changes before deleting the backup: \n{}".format(
                     parent.getDmdKey(), spec.name, self.id, backup.id, diff))

    def get_or_create_backup(self, parent, relname, object_id):
        """
        Create and return a backup of object given a parent zope object,    
        a relation name, and a target object id
        """
        backup_id = "{}-backup".format(object_id)
        backup_target = self.get_object(parent, relname, backup_id)
        # return or delete the template if it already exists
        # which could occur if zenpack installation fails and is re-attempted
        if backup_target:
            backup_target.getPrimaryParent()._delObject(backup_target.id)
        # move the object to its backup
        self.rename_object(parent, relname, object_id, backup_id)
        return self.get_object(parent, relname, backup_id)

    def get_object(self, parent, relname, object_id):
        """Attempt to retrieve an object given its id, parent instance, and relation name"""
        rel = getattr(parent, relname, None)
        if rel:
            try:
                return rel._getOb(object_id)
            except AttributeError:
                pass
        return None

    def rename_object(self, parent, relname, source_id, dest_id):
        """execute manage_renameObject and log exceptions"""
        rel = getattr(parent, relname, None)
        if rel:
            try:
                rel.manage_renameObject(source_id, dest_id)
            except Exception as e:
                LOG.warn("Could not move template {}/{} to {}/{} ({})".format(parent.getDmdKey(), source_id,
                                                                              parent.getDmdKey(), dest_id,
                                                                              e))
        else:
            LOG.warn("Cannot rename {} on nonexistent relation {}".format(source_id, relname))

    def move_object(self, parent, relname, source_id, dest_id):
        """Move object and overwrite if destination exists"""
        # check if destination object exists already
        dest_object = self.get_object(parent, relname, dest_id)
        if dest_object:
            dest_object.getPrimaryParent()._delObject(dest_object.id)

        source_object = self.get_object(parent, relname, source_id)
        if source_object:
            self.rename_object(parent, relname, source_id, dest_id)

    def remove_organizer_or_subs(self, dmd_root, classes, sub_class, remove_name):
        '''Remove the organizer or subclasses within an organizer
        Used for event classes, process classes, windows services
        The specs should use path to describe the organizer name/path
        For subclasses, use klass_string for the class type name
        Also be sure to set zpl_managed in the specs
        '''
        for cname, cspec in classes.iteritems():
            organizerPath = cspec.path
            try:
                organizer = dmd_root.getOrganizer(organizerPath)
            except KeyError:
                self.LOG.warning('Unable to find {} {}'.format(dmd_root.__class__.__name__, cspec.path))
                continue
            if cspec.remove and hasattr(organizer, 'zpl_managed') and organizer.zpl_managed:
                # make sure the organizer is zpl_managed before we try and delete it
                # also double-check that we do not remove anything important like /Status or Processes
                if organizerPath in RESERVED_CLASSES:
                    continue
                self.LOG.info('Removing {} {}'.format(organizer.__class__.__name__, cspec.path))
                dmd_root.manage_deleteOrganizer(organizer.getDmdKey())
            else:
                sub_classes = getattr(cspec, sub_class, {})
                remove_func = getattr(organizer, remove_name, None)
                if not remove_func:
                    continue
                for subclass_id, subclass_spec in sub_classes.items():
                    if subclass_spec.remove:
                        preppedId = organizer.prepId(subclass_id)
                        # make sure object is zpl managed
                        obj = organizer.findObject(preppedId)
                        if getattr(obj, 'zpl_managed', False):
                            self.LOG.info('Removing {} {} @ {}'.format(subclass_spec.klass_string, subclass_id, cspec.path))
                            remove_func(preppedId)

    def object_changed(self, app, object, spec, specparam):
        """Compare new and old objects with prototype creation"""
        # get YAML representation of object
        object_yaml = yaml.dump(specparam.fromObject(object), Dumper=Dumper)
        # get YAML representation of prototype
        proto_id = '{}-new'.format(spec.name)
        proto_object = spec.create(app.zport.dmd, False, proto_id)
        proto_object_param = specparam.fromObject(proto_object)
        proto_object_yaml = yaml.dump(proto_object_param, Dumper=Dumper)
        spec.remove(app.zport.dmd, proto_id)
        return self.get_yaml_diff(object_yaml, proto_object_yaml)

    @classmethod
    def get_yaml_diff(cls, yaml_existing, yaml_new):
        """Return diff between YAML files"""
        if yaml_existing != yaml_new:
            lines_existing = [x + '\n' for x in yaml_existing.split('\n')]
            lines_new = [x + '\n' for x in yaml_new.split('\n')]
            return ''.join(difflib.unified_diff(lines_existing, lines_new))
        return None

    def create_device_classes(self, app):
        """Create device classes. Set their zProperties and devtypes."""
        for dcname in sorted(self.device_classes):
            # Device classes must be created in alphanumeric order to
            # prevent children from implicitly creating their parents. When
            # children implicitly create their parents, zProperty values
            # won't get set on the parents.
            dcspec = self.device_classes[dcname]

            if dcspec.create:
                self.create_device_class(app, dcspec)
            else:
                device_class = dcspec.get_organizer(app.zport.dmd)
                if not device_class:
                    self.LOG.warn(
                        "Device Class (%s) not found",
                        dcspec.path)

    def create_device_class(self, app, dcspec):
        """Create and return a DeviceClass. Set zProperties and devtypes.

        zProperties and devtypes will only be set if the device class
        doesn't already exist. This is done to prevent overwriting of user
        customizations on upgrade.

        """
        dcObject = dcspec.get_organizer(app.zport.dmd)
        if dcObject:
            self.LOG.debug(
                "Existing %s device class - not overwriting properties",
                dcspec.path)

            return dcObject

        self.LOG.debug("Creating %s device class", dcspec.path)
        dcObject = app.zport.dmd.Devices.createOrganizer(dcspec.path)

        # Set zProperties.
        for zprop, value in dcspec.zProperties.iteritems():
            if dcObject.getPropertyType(zprop) is None:
                self.LOG.error(
                    "Unable to set zProperty %s on %s (undefined zProperty)",
                    zprop, dcspec.path)
            else:
                self.LOG.debug(
                    "Setting zProperty %s to %r on %s",
                    zprop, value, dcspec.path)

                # We want to explicitly set the value even if it's the same as
                # what's being acquired. This is why aq_base is required.
                aq_base(dcObject).setZenProperty(zprop, value)

        # Register devtype.
        if dcObject and dcspec.description and dcspec.protocol:
            self.LOG.debug(
                "Registering devtype for %s: %s (%s)",
                dcspec.path,
                dcspec.protocol,
                dcspec.description)

            try:
                # We want to explicitly set the value even if it's the same as
                # what's being acquired. This is why aq_base is required.
                aq_base(dcObject).register_devtype(
                    dcspec.description,
                    dcspec.protocol)
            except Exception as e:
                self.LOG.warn(
                    "Error registering devtype for %s: %s (%s)",
                    dcspec.path,
                    dcspec.protocol,
                    e)

        return dcObject

    def remove_device_class(self, app, dcspec):
        """Remove a DeviceClass"""
        path = [p for p in dcspec.path.lstrip('/').split('/') if p != 'Devices']
        organizerPath = '/{}'.format('/'.join(['Devices'] + path))
        try:
            app.zport.dmd.Devices.getOrganizer(organizerPath)
            try:
                app.zport.dmd.Devices.manage_deleteOrganizer(organizerPath)
            except Exception as e:
                self.LOG.error('Unable to remove DeviceClass {} ({})'.format(dcspec.path, e))
        except KeyError:
            self.LOG.warning('Unable to remove DeviceClass {} (not found)'.format(dcspec.path))

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
                                self.LOG.debug("Removing {} from {}".format(obj_path, filename))
                                pruned += 1

                                # if there's a comment before it with the
                                # primary path of the object, remove that first.
                                prev = elem.getprevious()
                                if '<!-- ' + repr(tuple('/'.join(path).split('/'))) + ' -->' == repr(prev):
                                    elem.getparent().remove(prev)

                                # Remove the ZPL-managed object
                                elem.getparent().remove(elem)

                        except Exception:
                            self.LOG.warning("Unable to postprocess {} in {}".format(obj_path, filename))

                        path.pop()

                if elem.tag == 'tomanycont':
                    if action == 'start':
                        path.append(elem.attrib.get('id'))
                    elif action == 'end':
                        path.pop()

            if len(tree.getroot()) == 0:
                self.LOG.info("Removing {}".format(filename))
                os.remove(filename)
            elif pruned:
                self.LOG.info("Pruning {} objects from {}".format(pruned, filename))
                with open(filename, 'w') as f:
                    f.write(etree.tostring(tree))
            else:
                self.LOG.debug("Leaving {} unchanged".format(filename))

        except Exception, e:
            self.LOG.error("Unable to postprocess {}: {}".format(filename, e))
