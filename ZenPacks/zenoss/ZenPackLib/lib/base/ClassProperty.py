from ..functions import LOG

class ClassProperty(property):

    """Decorator that works like @property for class methods.

    The @property decorator doesn't work for class methods. This
    @ClassProperty decorator does, but only for getters.

    """
    LOG=LOG

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

