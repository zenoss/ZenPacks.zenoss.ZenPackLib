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
            dcspecparam = self._v_specparams.device_classes.get(dcname)
            deviceclass = dcspec.get_organizer(app.zport.dmd)

            for mtname, mtspec in dcspec.templates.iteritems():
                mtspecparam = dcspecparam.templates.get(mtname)
                self.update_object(app, deviceclass, 'rrdTemplates', mtname, mtspec, mtspecparam)

        # Load event classes
        for ecname, ecspec in self.event_classes.iteritems():
            ec_org = ecspec.create_organizer(app.zport.dmd)

        # Create Process Classes
        for psname, psspec in self.process_class_organizers.iteritems():
            ps_org = psspec.create_organizer(app.zport.dmd)

        self.post_install(app)

    def validate_install(self, app):
        """Return dictionary containing installation status of created objects"""

        installed = {'device_classes': {}}
        for dcname, dcspec in self.device_classes.iteritems():
            installed['device_classes'][dcname] = {'templates': {}}
            installed['device_classes'][dcname].update(
                dcspec.is_installed_dict(app.zport.dmd))

            for mtname, mtspec in dcspec.templates.iteritems():
                installed['device_classes'][dcname]['templates'][
                    mtname] = mtspec.validate_install(app.zport.dmd)

        return installed

    def post_install(self, app):
        """
        Check previously installed ZenPacks for objects that 
        can now be installed if new depenencies are met
        """
        zpl_zenpacks = self.get_zpl_zenpacks(app)
        for zp in zpl_zenpacks:
            installed = zp.validate_install(app)
            self.LOG.debug(
                "Checking %s ZenPack for newly available capabilities",
                zp.id)
            for dc_name, dc_data in installed.get(
                'device_classes', {}).items():
                dc_spec = zp.device_classes.get(dc_name)
                for mt_name, mt_data in dc_data.get(
                    'templates', {}).items():
                    mt_spec = dc_spec.templates.get(mt_name)
                    mt = mt_spec.get_object(app.zport.dmd)
                    if not mt:
                        continue
                    for th_name, th_data in mt_data.get(
                        'thresholds').items():
                        if th_data.get('installed'):
                            continue
                        th_spec = mt_spec.thresholds.get(th_name)
                        self.LOG.debug(
                            "Checking if threshold %s can be installed", th_name)
                        th_spec.create(mt_spec, mt)

    def get_zpl_zenpacks(self, app):
        """Return a list of installed ZPL ZenPacks"""
        return [p for p in app.zport.dmd.ZenPackManager.packs()
                if hasattr(p, '_v_specparams') and p.id != self.id]

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
                deviceclass = dcspec.get_organizer(app.zport.dmd)
                if not deviceclass:
                    self.LOG.warning(
                        "DeviceClass {} has been removed at some point "
                        "after the {} ZenPack was installed.  It will be "
                        "reinstated if this ZenPack is upgraded or reinstalled".format(
                        dcname, self.id))
                    continue

                for orig_mtname, orig_mtspec in dcspec.templates.iteritems():
                    # attempt to find an existing template
                    template = self.get_object(deviceclass, 'rrdTemplates', orig_mtname)
                    # back it up if it exists
                    if template:
                        self.get_or_create_backup(deviceclass, 'rrdTemplates', orig_mtname)
                    else:
                        self.LOG.warning(
                            "Monitoring template {}/{} has been removed at some point "
                            "after the {} ZenPack was installed.  It will be "
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
                dcspec.remove_organizer(app.zport.dmd, self)

            for ecname, ecspec in self.event_classes.iteritems():
                ecspec.remove_organizer(app.zport.dmd, self)

            for pcname, pcspec in self.process_class_organizers.iteritems():
                pcspec.remove_organizer_or_subs(
                    app.zport.dmd, 'process_classes', 'removeOSProcessClasses', self)

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def update_object(self, app, parent, relname, object_id, spec, specparam):
        """Compare object to be installed to existing objects, optionally creating the new object"""
        # this backup should exist if previous installed version of this zenpack uses ZPL 2.0
        backup_target = self.get_object(parent, relname, "{}-backup".format(object_id))
        # otherwise this is the existing object pre-zpl 2.0
        existing_target = self.get_object(parent, relname, object_id)
        # we'll use whichever we get
        candidate_target = backup_target or existing_target

        if not candidate_target:
            # if no candidate target is found, then this is new to this zenpack
            spec.create(app.zport.dmd)
        else:
            # check the difference between our candidate and the new spec
            # and back up the candidate if there is a difference
            diff = self.check_diff(app, parent, relname, candidate_target, spec, specparam)
            # if there was a difference, keep the backup and create the new template
            if diff:
                spec.create(app.zport.dmd)
            else:
                # otherwise just return the backup template to its original location
                if backup_target:
                    self.move_object(parent, relname, backup_target.id, object_id)
                # or in the case of the existing object, leave it alone
                else:
                    pass

    def check_diff(self, app, parent, relname, object, spec, specparam):
        """Return True if object has changed creating preupgrade backup if needed"""
        diff = self.object_changed(app, object, spec, specparam)
        if not diff:
            return False
        # preserve the existing object if different
        time_str = time.strftime("%Y%m%d%H%M", time.localtime())
        preupgrade_id = "{}-preupgrade-{}".format(object.id, time_str)
        self.move_object(parent, relname, object.id, preupgrade_id)
        LOG.info("Existing object {}/{} differs from "
                 "the newer version included with the {} ZenPack.  "
                 "The existing object will be "
                 "backed up to '{}'.  Please review and reconcile any "
                 "local changes before deleting the backup: \n{}".format(
                    parent.getDmdKey(), spec.name, self.id, preupgrade_id, diff))
        return True

    def get_object(self, parent, relname, object_id):
        """Attempt to retrieve an object given its id, parent instance, and relation name"""
        rel = getattr(parent, relname, None)
        if rel:
            try:
                return rel._getOb(object_id)
            except AttributeError:
                pass
        return None

    def get_or_create_backup(self, parent, relname, object_id):
        """Create and return a backup of object"""
        backup_id = "{}-backup".format(object_id)
        backup_target = self.get_object(parent, relname, backup_id)
        # return or delete the template if it already exists
        # which could occur if zenpack installation fails and is re-attempted
        if backup_target:
            backup_target.getPrimaryParent()._delObject(backup_target.id)
        # move the object to its backup
        self.rename_object(parent, relname, object_id, backup_id)
        return self.get_object(parent, relname, backup_id)

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

    def object_changed_safe(self, object, specparam):
        """Compare new and old objects without prototype creation 
        or risk to existing Zope objects
        """
        # get YAML representation of object
        object_yaml = yaml.dump(specparam.fromObject(object), Dumper=Dumper)
        # get YAML representation from SpecPararm
        proto_yaml = yaml.dump(specparam, Dumper=Dumper)
        return self.get_yaml_diff(object_yaml, proto_yaml)

    @classmethod
    def get_yaml_diff(cls, yaml_existing, yaml_new):
        """Return diff between YAML files"""
        if yaml_existing != yaml_new:
            lines_existing = [x + '\n' for x in yaml_existing.split('\n')]
            lines_new = [x + '\n' for x in yaml_new.split('\n')]
            return ''.join(difflib.unified_diff(lines_existing, lines_new))
        return None

    def create_device_classes(self, app):
        """
        Device classes must be created in alphanumeric order to
        prevent children from implicitly creating their parents. When
        children implicitly create their parents, zProperty values
        won't get set on the parents.
        """
        for dcname in sorted(self.device_classes):
            dcspec = self.device_classes[dcname]
            device_class = dcspec.create_organizer(app.zport.dmd)
            if not device_class:
                self.LOG.warn("Device Class (%s) not found", dcspec.path)
                continue

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
