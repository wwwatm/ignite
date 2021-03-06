import autonetkit.log as log
import autonetkit.ank as ank_utils

def build_layer1(anm):
    import autonetkit.design.layer1
    autonetkit.design.layer1.build_layer1(anm)

def build_layer2(anm):
    import autonetkit.design.layer2
    autonetkit.design.layer2.build_layer2(anm)

def build_layer3(anm):
    """ l3_connectivity graph: switch nodes aggregated and exploded"""
    g_in = anm['input']
    gl2_conn = anm['layer2_conn']
    g_l3 = anm.add_overlay("layer3")
    g_l3.add_nodes_from(gl2_conn, retain=['label', 'devsubtype'])
    ank_utils.copy_attr_from(g_in, g_l3, "multicast")
    g_l3.add_nodes_from(g_in.switches(), retain=['asn'])
    g_l3.add_edges_from(gl2_conn.edges(),retain=['link_type'])

    edges_to_remove = [edge for edge in gl2_conn.edges()
                      if edge.link_type == 'is_not_l3']

    g_l3.remove_edges_from(edges_to_remove)
    edges_to_remove =[]

    switches = g_l3.switches()

    ank_utils.aggregate_nodes(g_l3, switches)
    exploded_edges = ank_utils.explode_nodes(g_l3,
                                             switches, retain=['link_type'])

    # also explode virtual switches
    vswitches = [n for n in g_l3.nodes()
                 if n['layer2'].device_type == "switch"
                 and n['layer2'].device_subtype == "virtual"]

    # explode each seperately?
    for edge in exploded_edges:
        edge.multipoint = True
        edge.src_int.multipoint = True
        edge.dst_int.multipoint = True