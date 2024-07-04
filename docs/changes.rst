.. _changes:

#######
Changes
#######

Version 2.1
===========

Release 2.1.5
-------------

Fixes

* Fix monitoring templates representation in infrastructure view for devices created via ZPL that have -addition templates (ZPS-8945)
* Fix ZenPackLib-based ZenPack removal if the expected suborganizer does not exist (ZPS-8863)

Release 2.1.4
-------------

Fixes

* Fix dependencies, dynamic view and impact relations for multi-YAML ZenPacks (ZPS-8835)

Release 2.1.3
-------------

Fixes

* Improve and correct ZenPackLib the -replacement and -addition templates handling (ZPS-8617)
* Improve ZenPackLib efficiency during loading multiple YAML files (ZPS-8777)


Release 2.1.2
-------------

Fixes

* Allow Class.filter_hide_from option to also work for contained components (ZPS-5107)


Release 2.1.1
-------------

Fixes

* Fix infinite recursion in yaml_load when no yaml files present (ZPS-3880)
* Update default value of threshold's escalationCount in the documentation (ZPS-4031)
* Ensure device class removal during various upgrade scenarios (ZPS-3906)
* Correct links from ZPL-provided renderers to honor the CSE_VIRTUAL_ROOT (ZEN-30544)


Release 2.1.0
-------------

Features

* Support additional GraphPoint subclasses (ZPS-855)
* EventClassInstance, OSProcessClass now support zProperties (ZPS-3636)
* EventClass, OSProcessOrganizer now support zProperties (ZPS-3189, ZPS-3190)
* Add "optional" field for thresholds (ZPS-1666)
* Add support for ZProperty "label" and "description" fields (ZPS-747)

Fixes

* Support Graph "descripton" attribute (ZPS-3696) 
* Support ABSOLUTE RRD type (ZPS-1733)
* All organizer classes respect the "create", "remove", and "reset" attributes (ZPS-810)
* Refactor unit tests to avoid build issues (ZPS-3035)
* Fix invalid RRD datapoint types (ZPS-1734)
* Update documentation for datapoint description (ZPS-1971)


Version 2.0
===========

Backwards Incompatible Changes

* Any installed ZenPacks using older versions of zenpacklib.py will continue to function unchanged.
* Using version 2.0 is slightly different.  The __init__.py file import statements should now contain the following:

.. code-block:: python

    from ZenPacks.zenoss.ZenPackLib import zenpacklib
    CFG = zenpacklib.load_yaml()
    schema = CFG.zenpack_module.schema

.. note::

  For better performance, specify the explicit path(s) to your yaml file.  e.g. *CFG = zenpacklib.load_yaml([os.path.join(os.path.dirname(__file__), "zenpack.yaml")])*

* zProperties will not be updated automatically on existing device classes.  These should be handled on a case basis by using migrate scripts.

Release 2.0.9
-------------

Fixes

* Fix incorrect removal of organizers such as /Status event class (ZPS-2660)


Release 2.0.8
-------------

Fixes

* Improve component grid loading performance. (ZPS-2033)
* Fix potential POSKeyError when modeling devices. (ZPS-2371)
* Improved support for multi-line text in YAML (ZPS-444)
* Improved component path reporters for mixin platform proxy classes (ZPS-1262)
* Fix zenpacklib.TestCase when Impact >= 5.2.2 is installed (ZPS-2011)


Release 2.0.7
-------------

Fixes

* Fix all the zenpacklib dump options. (ZPS-1601)
* Implement template replacement and addition on device level. (ZPS-1704)


Release 2.0.6
-------------

Fixes

* Fix mishandling of 0/clear severity (ZPS-1454)
* Fix attempts to load non-YAML files (ZPS-1483)
* Use appropriate sequence for graph points (ZPS-1361)
* Fix GUI ZenPack export of objects.xml (ZPS-1589)
* Fix datapoint alias shorthand export handling (ZPS-1589)


Release 2.0.5
-------------

Fixes

* Fix version reported by "zenpacklib --version". (ZPS-1145)
* Template backups use YYYYMMDDHHMM format instead of unix timestamp.
* Fix failure to back up customized templates during upgrade from pre-2.0 ZenPacks. (ZPS-1195)
* Fix failure to back up customized templates during upgrade. (ZPS-1176)


Release 2.0.4
-------------

Fixes

* Fix for missing Dynamic View on some components (ZPS-703)
* Fix for failure to create device classes in uncommon case (ZPS-1012)
* Fix event class mappings with mismatched id and eventClassKey (ZPS-1016)


Release 2.0.3
-------------

Fixes

* Preserve ordering when loading multiple YAML files (ZPS-921)
* Fix setting of zProperty values when loading multiple YAML files. (ZPS-925)


