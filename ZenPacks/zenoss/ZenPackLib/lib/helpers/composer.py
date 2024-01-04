
from yaml.composer import Composer, ComposerError
from yaml.nodes import ScalarNode, SequenceNode, MappingNode
from yaml.error import Mark

class ComposerFromDict(Composer):
    # composer for non-streaming loader that takes a dictionary
    # as the source of the nodes

    def __init__(self, dataDict, tag=u'tag:yaml.org,2002:map'):
        self.dataDict = dataDict
        self.tag = tag
        # need some kind of mark to keep some logging stuff from failing
        self.dummyMark = Mark("combinedYaml", 0, 0, 0, None, 0)

    def dispose(self):
        # since there is no parser, we need to fake out the dispose method
        # migth as well dispose of the dict we had passed in
        del self.dataDict

    def check_node(self):
        # called to check if there's a node to load
        # since this composer only supports one node but laod_all
        # uses this as a while-condition, we will return true
        # only if we haven't composed the node yet

        return self.dataDict is not None
     
    def get_single_node(self):
        if not self.dataDict:
            raise ComposerError(None, None, "source dict missing or empty", None)
        # Compose the root node and everything below it
        node = self.compose_node(self.dataDict)
        node.tag = self.tag
        return node

    get_node = get_single_node  # we will only ever have one node

    def compose_node(self, obj):
        if isinstance(obj, (int, str, float, bool, type(None))): 
            node = self.compose_scalar_node(obj)
        elif isinstance(obj, (list, tuple, set)):
            node = self.compose_sequence_node(obj)
        elif isinstance(obj, (dict,)):
            node = self.compose_mapping_node(obj)
        else:
            node = self.compose_scalar_node(obj)
        return node

    def compose_scalar_node(self, obj):
        if isinstance(obj, (bool,)):
            tag = u'tag:yaml.org,2002:bool'
        elif isinstance(obj, (str, unicide)):
            tag = u'tag:yaml.org,2002:str'
        elif isinstance(obj, (float,)):
            tag = u'tag:yaml.org,2002:float'
        elif isinstance(obj, (int,)):
            tag = u'tag:yaml.org,2002:int'
        elif isinstance(obj, (type(None),)):
            tag = u'tag:yaml.org,2002:null'
        else:
            tag = u'tag:yaml.org,2002:str'
        node = ScalarNode(tag, obj, start_mark=self.dummyMark, end_mark=self.dummyMark)
        return node

    def compose_sequence_node(self, obj):
        tag = u'tag:yaml.org,2002:seq'
        node = SequenceNode(tag, [], start_mark=self.dummyMark, end_mark=self.dummyMark)
        for value in obj:
            node.value.append(self.compose_node(value))
        return node

    def compose_mapping_node(self, obj):
        tag = u'tag:yaml.org,2002:map'
        node = MappingNode(tag, [], start_mark=self.dummyMark, end_mark=self.dummyMark)
        for key, value in obj.items():
            item_key = self.compose_node(key)
            item_value = self.compose_node(value)
            node.value.append((item_key, item_value))
        return node

