# TreeFormatConverter.py
# Converts between different formats of trees

from empress.topoSort import Tree  # Tree class

# Edge-based format is the primary format used by eMPRess algorithms.  This is the format that newickFormatReader.py
# constructs from a .newick input file.
# This format comprises  a dictionary in which each key is either the string "hTop" ("pTop") for the edge corresponding to 
# the handl of a host (parasite) tree or an edge tuple of the form (v1, v2) where v1 and v2 are strings denoting the 
# name of the top and bottom vertices of that edge.  Values are 4-tuples of the form (v1, v2, edge1, edge2) where 
# edge1 and edge2 are the edge tuples for the branches emanating from (v1, v2).  If the branch terminates at a leaf
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
    host_converted = dict_to_tree(host, Tree.TreeType.HOST)
    print("Leaves: ", host_converted.leaf_list)
    print()
    print("All nodes in postorder: ", host_converted.postorder_list)

def dict_to_tree(tree_dict, tree_type):
    """
    :param tree_dict: An edge-based representation of a tree as in the example above.
    :param tree_type: Tree.TreeType.{HOST, PARASITE} indicating the type of the tree.  This is used to 
        determine if the handle of the tree is "hTop" (host) or "pTop" (parasite)
    :return: A representation of the tree in Tree format (see Tree.py)
    """

    root = "hTop" if tree_type == Tree.TreeType.HOST else "pTop"
    output_tree = Tree.Tree()
    output_tree.tree_type = tree_type
    output_tree.root_node = dict_to_tree_helper(tree_dict, root)
    return output_tree

def dict_to_tree_helper(tree_dict, root_edge):
    """
    Helper function for dict_to_tree.
    """

    root_name = tree_dict[root_edge][1]
    new_node = Tree.Node(root_name)

    left_edge = tree_dict[root_edge][2] 
    right_edge = tree_dict[root_edge][3] 

    if left_edge is None and right_edge is None:
        return new_node
    else:
        new_left_node = dict_to_tree_helper(tree_dict, left_edge)
        new_right_node = dict_to_tree_helper(tree_dict, right_edge)
        new_node.left_node = new_left_node
        new_left_node.parent_node = new_node
        new_node.right_node = new_right_node
        new_left_node.parent_node = new_node
        return new_node
