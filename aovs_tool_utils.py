try:
    import nuke
    INSIDE_NUKE = True
except:
    print('[ERROR] Import nuke')
    INSIDE_NUKE = False

# ::::: NODES ::::: #


def create_shuffle_channels(parent: nuke.Node = None, channels: list = []):
    nuke_clear_selection()
    node = nuke.createNode("Shuffle2")
    node.setInput(0, resolve_node_name(parent))

    node["in2"].setValue("alpha")
    node["label"].setValue("[value in1]")

    if not channels:
        return node

    layer = sorted(set([channel.split('.', 1)[0] for channel in channels]))
    if len(layer) != 1:
        layer = None

    if not layer:
        return node

    layer = layer[0]
    node["in1"].setValue(layer)
    mapping = []
    output_channels = ['rgba.red', 'rgba.green', 'rgba.blue', 'rgba.alpha']
    for _ch, _out_ch in zip(channels, output_channels[:len(channels)]):
        mapping.append((0, _ch, _out_ch))
        pass
    mapping.append((1, f'rgba.alpha', 'rgba.alpha'))
    node["mappings"].setValue(mapping)

    return node


def create_dot(parent: nuke.Node = None, center_to_parent=True, _offset=50):
    nuke_clear_selection()
    node_dot = nuke.createNode("Dot")
    parent = resolve_node_name(parent)
    node_dot.setInput(0, parent)

    if parent:
        node_dot.setXpos(parent.xpos())
        node_dot["ypos"].setValue(parent.ypos() + _offset)
        if center_to_parent:
            # dot_pos = node_positions_datas(node_dot)
            # parent_pos = node_positions_datas(parent)

            # dot_pos_x = ((parent_pos["centerWidth"] - dot_pos["centerWidth"]))
            # node_dot["xpos"].setValue(dot_pos_x + node_dot["xpos"].getValue())
            center_node_to_node(node_a=node_dot, to_node=parent,
                                vertical=True, horizontal=False)

    return node_dot


def create_remove(node_parent: nuke.Node = None, channels="", keep=True):
    nuke_clear_selection()
    node = nuke.createNode("Remove")
    if keep:
        node["operation"].setValue('keep')
    if channels:
        node["channels"].setValue(channels)

    node_parent = resolve_node_name(node_parent)
    if node_parent:
        node.setInput(0, node_parent)
        center_node_to_node(node, node_parent)
        print(node_parent.screenHeight())
        node.setYpos(round(node.ypos() + (node_parent.screenHeight() / 2)))

    return node

# ::::: COMMON ::::: #


def nuke_clear_selection():
    if nuke.selectedNodes():
        nuke.selectAll()
        nuke.invertSelection()


def resolve_node_name(name):
    if isinstance(name, str):
        if nuke.exists(name):
            return nuke.toNode(name)
    elif isinstance(name, nuke.Node):
        return name


def node_positions_datas(node: nuke.Node):
    if not node:
        return
    node = resolve_node_name(node)
    node_screenHeight = node.screenHeight()
    node_screenWidth = node.screenWidth()
    dot_base = 12

    if node.screenHeight() == 0:
        if node.Class() == "Dot":
            node_screenHeight = dot_base * int(nuke.toNode('preferences')["dot_node_scale"].getValue())
        else:
            node_screenHeight = int(nuke.toNode('preferences')["TileHeight"].getValue())

    if node.screenWidth() == 0:
        if node.Class() == "Dot":
            node_screenWidth = dot_base * int(nuke.toNode('preferences')["dot_node_scale"].getValue())
        else:
            node_screenWidth = int(nuke.toNode('preferences')["TileWidth"].getValue())

    centerWidth = node.xpos() + (node_screenWidth * 0.5)
    centerHeight = node.ypos() + (node_screenHeight * 0.5)

    node_pos = {
        "name": node["name"].getValue(),
        "class": node.Class(),
        "xpos": node.xpos(),
        "ypos": node.ypos(),
        "screenWidth": node_screenWidth,
        "screenHeight": node_screenHeight,
        "centerWidth": centerWidth,
        "centerHeight": centerHeight,
    }
    return node_pos


def center_node_to_node(node_a: nuke.Node, to_node: nuke.Node, vertical=True, horizontal=False):
    node_a_newpos = {"xpos": 0, "ypos": 0}
    node_a_pos = node_positions_datas(node_a)
    to_node_pos = node_positions_datas(to_node)
    if vertical:
        node_a_center_x = node_a_pos["centerWidth"]
        node_a_pos_x = node_a_pos["xpos"]

        to_node_center_x = to_node_pos["centerWidth"]

        node_a_nPosX = ((to_node_center_x - node_a_center_x) + node_a_pos_x)

        node_a["xpos"].setValue(node_a_nPosX)
        node_a_newpos = {"xpos": node_a_nPosX}

    if horizontal:
        node_a_center_y = node_a_pos["centerHeight"]
        node_a_pos_y = node_a_pos["ypos"]

        to_node_center_y = to_node_pos["centerHeight"]

        node_a_nPosY = ((to_node_center_y - node_a_center_y) + node_a_pos_y)

        node_a["ypos"].setValue(node_a_nPosY)
        node_a_newpos = {"ypos": node_a_nPosY}

    return node_a_newpos
