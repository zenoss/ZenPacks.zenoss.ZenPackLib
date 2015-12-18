.. _tutorials-4:

#########
Tutorials
#########

The following tutorials provide step-by-step instructions on using zenpacklib to
extend Zenoss is common ways.

* :ref:`tutorial-snmp-device-4`

  This tutorial starts with the very basics of creating a ZenPack through
  Zenoss' web interface and adding configuration to it. Then it progresses to
  extending the model, creating a modeler plugin, monitoring components, and
  then to event management with SNMP traps as an example.

  This is most likely the first tutorial you should do.

* :ref:`tutorial-http-api-4`

  In this tutorial the basics are skipped and we jump right into extending the
  model, modeling a custom HTTP API, and monitoring the same API using the
  zenpython daemon provided by the PythonCollector ZenPack.

  This is a more advanced tutorial that contains more advanced Python code.


*************
Prerequisites
*************

To follow the steps in these tutorials you will need to have access to the
following:

* A Linux server with Zenoss installed on it. This should not be a Zenoss
  server you care about. We will break things. You can download Zenoss from
  the `Zenoss download site`_.

* An SSH client to connect to your Zenoss server. `PuTTY`_ works well for
  Windows, ssh from the command line works well for Mac and Linux.

* These tutorials.

You may need experience in the following areas to more easily follow these
tutorials.

* Zenoss: Familiarity administration and configuration.
* Linux: Ability to move around the file system, manage files and run commands.
* Programming: Any type of programming or scripting experience will help.


.. _Zenoss download site: http://community.zenoss.org/community/download
.. _PuTTY: http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html
