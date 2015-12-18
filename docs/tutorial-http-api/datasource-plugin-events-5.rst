**************************
Datasource Plugin (Events)
**************************

Now that we have one or more locations modeled on our `wunderground.com` device,
we'll want to start monitoring each location. Using `PythonCollector` we have
the ability to create events, record datapoints and even update the model. We'll
start with an example that creates events from weather alert data.

The idea will be that we'll create events for locations that have outstanding
weather alerts such as tornado warnings. We'll try to capture severity data so
tornado warnings are higher severity events than something like a frost
advisory.

Using PythonCollector
=====================

Before using a Python plugin in our ZenPack, we must make sure we install the
PythonCollector ZenPack, and make it a requirement for our ZenPack.

The `PythonCollector` ZenPack adds the capability to write high performance
datasources in Python. They will be collected by the `zenpython` daemon that
comes with the `PythonCollector` ZenPack. I'd recommend reading the
`PythonCollector Documentation`_ for more information.

.. _PythonCollector Documentation: http://wiki.zenoss.org/ZenPack:PythonCollector

Installing PythonCollector
--------------------------

The first thing we'll need to do is to make sure the `PythonCollector` ZenPack
is installed on our system. If it isn't, follow these instructions to install
it.

1. Download the latest release from the PythonCollector_ page.

2. Run the following command to install the ZenPack:

   .. code-block:: bash

      zenpack --install ZenPacks.zenoss.PythonCollector-<version>.egg

3. Restart Zenoss.

.. _PythonCollector: http://wiki.zenoss.org/ZenPack:PythonCollector

Add PythonCollector Dependency
------------------------------

Since we're going to be using `PythonCollector` capabilities in our ZenPack we
must now update our ZenPack to define the dependency.

Follow these instructions to define the dependency.

1. Navigate to `Advanced` -> `Settings` -> `ZenPacks`.

2. Click into the `ZenPacks.training.WeatherUnderground` ZenPack.

3. Check `ZenPacks.zenoss.PythonCollector` in the list of dependencies.

4. Click `Save`.

5. Export the ZenPack. (:ref:`export-zenpack`).  The resulting objects.xml should have an empty XML object for this ZenPack.


Create the Alerts Plugin
========================

Follow these steps to create the `Alerts` data source plugin:

