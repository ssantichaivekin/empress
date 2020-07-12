"""
utils.py
Utilities related to conversion between data types
"""

from typing import Dict, Tuple, List
from recon import MappingNode, ReconGraph, Reconciliation
from recon import Cospeciation, Duplication, Transfer, Loss, TipTip
import tree
from tree import NodeLayout
from tree import TreeType
from collections import OrderedDict 
from enum import Enum

__all__ = ['dict_to_tree', 'dict_to_reconciliation', 'build_trees_with_temporal_order']

# Master utility function coverts from dictionaries to objects

def convert_to_objects(host_dict, parasite_dict, recon_dict):
    """
    :param host_dict - dictionary representation of host tree
    :param parasite_dict - dictionary representation of parasite tree
    :param recon_dict - dictionary representation of reconciliation
    :return - corresondoing host_tree and parasite_tree Tree objects
        and recon Reconciliation object
    """
    host_tree, parasite_tree, consistency_type = build_trees_with_temporal_order(host_dict, parasite_dict, recon_dict)
    recon = dict_to_reconciliation(recon_dict)
    return host_tree, parasite_tree, recon, consistency_type

# Tree utilities

# Edge-based format is the primary format used by eMPRess algorithms.
# This format comprises a dictionary in which each key is either the string
# "hTop" ("pTop") for the edge corresponding to the handle of a host (parasite) tree
# or an edge tuple of the form (v1, v2) where v1 and v2 are strings denoting the
# name of the top and bottom vertices of that edge.  Values are 4-tuples of the form
# (v1, v2, edge1, edge2) where edge1 and edge2 are the edge tuples for the
# branches emanating from (v1, v2).  If the branch terminates at a leaf
# then edge1 and edge2 are both None.
# Here is an example of the host tree for the heliconius.newick file:

host = {'hTop': ('Top', 'm1', ('m1', 'm2'), ('m1', 'm8')),
        ('m1', 'm2'): ('m1', 'm2', ('m2', 'm3'), ('m2', 'm6')),
        ('m2', 'm3'): ('m2', 'm3', ('m3', 'm4'), ('m3', 'm5')),
        ('m3', 'm4'): ('m3', 'm4', ('m4', 'aglaope_EastPE'), ('m4', 'amaryllis_EastPE')),
        ('m4', 'aglaope_EastPE'): ('m4', 'aglaope_EastPE', None, None),
        ('m4', 'amaryllis_EastPE'): ('m4', 'amaryllis_EastPE', None, None),
        ('m3', 'm5'): ('m3', 'm5', ('m5', 'ecuadoriensis_EastE'), ('m5', 'malleti_EastE')), 
        ('m5', 'ecuadoriensis_EastE'): ('m5', 'ecuadoriensis_EastE', None, None),
        ('m5', 'malleti_EastE'): ('m5', 'malleti_EastE', None, None),
        ('m2', 'm6'): ('m2', 'm6', ('m6', 'm7'), ('m6', 'melpomene_EastT')),
        ('m6', 'm7'): ('m6', 'm7', ('m7', 'thelxiopeia_EastFG'), ('m7', 'melpomene_EastFG')), 
        ('m7', 'thelxiopeia_EastFG'): ('m7', 'thelxiopeia_EastFG', None, None),
        ('m7', 'melpomene_EastFG'): ('m7', 'melpomene_EastFG', None, None),
        ('m6', 'melpomene_EastT'): ('m6', 'melpomene_EastT', None, None),
        ('m1', 'm8'): ('m1', 'm8', ('m8', 'm9'), ('m8', 'm11')),
        ('m8', 'm9'): ('m8', 'm9', ('m9', 'm10'), ('m9', 'rosina_WestPA')),
        ('m9', 'm10'): ('m9', 'm10', ('m10', 'melpomene_WestPA'),
        ('m10', 'rosina_WestCR')), ('m10', 'melpomene_WestPA'): ('m10', 'melpomene_WestPA', None, None),
        ('m10', 'rosina_WestCR'): ('m10', 'rosina_WestCR', None, None),
        ('m9', 'rosina_WestPA'): ('m9', 'rosina_WestPA', None, None),
        ('m8', 'm11'): ('m8', 'm11', ('m11', 'melpomene_EastC'), ('m11', 'cythera_WestE')),
        ('m11', 'melpomene_EastC'): ('m11', 'melpomene_EastC', None, None),
        ('m11', 'cythera_WestE'): ('m11', 'cythera_WestE', None, None)}


