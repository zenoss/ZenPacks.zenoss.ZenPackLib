import inspect
import yaml
from Products.ZenRelations.Exceptions import RelationshipExistsError
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')

from ZenPacks.zenoss.ZenPackLib import zenpacklib

import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenUtils.ZenScriptBase import ZenScriptBase


class ZPLTestHarness(ZenScriptBase):
    '''Class containing methods to build out dummy objects representing YAML class instances'''

    def __init__(self, filename, connect=False):
        ''''''
        ZenScriptBase.__init__(self)
        self.cfg = zenpacklib.load_yaml(filename)
        self.yaml = yaml.load(open(filename, 'r'))
        self.zp = self.cfg.zenpack_module
        self.schema = self.zp.schema
        self.build_cfg_obs()
        # create relations between objects
        self.build_relations()
        self.build_cfg_relations()

    def build_ob(self, cls_name, inst=0):
        '''build an instance object from schema class'''
        cls = self.get_cls(cls_name)
        ob = cls('%s-%s' % (cls_name.lower(), inst))
        return ob

    def build_cfg_obs(self):
        '''return a list of object instances for ZPL classes'''
        self.obs = []
        for name, spec in self.cfg.classes.items():
            ob = self.build_ob(name)
            self.obs.append(ob)

    def get_cls(self, name):
        '''return ZPL class'''
        return getattr(getattr(self.zp, name), name)

    def build_relations(self):
        '''create relations between objects'''
        pairs = self.find_pairs()
        for ob_i, ob_j in pairs:
            self.link_obs(ob_i, ob_j)

    def get_ob_spec(self, ob):
        '''return a spec for a given ob'''
        return self.cfg.classes.get(self.classname(ob))

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
        #get object specs and relation specs
        rspec = self.find_relspec(ob_from, ob_to)
        # get object relations
        from_rel = self.get_ob_rel(ob_from, rspec)
        to_rel = self.get_ob_rel(ob_to, rspec)
        # add objects to relations
        self.add_rel(from_rel, ob_to)
        self.add_rel(to_rel, ob_from)

    def add_rel(self, rel, target):
        try:
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
        for i, ob_i in enumerate(self.obs):
            for j, ob_j in enumerate(self.obs):
                if self.has_relation(ob_i, ob_j):
                    pairs.append((ob_i, ob_j))
        return pairs

    def is_device(self, ob):
        '''return True if device'''
        if hasattr(d, 'deviceClass'):
            return True
        return False

    '''
        Tests
    '''

    def check_properties(self):
        '''compare class vs. spec properties'''
        for ob in self.obs:
            passed = self.compare_ob_to_spec(ob)
            if not passed:
                return False
        return True
        
    def check_ob_relations(self):
        '''compare class vs spec relations'''
        passed = True
        for i, j in self.find_pairs():
            if not self.check_rel(i,j):
                passed = False
        return passed

    def check_rel(self, ob_from, ob_to):
        '''Compare object relation attributes to spec'''
        rspec = self.find_relspec(ob_from, ob_to)
        rel_from = getattr(ob_from, rspec.left_relname)
        rel_to = getattr(ob_to, rspec.right_relname)
        # check target remote class
        bases_from = self.get_bases(ob_from.__class__)
        bases_to = self.get_bases(ob_from.__class__)
        cls_from = rel_to.remoteClass().__name__
        cls_to = rel_from.remoteClass().__name__
        spec_from = rspec.left_class
        spec_to = rspec.right_class
        # relnames
        relname_from = rel_to.remoteName()
        relname_to = rel_from.remoteName()
        spec_r_from = rspec.left_relname
        spec_r_to = rspec.right_relname
        # schema
        schema_from = rel_to.remoteTypeName()
        schema_to = rel_from.remoteTypeName()
        spec_s_from = self.classname(rspec.left_schema)
        spec_s_to = self.classname(rspec.right_schema)
        # checking classes
        if cls_from != spec_from:# and spec_from not in bases_from:
            print self.rel_spec_info(rspec)
            print 'Remote left class mismatch between spec (%s) and relation (%s)' % (spec_from, cls_from)
            return False
        if cls_to != spec_to: # and spec_to not in bases_to:
            print self.rel_spec_info(rspec)
            print 'Remote right class mismatch between spec (%s) and relation (%s)' % (spec_to, cls_to)
            return False
        # rel name
        if relname_from != spec_r_from:
            print 'Relation left id mismatch between spec (%s) and relation (%s)' % (spec_r_from, relname_from)
            return False
        if relname_to != spec_r_to:
            print 'Relation right id mismatch between spec (%s) and relation (%s)' % (spec_r_to, relname_to)
            return False
        # schema type
        if schema_from != spec_s_from:
            print 'Relation left schema type mismatch between spec (%s) and relation (%s)' % (spec_s_from, schema_from)
            return False
        if schema_to != spec_s_to:
            print 'Relation right schema type mismatch between spec (%s) and relation (%s)' % (spec_s_to, schema_to)
            return False
        return True

    def check_cfg_relations(self):
        '''
            Iterate through class specs and
                1) compare class spec to config.class_relations (YAML)
                2) compare class spec relations to ZPL-created class
                3) compare class spec relations to ZPL-created class instances
        '''
        passed = True
        for name, spec in self.cfg.classes.items():
            print '-'*80
            print name
            print ''
            cls = self.get_cls(name)
            bases = self.get_bases(cls)
            for relname, rspec in spec.relationships.items():
                rel_class = rspec.class_.name
                if name != rel_class:
                    if rel_class not in bases:
                        print '%s has relation %s inherited from invalid base class: %s' % (name, relname, rel_class)
                        passed = False
                # check class rel spec
                fwd = self.rel_cls_spec_info(rspec)
                rwd = self.rel_cls_spec_info(rspec, reverse=True)
                if not self.has_cfg_relation(fwd, rwd):
                    print 'Problem with %s RelationshipSchemaSpec "%s"' % (name, fwd)
                    passed = False
                # if inherited class, replace with this class for future matches
                if name != rel_class:
                    fwd = fwd.replace(rel_class, name, 1)
                    rwd = name.join(rwd.rsplit(rel_class, 1))
                # check class relation directly
                # localize inherited classes
                c_fwd = self.rel_cls_info(cls, relname)
                c_rwd = self.rel_cls_info(cls, relname, reverse=True)
                if c_fwd != fwd or c_rwd != rwd:
                    print 'Problem with %s class relation "%s"' % (name, c_fwd)
                    passed = False
                # check relation on object
                ob = self.build_ob(name)
                ob_fwd = self.rel_ob_info(ob, relname)
                ob_rwd = self.rel_ob_info(ob, relname, reverse=True)
                if ob_fwd != fwd or ob_rwd != rwd:
                    print 'Problem with %s object relation: "%s"' % (name, ob_fwd)
                    passed = False
        return passed

    def compare_ob_to_spec(self, ob):
        '''compare properties between spec and class'''
        passed = True
        cls_id = self.classname(ob)
        spec = self.get_ob_spec(ob)
        for name, prop in spec.properties.items():
            #print '  checking "%s"' % name
            # compare property default
            intended = getattr(prop, 'default')
            intended_type = getattr(prop, 'type_')
            if prop.api_only:
                continue
            actual = getattr(ob, name)
            actual_type = ob.getPropertyType(name)
            # check for None vs "None"
            if intended == 'None':
                print '%s (%s) has default value of "None" (string)' % (cls_id, name)
            # mismatch between intended and actual
            errmsg = '%s (%s) default type or value mismatch spec (%s) vs class (%s)'% (cls_id, name, intended, actual)
            if intended is None:
                if actual == "None" or actual != intended:
                    print errmsg
                    passed = False
            # check for intended versus actual type
            if intended_type != actual_type:
                print '%s (%s) type mismatch spec (%s) vs class (%s)'% (cls_id, name, intended_type, actual_type)
                passed = False
        return passed

    def check_templates_vs_specs(self):
        '''check that template objects match the specs'''
        self.connect()
        passed = True
        for dcid, dcs in self.cfg.device_classes.items():
            for tid, tcs in dcs.templates.items():
                # create a dummy template object
                t = tcs.create(self.dmd, False)
                print t.id, '-' * 80
                for th in t.thresholds():
                    thcs = tcs.thresholds.get(th.id)
                    test, msg = self.compare_template_ob_to_spec(th, thcs)
                    if not test:
                        print '%s threshold %s failed (%s)' % (t.id, th.id, msg)
                        passed = False
                for gd in t.graphDefs():
                    gdcs = tcs.graphs.get(gd.id)
                    test, msg = self.compare_template_ob_to_spec(gd, gdcs)
                    if not test:
                        print '%s graph %s failed (%s)' % (t.id, gd.id, msg)
                        passed = False
                for ds in t.datasources():
                    dscs = tcs.datasources.get(ds.id)
                    test, msg = self.compare_template_ob_to_spec(ds, dscs)
                    if not test:
                        print '%s datasource %s failed (%s)' % (t.id, ds.id, msg)
                        passed = False
                    for dp in ds.datapoints():
                        dpcs = dscs.datapoints.get(dp.id)
                        test, msg = self.compare_template_ob_to_spec(dp, dpcs)
                        if not test:
                            print '%s %s datapoint %s failed (%s)' % (t.id, ds.id, dp.id, msg)
                            passed = False
        return passed

    def compare_template_to_spec(self, template, spec):
        '''compare template to spec'''
        if template.id != spec.name:
            return False
        if template.description != spec.description:
            return False
        if tcs.targetPythonClass:
            if tcs.targetPythonClass != t.targetPythonClass:
                return False
        return True

    def compare_template_ob_to_spec(self, ob, dscs):
        '''compare template object to spec'''
        passed = True
        cls = self.classname(ob)
        msg = '%s passed inspection' % cls
        for p in ob._properties:
            id = p.get('id')
            default = getattr(ob, id)
            spec_default = getattr(dscs, id, getattr(dscs,'extra_params',{}).get(id))
            # skip if not defined:
            if not spec_default:
                continue
            print "comparing %s %s (%s) to %s (%s)" % (id, default, type(default), spec_default, type(spec_default))
            if default != spec_default:
                msg = '%s property %s mismatch between class (%s) and spec (%s)  and default' % (ob.id, id, default, spec_default)
                passed = False
        return (passed, msg)

    def check_templates_vs_yaml(self):
        '''check that template objects match the yaml'''
        self.connect()
        passed = True
        for dcid, dcs in self.cfg.device_classes.items():
            # get data from unparsed, loaded yaml
            y_dcs = self.yaml.get('device_classes').get(dcid)
            y_templates = y_dcs.get('templates')
            for tid, tcs in dcs.templates.items():
                y_t = y_templates.get(tid)
                # create a dummy template object
                t = tcs.create(self.dmd, False)
                if not self.check_ob_vs_yaml(t, y_templates):
                    passed = False
                for ds in t.datasources():
                    y_ds = y_t.get('datasources').get(ds.id)
                    if not self.check_ob_vs_yaml(ds, y_t.get('datasources')):
                        passed = False
                    for dp in ds.datapoints():
                        if not self.check_ob_vs_yaml(dp, y_ds.get('datapoints')):
                            passed = False
                for th in t.thresholds():
                    if not self.check_ob_vs_yaml(th, y_t.get('thresholds')):
                        import pdb ; pdb.set_trace()
                        passed = False
                for gd in t.graphDefs():
                    if not self.check_ob_vs_yaml(gd, y_t.get('graphs')):
                        passed = False
        return passed

    def check_ob_vs_yaml(self, ob, data):
        '''compare object values to YAML'''
        passed = True
        ob_data = data.get(ob.id)
        ob_data.update(data.get('DEFAULTS',{}))
        for k, v in ob_data.items():
            if isinstance(v, dict):
                continue
            if k == 'type':
                k = 'sourcetype'
            expected = v
            actual = getattr(ob, k)
            if expected != actual:
                print '%s (%s) property %s: acutal (%s) did not match expected (%s)' % (ob.id, ob.meta_type, k, actual, expected)
                passed = False
        return passed

    '''
        Informational
    '''

    def build_cfg_relations(self):
        '''build a list of string relation representations
           closest to the original YAML definition
        '''
        self.cfg_relations = []
        for rel in self.cfg.class_relationships:
            self.cfg_relations.append(self.rel_spec_info(rel))

    def has_cfg_relation(self, fwd, rwd):
        '''return True if relation in self.cfg_relations'''
        if fwd not in self.cfg_relations and rwd not in self.cfg_relations:
            return False
        return True

    def rel_string(self, cls_f, rel_f, type_f, type_t, rel_t, cls_t, reverse=False):
        '''return a basic string representation of a relation'''
        base_string = '%s (%s) %s : %s (%s) %s'
        if reverse:
            return base_string % (cls_t, rel_t, type_t,
                                  type_f, rel_f, cls_f)
        return base_string % (cls_f, rel_f, type_f, 
                              type_t, rel_t, cls_t)

    def print_relations(self):
        ''''''
        for rspec in self.cfg.class_relationships:
            print self.rel_spec_info(rspec)

    def rel_cls_info(self, cls, relname, reverse=False):
        '''return string representing Class relation'''
        schema = dict(cls._relations).get(relname)
        return self.rel_string(cls.__name__,
                               relname,
                               schema.__class__.__name__,
                               schema.remoteType.__name__,
                               schema.remoteName,
                               schema.remoteClass.split('.')[-1],
                               reverse)

    def rel_ob_info(self, ob, relname, reverse=False):
        '''return string representing Class instance relation'''
        rel = getattr(ob, relname)
        return self.rel_string(self.classname(ob),
                               relname,
                               self.classname(rel).replace('Relationship',''),
                               rel.remoteType().__name__,
                               rel.remoteName(),
                               rel.remoteClass().__name__,
                               reverse)

    def rel_spec_info(self, rspec, reverse=False):
        '''return string representing ClassRelationshipSpec relation'''
        return self.rel_string(rspec.left_class,
                               rspec.left_relname,
                               self.classname(rspec.left_schema),
                               self.classname(rspec.right_schema),
                               rspec.right_relname,
                               rspec.right_class,
                               reverse)

    def rel_cls_spec_info(self, rspec, reverse=False):
        '''return string representing RelationshipSchemaSpec relation'''
        return self.rel_string(rspec.class_.name,
                          rspec.name,
                          self.classname(rspec.schema),
                          rspec.schema.remoteType.__name__,
                          rspec.schema.remoteName,
                          rspec.remote_classname,
                          reverse)

    def print_class_relations(self):
        '''print out some relation details'''
        for name, spec in self.cfg.classes.items():
            self.relation_attributes(spec)

    def relation_attributes(self, spec):
        print '#' * 80
        print spec.name
        print ''
        self.print_attrs(spec.relationships)

    def class_attributes(self, spec):
        print '#' * 80
        print spec.name
        print ''
        self.print_attrs(spec)

    def print_attrs(self, data):
        for name, spec in data.items():
            print '#### %s' % name
            for k,v in spec.__dict__.items():
                if v is None: continue
                print '  %s: %s' % (k,v)
            print ''

    def list_all_paths(self):
        for ob in self.obs:
            if self.is_device(ob):
                continue
            try:
                self.list_paths(ob)
            except Exception as e:
                print e
                continue

    def list_paths(self, component):
        import collections
        from Acquisition import aq_chain
        from Products.ZenRelations.RelationshipBase import RelationshipBase
        all_paths = set()
        included_paths = set()
        class_summary = collections.defaultdict(set)
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
            print "%s is reachable from %s" % (source_class, ", ".join(sorted(class_summary[source_class])))
