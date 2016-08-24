##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from ..helpers.ZenPackLibLog import DEFAULTLOG


class ClassProperty(property):

    """Decorator that works like @property for class methods.

    The @property decorator doesn't work for class methods. This
    @ClassProperty decorator does, but only for getters.

    """
    LOG=DEFAULTLOG

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