def tester():
    """ Tester for dict_to_tree """
    host_converted = dict_to_tree(host, tree.TreeType.HOST)
    print("Leaves: ", host_converted.leaf_list)
    print()
    print("All nodes in postorder: ", host_converted.postorder_list)

class ConsistencyType(Enum):
    """ Defines type of the temporal consistency of a reconciliation """
    STRONG_CONSISTENCY = 1
    WEAK_CONSISTENCY = 2
    NO_CONSISTENCY = 3

    def __str__(self):
        if self == ConsistencyType.STRONG_CONSISTENCY:
            return "Strong temporal consistency"
        elif self == ConsistencyType.WEAK_CONSISTENCY:
            return "Weak temporal consistency"
        else:
            return "Not temporally consistent"

# Utility functions that covert from dictionaries to objects

def dict_to_tree(tree_dict: dict, tree_type: tree.TreeType) -> tree.Tree:
    """
    :param tree_dict: An edge-based representation of a tree as in the example above.
    :param tree_type: tree.TreeType.{HOST, PARASITE} indicating the type of the tree.
        This is used to determine if the handle of the tree is "hTop" (host) or
        "pTop" (parasite)
    :return: A representation of the tree in Tree format (see tree.py)
    """

    root = "hTop" if tree_type == tree.TreeType.HOST else "pTop"
    output_tree = tree.Tree()
    output_tree.tree_type = tree_type
    output_tree.root_node = _dict_to_tree_helper(tree_dict, root)
    return output_tree

def _dict_to_tree_helper(tree_dict, root_edge):
    """
    Helper function for dict_to_tree.
    """
    root_name = tree_dict[root_edge][1]
    new_node = tree.Node(root_name)
    left_edge = tree_dict[root_edge][2]
    right_edge = tree_dict[root_edge][3]
    
    if left_edge is None and right_edge is None:
        return new_node
    else:
        new_left_node = _dict_to_tree_helper(tree_dict, left_edge)
        new_right_node = _dict_to_tree_helper(tree_dict, right_edge)
        new_node.left_node = new_left_node
        new_left_node.parent_node = new_node
        new_node.right_node = new_right_node
        new_left_node.parent_node = new_node
        new_right_node.parent_node = new_node
        return new_node

# ReconGraph utilities

def _find_roots(old_recon_graph) -> List[MappingNode]:
    not_roots = set()
    for mapping in old_recon_graph:
        for event in old_recon_graph[mapping]:
            etype, left, right = event
            if etype in 'SDT':
                not_roots.add(left)
                not_roots.add(right)
            elif etype == 'L':
                child = left
                not_roots.add(child)
            elif etype == 'C':
                pass
            else:
                raise ValueError('%s not in "SDTLC' % etype)
    roots = []
    for mapping in old_recon_graph:
        if mapping not in not_roots:
            roots.append(mapping)
    return roots

def dict_to_reconciliation(old_recon: Dict[Tuple, List]):
    """
    Convert the old reconciliation graph format to Reconciliation.
    Example of old format:
    old_recon = {
        ('n0', 'm2'): [('S', ('n2', 'm3'), ('n1', 'm4'))],
        ('n1', 'm4'): [('C', (None, None), (None, None))],
        ('n2', 'm3'): [('T', ('n3', 'm3'), ('n4', 'm1'))],
        ('n3', 'm3'): [('C', (None, None), (None, None))],
        ('n4', 'm1'): [('C', (None, None), (None, None))],
    }
    """
    roots = _find_roots(old_recon)
    if len(roots) > 1:
        raise ValueError("old_recon has many roots")
    root = roots[0]
    recon = Reconciliation(root)
    for mapping in old_recon:
        host, parasite = mapping
        if len(old_recon[mapping]) != 1:
            raise ValueError('old_recon mapping node has no or multiple events')
        etype, left, right = old_recon[mapping][0]
        mapping_node = MappingNode(host, parasite)
        if etype in 'SDT':
            left_parasite, left_host = left
            right_parasite, right_host = right
            left_mapping = MappingNode(left_parasite, left_host)
            right_mapping = MappingNode(right_parasite, right_host)
            if etype == 'S':
                recon.set_event(mapping_node, Cospeciation(left_mapping, right_mapping))
            if etype == 'D':
                recon.set_event(mapping_node, Duplication(left_mapping, right_mapping))
            if etype == 'T':
                recon.set_event(mapping_node, Transfer(left_mapping, right_mapping))
        elif etype == 'L':
            child_parasite, child_host = left
            child_mapping = MappingNode(child_parasite, child_host)
            recon.set_event(mapping_node, Loss(child_mapping))
        elif etype == 'C':
            recon.set_event(mapping_node, TipTip())
        else:
            raise ValueError('%s not in "SDTLC"' % etype)
    return recon