Release 2.0.2
-------------

Fixes

* Only create a monitoring template if it changes or does not exist (ZPS-570)
* Ensure display of ZPL classes such as OSProcess in GUI elements (ZPS-572, ZPS-651)


Release 2.0.1
-------------

Fixes

* Ensure all datapoint attributes export to YAML (ZEN-26593)
* Ensure subsquent installations complete if ZP install fails (ZPS-627)


Release 2.0.0
-------------

Features

* zenpacklib is now an installable ZenPack
* Added Event Class definitions (ZEN-24903)
* Support multiple YAML file loading
* Support directory loading for YAML
* Support log verbosity per ZenPack
* Centralized, per-derived ZenPack logging
* Improved template change detection during install
* Improved type handling of yaml loaded/dumped data
* Support centralized use of older monolithic zenpacklib.py
* Added --optimize parameter to zenpacklib
* Dramatically enhanced unit testing
* Support for using enum proprty with datapoint properties (string/int mapping)
* Ability to call /opt/zenoss/bin/zenpacklib
* Added ZPLCommand to handle running zenpacklib with arguments
* Separated zenpacklib.py classes into module files
* Ability to use ZenPack-provided zenpacklib module
* Added support for Process Class definitions
* Deprecated support for python-based "yaml" specifications
* Support for threshold graphpoint legend and color (ZEN-24904)
* Ability to specify an initial sort column on a component grid
* Performance enhancments for grid display of metrics (ZEN-23870)
* Support for Device Link Providers
* Added troubleshooting aid for easily saving function data(writeDataToFile)
* Avoid setting zProperties on existing device class (ZPS-137)

Fixes

* Fix handling of boolean datasource options (ZEN-25315)
* Merge Detail View groups into 'Overview' group (ZEN-24759)
* Ensure that component detail pane honors relation "details_display" (ZEN-24762)
* Update ZenPackLib (ZP) Unit tests (ZEN-24599)
* Ensure that subcomponent nav JS uses relationship label if provided (ZEN-24305)
* Ensure ability to set label or a subclass on an inherited relationship (ZEN-24303)
* Ensure inherited relationship name overrides displayed in details pane (ZEN-24302)
* Ensure extra_paths is working (ZEN-24268)
* Ensure that 'extra_params' get applied to template-related objects (ZEN-24083)
* Improved handling of "custom columns exceed 750 pixels" warnings (ZEN-24022)
* Avoid patching _relations on ZPL-derived subclasse (ZEN-24018)
* Incorrect display of nested custom-named relations (ZEN-23995)
* Fix missing relations (ZEN-23968)
* Fix maximum recursion depth exceeded traceback in get_facets (ZEN-23840)
* Allow specifying properties on an inherited relationship (ZEN-23763)
* Zenpacklib logging  more helpful and less scary (ZEN-23621)
* Batch buildRelations() commits during ZenPack installs (ZEN-22655)
* Support adding devtypes (ZEN-22366)
* Improve ImportError logging in class files (ZEN-22927)
* Ensure non-cached datapoints return current value (ZEN-22288)
* Fix issue when setting datapoint_cached to False (ZEN-22287)
* Set all component property details to correct Python type (ZEN-22057)
* Honor relationship label containing component overrides in component (ZEN-21966)
* Prevent attempts to process relationships not in class_relationships (ZEN-21927)
* Ensure component display properties honored (ZEN-19798)
* Support setting datapoint alias as string (ZEN-19486)
* Check datapoint consistency in template graph points and thresholds (ZEN-19461)
* Check/warn against reserved keyword use (ZEN-19460)
* getRRDTemplateName can return label of base class (ZEN-19025)
* Ensure catalog creation respects spec property indexes (ZEN-18269)
* Ensure device classes can be removed properly (ZEN-18134)
* Ensure that datapoint alias keys do not exceed 31 chars (ZEN-17950)
* Log obscure error with ill-defined relationships (ZEN-16701)
* Fix handling of !ZenPackSpec tag in yaml definitions


Version 1.1
===========

Release 1.1.0
-------------

Features

* Add dynamicview_weight class field.
* Add overridable getDynamicViewGroup method to generated classes.
* Class icons beginning with / will be treated as absolute URL paths.
* Improve performance of entity properties in component grids.
* Simplify what device status means to critical event(s) in /Status.
* Improve grid performance with streamlined info adapters
* Add base class proxies for all platform component classes.

Fixes

