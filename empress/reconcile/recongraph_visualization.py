'''
First written by Dennis Wang,
modified by Santi Santichaivekin (Feb 28, 19).
'''

import networkx as nx
import sys
import os

EXAMPLE1 = {
    ('p1', 'h1'): [['C', (None, None), (None, None), 1.0], 0],
    ('p2', 'h3'): [['C', (None, None), (None, None), 1.0], 0],
    ('p3', 'h2'): [['C', (None, None), (None, None), 1.0], 0],
    ('p4', 'h4'): [['C', (None, None), (None, None), 1.0], 0],
    ('p6', 'h7'): [['S', ('p7', 'h1'), ('p8', 'h2'), 0.5], 2],
    ('p6', 'h8'): [['S', ('p7', 'h3'), ('p8', 'h4'), 0.5], 2],
    ('p7', 'h1'): [['T', ('p1', 'h1'), ('p2', 'h3'), 0.5], 1],
    ('p7', 'h3'): [['T', ('p2', 'h3'), ('p1', 'h1'), 0.5], 1],
    ('p8', 'h2'): [['T', ('p3', 'h2'), ('p4', 'h4'), 0.5], 1],
    ('p8', 'h4'): [['T', ('p4', 'h4'), ('p3', 'h2'), 0.5], 1]
}

EXAMPLE2 = {
    ('p1', 'h1'): [('C', (None, None), (None, None))],
    ('p2', 'h3'): [('C', (None, None), (None, None))],
    ('p3', 'h2'): [('C', (None, None), (None, None))],
    ('p4', 'h4'): [('C', (None, None), (None, None))],
    ('p6', 'h7'): [('S', ('p7', 'h1'), ('p8', 'h2'))],
    ('p6', 'h8'): [('S', ('p7', 'h3'), ('p8', 'h4'))],
    ('p7', 'h1'): [('T', ('p1', 'h1'), ('p2', 'h3'))],
    ('p7', 'h3'): [('T', ('p2', 'h3'), ('p1', 'h1'))],
    ('p8', 'h2'): [('T', ('p3', 'h2'), ('p4', 'h4'))],
    ('p8', 'h4'): [('T', ('p4', 'h4'), ('p3', 'h2'))]
}

def _event_node_type(event_node):
    """
    Returns 'S', 'T', 'D', L', or 'C'
    'S': speciation
    'D': duplication
    'T': transfer
    'L': loss
    'C': end event
    """
    return event_node[0]

def _mapping_node_to_str(mapping_node):
    return "{}-{}".format(mapping_node[0], mapping_node[1])

def _first_child(event_node):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # returns a mapping node
    assert(event_node[1][0] and event_node[1][1])
    return event_node[1]

def _second_child(event_node):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # ['C', (None, None), (None, None), 1.0]
    # returns a mapping node
    # do not use on null entities
    assert(event_node[2][0] and event_node[2][1])
    return event_node[2]

def _event_node_to_str(event_node):
    # ('S', ('p7', 'h1'), ('p8', 'h2'), 0.5], 2)
    # ('S', ('n32', 'm143'), ('n31', 'm144'))
    if _event_node_type(event_node) == 'S':
        return "spec | {}-{}, {}-{}".format(
            event_node[1][0], event_node[1][1],
            event_node[2][0], event_node[2][1]
        )
    elif _event_node_type(event_node) == 'T':
        return "tran | {}-{}, {}-{}".format(
            event_node[1][0], event_node[1][1],
            event_node[2][0], event_node[2][1]
        )
    elif _event_node_type(event_node) == 'D':
        return "dupl | {}-{}, {}-{}".format(
            event_node[1][0], event_node[1][1],
            event_node[2][0], event_node[2][1]
        )
    elif _event_node_type(event_node) == 'L':
        return "loss | {}-{}".format(
            event_node[1][0], event_node[1][1],
        )
    if _event_node_type(event_node) == 'C':
        return "END"

def edges_from_recongraph(dtl_graph):
    output_edges_list = []
    for mappingNode, event_nodes in list(dtl_graph.items()):
        mapping_node_name = _mapping_node_to_str(mappingNode)
        for event_node in event_nodes:
            # check whether this is an event node or just
            # extra data -- SEE EXAMPLE1
            try:
                assert event_node[0] in ['S', 'T', 'D', 'L', 'C']
            except:
                continue

            event_node_name = _event_node_to_str(event_node)
            # we do not have to insert the end event to
            # the visualization
            if _event_node_type(event_node) == 'C':
                pass
            # loss has only one children
            elif _event_node_type(event_node) == 'L':
                output_edges_list.append((mapping_node_name, event_node_name))

                next_mapping_node_name = _mapping_node_to_str(_first_child(event_node))
                output_edges_list.append((event_node_name, next_mapping_node_name))
            # other types have two children
            else:
                output_edges_list.append((mapping_node_name, event_node_name))
             
                next_mapping_node_name0 = _mapping_node_to_str(_first_child(event_node))
                output_edges_list.append((event_node_name, next_mapping_node_name0))
                next_mapping_node_name1 = _mapping_node_to_str(_second_child(event_node))
                output_edges_list.append((event_node_name, next_mapping_node_name1))

    return output_edges_list

def visualize_and_save(dtl_graph, target_file):
    """
    Receives that graph part of the reconciliation graph.
    Visualizes it and saves it to targetfile.

    Note: targetfile must ends with .png
    """
    filename, extension = os.path.splitext(target_file)
    # creates an empty graph
    nx_dtl_graph = nx.DiGraph()
    # add edges -- note that the library already prefers to place
    # topologically lower nodes on the top
    nx_dtl_graph.add_edges_from(edges_from_recongraph(dtl_graph))
    pydot_dtl_graph = nx.drawing.nx_pydot.to_pydot(nx_dtl_graph)
    try:
        pydot_dtl_graph.write_png(filename + '.png')
    except Exception:
        # Exception: "dot" not found in path.
        # For people with who does not have Graphviz installed
        print("Graphviz not installed. Cannot render image as .png, saved as .gv instead", file=sys.stderr)
        print("You can visualize the .gv file in http://www.webgraphviz.com/", file=sys.stderr)
        pydot_dtl_graph.write(filename + '.gv')

if __name__ == '__main__' :
    visualize_and_save(EXAMPLE1, "example1.png")
    visualize_and_save(EXAMPLE2, "example2.png")
