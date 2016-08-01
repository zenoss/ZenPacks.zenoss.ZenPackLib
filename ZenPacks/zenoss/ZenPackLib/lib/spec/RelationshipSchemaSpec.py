from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.ZenRelations.Exceptions import ZenSchemaError
from ..functions import relname_from_classname
from .Spec import Spec
from ..functions import LOG


class RelationshipSchemaSpec(Spec):
    """RelationshipSchemaSpec"""

    LOG = LOG

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
        log=LOG
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
        self.LOG=log

        if not RelationshipSchemaSpec.valid_orientation(left_type, right_type):
            raise ZenSchemaError("In %s(%s) - (%s)%s, invalid orientation- left and right may be reversed." % (left_class, left_relname, right_relname, right_class))

        self.zenpack_spec = zenpack_spec
        self.left_class = left_class
        self.left_relname = left_relname
        self.left_schema = self.make_schema(left_type, right_type, right_class, right_relname)
        self.right_class = right_class
        self.right_relname = right_relname
        self.right_schema = self.make_schema(right_type, left_type, left_class, left_relname)

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

    _relTypeCardinality = {
        ToOne: '1',
        ToMany: 'M',
        ToManyCont: 'MC'
    }

    _relTypeClasses = {
        "ToOne": ToOne,
        "ToMany": ToMany,
        "ToManyCont": ToManyCont
    }

    _relTypeNames = {
        ToOne: "ToOne",
        ToMany: "ToMany",
        ToManyCont: "ToManyCont"
    }

    @property
    def left_type(self):
        return self._relTypeNames.get(self.right_schema.__class__)

    @property
    def right_type(self):
        return self._relTypeNames.get(self.left_schema.__class__)

    @property
    def left_cardinality(self):
        return self._relTypeCardinality.get(self.right_schema.__class__)

    @property
    def right_cardinality(self):
        return self._relTypeCardinality.get(self.left_schema.__class__)

    @property
    def default_left_relname(self):
        return relname_from_classname(self.right_class, plural=self.right_cardinality != '1')

    @property
    def default_right_relname(self):
        return relname_from_classname(self.left_class, plural=self.left_cardinality != '1')

    @property
    def cardinality(self):
        return '%s:%s' % (self.left_cardinality, self.right_cardinality)

    def make_schema(self, relTypeName, remoteRelTypeName, remoteClass, remoteName):
        relType = self._relTypeClasses.get(relTypeName, None)
        if not relType:
            raise ValueError("Unrecognized Relationship Type '%s'" % relTypeName)

        remoteRelType = self._relTypeClasses.get(remoteRelTypeName, None)
        if not remoteRelType:
            raise ValueError("Unrecognized Relationship Type '%s'" % remoteRelTypeName)

        schema = relType(remoteRelType, remoteClass, remoteName)

        # Qualify unqualified classnames.
        if '.' not in schema.remoteClass:
            schema.remoteClass = '{}.{}'.format(
                self.zenpack_spec.name, schema.remoteClass)

        return schema

