##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec
from .RRDThresholdSpec import RRDThresholdSpec
from .RRDDatasourceSpec import RRDDatasourceSpec
from .GraphDefinitionSpec import GraphDefinitionSpec


class RRDTemplateSpec(Spec):
    """RRDTemplateSpec"""

    def __init__(
            self,
            deviceclass_spec,
            name,
            description=None,
            targetPythonClass=None,
            thresholds=None,
            datasources=None,
            graphs=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create an RRDTemplate Specification


            :param description: TODO
            :type description: str
            :param targetPythonClass: TODO
            :type targetPythonClass: str
            :param thresholds: TODO
            :type thresholds: SpecsParameter(RRDThresholdSpec)
            :param datasources: TODO
            :type datasources: SpecsParameter(RRDDatasourceSpec)
            :param graphs: TODO
            :type graphs: SpecsParameter(GraphDefinitionSpec)

        """
        super(RRDTemplateSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.deviceclass_spec = deviceclass_spec
        self.name = name
        self.description = description
        self.targetPythonClass = targetPythonClass

        self.thresholds = self.specs_from_param(
            RRDThresholdSpec, 'thresholds', thresholds, zplog=self.LOG)

        self.datasources = self.specs_from_param(
            RRDDatasourceSpec, 'datasources', datasources, zplog=self.LOG)

        self.graphs = self.specs_from_param(
            GraphDefinitionSpec, 'graphs', graphs, zplog=self.LOG)

        self.validate_references()

    def validate_references(self):
        """
            validate 
                - check that datapoint/datasources are valid
                - threshold and graph references to datapoints
        """
        ds_dp_names = self.get_ds_dp_names()
        # check threshold references
        for th_name, th_spec in self.thresholds.items():
            self.check_ds_dp_names(th_name,
                                   'Threshold',
                                   set(th_spec.dsnames),
                                   ds_dp_names)
        # check graph point references
        for g_name, g_spec in self.graphs.items():
            for gp_name, gp_spec in g_spec.graphpoints.items():
                self.check_ds_dp_names(gp_name,
                                       'Graph Point',
                                       set([gp_spec.dpName]),
                                       ds_dp_names)

    def get_ds_dp_names(self):
        """return set of dsname_dpname"""
        dp_names = []
        for ds_name, ds_spec in self.datasources.items():
            for dp_name, dp_spec in ds_spec.datapoints.items():
                dp_id = '{}_{}'.format(ds_name, dp_name)
                dp_names.append(dp_id)
        return set(dp_names)

    def check_ds_dp_names(self, spec_name, spec_type, dp_names, ref_names):
        valid_names = dp_names.intersection(ref_names)
        invalid_names = dp_names.difference(ref_names)
        if len(valid_names) == 0:
            self.LOG.error('{} {} has no valid datapoints'.format(spec_type,
                                                                  spec_name))
        if len(invalid_names) > 0:
            self.LOG.error('{} {} has invalid datapoints: {}'.format(spec_type,
                                                            spec_name,
                                                            ', '.join(list(invalid_names))))

    def create(self, dmd, addToZenPack=True):
        device_class = dmd.Devices.createOrganizer(self.deviceclass_spec.path)

        existing_template = device_class.rrdTemplates._getOb(self.name, None)
        if existing_template:
            self.speclog.info("replacing template")
            device_class.rrdTemplates._delObject(self.name)

        device_class.manage_addRRDTemplate(self.name)
        template = device_class.rrdTemplates._getOb(self.name)

        # Flag this as a ZPL managed object, that is, one that should not be
        # exported to objects.xml  (contained objects will also be excluded)
        template.zpl_managed = True

        # set to false to facilitate testing without ZP installation
        if addToZenPack:
            # Add this RRDTemplate to the zenpack.
            zenpack_name = self.deviceclass_spec.zenpack_spec.name
            template.addToZenPack(pack=zenpack_name)

        if not existing_template:
            self.speclog.info("adding template")

        if self.targetPythonClass is not None:
            template.targetPythonClass = self.targetPythonClass
        if self.description is not None:
            template.description = self.description

        self.speclog.debug("adding {} thresholds".format(len(self.thresholds)))
        for threshold_id, threshold_spec in self.thresholds.items():
            threshold_spec.create(self, template)

        self.speclog.debug("adding {} datasources".format(len(self.datasources)))
        for datasource_id, datasource_spec in self.datasources.items():
            datasource_spec.create(self, template)

        self.speclog.debug("adding {} graphs".format(len(self.graphs)))
        for i, (graph_id, graph_spec) in enumerate(self.graphs.items()):
            graph_spec.create(self, template, sequence=i)

        if not addToZenPack:
            return template
