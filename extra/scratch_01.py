from aovs_tool import aovs_tool_ui as asui
from importlib import reload
reload(asui)

# asui.nuke_launcher()


x, i = 0, 0
sh = []

nuke.toNode(nuke.root().name())


grab_layers = ["Beauty_HDR", "Beauty_spotLightA", "Beauty_spotLightB", "Beauty_default", "combineddiffuse_HDR", "combineddiffuse_spotLightA", "combineddiffuse_spotLightB", "combineddiffuse_default", "directdiffuse_HDR", "directdiffuse_spotLightA", "directdiffuse_spotLightB", "directdiffuse_default", "indirectdiffuse_HDR", "indirectdiffuse_spotLightA", "indirectdiffuse_spotLightB", "indirectdiffuse_default", "combinedglossyreflection_HDR", "combinedglossyreflection_spotLightA", "combinedglossyreflection_spotLightB", "combinedglossyreflection_default", "directglossyreflection_HDR", "directglossyreflection_spotLightA", "directglossyreflection_spotLightB", "directglossyreflection_default", "indirectglossyreflection_HDR", "indirectglossyreflection_spotLightA",
               "indirectglossyreflection_spotLightB", "indirectglossyreflection_default", "glossytransmission_HDR", "glossytransmission_spotLightA", "glossytransmission_spotLightB", "glossytransmission_default", "combinedemission_HDR", "combinedemission_spotLightA", "combinedemission_spotLightB", "combinedemission_default", "directemission_HDR", "directemission_spotLightA", "directemission_spotLightB", "directemission_default", "indirectemission_HDR", "indirectemission_spotLightA", "indirectemission_spotLightB", "indirectemission_default", "sss_HDR", "sss_spotLightA", "sss_spotLightB", "sss_default", "export_basecolor_HDR", "export_basecolor_spotLightA", "export_basecolor_spotLightB", "export_basecolor_default", "P", "N", "depth", "UV"]

for lyr in grab_layers:
    lyr = nuke.Layer(lyr, [f'{lyr}.red', f'{lyr}.green', f'{lyr}.blue'])
    print(lyr.name(), lyr.channels())
    mapping = []
    for cur_channel in lyr.channels():
        if cur_channel:
            mapping.append((-1, 'white', f"{cur_channel}"))
    if mapping:
        if i % 2 == 0:
            x = 0
            _node = nuke.createNode('Shuffle2')
        _node.knob(f'out{x+1}').setValue(lyr.name())
        # _node.knob(f'in{x+1}').setValue('rgba')
        print(mapping)
        _node["mappings"].setValue(mapping)
        lb = _node.knob('label').getValue()
        n_lb = f'{lyr.name()}'
        if lb:
            n_lb = lb + '\n' + n_lb
        _node.knob('label').setValue(n_lb)
        x += 1
        i += 1
