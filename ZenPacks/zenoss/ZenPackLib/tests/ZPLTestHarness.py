import yaml
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')
from Products.ZenRelations.Exceptions import RelationshipExistsError
from Acquisition import aq_base


# Zenoss Imports
import Globals
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenUtils.ZenScriptBase import ZenScriptBase

# change this to use other versions of zenpacklib
from ZenPacks.zenoss.ZenPackLib import zenpacklib
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import load_yaml_single
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper


def str_to_severity(value):
    '''
    Return numeric severity given a string representation of severity.
    '''
    try:
        severity = int(value)
    except (TypeError, ValueError):
        severity = {
            'crit': 5, 'critical': 5,
            'err': 4, 'error': 4,
            'warn': 3, 'warning': 3,
            'info': 2, 'information': 2, 'informational': 2,
            'debug': 1, 'debugging': 1,
            'clear': 0,
            }.get(value.lower())
    if severity is None:
        raise ValueError("'%s' is not a valid value for severity." % value)
    return severity


def _add(ob, obj):
    """ override of ToManyContRelationship _add method
    """
    id = obj.id
    if ob._objects.has_key(id):
        raise RelationshipExistsError
    ob._objects[id] = aq_base(obj)
    obj = aq_base(obj).__of__(ob)
    ob.setCount()


