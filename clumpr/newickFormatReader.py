# newickFormatReader.py
# Ran Libeskind-Hadas, October 2013
# Newick file reader and parser

# Uses BioPython's Phylo package to read and parse a newick tree with internal
# node names specified.  Specifically, the input is of the form
# (LeftTree, RightTree) RootName
# LeftTree and RightTree are themselves newick trees and RootName is the
# name given to the root node.

# All node names (internal and tips) must be non-numeric!

# Returns a dictionary representation of the tree where
# keys are strings that are the names of edges and values are 4-tuples
# of strings of the form:
# (topVertex, bottomVertex, leftEdgeName, rightEdgeName)

# python libraries
from io import StringIO

# BioPython libraries
from Bio import Phylo

def getInput(filename):
    """
    Takes a filename as input and returns the host tree, parasite tree, and tip mapping phi
    :param filename <str>   - filename of newick file to parse
    :return                 0 <dict> - the host tree,
                            1 <dict> - the parasite tree,
                            3 <dict> - and a map phi from the tips of the parasite
                                          tree to those of the host tree
    """

    file_handle = open(filename, 'r')
    host_tree, parasite_tree, phi = newick_format_reader(file_handle)
    file_handle.close()
    return host_tree, parasite_tree, phi

def newick_format_reader(file_handle):
    """
    Queries the user for a newick host tree, newick parasite tree, and
    a tip association file.  Reads those files, parses them, and returns
    the three items.  The file of associations contains entries of the form
    parasite_tip:host_tip, one entry per line.
    The trees are returned in the dictionary format
    used by xscape.
    :param file_handle <TextIOWrapper or str> - file_handle to read and parse
    :return                                   0 <dict> - the host tree,
                                              1 <dict> - the parasite tree,
                                              2 <dict> - and a map with parasite names as keys
                                                         and host tips as values
    """

    if isinstance(file_handle, str):
        file_handle = open(file_handle, 'r')
        autoclose = True
    else:
        autoclose = False

    # Read contents, split the host tree, parasite tree, and tip associations
    contents = file_handle.read()
    host_string, parasite_string, phi_string = contents.split(";")
    host_string = host_string.strip()
    parasite_string = parasite_string.strip()
    phi_list = phi_string.split()

    # Parse the input and build dictionary representations
    host_dict = parse_newick(host_string, "host")
    parasite_dict = parse_newick(parasite_string, "parasite")
    phi_dict = parse_phi(phi_list)

    if autoclose:
        file_handle.close()

    return host_dict, parasite_dict, phi_dict

def parse_newick(newick_string, tree_type):
    """
    Queries the user for a newick file name and returns the contents
    of that file in the dictionary representation used by the xscape
    tools
    :param newick_string <str>   - string representation of tree
    :param tree_type <str>       - "host" or "parasite"
    :return tree_dict <dict>     - dict representation of tree
    """

    tree = Phylo.read(StringIO(newick_string), "newick")
    distance_dict = tree.depths(unit_branch_lengths=True)
    D = {}
    for clade in distance_dict:
        name = clade.name
        dist = distance_dict[clade]
        D[name] = dist
    dfs_list = [(node.name, int(D[node.name])) for node in tree.find_clades()]
    tree_dict = {}
    build_tree_dictionary(build_tree(dfs_list), "Top", tree_dict, tree_type)
    return tree_dict

def build_tree(dfs_list):
    """
    Converts dfs_list into a tuple representation of the tree of the form
    (Root, Left, Right) where Left and Right are themselves of this form
    or None. This is an intermediate tree representation that can then
    be used to build the dictionary representation of trees used in
    the xscape tools.
    :param dfs_list <list>   - list of tuples of the form (node_name, distance_from_root)
    :return <tuple>          - tuple representation of the tree
    """

    if len(dfs_list) == 1:
        return (dfs_list[0][0], None, None)
    else:
        root_name = dfs_list[0][0]
        dist = dfs_list[0][1]
        split_point = 0
        for x in range(len(dfs_list)-1, 0, -1):
            if dfs_list[x][1] == dist+1:
                split_point = x
                break
        left_list = dfs_list[1:split_point]
        right_list = dfs_list[split_point:]
        left_tree = build_tree(left_list)
        right_tree = build_tree(right_list)
        return (root_name, left_tree, right_tree)

def build_tree_dictionary(tuple_tree, parent_vertex, D, tree_type):
    """
    Takes as input a tuple representation of a tree (constructed by
    the build_tree function, for example) and returns the dictionary
    representation of the tree used by the xscape tools
    :param tuple_tree <tuple>    - tuple representation of the tree from build_tree()
    :param parent_vertex <str>   - (name of the) root of the tuple_tree
    :param D <dict>              - dictionary representation of the tree
    :param tree_type <str>       - "host" or "parasite"
    :return <None>               - D is updated so that it may represent the tree
    """

    root = tuple_tree[0]
    left_tree = tuple_tree[1]
    right_tree = tuple_tree[2]
    if tree_type == "parasite" and parent_vertex == "Top":
        edge_name = "pTop"
    elif tree_type == "host" and parent_vertex == "Top":
        edge_name = "hTop"
    else:
        edge_name = (parent_vertex, root)

    if left_tree == None:  # and thus rightTree == None and this is a leaf
        D[edge_name] = edge_name + (None, None)
    else:
        left_edge_name = (root, left_tree[0])
        right_edge_name = (root, right_tree[0])
        if edge_name == "pTop":
            D[edge_name] = ("Top", root, left_edge_name, right_edge_name)
        elif edge_name == "hTop":
            D[edge_name] = ("Top", root, left_edge_name, right_edge_name)
        else:
            D[edge_name] = edge_name + (left_edge_name, right_edge_name)
        build_tree_dictionary(left_tree, root, D, tree_type)
        build_tree_dictionary(right_tree, root, D, tree_type)

def parse_phi(pairs):
    """
    Queries the user for a file name containing tip associations of
    the form parasite_tip:host_tip, one entry per line
    :param pairs <list>   - list of strings of the form parasite_tip:host_tip
    :return <dict>        - maps parasite_tip to host_tip for every string in pairs
    """

    phi_dict = {}
    for pair in pairs:
        parasite, colon, host = pair.partition(":")
        key = parasite.strip()
        value = host.strip()
        phi_dict[key] = value
    return phi_dict


