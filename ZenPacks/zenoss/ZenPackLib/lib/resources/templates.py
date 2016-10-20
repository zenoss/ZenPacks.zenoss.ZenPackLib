##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
JS_LINK_FROM_GRID = """
Ext.apply(Zenoss.render, {
    zenpacklib_{zenpack_id_prefix}_entityLinkFromGrid: function(obj, metaData, record, rowIndex, colIndex) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (colIndex != 1 || this.subComponentGridPanel)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="'+obj.uid+'"onClick="Ext.getCmp(\\'component_card\\').componentgrid.jumpToEntity(\\''+obj.uid +'\\', \\''+obj.meta_type+'\\');return false;">'+obj.title+'</a>';
        } else {
            return obj.title;
        }
    },

    zenpacklib_{zenpack_id_prefix}_entityTypeLinkFromGrid: function(obj, metaData, record, rowIndex, colIndex) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (colIndex != 1 || this.subComponentGridPanel)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="javascript:Ext.getCmp(\\'component_card\\').componentgrid.jumpToEntity(\\''+obj.uid+'\\', \\''+obj.meta_type+'\\');">'+obj.title+'</a> (' + obj.class_label + ')';
        } else {
            return obj.title;
        }
    }

});

ZC.ZPL_{zenpack_id_prefix}_ComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.text == 'Components';
                }

                // Zenoss < 4.2 / ExtJS3
                return n.text == 'Components';
            });

        var component_card = Ext.getCmp('component_card');

        if (components_node.data) {
            // Zenoss >= 4.2 / ExtJS4
            component_card.setContext(components_node.data.id, meta_type);
        } else {
            // Zenoss < 4.2 / ExtJS3
            component_card.setContext(components_node.id, meta_type);
        }

        component_card.selectByToken(uid);

        var component_type_node = components_node.findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.id == meta_type;
                }

                // Zenoss < 4.2 / ExtJS3
                return n.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});

Ext.reg('ZPL_{zenpack_id_prefix}_ComponentGridPanel', ZC.ZPL_{zenpack_id_prefix}_ComponentGridPanel);

Zenoss.ZPL_{zenpack_id_prefix}_RenderableDisplayField = Ext.extend(Zenoss.DisplayField, {
    constructor: function(config) {
        if (typeof(config.renderer) == 'string') {
          config.renderer = eval(config.renderer);
        }
        Zenoss.ZPL_{zenpack_id_prefix}_RenderableDisplayField.superclass.constructor.call(this, config);
    },
    valueToRaw: function(value) {
        if (typeof(value) == 'boolean' || typeof(value) == 'object') {
            return value;
        } else {
            return Zenoss.ZPL_{zenpack_id_prefix}_RenderableDisplayField.superclass.valueToRaw(value);
        }
    }
});

Ext.reg('ZPL_{zenpack_id_prefix}_RenderableDisplayField', 'Zenoss.ZPL_{zenpack_id_prefix}_RenderableDisplayField');

""".strip()



SETUP_PY = """
################################
# These variables are overwritten by Zenoss when the ZenPack is exported
# or saved.  Do not modify them directly here.
# NB: PACKAGES is deprecated
NAME = "{zenpack_name}"
VERSION = "1.0.0dev"
AUTHOR = "Your Name Here"
LICENSE = ""
NAMESPACE_PACKAGES = {namespace_packages}
PACKAGES = {packages}
INSTALL_REQUIRES = [ZenPacks.zenoss.ZenPackLib]
COMPAT_ZENOSS_VERS = ""
PREV_ZENPACK_NAME = ""
# STOP_REPLACEMENTS
################################
# Zenoss will not overwrite any changes you make below here.

from setuptools import setup, find_packages


setup(
    # This ZenPack metadata should usually be edited with the Zenoss
    # ZenPack edit page.  Whenever the edit page is submitted it will
    # overwrite the values below (the ones it knows about) with new values.
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    license=LICENSE,

    # This is the version spec which indicates what versions of Zenoss
    # this ZenPack is compatible with
    compatZenossVers=COMPAT_ZENOSS_VERS,

    # previousZenPackName is a facility for telling Zenoss that the name
    # of this ZenPack has changed.  If no ZenPack with the current name is
    # installed then a zenpack of this name if installed will be upgraded.
    prevZenPackName=PREV_ZENPACK_NAME,

    # Indicate to setuptools which namespace packages the zenpack
    # participates in
    namespace_packages=NAMESPACE_PACKAGES,

    # Tell setuptools what packages this zenpack provides.
    packages=find_packages(),

    # Tell setuptools to figure out for itself which files to include
    # in the binary egg when it is built.
    include_package_data=True,

    # Indicate dependencies on other python modules or ZenPacks.  This line
    # is modified by zenoss when the ZenPack edit page is submitted.  Zenoss
    # tries to put add/delete the names it manages at the beginning of this
    # list, so any manual additions should be added to the end.  Things will
    # go poorly if this line is broken into multiple lines or modified to
    # dramatically.
    install_requires=INSTALL_REQUIRES,

    # Every ZenPack egg must define exactly one zenoss.zenpacks entry point
    # of this form.
    entry_points={{
        'zenoss.zenpacks': '%s = %s' % (NAME, NAME),
    }},

    # All ZenPack eggs must be installed in unzipped form.
    zip_safe=False,
)
""".lstrip()