# Temporal ordering utilities

def build_trees_with_temporal_order(host_dict: dict, parasite_dict: dict, reconciliation: dict) \
        -> Tuple[tree.Tree, tree.Tree, ConsistencyType]:
    """
    This function uses topological sort to order the nodes inside host and parasite tree.
    The output trees can be used for visualization.
    
    :param host_dict: host tree dictionary
    :param parasite_dict: parasite tree dictionary
    :param reconciliation: reconciliation dictionary
    :return: a Tree object of type HOST, a Tree object of type PARASITE, and the
             ConsistencyType of the reconciliation. If the reconciliation is either
             strongly or weakly temporally consistent, then the tree objects have their
             nodes populated and the nodes will contain the temporal order information
             in the layout field. If the reconciliation is not temporally consistent, the
             function returns None, None, ConsistencyType.NO_CONSISTENCY.
    """

    consistency_type = ConsistencyType.NO_CONSISTENCY

    # find the temporal order for host and parasite nodes using strong temporal constraints
    temporal_graph = build_temporal_graph(host_dict, parasite_dict, reconciliation)
    ordering_dict = topological_order(temporal_graph)

    if ordering_dict is not None:
        consistency_type = ConsistencyType.STRONG_CONSISTENCY
    else:
        # the reconciliation is not strongly consistent, we relax the temporal constraints
        temporal_graph = build_temporal_graph(host_dict, parasite_dict, reconciliation, False)
        ordering_dict = topological_order(temporal_graph)
        if ordering_dict is not None:
            consistency_type = ConsistencyType.WEAK_CONSISTENCY

    host_tree_object = dict_to_tree(host_dict, TreeType.HOST)
    parasite_tree_object = dict_to_tree(parasite_dict, TreeType.PARASITE)

    # if there is a valid temporal ordering, we populate the layout with the order corresponding to the node
    if consistency_type != ConsistencyType.NO_CONSISTENCY:
        # calculate the temporal order for leaves, which all have the largest order
        max_order = 1
        for node in ordering_dict:
            if max_order < ordering_dict[node]:
                max_order = ordering_dict[node]
        leaf_order = max_order + 1
        populate_nodes_with_order(host_tree_object.root_node, TreeType.HOST, ordering_dict, leaf_order)
        populate_nodes_with_order(parasite_tree_object.root_node, TreeType.PARASITE, ordering_dict, leaf_order)
        return host_tree_object, parasite_tree_object, consistency_type
    else:
        return None, None, ConsistencyType.NO_CONSISTENCY

def create_parent_dict(host_dict: dict, parasite_dict: dict):
    """
    :param host_dict:  host tree dictionary
    :param parasite_dict:  parasite tree dictionary
    :return: A dictionary that maps the name of a child node to the name of its parent
             for both the host tree and the parasite tree.
    """
    parent_dict = {}
    for edge_name in host_dict:
        child_node = _bottom_node(host_dict[edge_name])
        parent_node = _top_node(host_dict[edge_name])
        parent_dict[child_node] = parent_node
    for edge_name in parasite_dict:
        child_node = _bottom_node(parasite_dict[edge_name])
        parent_node = _top_node(parasite_dict[edge_name])
        parent_dict[child_node] = parent_node
    return parent_dict

def build_formatted_tree(tree):
    """
    :param tree:  a tree dictionary
    :return: A temporal graph that contains all the temporal relations implied by
             the tree. Each key is a node tuple of the form (name, type) where name
             is a string representing the name of a parasite or host tree INTERNAL 
             node and type is either TreeType.HOST or TreeType.PARASITE which are 
             defined in Recon.py. The associated value is a list of node tuples that
             are the children of this node tuple in the tree.
    """
    tree_type = None
    if 'pTop' in tree:
        tree_type = TreeType.PARASITE
    else:
        tree_type = TreeType.HOST

    formatted_tree = {}
    for edge_name in tree:
        edge_four_tuple = tree[edge_name]
        # the temporal graph does not contain leaves as keys
        if _is_leaf_edge(edge_four_tuple):
            continue
        # the temporal graph contains internal node tuples as keys,
        # and their children nodes tuples as values
        node_name = _bottom_node(edge_four_tuple)
        left_child_name = edge_four_tuple[2][1]
        right_child_name = edge_four_tuple[3][1]
        formatted_tree[(node_name, tree_type)] = [(left_child_name, tree_type), \
                                               (right_child_name, tree_type)]
    return formatted_tree

