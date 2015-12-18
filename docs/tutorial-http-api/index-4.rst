.. _tutorial-http-api-4:

######################
Monitoring an HTTP API
######################

This tutorial will describe an efficient approach to monitoring data via a HTTP
API. We'll start by using `zenpack.yaml` to extend the Zenoss object model. Then
we'll use a Python modeler plugin to fill out the object model. Then we'll use
PythonCollector to monitor for events, datapoints and even to update the model.

For purposes of this guide we'll be building a ZenPack that monitors the weather
using The Weather Channel's Weather Underground API.

.. toctree::
    :maxdepth: 2

    wunderground-api
    create-zenpack-4
    modeler-plugin-4
    add-device-class-4
    datasource-plugin-events-4
    datasource-plugin-datapoints-4
    datasource-plugin-model-4
