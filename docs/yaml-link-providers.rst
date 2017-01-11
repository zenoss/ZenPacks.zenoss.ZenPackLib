.. _device-link-providers:

#####################
Device Link Providers
#####################

A device link provider is a subscriber interface that gives a hook for adding context-specific html links (for example, the device links on the Device Details page).  Zenpacklib provides a simple class to search the global catalog, device class catalog, or a device local catalog that match a specific query.

.. code-block:: yaml

      name: ZenPacks.zenoss.BasicZenPack

      link_providers:
        Virtual Machine:
          link_class: ZenPacks.example.XenServer
          catalog: device
          device_class: /Server/XenServer
          queries: [vm_id:manageIp]
        XenServer:
          global_search: True
          queries: [manageIp:vm_id]


To search the global catalog, set *global_search* to true.  If the catalog you wish to search is in a specific device class, set *global_search* to false and specify the class name with *device_class*.  To search a catalog on the local device, simply set *global_search* to false and do not set *device_class*.  You can use one or more queries to match up devices/components.  In the above example, the XenServer provider will search the global device catalog and match any device's *manageIp* attribute with the current device's *vm_id* attribute.

.. _device-link-provider-fields:

***************************
Device Link Provider Fields
***************************

The following fields are valid for a device link provider entry.

link_title:
  :Description: Title which will appear on the overview page of the type of device or component.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in relationships map)*

global_search:
  :Description: Search the global catalog?
  :Required: No
  :Type: boolean
  :Default Value: false

link_class:
  :Description: Python class on which this provider will apply.  You must supply the full python class name.  For example, 'ZenPacks.example.XenServer.Device.Device'.
  :Required: No
  :Type: string
  :Default Value: 'Products.ZenModel.Device.Device'

device_class:
  :Description: Device class containing the catalog which to search.  You must supply the full device class name.  For example, '/Server/XenServer'.
  :Required: No
  :Type: string
  :Default Value: None

catalog:
  :Description: Catalog name on which to search for linked devices/components
  :Required: No
  :Type: string
  :Default Value: 'device'

queries:
  :Description: Queries to use to match a linked device/component.  Each query must be in *remote:local* format, meaning that the catalog search will match a remote attribute with a local attribute.  The local search term could also be actual text.  Examples: *id:manageIp* will match the remote id attribute with the local device's manageIp attribute, and *meta_type:ClusterDevice* will match the meta_type on a remote device to "ClusterDevice".
  :Required: Yes
  :Type: list<string>
  :Default Value: None
