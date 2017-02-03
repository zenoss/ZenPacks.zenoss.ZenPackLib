******************
Create the ZenPack
******************

The first thing we'll need to do is create the Weather Underground ZenPack.
We'll use zenpacklib to create this ZenPack from the command line using the
following steps. These commands should be run as the *zenoss* user.

.. code-block:: bash

    cd /z
    zenpacklib --create ZenPacks.training.WeatherUnderground

You should see output similar to the following. Most importantly that
*zenpack.yaml* file is being created.

.. code-block:: text

    Creating source directory for ZenPacks.training.WeatherUnderground:
      - making directory: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground
      - creating file: ZenPacks.training.WeatherUnderground/setup.py
      - creating file: ZenPacks.training.WeatherUnderground/MANIFEST.in
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/datasources/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/thresholds/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/parsers/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/migrate/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/resources/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/modeler/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/tests/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/libexec/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/modeler/plugins/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/lib/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/__init__.py
      - creating file: ZenPacks.training.WeatherUnderground/ZenPacks/training/WeatherUnderground/zenpack.yaml

Define zProperties and Classes
==============================

The *zenpack.yaml* that's created within the ZenPack source directory above
contains only the absolute minimum to be a valid YAML file. Let's take a look at
its current contents.

1. First let's set a couple of environment variables to reduce some typing.

  .. code-block:: bash

      export ZP_TOP_DIR=/z/ZenPacks.training.WeatherUnderground
      export ZP_DIR=$ZP_TOP_DIR/ZenPacks/training/WeatherUnderground

2. Now let's look at the contents of zenpack.yaml.

  .. code-block:: bash

      cd $ZP_DIR
      cat zenpack.yaml

  You should only see the following line.

  .. code-block:: text

      name: ZenPacks.training.WeatherUnderground

3. Replace the contents of zenpack.yaml with the following.

  .. code-block:: yaml

      name: ZenPacks.training.WeatherUnderground

      zProperties:
        DEFAULTS:
          category: Weather Underground

        zWundergroundAPIKey: {}
        zWundergroundLocations:
          type: lines
          default:
            - Austin, TX
            - San Jose, CA
            - Annapolis, MD

      classes:
        WundergroundDevice:
          base: [zenpacklib.Device]
          label: Weather Underground API

        WundergroundLocation:
          base: [zenpacklib.Component]
          label: Location

          properties:
            country_code:
              label: Country Code

            timezone:
              label: Time Zone

            api_link:
              label: API Link
              grid_display: False

      class_relationships:
        - WundergroundDevice 1:MC WundergroundLocation

  You can see this YAML defines the following important aspects of our ZenPack.

  1. The *name* field is mandatory. It must match the name of the ZenPack's
     source directory.

  2. The *zProperties* field contains configuration properties we want the
     ZenPack to add to the Zenoss system when it is installed.

     Note that *DEFAULTS* is not added as configuration property. It is a
     special value that will cause it's properties to be added as the default
     for all of the other listed zProperties. Specifically in this case it will
     cause the *category* of *zWundergroundAPIKey* and *zWundergroundLocations*
     to be set to ``Weather Underground``. This is a convenience to avoid having
     to repeatedly type the category for each added property.

     The *zWundergroundAPIKey* zProperty has an empty dictionary (``{}``). This
     is because we want it to be a *string* type with an empty default value.
     These happen to be the defaults so they don't need to be specified.

     The *zWundergroundLocations* property uses the *lines* type which allows
     the user to specify multiple lines of text. Each line will be turned into
     an element in a list which you can see is also how the default value is
     specified. The idea here is that unless the user configures otherwise, we
     will default to monitoring weather alerts and conditions for Austin, TX,
     San Jose, CA, and Annapolis, MD.

  3. The *classes* field contains each of the object classes we want the ZenPack
     to add.

     In this case we're adding *WundergroundDevice* which because *base* is set
     to *Device* will be a subclass or specialization of the standard Zenoss
     device type. We're also adding *WundergroundLocation* which because *base*
     is set to *Component* will be a subclass of the standard component type.

     The *label* for each is simply the human-friendly name that will be used to
     refer to the resulting objects when they're seen in the Zenoss web
     interface.

     The *properties* for *WundergroundLocation* are extra bits of data we want
     to model from the API and show to the user in the web interface. *order*
     will be used to show the properties in the defined order, and setting
     *grid_display* to false for *api_link* will allow it be shown in the
     details panel of the component, but not in the component grid.

  4. *class_relationships* uses a simple syntax to define a relationship
     between *WundergroundDevice* and *WundergroundLocation*. Specifically it is
     saying that each (1) *WundergroundDevice* object can contain many (MC)
     *WundergroundLocation* objects.

Install the ZenPack
===================

Creating the ZenPack with zenpacklib doesn't install the ZenPack for you. So you
must now install the ZenPack in developer (--link) mode.

1. Run the following command to install the ZenPack in developer mode.

  .. code-block:: bash

      zenpack --link --install $ZP_TOP_DIR