class ZPLTestHarness(ZenScriptBase):
    '''Class containing methods to build out dummy objects representing YAML class instances'''

    def __init__(self, filename, connect=False):
        ''''''
        ZenScriptBase.__init__(self)
        self.filename = filename
        self.cfg = zenpacklib.load_yaml(filename, verbose=True)
        self.yaml = load_yaml_single(filename, useLoader=False)
        self.zp = self.cfg.zenpack_module
        self.schema = self.zp.schema
        self.build_cfg_obs()
        # create relations between objects
        self.build_relations()
        self.build_cfg_relations()
        self.exported_yaml = yaml.dump(self.cfg, Dumper=Dumper)
        self.reloaded_yaml = load_yaml_single(self.exported_yaml, useLoader=False)

    def build_ob(self, cls_name, inst=0):
        '''build an instance object from schema class'''
        cls = self.get_cls(cls_name)
        ob = cls('{}-{}'.format(cls_name.lower(), inst))
        return ob

    def build_cfg_obs(self):
        '''return a list of object instances for ZPL classes'''
        self.obs = []
        for name, spec in self.cfg.classes.items():
            ob = self.build_ob(name)
            ob.buildRelations()
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
        for i, ob_i in enumerate(self.obs):
            for j, ob_j in enumerate(self.obs):
                if self.has_relation(ob_i, ob_j):
                    pairs.append((ob_i, ob_j))
        return pairs

    def is_device(self, ob):
        '''return True if device'''
        if hasattr(ob, 'deviceClass'):
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
        if cls_from != spec_from and spec_from not in bases_from:
            log.warn('Remote left class mismatch between spec ({}) and relation ({})'.format(spec_from, cls_from))
            return False
        if cls_to != spec_to and spec_to not in bases_to:
            log.warn('Remote right class mismatch between spec ({}) and relation ({})'.format(spec_to, cls_to))
            return False
        # rel name
        if relname_from != spec_r_from:
            log.warn('Relation left id mismatch between spec ({}) and relation ({})'.format(spec_r_from, relname_from))
            return False
        if relname_to != spec_r_to:
            log.warn('Relation right id mismatch between spec ({}) and relation ({})'.format(spec_r_to, relname_to))
            return False
        # schema type
        if schema_from != spec_s_from:
            log.warn('Relation left schema type mismatch between spec ({}) and relation ({})'.format(spec_s_from, schema_from))
            return False
        if schema_to != spec_s_to:
            log.warn('Relation right schema type mismatch between spec ({}) and relation ({})'.format(spec_s_to, schema_to))
            return False
        return True

    def check_cfg_relations(self):
        '''
            Iterate through class specs and
                1) compare class spec to config.class_relations (YAML)
                2) compare class spec relations to ZPL-created class
                3) compare class spec relations to ZPL-created class instances
        '''
        def check_relation_schema(fwd, rwd, rel_class, bases):
            """ check RelationshipSchemaSpec """
            for b in bases:
                b_fwd = fwd.replace(rel_class, b, 1)
                b_rwd = b.join(rwd.rsplit(rel_class, 1))
                if self.has_cfg_relation(b_fwd, b_rwd):
                    return True
            log.warn('Problem with {} RelationshipSchemaSpec "{}"'.format(name, fwd))
            return False
        def check_class_relation(fwd, rwd, cls, relname):
            """ check class relation """
            c_fwd = self.rel_cls_info(cls, relname)
            c_rwd = self.rel_cls_info(cls, relname, reverse=True)
            for x, y in [(fwd, c_fwd), (rwd, c_rwd)]:
                if x != y:
                    log.warn('Class ({}) relation mismatch between:\n    {}\n    {}'.format(cls.__name__, x, y))
                    return False
            return True
        def check_object_relation(fwd, rwd, name, relname):
            """check relation on object"""
            ob = self.build_ob(name)
            ob_fwd = self.rel_ob_info(ob, relname)
            ob_rwd = self.rel_ob_info(ob, relname, reverse=True)
            for x, y in [(fwd, ob_fwd), (rwd, ob_rwd)]:
                if x != y:
                    log.warn('Object ({}) relation mismatch between:\n    {}\n    {}'.format(name, x, y))
                    return False
            return True
        passed = True
        for name, spec in self.cfg.classes.items():
            cls = self.get_cls(name)
            bases = self.get_bases(cls)
            for relname, rspec in spec.relationships.items():
                rel_class = rspec.class_.name
                fwd = self.rel_cls_spec_info(rspec)
                rwd = self.rel_cls_spec_info(rspec, reverse=True)
                # check RelationshipSchemaSpec
                if not self.has_cfg_relation(fwd, rwd):
                    if not check_relation_schema(fwd, rwd, rel_class, bases):
                        passed = False
                if name != rel_class:
                    if rel_class not in bases:
                        log.warn('{} has relation {} inherited from invalid base class: {}'.format(name, relname, rel_class))
                        passed = False
                        continue
                    else:
                        # if inherited class, replace with this class for future matches
                        fwd = fwd.replace(rel_class, name, 1)
                        rwd = name.join(rwd.rsplit(rel_class, 1))
                # check class relation
                if not check_class_relation(fwd, rwd, cls, relname):
                    passed = False
                # check relation on object
                if not check_object_relation(fwd, rwd, name, relname):
                    passed = False
        return passed

    def compare_ob_to_spec(self, ob):
        '''compare properties between spec and class'''
        passed = True
        cls_id = self.classname(ob)
        spec = self.get_ob_spec(ob)
        for name, prop in spec.properties.items():
            # compare property default
            intended = getattr(prop, 'default')
            intended_type = getattr(prop, 'type_')
            if prop.api_only:
                continue
            actual = getattr(ob, name)
            actual_type = ob.getPropertyType(name)
            # check for None vs "None"
            if intended == 'None':
                log.debug('{} ({}) has default value of "None" (string)'.format(cls_id, name))
            # mismatch between intended and actual
            errmsg = '{} ({}) type or value mismatch between spec "{}" ({}) and class "{}" ({})'.format(cls_id, name, 
                                                                                                   intended, type(intended).__name__,
                                                                                                   actual, type(actual).__name__)
            if intended is None:
                if actual == "None" or actual != intended:
                    log.warn(errmsg)
                    passed = False
            # check for intended versus actual type
            if intended_type != actual_type:
                log.warn('{} ({}) type mismatch spec ({}) vs class ({})'.format(cls_id, name, intended_type, actual_type))
                passed = False
        return passed

    def check_templates_vs_specs(self):
        '''check that template objects match the specs'''
        self.connect()
        passed = True
        for dcid, dcs in self.cfg.device_classes.items():
            for tid, tcs in dcs.templates.items():
                # create a dummy template object
                try:
                    t = tcs.create(self.dmd, False)
                except Exception as e:
                    log.warn("Could not test {}: {}".format(tid, e))
                    continue
                for th in t.thresholds():
                    thcs = tcs.thresholds.get(th.id)
                    test, msg = self.compare_template_ob_to_spec(th, thcs)
                    if not test:
                        log.warn('{} threshold {} failed ({})'.format(t.id, th.id, msg))
                        passed = False
                for gd in t.graphDefs():
                    gdcs = tcs.graphs.get(gd.id)
                    test, msg = self.compare_template_ob_to_spec(gd, gdcs)
                    if not test:
                        log.warn('{} graph {} failed ({})'.format(t.id, gd.id, msg))
                        passed = False
                for ds in t.datasources():
                    dscs = tcs.datasources.get(ds.id)
                    test, msg = self.compare_template_ob_to_spec(ds, dscs)
                    if not test:
                        log.warn('{} datasource {} failed ({})'.format(t.id, ds.id, msg))
                        passed = False
                    for dp in ds.datapoints():
                        dpcs = dscs.datapoints.get(dp.id)
                        test, msg = self.compare_template_ob_to_spec(dp, dpcs)
                        if not test:
                            log.warn('{} {} datapoint {} failed ({})'.format(t.id, ds.id, dp.id, msg))
                            passed = False
        return passed

    def compare_template_to_spec(self, template, spec):
        '''compare template to spec'''
        if template.id != spec.name:
            return False
        if template.description != spec.description:
            return False
        if spec.targetPythonClass:
            if spec.targetPythonClass != template.targetPythonClass:
                return False
        return True

    def compare_template_ob_to_spec(self, ob, dscs):
        '''compare template object to spec'''
        passed = True
        cls = self.classname(ob)
        msg = '{} passed inspection'.format(cls)
        for p in ob._properties:
            id = p.get('id')
            default = getattr(ob, id)
            spec_default = getattr(dscs, id, getattr(dscs,'extra_params',{}).get(id))
            # skip if not defined:
            if not spec_default:
                continue
            if default != spec_default:
                msg = '{} property {} mismatch between class ({}) and spec ({})  and default'.format(ob.id, id, default, spec_default)
                passed = False
        return (passed, msg)

    def check_templates_vs_yaml(self):
        '''check that template objects match the yaml'''
        self.connect()
        passed = True
        for dcid, dcs in self.cfg.device_classes.items():
            # get data from unparsed, loaded yaml
            y_dcs = self.reloaded_yaml.get('device_classes').get(dcid)
            y_templates = y_dcs.get('templates')
            for tid, tcs in dcs.templates.items():
                y_t = y_templates.get(tid)
                # create a dummy template object
                try:
                    t = tcs.create(self.dmd, False)
                except Exception as e:
                    log.warn("Could not test {}: {}".format(tid, e))
                    continue
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
                        passed = False
                for gd in t.graphDefs():
                    if not self.check_ob_vs_yaml(gd, y_t.get('graphs')):
                        passed = False
        return passed

    def test_severity(self, severity):
        ''''''
        try:
            test = int(severity)
            return severity
        except:
            if isinstance(severity, str):
                return str_to_severity(severity)
        return severity

    def check_ob_vs_yaml(self, ob, data):
        '''compare object values to YAML'''
        passed = True
        ob_data = data.get('DEFAULTS',{})
        if not isinstance(data.get(ob.id,{}), dict):
            # this is the dataoint aliases
            if self.classname(ob) == 'RRDDataPoint':
                return passed
        ob_data.update(data.get(ob.id,{}))
        for k, v in ob_data.items():
            if isinstance(v, dict):
                continue
            if k == 'type':
                continue
            expected = v
            actual = getattr(ob, k)
            # this can be string or integer
            if k == 'severity':
                expected = self.test_severity(expected)
                actual = self.test_severity(actual)
            if expected != actual:
                if k in ['rrdmin', 'rrdmax']:
                    if str(expected) == str(actual):
                        continue
                log.warn('{} ({}) property {}: acutal: {} ({}) did not match expected: {} ({})'.format(ob.id, ob.meta_type, k, 
                                                                                                actual, type(actual).__name__, 
                                                                                                expected, type(expected).__name__))
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
        base_string = '{} ({}) {} : {} ({}) {}'
        if reverse:
            return base_string.format(cls_t, rel_t, type_t,
                                  type_f, rel_f, cls_f)
        return base_string.format(cls_f, rel_f, type_f, 
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
        '''return string representing RelationshipSchemaSpec relation'''
        return self.rel_string(rspec.left_class.split('.')[-1],
                               rspec.left_relname,
                               self.classname(rspec.left_schema),
                               self.classname(rspec.right_schema),
                               rspec.right_relname,
                               rspec.right_class.split('.')[-1],
                               reverse)

    def rel_cls_spec_info(self, rspec, reverse=False):
        '''return string representing ClassRelationshipSpec  relation'''
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
            print '#### {}'.format(name)
            for k,v in spec.__dict__.items():
                if v is None: continue
                print '  {}: {}'.format(k,v)
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
                    print "DIRECT {}".format(path)
                else:
                    # sometimes extra paths are pulled in due to extra_paths
                    # configuration.
                    print "EXTRA {}".format(path)
            else:
                print "EXCLUDE {}".format(path)
        print "\nClass Summary\n-------------\n"
        for source_class in sorted(class_summary.keys()):
            print "{} is reachable from {}".format(source_class, ", ".join(sorted(class_summary[source_class])))
