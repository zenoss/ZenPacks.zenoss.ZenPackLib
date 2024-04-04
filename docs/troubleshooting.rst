.. _troubleshooting:

###############
Troubleshooting
###############

Using the Python Debugger
=========================

One of the most powerful tools when debugging the Python portions of a ZenPack
is the Python debugger (*pdb*). With *pdb* you can set breakpoints in your code.
When the breakpoints are hit, you get a *(pdb)* prompt that has full access to
examine the stack and any local or global variables.

To set a breakpoint in your code you add the following line.

.. code-block:: python

    import pdb; pdb.set_trace()

As with any code change, you must restart the Zenoss process that executes the
code in question.

*************
Pickling data
*************

ZenPackLib v2.0 also adds a decorator, *writeDataToFile*, that can be used to save real-world results that your plugins will be processing.  This data can then be used to determine why a plugin is not behaving as expected or to create your own unit tests.

In order to use this decorator, import it from the ZenPackLib zenpack:

.. code-block:: python

    from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import writeDataToFile

Then use as a decorator for your plugin's process function.  *writeDataToFile* is generic and can be used on any python function or class method.  It does not pickle file or logger objects.  You can also specify keywords which, when matched against an object's attributes, will cause an object not to be pickled.

.. code-block:: python

    class MyPlugin(PythonPlugin):
        @writeDataToFile(keywords=['zCommandPassword', 'windows_password'])
        def process(self, device, results, log):
            '''Perform device specific processing on modeler plugin results'''
            rm = self.relMap()
            # Add data to relationship map
            rm.attr1 = results.attr1
            rm.attr2 = results.attr2
            return rm


The save functionality is disabled unless you use the *ZPL_DUMP_DATA* environment variable.  Be sure to only use in limited runs or you will end up with a large number of pickle files.

.. code-block:: text

    $ export ZPL_DUMP_DATA=1; zenmodeler run -d mydevice; unset ZPL_DUMP_DATA


The pickle file(s) will be written to your */tmp* folder using the class name and function name with current timestamp.  Using the definition from above, the file name would be *MyPlugin_process_XXXXXX.pickle* where *XXXXXX* is the time at which the data was processed.  Assuming *device* has either a zCommandPassword or windows_password attribute, the *self*, *device*, and *log* objects will not be pickled.

************
Known Issues
************

* When dumping existing event classes using the zenpacklib tool with *--dump-event-classes* option, some transforms and/or explanations may show as either unformatted text within double quotes or as formatted text within single quotes.  This is due to how the python yaml package handles strings.  Either of these two formats are acceptable when used in zenpack.yaml.
* ZenPacks using earlier verisons of ZenPackLib logged template changes to the console during installation.  These messages might have disturbed some users due to their wording and logging as "ERROR" status.  These have been revised and now log as informational, but the old format will be displayed when upgrading from a pre-ZenPacklib 2.0 ZenPack to one using the latest version.  Subsequent installs will use the newer format.
* ZenPackLib 2.1.3 has an issue with building impact relations, dependencies, and dynamic view for multi-YAML ZenPacks. We recommend upgrading to 2.1.4 or newer versions. After the upgrade from the 2.1.3 version the additional command **zenimpactgraph run --update** should be executed to fix broken impact relations.
