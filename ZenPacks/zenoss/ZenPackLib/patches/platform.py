##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenUtils.Utils import monkeypatch

# ZPS-561 Make sure our instances are included in GUI tabs
from Products.Zuul.facades.processfacade import ProcessFacade
from Products.Zuul.facades.servicefacade import ServiceFacade

@property
def get_instance_class(ob):
    return ob._types

ProcessFacade._types = ('Products.ZenModel.OSProcess.OSProcess')
ProcessFacade._instanceClass = get_instance_class

ServiceFacade._types = ('Products.ZenModel.Service.Service')
ServiceFacade._instanceClass = get_instance_class
