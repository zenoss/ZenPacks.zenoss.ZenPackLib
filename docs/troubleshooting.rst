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