def uniquify(elements):
    """
    :param elements:  a list whose elements might not be unique
    :return: A list that contains only the unique elements of the input list. 
    """
    return list(set(elements))

def build_temporal_graph(host_dict: dict, parasite_dict: dict, reconciliation: dict, add_strong_constraints = True):
    """
    :param host_dict:  host tree dictionary
    :param parasite_dict:  parasite tree dictionary
    :param reconciliation:  reconciliation dictionary
    :param add_strong_constraints:  a boolean indicating whether we are using the strongest
                                    temporal constraints, i.e. adding the constraints implied
                                    by a transfer event
    :return: The temporal graph which is defined as follows:
        Each key is a node tuple of the form (name, type) where name is a string representing
        the name of a parasite or host tree INTERNAL node and type is either TreeType.HOST or 
        TreeType.PARASITE which are defined in Recon.py. 
        Note that leaves of the host and parasite trees are not considered here.
        The associated value is a list of node tuples that are the children of this node tuple
        in the temporal graph.
    """
    # create a dictionary that maps each host and parasite node to its parent
    parent = create_parent_dict(host_dict, parasite_dict)
    # create temporal graphs for the host and parasite tree
    temporal_host_tree = build_formatted_tree(host_dict)
    temporal_parasite_tree = build_formatted_tree(parasite_dict)
    # initialize the final temporal graph to the combined temporal graphs of host and parasite tree
    temporal_graph = temporal_host_tree
    temporal_graph.update(temporal_parasite_tree)
    # add temporal relations implied by each node mapping and the corresponding event
    for node_mapping in reconciliation:
        parasite, host = node_mapping
        host_parent = parent[host]
        # get the event corresponding to this node mapping
        event_tuple = reconciliation[node_mapping][0]
        event_type = event_tuple[0]
        # if event type is a loss, the parasite is not actually mapped to the host in final 
        # reconciliation, so we skip the node_mapping
        if event_type == 'L':
            continue
        # if the node_mapping is not a leaf_mapping, we add the first relation
        if event_type != 'C':
            temporal_graph[(parasite, TreeType.PARASITE)].append((host, TreeType.HOST))
        # if the node_mapping is not a mapping onto the root of host tree, we add the second relation
        if host_parent != 'Top':
            temporal_graph[(host_parent, TreeType.HOST)].append((parasite, TreeType.PARASITE))
        
        # if event is a transfer, then we add two more temporal relations
        if event_type == 'T' and add_strong_constraints:
            # get the mapping for the right child which is the transferred child
            right_child_mapping = event_tuple[2]
            right_child_parasite, right_child_host = right_child_mapping
            # since a transfer event is horizontal, we have these two implied relations
            temporal_graph[(parent[right_child_host], TreeType.HOST)].append((parasite, TreeType.PARASITE))
            # the second relation is only added if the right child mapping is not a leaf mapping
            if right_child_mapping not in reconciliation or reconciliation[right_child_mapping][0][0]!='C':
                temporal_graph[(right_child_parasite, TreeType.PARASITE)].append((host, TreeType.HOST))

    for node_tuple in temporal_graph:
        # we need to make sure the associated value in the dictionary does not contain repeated node tuples
        temporal_graph[node_tuple] = uniquify(temporal_graph[node_tuple])
    return temporal_graph
    