1. Create ``$ZP_DIR/dsplugins.py`` with the following contents.

   .. code-block:: python

      """Monitors current conditions using the Weather Underground API."""

      # Logging
      import logging
      LOG = logging.getLogger('zen.WeatherUnderground')

      # stdlib Imports
      import json
      import time

      # Twisted Imports
      from twisted.internet.defer import inlineCallbacks, returnValue
      from twisted.web.client import getPage

      # PythonCollector Imports
      from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
          PythonDataSourcePlugin,
          )


      class Alerts(PythonDataSourcePlugin):

          """Weather Underground alerts data source plugin."""

          @classmethod
          def config_key(cls, datasource, context):
              return (
                  context.device().id,
                  datasource.getCycleTime(context),
                  context.id,
                  'wunderground-alerts',
                  )

          @classmethod
          def params(cls, datasource, context):
              return {
                  'api_key': context.zWundergroundAPIKey,
                  'api_link': context.api_link,
                  'location_name': context.title,
                  }

          @inlineCallbacks
          def collect(self, config):
              data = self.new_data()

              for datasource in config.datasources:
                  try:
                      response = yield getPage(
                          'http://api.wunderground.com/api/{api_key}/alerts{api_link}.json'
                          .format(
                              api_key=datasource.params['api_key'],
                              api_link=datasource.params['api_link']))

                      response = json.loads(response)
                  except Exception:
                      LOG.exception(
                          "%s: failed to get alerts data for %s",
                          config.id,
                          datasource.location_name)

                      continue

                  for alert in response['alerts']:
                      severity = None

                      if int(alert['expires_epoch']) <= time.time():
                          severity = 0
                      elif alert['significance'] in ('W', 'A'):
                          severity = 3
                      else:
                          severity = 2

                      data['events'].append({
                          'device': config.id,
                          'component': datasource.component,
                          'severity': severity,
                          'eventKey': 'wu-alert-{}'.format(alert['type']),
                          'eventClassKey': 'wu-alert',

                          'summary': alert['description'],
                          'message': alert['message'],

                          'wu-description': alert['description'],
                          'wu-date': alert['date'],
                          'wu-expires': alert['expires'],
                          'wu-phenomena': alert['phenomena'],
                          'wu-significance': alert['significance'],
                          'wu-type': alert['type'],
                          })

              returnValue(data)

   Let's walk through this code to explain what is being done.

   1. Logging

      The first thing we do is import `logging` and create `LOG` as our logger.
      It's important that the name of the logger in the ``logging.getLogger()``
      begins with ``zen.``. You will not see your logs otherwise.

      The stdlib and Twisted imports are almost identical to what we used in
      the modeler plugin, and they're used for the same purposes.

      Finally we import `PythonDataSourcePlugin` from the `PythonCollector`
      ZenPack. This is the class our data source plugin will extend, and
      basically allows us to write code that will be executed by the
      `zenpython` collector daemon.

   2. `Alerts` Class

      Unlike our modeler plugin, there's no need to make the plugin class' name
      the same as the filename. As we'll see later when we're setting up the
      monitoring template that will use this plugin, there's no specific
      name for the file or the class required because we configure where to
      find the plugin in the datasource configuration within the monitoring
      template.

   3. `config_key` Class Method

      The `config_key` method must have the ``@classmethod`` decorator. It is
      passed `datasource`, and `context`. The `datasource` argument will be
      the actual datasource that the user configures in the monitoring
      templates section of the web interface. It has properties such as
      `eventClass`, `severity`, and as you can see a `getCycleTime()` method
      that returns the interval at which it should be polled. The `context`
      argument will be the object to which the monitoring template and
      datasource is bound. In our case this will be a location object such as
      Austin, TX.

      The purpose of the `config_key` method is to split monitoring
      configuration into tasks that will be executed by the zenpython daemon.
      The zenpython daemon will create one task for each unique value returned
      from `config_key`. It should be used to optimize the way data is
      collected. In some cases it is possible to make a single query to an API
      to get back data for many components. In these cases it would be wise to
      remove ``context.id`` from the config_key so we get one task for all
      components.

      In our case, the Weather Underground API must be queried once per
      location so it makes more sense to put ``context.id`` in the config_key
      so we get one task per location.

      The value returned by `config_key` will be used when `zenpython` logs. So
      adding something like `wunderground-alerts` to the end makes it easy to
      see logs related to collecting alerts in the log file.

      The `config_key` method will only be executed by `zenhub`. So you must
      restart `zenhub` if you make changes to the `config_key` method. This
      also means that if there's an exception in the `config_key` method it
      will appear in the `zenhub` log, not `zenpython`.

   4. `params` Class Method

      The `params` method must have the ``@classmethod`` decorator. It is
      passed the same `datasource` and `context` arguments as `config_key`.

      The purpose of the `params` method is to copy information from the Zenoss
      database into the `config.datasources[*]` that will be passed as an
      argument to the `collect` method. Since the `collect` method is run by
      `zenpython` it won't have direct access to the database, so it relies
      on the `params` method to provide it with any information it will need
      to collect.

      In our case you can see that we're copying the context's
      `zWundergroundAPIKey`, `api_link` and `title` properties. All of these
      will be used in the `collect` method.

      Just like the `config_key` method, `params` will only be executed by
      `zenhub`. So be sure to restart `zenhub` if you make changes, and look
      in the `zenhub` log for errors.

   5. `collect` Method

      The `collect` method does all of the real work. It will be called once
      per cycletime. It gets passed a `config` argument which for the most part
      has two useful properties: `config.id` and `config.datasources`.
      `config.id` will be the device's id, and `config.datasources` is a list
      of the datasources that need to be collected.

      You'll see in the collect method that each datasource in
      `config.datasources` has some useful properties. `datasource.component`
      will be the id of the component against which the datasource is run, or
      blank in the case of a device-level monitoring template.
      `datasource.params` contains whatever the `params` method returned.

      Within the body of the collect method we see that we create a new `data`
      variable using ``data = self.new_data()``. `data` is a place where we
      stick all of the collected events, values and maps. `data` looks like the
      following:

      .. code-block:: python

         data = {
             'events': [],
             'values': defaultdict(<type 'dict'>, {}),
             'maps': [],
         }

      Next we iterate over every configured datasource. For each one we make
      a call to Weather Underground's `Alerts` API, then iterate over each
      alert in the response creating an event for each.

      The following standard fields are being set for every event. You should
      read Zenoss' event management documentation if the purpose of any of
      these fields is not clear. I highly recommend setting all of these fields
      to an appropriate value for any event you send into Zenoss to improve the
      ability of Zenoss and Zenoss' operators to manage the events.

      * `device`: Mandatory. The device id related to the event.
      * `component`: Optional. The component id related to the event.
      * `severity`: Mandatory. The severity for the event.
      * `eventKey`: Optional. A further uniqueness key for the event. Used for de-duplication and clearing.
      * `eventClassKey`: Optional. An identifier for the *type* of event. Used during event class mapping.
      * `summary`: Mandatory: A (hopefully) short summary of the event. Truncated to 128 characters.
      * `message`: Optional: A longer text description of the event. Not truncated.

      You will also see many `wu-*` fields being added to the event. Zenoss
      allows arbitrary fields on events so it can be a good practice to add any
      further information you get about the event in this way. It can make
      understanding and troubleshooting the resulting event easier.

      Finally we return data with all of events we appended to it. `zenpython`
      will take care of getting the events sent from this point.

2. Restart Zenoss.

   After adding a new datasource plugin you must restart Zenoss. While
   developing it's enough to just restart *zenhub* with the following command.

   .. code-block:: bash

      serviced restart zenhub

