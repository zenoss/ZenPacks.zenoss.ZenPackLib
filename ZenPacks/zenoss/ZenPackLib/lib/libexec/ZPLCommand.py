##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
import os.path
import re
import inspect
import sys
import yaml
import collections
import logging
from optparse import OptionGroup

import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

from Acquisition import aq_base
from Products.ZenModel.ZenPack import ZenPack
from Products.ZenUtils.ZenScriptBase import ZenScriptBase

from ..functions import create_module, LOG
from ..spec.Spec import Spec
from ..params.ZenPackSpecParams import ZenPackSpecParams
from ..params.DeviceClassSpecParams import DeviceClassSpecParams
from ..params.RRDTemplateSpecParams import RRDTemplateSpecParams
from ..resources.templates import SETUP_PY
from ..helpers.WarningLoader import WarningLoader
from ..helpers.Dumper import Dumper
from ..helpers.Loader import Loader
from ..helpers.utils import optimize_yaml


class ZPLCommand(ZenScriptBase):
    '''ZPLCommand'''
    
    def __init__(self, noopts=0, app=None, connect=False, version=None):
        ''''''
        if not version:
            from ZenPacks.zenoss.ZenPackLib import zenpacklib
            version = zenpacklib.__version__
        self.version = version
        ZenScriptBase.__init__(self, noopts, app, connect)

    def buildOptions(self):
        ''''''
        ZenScriptBase.buildOptions(self)
        # remove unneeded
        self.parser.remove_option('-C')
        self.parser.remove_option('--genconf')
        self.parser.remove_option('--genxmltable')
        self.parser.remove_option('--genxmlconfigs')
        self.parser.option_groups = []
        self.parser.usage = "%prog [options] [FILENAME|ZENPACK|DEVICE]"
        self.parser.version = self.version
        
        group = OptionGroup(self.parser, "ZenPack Conversion")
        group.add_option("-t", "--dump-templates",
                    dest="dump",
                    action="store_true",
                    help="export existing monitoring templates to YAML")
        group.add_option("-y", "--yaml-convert",
                    dest="convert",
                    action="store_true",
                    help="convert existing ZenPack to YAML")
        self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "New ZPL ZenPacks")
        group.add_option("-c", "--create",
                    dest="create",
                    action="store_true",
                    help="Create a new ZenPack source directory")
        self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "ZenPack Development")
        group.add_option("-l", "--lint",
                    dest="lint",
                    action="store_true",
                    help="check zenpack.yaml syntax for errors")
        group.add_option("-o", "--optimize",
                    dest="optimize",
                    action="store_true",
                    help="optimize zenpack.yaml format and DEFAULTS")
        group.add_option("-d", "--diagram",
                    dest="diagram",
                    action="store_true",
                    help="print YUML (http://yuml.me/) class diagram source based on zenpack.yaml")
        self.parser.add_option_group(group)

        self.parser.add_option("-p", "--paths",
                    dest="paths",
                    action="store_true",
                    help="print possible facet paths for a given device and whether currently filtered.")

    def is_valid_file(self):
        '''Determine if supplied file is valid'''
        errorMessage = ''
        valid = False
        if not os.path.exists(self.options.filename):
            errorMessage = ('WARN: unable to find file {filename}').format(
                filename=self.options.filename,
            )
        else:
            try:
                file = open(self.options.filename)
                valid = True
            except IOError as e:
                errorMessage = ('WARN: unable to read file {filename} '
                    '-- skipping. ({exceptionName}: {exception})').format(
                    filename=self.options.filename,
                    exceptionName=e.__class__.__name__,
                    exception=e
                )
        return (valid, errorMessage)

    def is_valid_zenpack(self):
        '''Determine if ZenPack is valid'''
        self.connect()
        self.app = self.dmd
        zenpack = self.dmd.ZenPackManager.packs._getOb(self.options.zenpack)
        if zenpack is None:
            return False
        return True

    def parseOptions(self):
        """
        Uses the optparse parse previously populated and performs common options.
        """

        if self.noopts:
            args = []
        else:
            args = self.inputArgs

        (self.options, self.args) = self.parser.parse_args(args=args)
        self.options.filename = None
        self.options.zenpack = None
        self.options.device = None
        # check that necessary options are supplied
        # requires filename
        if len(self.args) != 1:
            self.parser.print_help()
            self.parser.exit(1)

        if self.options.lint or self.options.diagram or self.options.optimize:

            self.parser.usage = "%prog [options] FILENAME"
            if len(self.args) != 1:
                self.parser.error('No filename given')

            # set filename if given
            self.options.filename = self.args[0]
            # check validity of file
            is_valid, msg = self.is_valid_file()
            if not is_valid:
                self.parser.error(msg)

        if self.options.convert or self.options.dump or self.options.create:
            self.parser.usage = "%prog [options] ZENPACKNAME"
            if len(self.args) != 1:
                self.parser.error('No ZenPack given')

            self.options.zenpack = self.args[0]

        if self.options.paths:
            self.parser.usage = "%prog [options] DEVICE"
            if len(self.args) != 1:
                self.parser.error('No device given')
            self.options.device = self.args[0]

    def run(self):
        ''''''
        if self.options.convert or self.options.dump:
            if not self.is_valid_zenpack():
                self.parser.error('{} was not found'.format(self.options.zenpack))

        if self.options.create:
            self.create_zenpack_srcdir(self.options.zenpack)

        elif self.options.convert:
             self.py_to_yaml(self.options.zenpack)

        elif self.options.dump:
            self.dump_templates(self.options.zenpack)

        elif self.options.lint:
            self.lint(self.options.filename)

        elif self.options.optimize:
            self.optimize(self.options.filename)

        elif self.options.diagram:
            self.class_diagram('yuml', self.options.filename)

        elif self.options.paths:
            self.list_paths()

    def optimize(self, filename):
        '''return formatted YAML with DEFAULTS optimized'''
        try:
            new_yaml = optimize_yaml(filename)
            print new_yaml
        except Exception, e:
            LOG.exception(e)

    def lint(self, filename):
        '''parse YAML file and check syntax'''
        with open(filename, 'r') as file:
            linecount = len(file.readlines())

        # Change our logging output format.
        logging.getLogger().handlers = []
        for logger in logging.Logger.manager.loggerDict.values():
            logger.handlers = []
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='{}:{}:0: %%(message)s'.format(filename, linecount))
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

        try:
            with open(filename, 'r') as stream:
                yaml.load(stream, Loader=WarningLoader)
        except Exception, e:
            LOG.exception(e)

    def create_zenpack_srcdir(self, zenpack_name):
        """Create a new ZenPack source directory."""
        import errno

        if os.path.exists(zenpack_name):
            sys.exit("{} directory already exists.".format(zenpack_name))

        print "Creating source directory for {}:".format(zenpack_name)

        zenpack_name_parts = zenpack_name.split('.')

        packages = reduce(
            lambda x, y: x + ['.'.join((x[-1], y))],
            zenpack_name_parts[1:],
            ['ZenPacks'])

        namespace_packages = packages[:-1]

        # Create ZenPacks.example.Thing/ZenPacks/example/Thing directory.
        module_directory = os.path.join(zenpack_name, *zenpack_name_parts)

        try:
            print "  - making directory: {}".format(module_directory)
            os.makedirs(module_directory)
        except OSError as e:
            if e.errno == errno.EEXIST:
                sys.exit("{} directory already exists.".format(zenpack_name))
            else:
                sys.exit(
                    "Failed to create {!r} directory: {}"
                    .format(zenpack_name, e.strerror))

        # Create setup.py.
        setup_py_fname = os.path.join(zenpack_name, 'setup.py')
        print "  - creating file: {}".format(setup_py_fname)
        with open(setup_py_fname, 'w') as setup_py_f:
            setup_py_f.write(
                SETUP_PY.format(
                    zenpack_name=zenpack_name,
                    namespace_packages=namespace_packages,
                    packages=packages))

        # Create MANIFEST.in.
        manifest_in_fname = os.path.join(zenpack_name, 'MANIFEST.in')
        print "  - creating file: {}".format(manifest_in_fname)
        with open(manifest_in_fname, 'w') as manifest_in_f:
            manifest_in_f.write("graft ZenPacks\n")

        # Create __init__.py files in all namespace directories.
        for namespace_package in namespace_packages:
            namespace_init_fname = os.path.join(
                zenpack_name,
                os.path.join(*namespace_package.split('.')),
                '__init__.py')

            print "  - creating file: {}".format(namespace_init_fname)
            with open(namespace_init_fname, 'w') as namespace_init_f:
                namespace_init_f.write(
                    "__import__('pkg_resources').declare_namespace(__name__)\n")

        # Create __init__.py in ZenPack module directory.
        init_fname = os.path.join(module_directory, '__init__.py')
        print "  - creating file: {}".format(init_fname)
        with open(init_fname, 'w') as init_f:
            init_f.write(
                "import os\n"
                "from ZenPacks.zenoss.ZenPackLib import zenpacklib\n\n"
                "FILE=os.path.join(os.path.dirname(__file__), 'zenpack.yaml')\n"
                "CFG = zenpacklib.load_yaml(FILE)\n")

        # Create zenpack.yaml in ZenPack module directory.
        yaml_fname = os.path.join(module_directory, 'zenpack.yaml')
        print "  - creating file: {}".format(yaml_fname)
        with open(yaml_fname, 'w') as yaml_f:
            yaml_f.write("name: {}\n".format(zenpack_name))

    def py_to_yaml(self, zenpack_name):
        '''Create YAML based on existing ZenPack'''
        self.connect()
        zenpack = self.dmd.ZenPackManager.packs._getOb(zenpack_name)
        if zenpack is None:
            LOG.error("ZenPack '{}' not found.".format(zenpack_name))
            return
        zenpack_init_py = os.path.join(os.path.dirname(inspect.getfile(zenpack.__class__)), '__init__.py')

        # create a dummy zenpacklib sufficient to be used in an
        # __init__.py, so we can capture export the data.
        spec = Spec()
        zenpacklib_module = spec.create_module("zenpacklib")
        zenpacklib_module.ZenPackSpec = type('ZenPackSpec', (dict,), {})
        zenpack_schema_module = spec.create_module("schema")
        zenpack_schema_module.ZenPack = ZenPack

        def zpl_create(self):
            zenpacklib_module.CFG = dict(self)
        zenpacklib_module.ZenPackSpec.create = zpl_create

        stream = open(zenpack_init_py, 'r')
        inputfile = stream.read()

        # tweak the input slightly.
        inputfile = re.sub(r'from .* import zenpacklib', '', inputfile)
        inputfile = re.sub(r'from .* import schema', '', inputfile)
        inputfile = re.sub(r'__file__', '"{}"'.format(zenpack_init_py), inputfile)

        # Kludge 'from . import' into working.
        import site
        site.addsitedir(os.path.dirname(zenpack_init_py))
        inputfile = re.sub(r'from . import', 'import', inputfile)

        g = dict(zenpacklib=zenpacklib_module, schema=zenpack_schema_module)
        l = dict()
        exec inputfile in g, l

        CFG = zenpacklib_module.CFG
        CFG['name'] = zenpack_name

        # convert the cfg dictionary to yaml
        specparams = ZenPackSpecParams(**CFG)

        # Dig around in ZODB and add any defined monitoring templates
        # to the spec.
        templates = self.zenpack_templatespecs(zenpack_name)
        for dc_name in templates:
            if dc_name not in specparams.device_classes:
                LOG.warning("Device class '{}' was not defined in {} - adding to the YAML file.  You may need to adjust the 'create' and 'remove' options.".format(
                            dc_name, zenpack_init_py))
                specparams.device_classes[dc_name] = DeviceClassSpecParams(specparams, dc_name)

            # And merge in the templates we found in ZODB.
            specparams.device_classes[dc_name].templates.update(templates[dc_name])

        outputfile = yaml.dump(specparams, Dumper=Dumper)

        # tweak the yaml slightly.
        outputfile = outputfile.replace("__builtin__.object", "object")
        outputfile = re.sub(r"!!float '(\d+)'", r"\1", outputfile)

        print outputfile

    def dump_templates(self, zenpack_name):
        ''''''
        self.connect()

        templates = self.zenpack_templatespecs(zenpack_name)
        if templates:
            zpsp = ZenPackSpecParams(
                zenpack_name,
                device_classes={x: {} for x in templates})

            for dc_name in templates:
                zpsp.device_classes[dc_name].templates = templates[dc_name]

            print yaml.dump(zpsp, Dumper=Dumper)

    def class_diagram(self, diagram_type, filename):
        ''''''
        with open(filename, 'r') as stream:
            CFG = yaml.load(stream, Loader=Loader)

        if diagram_type == 'yuml':
            print "# Classes"
            for cname in sorted(CFG.classes):
                print "[{}]".format(cname)

            print "\n# Inheritence"
            for cname in CFG.classes:
                cspec = CFG.classes[cname]
                for baseclass in cspec.bases:
                    if type(baseclass) != str:
                        baseclass = aq_base(baseclass).__name__
                    print "[{}]^-[{}]".format(baseclass, cspec.name)

            print "\n# Containing Relationships"
            for crspec in CFG.class_relationships:
                if crspec.cardinality == '1:MC':
                    print "[{}]++{}-{}[{}]".format(
                        crspec.left_class, crspec.left_relname,
                        crspec.right_relname, crspec.right_class)

            print "\n# Non-Containing Relationships"
            for crspec in CFG.class_relationships:
                if crspec.cardinality == '1:1':
                    print "[{}]{}-.-{}[{}]".format(
                        crspec.left_class, crspec.left_relname,
                        crspec.right_relname, crspec.right_class)
                if crspec.cardinality == '1:M':
                    print "[{}]{}-.-{}++[{}]".format(
                        crspec.left_class, crspec.left_relname,
                        crspec.right_relname, crspec.right_class)
                if crspec.cardinality == 'M:M':
                    print "[{}]++{}-.-{}++[{}]".format(
                        crspec.left_class, crspec.left_relname,
                        crspec.right_relname, crspec.right_class)
        else:
            LOG.error("Diagram type '{}' is not supported.".format(diagram_type))

    def list_paths(self):
        ''''''
        self.connect()
        device = self.dmd.Devices.findDevice(self.options.device)
        if device is None:
            LOG.error("Device '{}' not found.".format(self.options.device))
            return

        from Acquisition import aq_chain
        from Products.ZenRelations.RelationshipBase import RelationshipBase

        all_paths = set()
        included_paths = set()
        class_summary = collections.defaultdict(set)

        for component in device.getDeviceComponents():
            for facet in component.get_facets(recurse_all=True):
                path = []
                for obj in aq_chain(facet):
                    if obj == component:
                        break
                    if isinstance(obj, RelationshipBase):
                        path.insert(0, obj.id)
                all_paths.add(component.meta_type + ":" + "/".join(path) + ":" + facet.meta_type)

            for facet in component.get_facets():
                path = []
                for obj in aq_chain(facet):
                    if obj == component:
                        break
                    if isinstance(obj, RelationshipBase):
                        path.insert(0, obj.id)
                all_paths.add(component.meta_type + ":" + "/".join(path) + ":" + facet.meta_type)
                included_paths.add(component.meta_type + ":" + "/".join(path) + ":" + facet.meta_type)
                class_summary[component.meta_type].add(facet.meta_type)

        print "Paths\n-----\n"
        for path in sorted(all_paths):
            if path in included_paths:
                if "/" not in path:
                    # normally all direct relationships are included
                    print "DIRECT  " + path
                else:
                    # sometimes extra paths are pulled in due to extra_paths
                    # configuration.
                    print "EXTRA   " + path
            else:
                print "EXCLUDE " + path

        print "\nClass Summary\n-------------\n"
        for source_class in sorted(class_summary.keys()):
            print "{} is reachable from {}".format(source_class, ", ".join(sorted(class_summary[source_class])))

    def zenpack_templatespecs(self, zenpack_name):
        """Return dictionary of RRDTemplateSpecParams by device_class.

        Example return value:

            {
                '/Server/Linux': {
                    'Device': RRDTemplateSpecParams(...),
                },
                '/Server/SSH/Linux': {
                    'Device': RRDTemplateSpecParams(...),
                    'IpInterface': RRDTemplateSpecParams(...),
                },
            }

        """
        self.connect()
        zenpack = self.dmd.ZenPackManager.packs._getOb(zenpack_name, None)
        if zenpack is None:
            LOG.error("ZenPack '{}' not found.".format(zenpack_name))
            return

        # Find explicitly associated templates, and templates implicitly
        # associated through an explicitly associated device class.
        from Products.ZenModel.DeviceClass import DeviceClass
        from Products.ZenModel.RRDTemplate import RRDTemplate

        templates = []
        for packable in zenpack.packables():
            if isinstance(packable, DeviceClass):
                templates.extend(packable.getAllRRDTemplates())
            elif isinstance(packable, RRDTemplate):
                templates.append(packable)

        # Only create specs for templates that have an associated device
        # class. This prevents locally-overridden templates from being
        # included.
        specs = collections.defaultdict(dict)
        for template in templates:
            deviceClass = template.deviceClass()
            if deviceClass:
                dc_name = deviceClass.getOrganizerName()
                spec = RRDTemplateSpecParams.fromObject(template)
                specs[dc_name][template.id] = spec

        return specs

if __name__ == '__main__':
    script = ZPLCommand()
    script.run()
