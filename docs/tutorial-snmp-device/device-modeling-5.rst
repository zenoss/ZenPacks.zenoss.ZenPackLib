***************
Device Modeling
***************

This section will cover creation of a custom *Device* subclass and modeling of
device attributes.

For purposes of this example, we'll add a *temp_sensor_count* attribute to
NetBotz devices. We'll walk through adding the attribute to the model, modeling
it from the device, and displaying it in the overview screen for NetBotz
devices.

Starting in this section we'll be working with files within the NetBotz
ZenPack's directory. To keep the path names short, I'll assume the *$ZP_TOP_DIR*
and *$ZP_DIR* environment variables have been set as follows.

.. code-block:: bash

    export ZP_TOP_DIR=/z/ZenPacks.training.NetBotz
    export ZP_DIR=$ZP_TOP_DIR/ZenPacks/training/NetBotz

Create the NetBotzDevice Class
==============================

A *Device* subclass should not be confused with a *device class*. In the
previous section we created the /NetBotz device class from the web interface.
Creating a *Device* subclass means to extend the actual Python class of a
*Device* object. You'd do this to add new attributes, methods or relationships
to special device types.

Use the following steps to create a *NetBotzDevice* class with a new attribute
called *temp_sensor_count*.

1. Update ``$ZP_DIR/zenpack.yaml`` to contain following contents.

   .. code-block:: yaml

       name: ZenPacks.training.NetBotz

       classes:
         NetBotzDevice:
           base: [zenpacklib.Device]
           label: NetBotz
           properties:
             temp_sensor_count:
               type: int

       device_classes:
         /NetBotz:
           zProperties:
             zPythonClass: ZenPacks.training.NetBotz.NetBotzDevice
             zSnmpMonitorIgnore: false
             zCollectorPlugins:
               - training.snmp.NetBotz
               - zenoss.snmp.NewDeviceMap
               - zenoss.snmp.DeviceMap
               - zenoss.snmp.InterfaceMap

   1. The *name* field is mandatory and must match the full Python module name
      of your ZenPack.

   2. The classes section is where we define extensions to the standard Zenoss
      model. In this case we're creating a special device type called
      *NetBotzDevice* because we want to add a new property called
      *temp_sensor_count*. See :ref:`classes-and-relationships` for more
      information on defining classes.

   3. The *device_classes* section allows us to also configure the `/NetBotz`
      device class in YAML. Note that we're configuring the same options that
      we already set through the web interface. You can set them either way, but
      once you add a device class to zenpack.yaml you'll likely find its easier
      to maintain all of the information in one place.

      The most important property we're setting on the `/NetBotz` device class
      is `zPythonClass`. This is required so that the new `NetBotzDevice` class
      we've defined will be used for devices in this device class.

      You'll also note that we're adding *training.snmp.NetBotz* to the list of
      modeler plugins (*zCollectorPlugins*) even though it doesn't yet exist.
      This is safe to do, and we'll shortly be creating the modeler plugin.

2. Reinstall the ZenPack to have the device class changes made.

   .. code-block:: bash

      zenpack --link --install $ZP_TOP_DIR

3. Restart *Zope* process so the web interface can load our new module.

   .. code-block:: bash

      serviced service restart zope

4. Reset the Python class of our existing device.

   Run ``zendmd`` and execute the following snippet.

   .. code-block:: python

      device = find("Netbotz01")
      print device.__class__

   You should see *<class 'Products.ZenModel.Device.Device'>*. We see this
   instead of the Python class we just created because the *zPythonClass*
   property is only used when a new device is created in a device class, or
   when a device is moved into a device class with a differing *zPythonClass*
   value.

   So we have two options for getting our NetBotz device to use the new Python
   class we created. We can either delete the device and add it back, or move
   it to a different device class and back. Actually, there's a third option
   that I use most frequently to solve this problem. I move it into the same
   device class using *zendmd*. Execute the following snippet within *zendmd*
   to reset the device's Python class.

   .. code-block:: python

      dmd.Devices.NetBotz.moveDevices('/NetBotz', 'Netbotz01')
      commit()

      device = find("Netbotz01")
      print device.__class__

   Now you should see *<class 'ZenPacks.training.NetBotz.NetBotzDevice'>*
   printed. This confirms that our *Device* subclass works, and that we've
   configure *zPythonClass* correctly for the */NetBotz* device class.

