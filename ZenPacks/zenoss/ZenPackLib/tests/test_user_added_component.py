#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
""" Test user added component
"""

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
class_relationships:
  - HTTPDevice 1:MC HTTPComponent
classes:
  HTTPDevice:
    base: [zenpacklib.Device]
  HTTPComponent:
    base: [zenpacklib.Component]
    label: URL Monitor
    monitoring_templates: [HTTPComponent]
    allow_user_creation: true
    properties:
      DEFAULTS:
        editable: true
      host_or_ip:
        label: Hostname or IP
      port:
        label: Port
      url:
        label: URL
      ssl:
        label: SSL
        type: bool
        default: false
"""

expected_js = "\n(function() {\n        function getPageContext() {\n            return Zenoss.env.device_uid || Zenoss.env.PARENT_CONTEXT;\n        }\n        Ext.ComponentMgr.onAvailable('component-add-menu', function(config) {\n            var menuButton = Ext.getCmp('component-add-menu');\n            menuButton.menuItems.push({\n                xtype: 'menuitem',\n                text: _t('Add URL Monitor') + '...',\n                hidden: Zenoss.Security.doesNotHavePermission('Manage Device'),\n                handler: function() {\n                    var win = new Zenoss.dialog.CloseDialog({\n                        width: 300,\n                        title: _t('Add URL Monitor'),\n                        items: [{\n                            xtype: 'form',\n                            buttonAlign: 'left',\n                            monitorValid: true,\n                            labelAlign: 'top',\n                            footerStyle: 'padding-left: 0',\n                            border: false,\n                            items: [{'fieldLabel': 'Hostname or IP', 'allowBlank': 'true', 'name': 'host_or_ip', 'width': 260, 'id': 'host_or_ip_field', 'xtype': 'textfield'},\n                                    {'fieldLabel': 'Port', 'allowBlank': 'true', 'name': 'port', 'width': 260, 'id': 'port_field', 'xtype': 'textfield'},\n                                    {'fieldLabel': 'URL', 'allowBlank': 'true', 'name': 'url', 'width': 260, 'id': 'url_field', 'xtype': 'textfield'},\n                                    {'fieldLabel': 'SSL', 'allowBlank': 'true', 'name': 'ssl', 'width': 260, 'id': 'ssl_field', 'xtype': 'textfield'},\n                                    ],\n                            buttons: [{\n                                xtype: 'DialogButton',\n                                id: 'HTTPComponent-submit',\n                                text: _t('Add'),\n                                formBind: true,\n                                handler: function(b) {\n                                    var form = b.ownerCt.ownerCt.getForm();\n                                    var opts = form.getFieldValues();\n                                    Zenoss.remote.HTTPComponentRouter.addHTTPComponentRouter(opts,\n                                    function(response) {\n                                        if (response.success) {\n                                            new Zenoss.dialog.SimpleMessageDialog({\n                                                title: _t('URL Monitor Added'),\n                                                message: response.msg,\n                                                buttons: [{\n                                                    xtype: 'DialogButton',\n                                                    text: _t('OK'),\n                                                    handler: function() { \n                                                        window.top.location.reload();\n                                                        }\n                                                    }]\n                                            }).show();\n                                        }\n                                        else {\n                                            new Zenoss.dialog.SimpleMessageDialog({\n                                                message: response.msg,\n                                                buttons: [{\n                                                    xtype: 'DialogButton',\n                                                    text: _t('OK'),\n                                                    handler: function() { \n                                                        window.top.location.reload();\n                                                        }\n                                                    }]\n                                            }).show();\n                                        }\n                                    });\n                                }\n                            }, Zenoss.dialog.CANCEL]\n                        }]\n                    });\n                    win.show();\n                }\n            });\n        });\n    }()\n);\n"

class TestUserAddedComponent(BaseTestCase):
    """Test User added component"""

    def test_component_js(self):
        ''''''
        z = ZPLTestHarness(YAML_DOC)
        cls = z.cfg.classes.get('HTTPComponent')
        self.assertEquals(cls.add_component_js,
                          expected_js,
                          'Unexpected add_component_js Javascript ')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserAddedComponent))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
