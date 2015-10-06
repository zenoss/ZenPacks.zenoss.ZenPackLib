******************
Add a Device Class
******************

To support adding our special `WundergroundDevice` devices that we defined in
``zenpack.yaml`` to Zenoss we must create a new device class. This will give us
control of the `zPythonClass` configuration property that defines what type of
devices will be created. It will also allow us to control what modeler plugins
and monitoring templates will be used.

Use the following steps to add the device class.

1. Add the following content to the end of ``$ZP_DIR/zenpack.yaml``.

  .. code-block:: yaml

      device_classes:
        /WeatherUnderground:
          zProperties:
            zPythonClass: ZenPacks.training.WeatherUnderground.WundergroundDevice
            zPingMonitorIgnore: true
            zSnmpMonitorIgnore: true
            zCollectorPlugins:
              - WeatherUnderground.Locations

  Let's take a look at what we're doing here.

  1. First we're saying the device class is going to be `/WeatherUnderground`.
     We add it at the top level because it doesn't fall into one of the existing
     categories like /Server or /Network.

  2. Next we set `zPythonClass` to
     `ZenPacks.training.WeatherUnderground.WundergroundDevice`. The zPythonClass
     property controls what type of device will be created in this device class.
     Note that the value for this is the name of the ZenPack followed by the
     name of the class we created in the above `classes` section.

  3. We then set both `zPingMonitorIgnore` and `zSnmpMonitorIgnore` to true to
     prevent any ping or SNMP monitoring Zenoss would perform on the device by
     default. Neither of these make sense since we're dealing with an HTTP API,
     not a traditional device.

  4. Finally we set `zCollectorPlugins` to contain the name of the modeler
     plugin we created in the previous section. Note that `zCollectorPlugins` is
     a `lines` property, meaning it accepts multiple values in a list format.

2. Reinstall the ZenPack to create the device class.

  .. code-block:: bash
  
      zenpack --link --install $ZP_TOP_DIR

3. Restart Zenoss to make sure all of the changes in our ZenPack are picked up.

  .. code-block:: bash
  
      zenoss restart

Add a Device
============

Now would be a good time to add a device to the new device class. There are many
ways to add a device to Zenoss. Either of the following approaches can be easily
done from the command line.

Using `zendisc`
---------------

Using `zendisc` is the easiest way to add device from the command line. However,
it only lets you specify the device class and the device's address.

Run the following command to add `wunderground.com`.

.. code-block:: bash

    zendisc run --deviceclass=/WeatherUnderground --device=wunderground.com

You should see output similar to the following.

.. code-block:: text

    INFO zen.ZenModeler: Collecting for device wunderground.com
    INFO zen.ZenModeler: No WMI plugins found for wunderground.com
    INFO zen.ZenModeler: Python collection device wunderground.com
    INFO zen.ZenModeler: plugins: WeatherUnderground.Locations
    INFO zen.PythonClient: wunderground.com: collecting data
    ERROR zen.PythonClient: wunderground.com: zWundergroundAPIKey not set. Get one from http://www.wunderground.com/weather/api
    INFO zen.PythonClient: Python client finished collection for wunderground.com
    WARNING zen.ZenModeler: The plugin WeatherUnderground.Locations returned no results.
    INFO zen.ZenModeler: No change in configuration detected
    INFO zen.ZenModeler: No command plugins found for wunderground.com
    INFO zen.ZenModeler: SNMP monitoring off for wunderground.com
    INFO zen.ZenModeler: No portscan plugins found for wunderground.com
    INFO zen.ZenModeler: Scan time: 0.02 seconds
    INFO zen.ZenModeler: Daemon ZenModeler shutting down

.. note::

  The error about `zWundergroundAPIKey` not being set is expected because we
  haven't set it. The solution is to go to the `wunderground.com` device in the
  web interface and add your API key to the `zWundergroundAPIKey` configuration
  property. After adding the API key you should remodel the device.

Using `zenbatchload`
--------------------

Another good way to add a device to Zenoss from the command line is
`zenbatchload`. Using `zenbatchload` also allows us to set configuration
properties such as `zWundergroundAPIKey` as the device is added.

Create a ``wunderground.zenbatchload`` file with the following contents.

.. code-block:: text

    /Devices/WeatherUnderground
    wunderground.com zWundergroundAPIKey='<your-api-key>', zWundergroundLocations=['Austin, TX', 'Des Moines, IA']
    
Before you remodel the device, you need to remove the existing device, or its stored state will prevent remodeling.  Find your wunderground.com device in the device list.  Select it, and click the Remove Devices button (has a Do Not Enter icon).

Now run the following command to load from that file.

.. code-block:: bash

    zenbatchload wunderground.zenbatchload

You should now be able to see a list of locations on the `wunderground.com`
device!
