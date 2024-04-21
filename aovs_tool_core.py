import fnmatch
import re
from collections import defaultdict

try:
    import nuke
    from aovs_tool import aovs_tool_utils as aovs_utils
    INSIDE_NUKE = True
except:
    print('[ERROR] Import nuke')
    INSIDE_NUKE = False

GROUP_TAGS = {
    'technicals': {
        'alias': ['technicals', 'technical', 'tech'],
        'keys': ['P', 'Pref', 'N', 'UV', 'depth']
    }
}

TAGS = [_tag for _v in GROUP_TAGS.values() for _tag in _v.get('alias', [])]


def is_match(_pattern: str, keyword: str, regex=False):
    _pattern_low = _pattern.lower()
    keyword_low = keyword.lower()
    if _pattern in TAGS:
        for v in GROUP_TAGS.values():
            if _pattern in v['alias']:
                return keyword in v['keys']

    elif not regex:
        if _pattern_low[0] not in [*'[]/?*']:
            _pattern_low = '*' + _pattern_low
        if _pattern_low[-1] not in [*'[]/?*']:
            _pattern_low += '*'
        fn_match = fnmatch.fnmatch(keyword_low, _pattern_low)
        return fn_match
    else:
        re_match = re.match(_pattern_low, keyword_low)
        return re_match


class NewBranch:
    def __init__(self, parent=None, layer=None) -> None:
        self.layer = layer
        channels = None
        self.node_parent = parent

        if self.layer:
            channels = self.layer.channels()

        self.node_shuffle = aovs_utils.create_shuffle_channels(parent=parent, channels=channels)
        self.node_remove = aovs_utils.create_remove(node_parent=self.node_shuffle, channels="rgba", keep=True)
        self.node_dot = aovs_utils.create_dot(parent=self.node_remove, center_to_parent=True)
        pass


class AovsToolNuke():
    """
    classer la partie nuke pour pourvoir lancer l'ui en dehors de nuke
    """

    def __init__(self) -> None:
        self.selected_node = None
        pass

    def get_selected_node(self):
        try:
            self.selected_node = nuke.selectedNode()
        except ValueError:
            self.selected_node = None

    def get_layers(self, node=None):
        node = aovs_utils.resolve_node_name(node)
        if not node:
            node = self.selected_node
        channels = node.channels()
        layers = defaultdict(list)
        for _ch in channels:
            l_name, _channel = _ch.rsplit('.', 1)
            layers[l_name].append(_channel)
        return layers

    def build_recompo_template(self, layers: list):
        # TODO: creer base branche (black shuffle + remove)
        for layer in layers:
            layer = nuke.Layer(layer)
            channels = layer.channels()
            branch = NewBranch(layer=layer, premult=False)  # shuffle, remove, dot
            branch.add_offset(scale_y=BRANCH_SCALE_Y)
