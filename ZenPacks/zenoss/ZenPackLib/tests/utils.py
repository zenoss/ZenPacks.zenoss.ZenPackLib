#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" 
    Basic Unit test utilizing ZPLTestHarness
"""
import io
import yaml
import os
import subprocess
import logging
from Products.ZenRelations.Exceptions import RelationshipExistsError
from Acquisition import aq_base
from ZenPacks.zenoss.ZenPackLib.lib.helpers.loaders import WarningLoader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.ZenPackLibLog import ZPLOG



def _add(ob, obj):
    """ override of ToManyContRelationship _add method
    """
    id = obj.id
    if ob._objects.has_key(id):
        raise RelationshipExistsError
    ob._objects[id] = aq_base(obj)
    obj = aq_base(obj).__of__(ob)
    ob.setCount()


class ClassObjectHelper(object):
    """Provide resources for instantiating ZenPackLib class objects"""
    dmd = None
    cfg = None
    device_class_objects = None
    class_objects = None
    
    def __init__(self, dmd, cfg, build=False):
        self.dmd = dmd
        self.cfg = cfg
        self.device_class_objects = {}
        self.class_objects = {}
        self.create(build)

    def create(self, build=False):
        if build:
            self.create_device_class_objects()
            self.create_class_objects()
            self.build_relations()
        
    def create_device_class_objects(self):
        """Create DMD objects for device classes and templates"""
        self.device_class_objects = {}
        for dc_name, dc_spec in self.cfg.device_classes.iteritems():
            dc_ob = self.dmd.Devices.createOrganizer(dc_spec.path)
            self.device_class_objects[dc_name] = {'ob': dc_ob, 'templates': {}}
            # set zproperties
            for zprop_name, zprop_spec in self.cfg.zProperties.iteritems():
                dc_ob._setProperty(zprop_name, zprop_spec.default)
            # create templates
            for mt_name, mt_spec in dc_spec.templates.iteritems():
                mt_ob = mt_spec.create(self.dmd, False, mt_name)
                self.device_class_objects[dc_name]['templates'][mt_name] = mt_ob

    def create_class_objects(self):
        '''return a list of object instances for ZPL classes'''
        self.class_objects = {}
        for name, spec in self.cfg.classes.items():
            ob = self.create_object(name)
            ob.buildRelations()
            self.class_objects[name] = {'spec': spec, 'ob': ob, 'cls': self.get_cls(name)}

    def build_relations(self):
        '''create relations between objects'''
        pairs = self.find_pairs()
        for ob_i, ob_j in pairs:
            self.link_obs(ob_i, ob_j)

    def create_object(self, cls_name, inst=0):
        '''build an instance object from schema class'''
        cls = self.get_cls(cls_name)
        ob = cls('{}-{}'.format(cls_name.lower(), inst))
        return ob

    def get_cls(self, cls_name):
        '''return ZPL class'''
        return getattr(getattr(self.cfg.zenpack_module, cls_name), cls_name)

    def classname(self, ob):
        ''''''
        return ob.__class__.__name__

    def get_bases(self, cls):
        bases = []
        for base in cls.mro():
            if not hasattr(base, '_relations'):
                continue
            if len(base._relations) == 0:
                continue
            if base.__name__ not in bases:
                bases.append(base.__name__)
        return bases

    def get_ob_rel(self, ob, relspec):
        ''''''
        relname = self.get_relname(ob, relspec)
        return getattr(ob, relname)

    def link_obs(self, ob_from, ob_to):
        '''link two schema instance objects'''
        # get object specs and relation specs
        rspec = self.find_relspec(ob_from, ob_to)
        # get object relations
        from_rel = self.get_ob_rel(ob_from, rspec)
        to_rel = self.get_ob_rel(ob_to, rspec)
        # add objects to relations
        self.add_rel(from_rel, ob_to)
        self.add_rel(to_rel, ob_from)

    def add_rel(self, rel, target):
        try:
            if rel.__class__.__name__ == 'ToManyContRelationship':
                _add(rel, target)
            else:
                rel._add(target)
        except RelationshipExistsError:
            pass

    def get_relname(self, ob, relspec):
        '''return the correct name for a relation'''
        if self.classname(ob) == relspec.left_class:
            return relspec.left_relname
        if self.classname(ob) == relspec.right_class:
            return relspec.right_relname
        return None

    def find_relspec(self, ob_i, ob_j):
        '''find relation spec for a given target class'''
        for rel in self.cfg.class_relationships:
            i_cls = self.classname(ob_i)
            j_cls = self.classname(ob_j)
            if rel.left_class == i_cls and rel.right_class == j_cls:
                    return rel
        return None

    def has_relation(self, ob_from, ob_to):
        '''return True if two objects have a relation'''
        if self.find_relspec(ob_from, ob_to):
            return True
        return False

    def orient_pair(self, ob_from, ob_to):
        rspec = self.find_relspec(ob_from, ob_to)
        if rspec.left_class == self.classname(ob_from) and rspec.right_class == self.classname(ob_to):
            return (ob_from, ob_to)

    def find_pairs(self):
        '''return pairs of related objects'''
        pairs = []
        for i_name, i_cfg in self.class_objects.iteritems():
            i_ob = i_cfg.get('ob')
            for j_name, j_cfg in self.class_objects.iteritems():
                j_ob = j_cfg.get('ob')
                if self.has_relation(i_ob, j_ob):
                    pairs.append((i_ob, j_ob))
        return pairs

    def is_device(self, ob):
        '''return True if device'''
        if hasattr(ob, 'deviceClass'):
            return True
        return False


# Using this ZenPackSpec name for logging-type tests
LOG = ZPLOG.add_log('ZenPacks.zenoss.TestLogging')
LOG.propagate = False


class WarningLoader(WarningLoader):
    """Subclassing here to add logging capability"""
    LOG = LOG

class LogCapture(object):
    """Class mixin to add log capture for unit test evaluation"""
    def start_capture(self):
        self.buffer = io.StringIO()
        WarningLoader.LOG.setLevel(logging.WARNING)
        self.handler = logging.StreamHandler(self.buffer)
        self.handler.setFormatter(logging.Formatter(u'[%(levelname)s] %(message)s'))
        WarningLoader.LOG.addHandler(self.handler)

    def stop_capture(self):
        WarningLoader.LOG.removeHandler(self.handler)
        self.handler.flush()
        self.buffer.flush()
        return self.buffer.getvalue()

    def test_yaml(self, yaml_doc):
        self.start_capture()
        cfg = yaml.load(yaml_doc, Loader=WarningLoader)
        logs = self.stop_capture()
        return str(logs)


class CommandMixin(object):
    """Add support for command line testing"""
    log = logging.getLogger("ZenPackLib.test.command")
    log.setLevel(logging.INFO)
    zenpacklib_path = os.path.join(os.path.dirname(__file__), "../zenpacklib.py")

    def zenpacklib_cmd_output(self, *args):
        """test output of zenpacklib.py"""
        cmd = ('python', self.zenpacklib_path,) + args
        cmdstr = " ".join(cmd)
        self.log.info("Running %s" % cmdstr)
        return self.get_cmd_output(cmd)

    @classmethod
    def get_cmd_output(cls, cmd, vars=None):
        """execute a command and return the output"""
        if vars is None:
            vars = {}
        cls.log.info(" ".join(cmd))
        env = dict(os.environ)
        env.update(vars)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        p.wait()
        return (cmd, p, out, err)