Find Temperature Sensor Count
=============================

Before we can write a modeler plugin to populate our new *temp_sensor_count*
attribute, we need to figure out how to get the information. There are a few
ways we could approach this. One way is to use that NETBOTZV2-MIB as a
reference to see if we can find anything about temperature sensors
specifically.

Find temperature information in NETBOTZV2-MIB using the following command.

.. code-block:: bash

   smidump -f identifiers /usr/share/snmp/mibs/NETBOTZV2-MIB.mib | egrep -i temp

You should see the following in the output::

    NETBOTZV2-MIB tempSensorTable        table   1.3.6.1.4.1.5528.100.4.1.1
    NETBOTZV2-MIB tempSensorEntry        row     1.3.6.1.4.1.5528.100.4.1.1.1
    NETBOTZV2-MIB tempSensorId           column  1.3.6.1.4.1.5528.100.4.1.1.1.1
    NETBOTZV2-MIB tempSensorValue        column  1.3.6.1.4.1.5528.100.4.1.1.1.2
    NETBOTZV2-MIB tempSensorErrorStatus  column  1.3.6.1.4.1.5528.100.4.1.1.1.3
    NETBOTZV2-MIB tempSensorLabel        column  1.3.6.1.4.1.5528.100.4.1.1.1.4
    NETBOTZV2-MIB tempSensorEncId        column  1.3.6.1.4.1.5528.100.4.1.1.1.5
    NETBOTZV2-MIB tempSensorPortId       column  1.3.6.1.4.1.5528.100.4.1.1.1.6
    NETBOTZV2-MIB tempSensorValueStr     column  1.3.6.1.4.1.5528.100.4.1.1.1.7
    NETBOTZV2-MIB tempSensorValueInt     column  1.3.6.1.4.1.5528.100.4.1.1.1.8
    NETBOTZV2-MIB tempSensorValueIntF    column  1.3.6.1.4.1.5528.100.4.1.1.1.9

You'll also see another *node* and a bunch of *notification* entries. These are
related to SNMP traps, and not relevant to what we're interested in polling
right now.

What we see here is that there isn't a single OID we can request that will tell
us the number of temperature sensors. We're going to have to do an *snmpwalk*
of the table then count how many rows are in the response. Specifically we want
to remember the name and OID for the *row*: *tempSensorEntry*. Due to the
hierarchical nature of a MIBs representation this is the most specific OID that
will return the data we need.

.. code-block:: bash

   snmpwalk 172.17.42.1 1.3.6.1.4.1.5528.100.4.1.1.1

You'll see a lot of output that starts with::

    NETBOTZV2-MIB::tempSensorId.21604919 = STRING: nbHawkEnc_1_TEMP
    NETBOTZV2-MIB::tempSensorId.1095346743 = STRING: nbHawkEnc_0_TEMP
    NETBOTZV2-MIB::tempSensorId.1382714817 = STRING: nbHawkEnc_2_TEMP1
    NETBOTZV2-MIB::tempSensorId.1382714818 = STRING: nbHawkEnc_2_TEMP2
    NETBOTZV2-MIB::tempSensorId.1382714819 = STRING: nbHawkEnc_2_TEMP3
    NETBOTZV2-MIB::tempSensorId.1382714820 = STRING: nbHawkEnc_2_TEMP4
    NETBOTZV2-MIB::tempSensorId.1382714833 = STRING: nbHawkEnc_3_TEMP1
    NETBOTZV2-MIB::tempSensorId.1382714834 = STRING: nbHawkEnc_3_TEMP2
    NETBOTZV2-MIB::tempSensorId.1382714865 = STRING: nbHawkEnc_1_TEMP1
    NETBOTZV2-MIB::tempSensorId.1382714866 = STRING: nbHawkEnc_1_TEMP2
    NETBOTZV2-MIB::tempSensorId.1382714867 = STRING: nbHawkEnc_1_TEMP3
    NETBOTZV2-MIB::tempSensorId.1382714868 = STRING: nbHawkEnc_1_TEMP4
    NETBOTZV2-MIB::tempSensorId.2169088567 = STRING: nbHawkEnc_3_TEMP
    NETBOTZV2-MIB::tempSensorId.3242830391 = STRING: nbHawkEnc_2_TEMP

