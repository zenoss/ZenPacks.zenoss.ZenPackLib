from ..base.ComponentBase import ComponentBase
from .ModelTypeFactory import ModelTypeFactory


def ComponentTypeFactory(name, bases):
    """Return a "ZenPackified" component class given bases tuple."""
    return ModelTypeFactory(name, (ComponentBase,) + bases)

