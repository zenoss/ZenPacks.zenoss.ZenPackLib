******************
Component Modeling
******************

This section will cover creation of a custom *Component* subclass, creation of a
relationship to our *NetBotDevice* class, and modeling of the components to fill
the relationship.

In the *Device Modeling* section we added a *temp_sensor_count* attribute to our
NetBotz devices. This isn't very useful. It would be more useful to monitor the
temperature being reported by each of these sensors. So that's what we'll do.
Modeling each sensor as a component allows Zenoss to automatically discover and
monitor sensors regardless of how many a particular device has.

Find Temperature Sensor Attributes
==================================

In the *Device Modeling* section we used `smidump` to extract temperature sensor
information from `NETBOTZV2-MIB`. This will be even more applicable as we decide
what attributes and metrics are available on each sensor. Let's use `smidump`
and `snmpwalk` for a refresher on what's available.

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

Let's now use `snmpwalk` to see what these values look like on our NetBotz
device.

.. code-block:: bash

   snmpwalk 172.17.42.1 1.3.6.1.4.1.5528.100.4.1.1.1

You should see a lot of output that begins with the following::

    NETBOTZV2-MIB::tempSensorId.21604919 = STRING: nbHawkEnc_1_TEMP
    NETBOTZV2-MIB::tempSensorId.1095346743 = STRING: nbHawkEnc_0_TEMP
    NETBOTZV2-MIB::tempSensorId.1382714817 = STRING: nbHawkEnc_2_TEMP1
    NETBOTZV2-MIB::tempSensorId.1382714818 = STRING: nbHawkEnc_2_TEMP2

Note the `21604919` in the first response. This is the SNMP index of the first
temperature sensor, or the first row in the table. I like to then restrict my
snmpwalk results to only show this row with a command like the following.

.. code-block:: bash

   snmpwalk 172.17.42.1 1.3.6.1.4.1.5528.100.4.1.1.1 | grep "\.21604919 ="

Which will show us the value of each column for that one temperature sensor::

    NETBOTZV2-MIB::tempSensorId.21604919 = STRING: nbHawkEnc_1_TEMP
    NETBOTZV2-MIB::tempSensorValue.21604919 = INTEGER: 265
    NETBOTZV2-MIB::tempSensorErrorStatus.21604919 = INTEGER: normal(0)
    NETBOTZV2-MIB::tempSensorLabel.21604919 = STRING: Temperature
    NETBOTZV2-MIB::tempSensorEncId.21604919 = STRING: nbHawkEnc_1
    NETBOTZV2-MIB::tempSensorPortId.21604919 = STRING:
    NETBOTZV2-MIB::tempSensorValueStr.21604919 = STRING: 26.500000
    NETBOTZV2-MIB::tempSensorValueInt.21604919 = INTEGER: 26
    NETBOTZV2-MIB::tempSensorValueIntF.21604919 = INTEGER: 79

Now we have everything we should need to make decisions about what attributes
we should model for our sensors and which would better be collected as
datasources to have thresholds applied and plotted over time on graphs.

My initial thoughts would be to model the following as attributes.

- `tempSensorId`
- `tempSensorEncId` (enclosure ID)
- `tempSensorPortId`

I would then want to collect `tempSensorValueStr` as a datasource because it
offers the best precision. Zenoss is capable of handling numeric strings so we
don't have to collect `tempSensorValue` and divide it by 10 like other systems
might.

Create a Component Subclass
===========================

Use the following steps to create a *NetBotzTemperatureSensor* class with the
attributes discovered above.

1. Update ``$ZP_DIR/zenpack.yaml`` to include the following
   *NetBotzTemperatureSensor* entry in the *classes* section, and the new
   *class_relationships* section.

   .. code-block:: yaml

       classes:
         NetBotzDevice:
           base: [zenpacklib.Device]
           label: NetBotz
           properties:
             temp_sensor_count:
               type: int

         NetBotzTemperatureSensor:
           base: [zenpacklib.Component]
           label: Temperature Sensor
           properties:
             enclosure:
               label: Enclosure

             port:
               label: Port

       class_relationships:
         - NetBotzDevice 1:MC NetBotzTemperatureSensor

   1. It's important to pick class names that will be unique. The best practice
      is to use a short prefix based on the ZenPack's name followed by the type
      of thing the class represents as is being done here.

   2. Both of the new properties should be strings. Since string is the default
      type, we don't need to specify it. This just leaves the label.

      .. note::

         Despite noting above that we always wanted to model the *tempSensorId*
         attribute, we aren't adding an attribute for it here. This is because
         `DeviceComponent` already has both an `id` and `title` attribute that
         wherein we can store the value of *tempSensorId*.

   3. The *class_relationships* section is very important. We could never have
      any temperature sensors in the system if we didn't relate them to
      something else. The *1:MC* between the two class names describes the type
      of relationship. Specifically it says that one *NetBotzDevice* can contain
      many *NetBotzTemperatureSensor* objects. See
      :ref:`zenpacklib-relationships` for more information.

Test TemperatureSensor Class
----------------------------

