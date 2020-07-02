# ReconInput class
from io import StringIO

# BioPython libraries
from Bio import Phylo

from pathlib import Path

class ReconInputError(Exception):
    pass

class ReconInput:
    """
    Storage class for the newick data (trees, tip mapping, and optional distance parameters)
    Distances encode branch lengths in the newick file, if given
    """

    def __init__(self, host_dict=None, host_distances=None, parasite_dict=None,
                 parasite_distances=None, tip_mapping=None):
        if tip_mapping is not None:
            ReconInput._verify_tip_mapping(host_dict, parasite_dict, tip_mapping)
        self.host_dict = host_dict
        self.host_distances = host_distances
        self.parasite_dict = parasite_dict
        self.parasite_distances = parasite_distances
        self.tip_mapping = tip_mapping

    @classmethod
    def from_files(cls, host_fname: str, parasite_fname: str, mapping_fname: str):
        recon_input = cls()
        recon_input.read_host(host_fname)
        recon_input.read_parasite(parasite_fname)
        recon_input.read_mapping(mapping_fname)
        return recon_input

    def is_complete(self):
        return self.host_dict is not None and self.parasite_dict is not None and self.tip_mapping is not None

    def read_host(self, file_name: str):
        """
        Takes a host filename as input and sets self.host_dict and self.host_distances
        :param file_name <str>    - filename of host file to parse
        """
        self.host_dict, self.host_distances = ReconInput._read_newick_tree(file_name, "host")
  
    def read_parasite(self, file_name: str):
        """
        Takes a parasite filename as input and sets self.parasite_dict and self_host_distances
        :param file_name <str>   - filename of parasite file to parse
        """
        self.parasite_dict, self.parasite_distances = ReconInput._read_newick_tree(file_name, "parasite")

    def read_mapping(self, file_name: str):
        """
        Takes a mapping filename as input and returns the mapping dictionary between a host and parasite
        :param file_name <str>   - filename of the map file to parse
        """
        if not isinstance(file_name, str):
            raise ReconInputError("file_name %s is not a string" % file_name)

        if self.host_dict is None:
            raise ReconInputError("attempt to read tip mapping before reading host tree")

        if self.parasite_dict is None:
            raise ReconInputError("attempt to read tip mapping before reading parasite tree")

        try:
            with open(file_name) as map_file:
                map_list = map_file.read().split()
                tip_mapping = ReconInput._parse_tip_mapping(map_list)
                ReconInput._verify_tip_mapping(self.host_dict, self.parasite_dict, tip_mapping)
                self.tip_mapping = tip_mapping
        except Exception as e:
            raise ReconInputError(e)

    def save_to_files(self, host_fname: str, parasite_fname: str, tip_mapping_fname: str):
        ReconInput._save_newick_tree_to_file(self.host_dict, host_fname)
        ReconInput._save_newick_tree_to_file(self.parasite_dict, parasite_fname)
        ReconInput._save_tip_mapping_to_file(self.tip_mapping, tip_mapping_fname)

    @staticmethod
    def _save_newick_tree_to_file(tree_dict, fname):
        if Path(fname).suffix not in [".tree", ".nwk", ".newick"]:
            raise ReconInputError("Newick file name %s does not end with .tree, .nwk, or .newick" % fname)

        root_name = 'hTop' if 'hTop' in tree_dict else 'pTop'
        tree_dict_str = ReconInput._tree_dict_to_str(tree_dict, root_name)
        with open(fname, 'w') as f:
            print(tree_dict_str, file=f)

    @staticmethod
    def _tree_dict_to_str(tree_dict, root):
        parent, child, left_edge, right_edge = tree_dict[root]
        if left_edge is None: # tip
            return child
        else:
            return "({},{}){}".format(
                ReconInput._tree_dict_to_str(tree_dict, left_edge),
                ReconInput._tree_dict_to_str(tree_dict, right_edge),
                child
            )

    @staticmethod
    def _save_tip_mapping_to_file(tip_mapping: dict, fname: str):
        if Path(fname).suffix != ".mapping":
            raise ReconInputError("Mapping file name %s does not end with .mapping" % fname)

        with open(fname, 'w') as f:
            for parasite_node, host_node in tip_mapping.items():
                print("%s:%s" % (parasite_node, host_node), file=f)

    @staticmethod
    def _read_newick_tree(file_name: str, tree_type: str):
        if not isinstance(file_name, str):
            raise ReconInputError("file_name %s is not a string" % file_name)

        try:
            with open(file_name) as host_file:
                tree_string = host_file.read().strip()
                return ReconInput._parse_newick(tree_string, tree_type)
        except Exception as e:
            raise ReconInputError(e)

    @staticmethod
    def _parse_newick(newick_string, tree_type):
        """
        :param newick_string <str>   - string representation of tree
        :param tree_type <str>       - "host" or "parasite"
        :return tree_dict <dict>     - dict representation of tree
        :return real_distance_dict <dict> - maps node name to distance of that node from the root
        """

        tree = Phylo.read(StringIO(newick_string), "newick")
        distance_dict = tree.depths(unit_branch_lengths=True)
        # Get the actual distance annotations (zero for unannotated trees)
        D = {}
        for clade in distance_dict:
            name = clade.name
            dist = distance_dict[clade]
            D[name] = dist
        dfs_list = [(node.name, float(D[node.name])) for node in tree.find_clades()]
        tree_dict = {}
        ReconInput._build_tree_dictionary(ReconInput._build_tree(dfs_list), "Top", tree_dict, tree_type)
        real_distances = tree.depths()
        real_distance_dict = {}
        for clade in real_distances:
            name = clade.name
            real_distance_dict[name] = dist
        return tree_dict, real_distance_dict

    @staticmethod
    def _build_tree(dfs_list):
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
            return dfs_list[0][0], None, None
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
            left_tree = ReconInput._build_tree(left_list)
            right_tree = ReconInput._build_tree(right_list)
            return root_name, left_tree, right_tree

    @staticmethod
    def _build_tree_dictionary(tuple_tree, parent_vertex, tree_dict, tree_type):
        """
        Takes as input a tuple representation of a tree (constructed by
        the _build_tree function, for example) and returns the dictionary
        representation of the tree used by the xscape tools
        :param tuple_tree <tuple>    - tuple representation of the tree from _build_tree()
        :param parent_vertex <str>   - (name of the) root of the tuple_tree
        :param tree_dict <dict>              - dictionary representation of the tree
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

        if left_tree is None:  # and thus rightTree == None and this is a leaf
            tree_dict[edge_name] = edge_name + (None, None)
        else:
            left_edge_name = (root, left_tree[0])
            right_edge_name = (root, right_tree[0])
            if edge_name == "pTop":
                tree_dict[edge_name] = ("Top", root, left_edge_name, right_edge_name)
            elif edge_name == "hTop":
                tree_dict[edge_name] = ("Top", root, left_edge_name, right_edge_name)
            else:
                tree_dict[edge_name] = edge_name + (left_edge_name, right_edge_name)
            ReconInput._build_tree_dictionary(left_tree, root, tree_dict, tree_type)
            ReconInput._build_tree_dictionary(right_tree, root, tree_dict, tree_type)

    @staticmethod
    def _parse_tip_mapping(pairs):
        """
        :param pairs <list>   - list of strings of the form parasite_tip:host_tip
        :return <dict>        - maps parasite_tip to host_tip for every string in pairs
        """
        tip_mapping_dict = {}
        for pair in pairs:
            parasite, colon, host = pair.partition(":")
            key = parasite.strip()
            value = host.strip()
            tip_mapping_dict[key] = value
        return tip_mapping_dict

    @staticmethod
    def _leaves_from_tree_dict(tree_dict):
        leaves = []
        for key in tree_dict:
            parent, child, left_edge, right_edge = tree_dict[key]
            if left_edge is None and right_edge is None:
                leaves.append(child)
        return leaves

    @staticmethod
    def _verify_tip_mapping(host_dict, parasite_dict, tip_mapping_dict):
        """
        Throws exception if tip_mapping_dict is not valid
        """
        host_leaves = ReconInput._leaves_from_tree_dict(host_dict)
        parasite_leaves = ReconInput._leaves_from_tree_dict(parasite_dict)
        for parasite in tip_mapping_dict:
            host = tip_mapping_dict[parasite]
            if host not in host_leaves:
                raise ReconInputError("Mapping %s [parasite] -> %s [host] found but %s is not in host tree" %
                               (parasite, host, host))
            if parasite not in parasite_leaves:
                raise ReconInputError("Mapping %s [parasite] -> %s [host] found but %s is not in parasite tree" %
                               (parasite, host, parasite))