What you're seeing above is the tempSensorId column for all 14 rows in the
tempSensorTable. Continuing on you will see 14 rows for each of the other
columns in the table.

Create a Modeler Plugin
=======================

The next step is to build a modeler plugin. A modeler plugin's responsibility
reach out into the world, gather data, and plug it into the attributes and
relationships of our model classes. In this example, this means to make the
SNMP requests necessary to determine how many temperature sensors a NetBotz
device has, and populate our *temp_sensor_count* attribute with the result.

Use the following steps to create our modeler plugin.

1. Make the directory that'll contain our modeler plugin.

   .. code-block:: bash

      mkdir -p $ZP_DIR/modeler/plugins/training/snmp

   Note that we're using our ZenPack's *training* namespace, then *snmp*.
   This is the recommended approach to make it clear what protocol the
   modeler plugin will use, and to avoid our modeler plugin conflicting with
   one from someone else's ZenPack.

2. Create *__init__.py* or *dunder-init* files.

   .. code-block:: bash

      touch $ZP_DIR/modeler/__init__.py
      touch $ZP_DIR/modeler/plugins/__init__.py
      touch $ZP_DIR/modeler/plugins/training/__init__.py
      touch $ZP_DIR/modeler/plugins/training/snmp/__init__.py

   These empty *__init__.py* files are mandatory if we ever expect Python to
   import modules from these directories.