That's it. The datasource plugin has been created. Now we just need to do some
Zenoss configuration to allow us to use it.

Configure Monitoring Templates
==============================

Rather than use the web interface to manually create a monitoring template,
we'll specify it in our `zenpack.yaml` instead.

1. Edit `$ZP_DIR/zenpack.yaml` and add the `templates` section below to the
   existing `/WeatherUnderground'` device class.

   .. code-block:: yaml

       device_classes:
        /WeatherUnderground:
          templates:
            Location:
              description: Location weather monitoring using the Weather Underground API.
              targetPythonClass: ZenPacks.training.WeatherUnderground.WundergroundLocation

              datasources:
                alerts:
                  type: Python
                  plugin_classname: ZenPacks.training.WeatherUnderground.dsplugins.Alerts
                  cycletime: "600"

   At least some of this should be self-explanatory. The YAML vocabulary has
   been designed to be as intuitive and concise as possible. Let's walk through
   it.

   1. The highest-level element (based on indentation) is
      `/WeatherUnderground/Location`. This means to create a `Location`
      monitoring template in the `/WeatherUnderground` device class.

      .. note::

         The monitoring template must be called ``Location`` because that is the
         `label` for the `WundergroundLocation` class to which we want the
         template bound.

   2. The `description` is for documentation purposes and should describe the
      purpose of the monitoring template.

   3. The `targetPythonClass` is a hint to what type of object the template is
      meant to be bound to. Currently this is only used to determine if users
      should be allowed to manually bind the template to device classes or
      devices. Providing a valid component type like we've done prevents users
      from making this mistake.

   4. Next we have `datasources` with a single `alerts` datasource defined.

      The `alerts` datasource only has three properties:

      * `type`: This is what makes `zenpython` collect the data.

      * `plugin_classname`: This is the fully-qualified class name for the
        `PythonDataSource` plugin we created that will be responsible for
        collecting the datasource.

      * `cycletime`: The interval in seconds at which this datasource should be
        collected.

2. Reinstall the ZenPack to add the monitoring templates.

   Some sections of `zenpack.yaml` such as zProperties and templates only get
   created when the ZenPack is installed.

   Run the usual command to reinstall the ZenPack in development mode.

   .. code-block:: bash

       zenpack --link --install $ZP_TOP_DIR

3. Navigate to `Advanced` -> `Monitoring Templates` in the web interface to
   verify that the `Location` monitoring template has been created as defined.

Test Monitoring Weather Alerts
==============================

Testing this is a bit tricky since we'll have to be monitoring a location that
currently has an active weather alert. Fortunately there's an easy way to find
one of these locations.

Follow these steps to test weather alert monitoring:

1. Go to the following URL for the current severe weather map of the United
   States.

   http://www.wunderground.com/severe.asp

2. Click on one of the colored areas. Orange and red are more exciting. This
   will take you to the text of the warning. It should reference city or county
   names.

3. Update `zWundergroundLocations` on the `wunderground.com` device to add one
   of the cities or counties that has an active weather alert. For example,
   "Buffalo, South Dakota".

4. Remodel the `wunderground.com` device then verify that the new location is
   modeled.

5. Run the following command to collect from `wunderground.com`.

   .. code-block:: bash

      zenpython run -v10 --device=wunderground.com

   There will be a lot of output from this command, but we're mainly looking
   for an event to be sent for the weather alert. It will look similar to the
   following output::

       DEBUG zen.zenpython: Queued event (total of 1) {'rcvtime': 1403112635.631883, 'wu-type': u'FIR', 'wu-significance': u'W', 'eventClassKey': 'wu-alert', 'wu-expires': u'8:00 PM MDT on June 18, 2014', 'component': '80901.1.99999', 'monitor': 'localhost', 'agent': 'zenpython', 'summary': u'Fire Weather Warning', 'wu-date': u'3:39 am MDT on June 18, 2014', 'manager': 'zendev.damsel.loc', 'eventKey': 'wu-alert-FIR', 'wu-phenomena': u'FW', 'wu-description': u'Fire Weather Warning', 'device': 'wunderground.com', 'message': u'\n...Red flag warning remains in effect from noon today to 8 PM MDT\nthis evening for gusty winds...low relative humidity and dry fuels for\nfire weather zones 222...226 and 227...\n\n* affected area...fire weather zones 222...226 and 227.\n\n* Winds...southwest 10 to 20 mph with gusts up to 35 mph.\n\n* Relative humidity...as low as 13 percent.\n\n* Impacts...extreme fire behavior will be possible if a fire \n starts. \n\nPrecautionary/preparedness actions...\n\nA red flag warning means that critical fire weather conditions\nare either occurring now...or will shortly. A combination of\nstrong winds...low relative humidity...and warm temperatures can\ncontribute to extreme fire behavior.\n\n\n\n\n', 'device_guid': 'f59e7e4d-be5d-4b86-b005-7357ce58f79c', 'severity': 3}

You should now be able to confirm that this event was created in the Zenoss
event console.