# This is a topological sort based on depth-first-search 
# https://en.wikipedia.org/wiki/Topological_sorting#Depth-first_search
def topological_order(temporal_graph):
    """
    :param temporal_graph: as described in the return type of build_temporal_graph
    :return: A dictionary in which a key is a node tuple (name, type) as described
        in build_temporal_graph and the value is a positive integer representing its topological ordering.
        The ordering numbers are consecutive values beginning at 1.
        If the graph has a cycle and the topological ordering therefore fails, this
        function returns None.
    """
    # the ordering of nodes starts at 1
    next_order = 1
    unvisited_nodes = OrderedDict.fromkeys(sorted(temporal_graph.keys()))
    # the visitng_nodes is used to detect cycles. If the visiting_nodes add an element that is already
    # in the list, then we have found a cycle
    visiting_nodes = set()
    ordering_dict = {}
    while unvisited_nodes:
        # removes the first node from unvisited_nodes
        start_node = unvisited_nodes.popitem(last=False)[0]
        has_cycle, next_order = topological_order_helper(start_node, next_order, visiting_nodes,
                               unvisited_nodes, temporal_graph, ordering_dict)
        if has_cycle: return None
    # reverse the ordering of the nodes
    for node_tuple in ordering_dict:
        ordering_dict[node_tuple] = next_order - ordering_dict[node_tuple]
    return ordering_dict 
           
def topological_order_helper(start_node, start_order, visiting_nodes, unvisited_nodes, temporal_graph, ordering_dict):
    """
    :param start_node: is the starting node to explore the temporal_graph
    :param start_order: is the order we start to label the nodes with
    :param visiting_nodes: are nodes that are on the same path and are currently being explored
    :param unvisited_nodes: are nodes in temporal graph that have not been visited
    :param temporal graph: as described in the return type of build_temporal_graph
    :param ordering_dict: is the dictionary that contains labeled node tuples and their ordering as described
            in topological_order
    :return: a Boolean value that denotes whether the part of temporal graph reachable from start_node
             contains a cycle
    :return: the start order to be used by the remaing nodes of temporal graph that have not been labeled
    """
    next_order = start_order
    is_leaf = start_node not in temporal_graph
    if is_leaf:
        return False, next_order
    else:
        has_cycle = start_node in visiting_nodes
        if has_cycle:
            return True, next_order
        visiting_nodes.add(start_node)
        child_nodes = sorted(temporal_graph[start_node])
        for child_node in child_nodes:
            # if the child_node is already labeled, we skip it
            if child_node in ordering_dict:
                continue
            if child_node in unvisited_nodes:
                unvisited_nodes.pop(child_node)
            has_cycle_child, next_order = topological_order_helper(child_node, next_order,  visiting_nodes,
                                   unvisited_nodes, temporal_graph, ordering_dict)
            # if we find a cycle, we stop the process
            if has_cycle_child: return True, next_order
        # if children are all labeled, we can label the start_node
        visiting_nodes.remove(start_node)
        ordering_dict[start_node] = next_order
        return False, next_order + 1

def populate_nodes_with_order(tree_node, tree_type, ordering_dict, leaf_order):
    """
    :param tree_node: the root node of the subtree we want to populate the temporal order information
    :param tree_type: the type of the tree
    :param ordering_dict: a dictionary that maps node tuples to their temporal order as described in topological_order
    :param leaf_order: the temporal order we should assign to the leaves of the tree
    """
    layout = NodeLayout()
    if tree_node.is_leaf:
        layout.col = leaf_order
        tree_node.layout = layout
    else:
        node_tuple = (tree_node.name, tree_type)
        layout.col = ordering_dict[node_tuple]
        tree_node.layout = layout
        populate_nodes_with_order(tree_node.left_node, tree_type, ordering_dict, leaf_order)
        populate_nodes_with_order(tree_node.right_node, tree_type, ordering_dict, leaf_order)
        

def _get_names_of_internal_nodes(tree):
    """
    :param: A host or parasite tree
    :return: A list of the names (strings) of the internal nodes in that tree
    """
    node_names = list()
    for edge_name in tree:
        edge_four_tuple = tree[edge_name]
        if not _is_leaf_edge(edge_four_tuple):
            node_names.append(_bottom_node(edge_four_tuple))
    return node_names

def _top_node(edge_four_tuple):
    """
    :param: 4-tuple of the form (top_vertex_name, bottom_vertex_name, child_edge1, child_edge2)
    :return: top_vertex_name
    """
    return edge_four_tuple[0]

def _bottom_node(edge_four_tuple):
    """
    :param: 4-tuple of the form (top_vertex_name, bottom_vertex_name, child_edge1, child_edge2)
    :return: bottom_vertex_name
    """
    return edge_four_tuple[1]

def _is_leaf_edge(edge_four_tuple):
    """
    :param: 4-tuple of the form (top_vertex_name, bottom_vertex_name, child_edge1, child_edge2)
    :return: True if child_edge1 = child_edge2 = None.
        This signifies that this edge terminates at a leaf. 
    """
    return edge_four_tuple[3] == None