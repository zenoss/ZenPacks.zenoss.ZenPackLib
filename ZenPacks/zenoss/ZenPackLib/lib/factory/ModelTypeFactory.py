from ..base.ClassProperty import ClassProperty
from ..helpers.OrderedDict import OrderedDict

def ModelTypeFactory(name, bases):
    """Return a "ZenPackified" model class given name and bases tuple."""

    @ClassProperty
    @classmethod
    def _relations(cls):
        """Return _relations property

        This is implemented as a property method to deal with cases
        where ZenPacks loaded after ours in easy-install.pth monkeypatch
        _relations on one of our base classes.

        """

        relations = OrderedDict()
        for base in cls.__bases__:
            base_relations = getattr(base, '_relations', [])
            for base_name, base_schema in base_relations:
                # In the case of multiple bases having relationships
                # by the same name, we want to use the first one.
                # This is consistent with Python method resolution
                # order.
                relations.setdefault(base_name, base_schema)

        if hasattr(cls, '_v_local_relations'):
            for local_name, local_schema in cls._v_local_relations:
                # In the case of a local relationship having a
                # relationship by the same name as one of the bases, we
                # use the local relationship.
                relations[local_name] = local_schema

        return tuple(relations.items())

    def index_object(self, idxs=None):
        for base in bases:
            if hasattr(base, 'index_object'):
                try:
                    base.index_object(self, idxs=idxs)
                except TypeError:
                    base.index_object(self)

    def unindex_object(self):
        for base in bases:
            if hasattr(base, 'unindex_object'):
                base.unindex_object(self)

    attributes = {
        '_relations': _relations,
        'index_object': index_object,
        'unindex_object': unindex_object,
        }

    return type(name, bases, attributes)