3. Create ``$ZP_DIR/modeler/plugins/training/snmp/NetBotz.py`` with the
   following contents.

   .. code-block:: python

      from Products.DataCollector.plugins.CollectorPlugin import (
          SnmpPlugin, GetTableMap,
          )


      class NetBotz(SnmpPlugin):
          snmpGetTableMaps = (
              GetTableMap(
                  'tempSensorTable', '1.3.6.1.4.1.5528.100.4.1.1.1', {
                      '.1': 'tempSensorId',
                      }
                  ),
              )

          def process(self, device, results, log):
              temp_sensors = results[1].get('tempSensorTable', {})

              return self.objectMap({
                  'temp_sensor_count': len(temp_sensors.keys()),
                  })

   1. Start by importing SnmpPlugin and GetTableMap from Zenoss. SnmpPlugin
      will handle all of the SNMP requests for us and present the results in
      a format we can easily work with. GetTableMap will be used here because
      we need to request an SNMP table rather than specific OIDs.

   2. Our NetBotz class extends SnmpPlugin. Note that the NetBotz class name
      must match the filename (module name) of the modeler plugin.

   3. By defining snmpGetTableMaps as a tuple or list on our class we can add
      a GetTableMap object that requests that 1.3.6.1.4.1.5528.100.4.1.1.1 row
      OID and specify that we only want to get the first (.1) column and name
      it tempSensorId.

   4. The *process* method will receive a two-element tuple containing the SNMP
      request results in the *request* parameter. The first elememt,
      *results[0]*, of this tuple would be any direct OID gets of which we
      didn't request any in this plugin. The second element, *results[1]* will
      contain a dictionary of the table results. In this case *results[1]*
      would look like the following.

      .. code-block:: python

         {
             'tempSensorTable': {
                 '21604919': 'nbHawkEnc_1_TEMP',
                 '1095346743': 'nbHawkEnc_0_TEMP',
                 '1382714817': 'nbHawkEnc_2_TEMP1',
                 '1382714818': 'nbHawkEnc_2_TEMP2',
                 '1382714819': 'nbHawkEnc_2_TEMP3',
                 '1382714820': 'nbHawkEnc_2_TEMP4',
                 '1382714833': 'nbHawkEnc_3_TEMP1',
                 '1382714834': 'nbHawkEnc_3_TEMP2',
                 '1382714865': 'nbHawkEnc_1_TEMP1',
                 '1382714866': 'nbHawkEnc_1_TEMP2',
                 '1382714867': 'nbHawkEnc_1_TEMP3',
                 '1382714868': 'nbHawkEnc_1_TEMP4',
                 '2169088567': 'nbHawkEnc_3_TEMP',
                 '3242830391': 'nbHawkEnc_2_TEMP',
             },
         }

   5. We then extract just the *tempSensorTable* results into *temp_sensors*
      to make the next *return* line a bit easier to understand.

   6. We then return a dictionary that sets the *temp_sensor_count* key's
      value to the number of keys in *temp_sensors*. Actually we return a
      dictionary that's been wrapped in an ObjectMap by the modeler plugin's
      *objectMap* utility method.

      The *process* method within all modeler plugins must return one of the
      following types of data.

      - None (makes no changes to the model)
      - ObjectMap (to apply directly to the device that's being modeled)
      - RelationshipMap (to apply to a relationship within the device)
      - A list containing zero or more ObjectMap and/or RelationShipMap objects.

      An *ObjectMap* is simply a `dict` wrapped with some meta-data. A
      *RelationshipMap* is a `list` wrapped with some meta-data and containing
      zero or more *ObjectMap* instances.

4. Restart *Zope* and *zenhub* to load the new module.

   .. code-block:: bash

      serviced service restart zope
      serviced service restart zenhub


Test the Modeler Plugin
-----------------------

Now that we've created and enabled a basic modeler plugin, we should test it.

1. Remodel the NetBotz device.

   You can do this from the web interface, but I usually use the command line
   because it can be easier to work with if further debugging is necessary.

   .. code-block:: bash

      zenmodeler run --device=Netbotz01

2. Execute the following snippet in *zendmd*.

   .. code-block:: python

      device = find("Netbotz01")
      print device.temp_sensor_count

   You should see *14* printed as the number of temperature sensors.

Change the Device Overview
==========================

The next step will be to show the number of temperature sensors to users of the
web interface. We'll replace the *Memory/Swap* field in the top-left box of the
device overview page with the count of temperature sensors.

Follow these steps to customize the device Overview page.

1. Create a directory to store our ZenPack's JavaScript.

   .. code-block:: bash

      mkdir -p $ZP_DIR/resources

2. Create ``$ZP_DIR/resources/device.js`` with the following contents.

   .. code-block:: javascript

      Ext.onReady(function() {
          var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_summary';
          Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
              var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);
              overview.removeField('memory');

              overview.addField({
                  name: 'temp_sensor_count',
                  fieldLabel: _t('# Temperature Sensors')
              });
          });
      });

   1. Wait for Ext to be ready.
   2. Find the overview summary panel (top-left on Overview page)
   3. Remove the *memory* field.
   4. Add our *temp_sensor_count* field.

   Zenoss uses ExtJS as its JavaScript framework. You can find more in ExtJS's
   documentation about manipulating objects in this way.

Test the Device Overview
------------------------

That's it. We can restart *zopectl* and navigate to our NetBotz device's
overview page in the web interface. You should see ``# Temperature Sensors``
label with a value of 14 at the bottom of the top-left panel.