With our component class defined and relationships setup we can use *zendmd* to
make sure we didn't make any mistakes. Execute the following snippet in
*zendmd*.

.. code-block:: python

   from ZenPacks.training.NetBotz.NetBotzTemperatureSensor import NetBotzTemperatureSensor

   sensor = NetBotzTemperatureSensor('test_sensor_01')
   device = find("Netbotz01")
   device.netBotzTemperatureSensors._setObject(sensor.id, sensor)
   sensor = device.netBotzTemperatureSensors._getOb(sensor.id)
   print sensor
   print sensor.device()

You'll most likely get the following error when executing the above snippet::

    Traceback (most recent call last):
      File "<console>", line 1, in <module>
    AttributeError: netBotzTemperatureSensors

This error is indicating that we have no `netBotzTemperatureSensors`
relationship on the device object. This would seemingly make no sense because we
just added it. The key here is that existing objects like the *Netbotz01* device
don't automatically get new relationships. We have to either delete the device
and add it again, or execute the following in *zendmd* to create the newly-
defined relationship.

.. code-block:: python

   device.buildRelations()
   commit()

Now you can go back and run the original snippet again. You should see the name
of the sensor and device objects printed if everything worked as planned.

Update the Modeler Plugin
=========================

As with the `NetBotzDevice` class, the next step after creating our model class
is to populate it with a modeler plugin. We could create a new modeler plugin to
only capture the temperature sensor components, but we'll update the `NetBotz`
modeler plugin we previously created to model the sensors instead.

1. Edit ``$ZP_DIR/modeler/plugins/training/snmp/NetBotz.py`` and replace its
   contents with the following.

   .. code-block:: python

      from Products.DataCollector.plugins.CollectorPlugin import (
          SnmpPlugin, GetTableMap,
          )


      class NetBotz(SnmpPlugin):
          relname = 'netBotzTemperatureSensors'
          modname = 'ZenPacks.training.NetBotz.NetBotzTemperatureSensor'

          snmpGetTableMaps = (
              GetTableMap(
                  'tempSensorTable', '1.3.6.1.4.1.5528.100.4.1.1.1', {
                      '.1': 'tempSensorId',
                      '.5': 'tempSensorEncId',
                      '.6': 'tempSensorPortId',
                      }
                  ),
              )

          def process(self, device, results, log):
              temp_sensors = results[1].get('tempSensorTable', {})

              rm = self.relMap()
              for snmpindex, row in temp_sensors.items():
                  name = row.get('tempSensorId')
                  if not name:
                      log.warn('Skipping temperature sensor with no name')
                      continue

                  rm.append(self.objectMap({
                      'id': self.prepId(name),
                      'title': name,
                      'snmpindex': snmpindex.strip('.'),
                      'enclosure': row.get('tempSensorEncId'),
                      'port': row.get('tempSensorPortId'),
                      }))

              return rm

   Let's take a closer look at how we changed the modeler plugin.

   1. We added `relname` and `modname` as class attributes.

      These two settings control the meta-data that will automatically be set
      when the `self.relMap` and `self.objectMap` methods are called in the
      `process` method.

      The target `relname` we should use depends on a couple of things.  First,
      all leading uppercase letters of the class name will be converted to
      lowercase, i.e. `NetBotzTemperatureSensor` becomes
      `netBotzTemperatureSensor`.  Second, the  letter "s" is added to the end
      if it is a to-many relationship, i.e.  `netBotzTemperatureSensor` becomes
      `netBotzTemperatureSensors`.

      Setting `relname` to ``netBotzTemperatureSensors`` will cause the
      `self.relMap` call to create a `RelationshipMap` that will be applied to
      the `netBotzTemperatureSensors` relationship defined on the
      `NetBotzDevice` object.

      Setting `modname` to ``ZenPacks.training.NetBotz.TemperatureSensor`` will
      cause the `self.objectMap` calls in the `process` method to create
      `ObjectMap` instances that will be turned into instances of our
      `TemperatureSensor` class.

   2. We're now requesting the *tempSensorEncId* and *tempSensorPortId* columns
      be returned in the SNMP table request results. We'll use these to
      populate their corresponding fields on the `TemperatureSensor` class.

   3. Most of the `process` method has been changed.

      We're now creating a `RelationshipMap` and appending an `ObjectMap` to it
      for each temperature sensor in the results. We use the `self.relMap` and
      `self.objectMap` utility methods to make this easier.

2. Restart *zopectl* and *zenhub* to load the changed module.

Test the Modeler Plugin
-----------------------

We already added the *training.snmp.NetBotz* modeler plugin the the */NetBotz*
device class in an earlier exercise. So we only need to run *zenmodeler* to test
the temperature sensor modeling updates.

1. Run ``zenmodeler run --device=Netbotz01``

   We should see *Changes in configuration applied* near the end of zenmodeler's
   output. The changes referred to should be 14 temperature sensor objects being
   created and added to the device's netBotzTemperatureSensors relationship.

2. Check the *Netbotz01* device in the web interface. The temperature sensors
   should now be visible.
