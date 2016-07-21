from .Spec import Spec
from .RRDThresholdSpec import RRDThresholdSpec
from .RRDDatasourceSpec import RRDDatasourceSpec
from .GraphDefinitionSpec import GraphDefinitionSpec

class RRDTemplateSpec(Spec):

    """TODO."""

    def __init__(
            self,
            deviceclass_spec,
            name,
            description=None,
            targetPythonClass=None,
            thresholds=None,
            datasources=None,
            graphs=None,
            _source_location=None
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

        self.deviceclass_spec = deviceclass_spec
        self.name = name
        self.description = description
        self.targetPythonClass = targetPythonClass

        self.thresholds = self.specs_from_param(
            RRDThresholdSpec, 'thresholds', thresholds)

        self.datasources = self.specs_from_param(
            RRDDatasourceSpec, 'datasources', datasources)

        self.graphs = self.specs_from_param(
            GraphDefinitionSpec, 'graphs', graphs)

    def create(self, dmd):
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

