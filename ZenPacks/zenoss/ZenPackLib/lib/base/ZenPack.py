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

from transaction import commit
from ZODB.POSException import ConflictError

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from ..helpers.Dumper import Dumper
from ..helpers.ZenPackLibLog import ZenPackLibLog, new_log
from ..params.RRDTemplateSpecParams import RRDTemplateSpecParams
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

    def _buildDeviceRelations(self, batch=10):
        '''split device buildRelations across multiple commits'''
        count = 0

        def build_relations(d, retries=5, count=0):
            if count >= retries:
                self.LOG.error('max retries exceeded for {}'.format(d.id))
            else:
                try:
                    d.buildRelations()
                except ConflictError as e:
                    self.LOG.warn('Reattempting buildRelations() on {} ({})'.format(d.id, e))
                    self.dmd._p_jar.sync()
                    build_relations(d, retries, count + 1)
                except Exception as e:
                    self.LOG.error('buildRelations() failed for {} ({})'.format(d.id, e))

        for d in self.dmd.Devices.getSubDevicesGen():
            build_relations(d)
            count += 1
            if count % batch == 0:
                sys.stdout.write('.')
                commit()
        commit()
        self.LOG.info('Finished adding {} relationships to existing devices'.format(self.id))

    def install(self, app):
        self.createZProperties(app)

        # create device classes and set zProperties on them
        for dcname, dcspec in self.device_classes.iteritems():
            if dcspec.create:
                dcObject = self.create_device_class(app, dcspec)

            # if device class has description and protocol, register a devtype
            if dcspec.description and dcspec.protocol:
                try:
                    if (dcspec.description, dcspec.protocol) not in dcObject.devtypes:
                        self.LOG.info('Registering devtype for {}: {} ({})'.format(dcObject,
                                                                                   dcspec.protocol,
                                                                                   dcspec.description))
                        dcObject.register_devtype(dcspec.description, dcspec.protocol)
                except Exception as e:
                    self.LOG.warn('Error registering devtype for {}: {} ({})'.format(dcObject,
                                                                                     dcspec.protocol,
                                                                                     e))

        # Load objects.xml now
        super(ZenPack, self).install(app)
        if self.NEW_COMPONENT_TYPES:
            self.LOG.info('Adding {} relationships to existing devices'.format(self.id))
            self._buildDeviceRelations()

        # load monitoring templates
        for dcname, dcspec in self.device_classes.iteritems():
            for mtname, mtspec in dcspec.templates.iteritems():
                mtspec.create(self.dmd)

        # Load event classes
        for ecname, ecspec in self.event_classes.iteritems():
            ecspec.instantiate(self.dmd)

        # Create Process Classes
        for psname, psspec in self.process_class_organizers.iteritems():
            psspec.create(self.dmd)

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
                        "DeviceClass {} has been removed at some point "
                        "after the {} ZenPack was installed.  It will be "
                        "reinstated if this ZenPack is upgraded or reinstalled".format(
                        dcname, self.id))
                    continue

                for orig_mtname, orig_mtspec in dcspec.templates.iteritems():
                    try:
                        template = deviceclass.rrdTemplates._getOb(orig_mtname)
                    except AttributeError:
                        template = None

                    if template is None:
                        self.LOG.warning(
                            "Monitoring template {}/{} has been removed at some point "
                            "after the {} ZenPack was installed.  It will be "
                            "reinstated if this ZenPack is upgraded or reinstalled".format(
                            dcname, orig_mtname, self.id))
                        continue

                    # back up the template
                    newname = "{}-upgrade-{}".format(orig_mtname, int(time.time()))
                    deviceclass.rrdTemplates.manage_renameObject(template.id, newname)
                    # corresponding DeviceClassSpec
                    dc_spec = self.device_classes.get(dcname)
                    # RRDTemplateSpec
                    template_spec = dc_spec.templates.get(orig_mtname)

                    diff = self.template_changed(app, template, template_spec)
                    if diff:
                        self.LOG.info(
                            "Existing monitoring template {}/{} differs from "
                            "the newer version included with the {} ZenPack.  "
                            "The existing template will be "
                            "backed up to '{}'.  Please review and reconcile any "
                            "local changes before deleting the backup:\n{}".format(
                            dcname, orig_mtname, self.id, template.id, diff))
                    else:
                        # if unchanged, delete the backup template
                        template.getPrimaryParent()._delObject(template.id)

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
                self._buildDeviceRelations()

            for dcname, dcspec in self.device_classes.iteritems():
                if dcspec.remove:
                    self.remove_device_class(app, dcspec)

            # Remove EventClasses with remove flag set
            self.remove_organizer_or_subs(app.dmd.Events,
                                          self.event_classes,
                                          'mappings',
                                          'removeInstances')
            # Remove Process Classes/Organizers with remove flag set
            self.remove_organizer_or_subs(app.dmd.Processes,
                                          self.process_class_organizers,
                                          'process_classes',
                                          'removeOSProcessClasses')

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

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
                dmd_root.manage_deleteOrganizer(organizerPath)
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

    def template_changed(self, app, existing, new_spec):
        """
            Return True if existing template is changed from spec
        """
        diff = None
        # get spec params from object
        existing_specparams = RRDTemplateSpecParams.fromObject(existing)
        # build a dummy template based on YAML spec
        # create new template
        new_template = new_spec.create(app.dmd, False)
        new_specparams = RRDTemplateSpecParams.fromObject(new_template)
        # remove new template
        new_template.getPrimaryParent()._delObject(new_template.id)
        # dump to yaml for both specparams
        yaml_existing = yaml.dump(existing_specparams, Dumper=Dumper)
        yaml_new = yaml.dump(new_specparams, Dumper=Dumper)
        if yaml_existing != yaml_new:
            lines_existing = [x + '\n' for x in yaml_existing.split('\n')]
            lines_new = [x + '\n' for x in yaml_new.split('\n')]
            diff = ''.join(difflib.unified_diff(lines_existing, lines_new))
        return diff

    def create_device_class(self, app, dcspec):
        ''''''
        try:
            dcObject = app.dmd.Devices.getOrganizer(dcspec.path)
        except KeyError:
            self.LOG.info('Creating DeviceClass {}'.format(dcspec.path))
            dcObject = app.dmd.Devices.createOrganizer(dcspec.path)

        for zprop, value in dcspec.zProperties.iteritems():
            if dcObject.getPropertyType(zprop) is None:
                self.LOG.error("Unable to set zProperty {} on {} (undefined zProperty)".format(zprop, dcspec.path))
            else:
                self.LOG.info('Setting zProperty {} on {}'.format(zprop, dcspec.path))
                dcObject.setZenProperty(zprop, value)
        return dcObject

    def remove_device_class(self, app, dcspec):
        ''''''
        path = [p for p in dcspec.path.lstrip('/').split('/') if p != 'Devices']
        organizerPath = '/{}'.format('/'.join(['Devices'] + path))
        try:
            app.dmd.Devices.getOrganizer(organizerPath)
            try:
                app.dmd.Devices.manage_deleteOrganizer(organizerPath)
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