* Fix tracebacks caused by property datapoint_cached. (ZEN-22287)
* Fix 'display' property to honor initialized values. (ZEN-19798)
* Fix wrong template displayed for subclassed component (ZEN-19025)
* Fix inheritance for displayed relationship properties (ZEN-23763)
* Fix traceback in get_facets (maximum recursion depth exceeded) (ZEN-23840)
* Ensure that 'extra_params' get applied to template-related objects (ZEN-24083)
* Fix for lost relationships on ZPL-derived subclasses (ZEN-24018)
* Fix for extra_paths failures (ZEN-24268)
* Fix to gracefully handle unknown relationship properties (ZEN-21927)
* Ensure that inherited relationship names are used (ZEN-24302)
* Ensure that inherited relationship names are displayed consistently (ZEN-24303)
* Ensure that subcomponent nav JS uses relationship label if given (ZEN-24305)
* Fix for setting of zProperty values before zProperty exists
* Fix "unexpected keyword default" message
* Fix support for extending platform component classes. (ZEN-25559)

Documentation

* Fix YAML reference for dynamicview_group class field.
* Fix documentation of default value for dynamicview_views.
* Document new component class proxies such as IpInterface and FileSystem.


Version 1.0
===========

Release 1.0.13
--------------

Fixes

* Honor graph and graphpoint ordering in zenpack.yaml. (ZEN-23590)


Release 1.0.12
--------------

Fixes 

* Fix tracebacks due to stale catalog entries. (ZEN-22592)
* Fix hidden zenpacklib errors due to unitialized logging.
* Prevent setting values on undefined zProperties.
* Drastically reduce catalog creation time.

Documentation

* Add missing types to zProperty documentation.


Release 1.0.11
--------------

Fixes

* Only show Dynamic View for components that support it. (ZEN-22391)
* Fix created __init__.py to work with zenpacklib.TestCase. (ZEN-22387)


Release 1.0.10
--------------

Fixes

* Fix display of nested component container-of-container. (ZEN-21897)

Documentation

* Fix graphpoint lineType documentation.


Release 1.0.9
-------------

Fixes

* Fix non-containing setters with standard device types. (ZEN-21747)
* Fix filtering of YAML templates in ZenPack export. (ZEN-21697)
* Prevent backups of unchanged monitoring templates. (ZEN-21719)


Release 1.0.8
-------------

Fixes

* Fix various dump_templates issues. (ZEN-18824)


Release 1.0.7
-------------

Fixes

* Fix dynamicview_relations type issue.


Release 1.0.6
-------------

Fixes

* Make YAML-defined JMX datasources work. (ZEN-21467)


Release 1.0.5
-------------

Fixes

* Fix KeyError on install after adding device class. (ZEN-21461)


Release 1.0.4
-------------

Features

* TestCase: Automatically load ZenPack's configure.zcml if it exists.
* Default to checkbox renderer for boolean properties. (ZEN-19585)

Fixes

* TestCase: Fix transaction error without DynamicView or Impact installed.
* Fix entity grid renderer to make it possible to click links into a new tab. (ZEN-19922)
* Fix enum property type. (ZEN-20769)


Release 1.0.3
-------------

Fixes

* Fix testing of SNMP datasources by converting OIDs to string.
* Fix for inherited relationships and properties not appearing in UI.


Release 1.0.2
-------------

Fixes

* Log YAML errors more concisely instead of full traceback. (ZEN-17681)
* Fix "[Object]" details panel display for custom renderers. (ZEN-17732)
* Fix handling of nested device class remove field.
* Fix KeyError when removing non-existent device class.
* Fix handling of datapoint rrdtype. (ZEN-18188)


Release 1.0.1
-------------

Features

* Add Class.extra_paths for controlling object path indexing.
* Add Class.filter_hide_from option.

Fixes

* Fix handling of class _properties and _relationships.
* Prefix ExtJS components to avoid conflicting zenpacklib versions.
* Fix handling of Class property types.
* Fix py_to_yaml for ZenPacks that subclass ZenPack.
* Remove superfluous YAML type hints from py_to_yaml conversion.
* Fix "Unable to find TEMPLATE_ID" installation error.
* Base component status on events in /Status event class.
* Fix removal of objects when PyYAML isn't installed.


Release 1.0.0
-------------

Features

* Added ability to define ZenPack with YAML.
* Added support for model classes and relationships.
* Added support for zProperties.
* Added support for device classes.
* Added support for monitoring templates.
* Added *create* command for creating ZenPacks from the command line.
* Added *lint* command to check YAML for correctness.
* Added *class_diagram* command to create yUML class diagram from YAML.
* Added *dump_templates* command to export monitoring templates to YAML.
* Added *py_to_yaml* command to convert old Python specs to YAML.
* Added *version* command to print zenpacklib's version.

Documentation

* Added first pass at documentation (`<http://zenpacklib.zenoss.com/>`_).
