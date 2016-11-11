##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenRelations.Exceptions import ZenSchemaError
from ..functions import relname_from_classname
from .Spec import Spec
from .ClassRelationshipSpec import ClassRelationshipSpec

from ..base.types import Relationship
from Products.ZenUtils.Utils import monkeypatch, importClass

class RelationshipSchemaSpec(Spec):
    """RelationshipSchemaSpec"""
    _left_schema = None
    _right_schema = None
    _left_type = None
    _right_type = None

    def __init__(
        self,
        zenpack_spec=None,
        left_class=None,
        left_relname=None,
        left_type=None,
        right_type=None,
        right_class=None,
        right_relname=None,
        _source_location=None,
        zplog=None
    ):
        """
            Create a Relationship Schema specification.  This describes both sides
            of a relationship (left and right).

            :param left_class: TODO
            :type left_class: class
            :param left_relname: TODO
            :type left_relname: str
            :param left_type: TODO
            :type left_type: reltype
            :param right_type: TODO
            :type right_type: reltype
            :param right_class: TODO
            :type right_class: class
            :param right_relname: TODO
            :type right_relname: str

        """
        super(RelationshipSchemaSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        if not RelationshipSchemaSpec.valid_orientation(left_type, right_type):
            raise ZenSchemaError("In %s(%s) - (%s)%s, invalid orientation- left and right may be reversed." % (left_class, left_relname, right_relname, right_class))

        self.zenpack_spec = zenpack_spec
        self.left_rel = Relationship(left_type)
        self.left_class = left_class
        self.left_relname = left_relname
        self.left_spec = self.zenpack_spec.classes.get(self.left_class)
        # if spec is not provded, import the target class
        if not self.left_spec:
            self.get_imported_class(self.left_class)

        self.right_rel = Relationship(right_type)
        self.right_class = right_class
        self.right_relname = right_relname
        self.right_spec = self.zenpack_spec.classes.get(self.right_class)
        # if spec is not provded, import the target class
        if not self.right_spec:
            self.get_imported_class(self.right_class)

        # update ClassRelationshipSpec or imported class
        self.update_class_relationship_spec(self.left_spec, self.left_relname, self.left_schema, self.left_class)
        self.update_class_relationship_spec(self.right_spec, self.right_relname, self.right_schema, self.right_class)

    def get_imported_class(self, classname):
        """import target class by reference"""
        # this might be provided by the ZenPack but not defined in the YAML
        if '.' not in classname:
            classname = '{}.{}.{}'.format(self.zenpack_spec.name, classname, classname)
        if '.' in classname and classname.split('.')[-1] not in self.zenpack_spec.classes:
            module = ".".join(classname.split('.')[0:-1])
            try:
                kls = importClass(module)
                self.zenpack_spec.imported_classes[classname] = kls
            except ImportError as e:
                self.LOG.error('Failed to import class {} from {} ({})'.format(classname, module, e))
                pass

    def update_children(self):
        """update child classes of this relationship's target specs"""
        spec_map = {self.left_relname: self.left_spec,
                    self.right_relname: self.right_spec}
        for relname, spec in spec_map.items():
            # skip if this is an imported class
            if not spec:
                continue
            spec.update_child_relations(relname)

    def update_class_relationship_spec(self, spec, relname, schema, classname):
        """Add or Update ClassRelationshipSpec based on this RelationshipSpec"""
        if spec:
            # this shouldn't happen
            if not schema:
                self.LOG.error('Schema relation not provided for {} ({})'.format(spec, relname))
                return
            # ClassRelationshipSpec may exist already if relationships property overrides were
            # specified in the YAML, but they won't have a schema since it wasn't
            # created yet
            if relname in spec.relationships:
                rel_spec = spec.relationships[relname]
                if not rel_spec.schema:
                    rel_spec.schema = schema
            # Otherwise we create it now with defaults
            else:
                spec.relationships[relname] = ClassRelationshipSpec(spec, relname, schema)
        # if ClassSpec doesn't exist, then we are modifying an imported class
        else:
            kls = self.zenpack_spec.imported_classes.get(classname)
            if kls:
                if relname not in (x[0] for x in kls._relations):
                    rel = ((relname, schema.__class__(schema.remoteType,
                                                      schema.remoteClass,
                                                      schema.remoteName)),)
                    # avoid modifying _relations if this is a ZPL-derived class
                    if hasattr(kls, '_v_local_relations'):
                        kls._v_local_relations += rel
                    else:
                        kls._relations += rel
            else:
                self.LOG.error('Failed to add relationship ({}) to imported class ({}).'.format(relname, classname))

    @classmethod
    def valid_orientation(cls, left_type, right_type):
        # The objects in a relationship are always ordered left to right
        # so that they can be easily compared and consistently represented.
        #
        # The valid combinations are:

        # 1:1 - One To One
        if right_type == 'ToOne' and left_type == 'ToOne':
            return True

        # 1:M - One To Many
        if right_type == 'ToOne' and left_type == 'ToMany':
            return True

        # 1:MC - One To Many (Containing)
        if right_type == 'ToOne' and left_type == 'ToManyCont':
            return True

        # M:M - Many To Many
        if right_type == 'ToMany' and left_type == 'ToMany':
            return True

        return False

    @property
    def left_type(self):
        if not self._left_type:
            self._left_type = self.left_rel.name
        return self._left_type

    @left_type.setter
    def left_type(self, value):
        pass

    @property
    def right_type(self):
        if not self._right_type:
            self._right_type = self.right_rel.name
        return self._right_type

    @right_type.setter
    def right_type(self, value):
        pass

    @property
    def left_cardinality(self):
        return self.right_rel.cardinality

    @property
    def right_cardinality(self):
        return self.left_rel.cardinality

    @property
    def default_left_relname(self):
        return relname_from_classname(self.right_class, plural=self.right_cardinality != '1')

    @property
    def default_right_relname(self):
        return relname_from_classname(self.left_class, plural=self.left_cardinality != '1')

    @property
    def cardinality(self):
        return '%s:%s' % (self.left_cardinality, self.right_cardinality)

    @property
    def left_schema(self):
        if not self._left_schema:
            self._left_schema = self.left_rel.cls(self.right_rel.cls, self.right_class, self.right_relname)
            self.qualify_remote_class(self._left_schema)
        return self._left_schema

    @property
    def right_schema(self):
        if not self._right_schema:
            self._right_schema = self.right_rel.cls(self.left_rel.cls, self.left_class, self.left_relname)
            self.qualify_remote_class(self._right_schema)
        return self._right_schema

    def qualify_remote_class(self, schema):
        """Qualify unqualified classnames"""
        if '.' not in schema.remoteClass:
            schema.remoteClass = '{}.{}'.format(
                self.zenpack_spec.name, schema.remoteClass)
