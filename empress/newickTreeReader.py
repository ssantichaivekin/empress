# ReconInput class
from io import StringIO

# BioPython libraries
from Bio import Phylo

class ReconInput(object):
    """
    Storage class for the newick data (trees, tip mapping, and optional distance parameters)
    Distances encode branch lengths in the newick file, if given
    """

    def __init__(self, host_tree = None, host_distances = None, parasite_tree = None, 
                parasite_distances = None, phi = None):
        self.host_tree = host_tree
        self.host_distances = host_distances
        self.parasite_tree = parasite_tree
        self.parasite_distances = parasite_distances
        self.phi = phi

    def complete(self):
        return not self.host_tree is None and not self.parasite_tree is None and not self.phi is None

    def read_host(self, file_name : str):
        """
        Takes a host filename as input and sets self.host_dict and self.host_distances
        :param file_name <str>    - filename of host file to parse
        :return None
        """
        self.host_tree, self.host_distances = ReconInput.read_newick_tree(file_name, "host")
  
    def read_parasite(self, file_name : str):
        """
        Takes a parasite filename as input and sets self.parasite_dict and self_host_distances
        :param file_name <str>   - filename of parasite file to parse
        :return None
        """
        self.parasite_tree, self.parasite_distances = ReconInput.read_newick_tree(file_name, "parasite")

    def read_mapping(self, file_name : str):
        """
        Takes a mapping filename as input and reutrns the mapping dictionary between a host and parasite
        :param filename <str>   - filename of the map file to parse
        :return None
        """
        if isinstance(file_name, str):
            map_file = open(file_name, 'r')
        else:
            return None

        map_string = map_file.read()
        map_list = map_string.split()
        self.phi = ReconInput.parse_phi(map_list)
        map_file.close()

    @staticmethod
    def imply_mapping(host_tree : tree, parasite_tree : tree):
        """
        Takes in a host and parasite tree and tries to implicitely find a mapping for them
        :param host_tree <tree> - the host tree
        :param parasite_tree <tree> - the parasite tree
        """
        prefix_mode = True
        host_tips = host_tree.get_terminals()
        parasite_tips = parasite_tree.get_terminals()
        mapping = {}
        for host in host_tips:
            has_val = False
            for parasite in parasite_tips:
                if parasite.find(host) == 0:
                    mapping[parasite] = host
                    has_val = True
            if not has_val:
                prefix_mode = False
        if prefix_mode:
            return mapping

        mapping = {}
        postfix_mode = True
        for host in host_tips:
            has_val = False
            for parasite in parasite_tips:
                if parasite.find(host + "_") == 0:
                    mapping[parasite] = host
                    has_val = True
            if not has_val:
                postfix_mode = False
        if postfix_mode:
            return mapping
        
        print("Unable to match host and parasite trees.")
        return {}

    @staticmethod
    def read_newick_tree(file_name : str, tree_type: str):
        """
        Take a filename of a newick tree as input and returns the parsed version of that tree.
        :param filename <str>
        :param tree_type (either "host" or "parasite")
        """
        if isinstance(file_name, str):
            host_file = open(file_name, 'r')
        else:
            return None

        tree_string = host_file.read().strip()
        return ReconInput.parse_newick(tree_string, tree_type)
        host_file.close()

    @staticmethod
    def parse_newick(newick_string, tree_type):
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
        dfs_list = [(node.name, int(D[node.name])) for node in tree.find_clades()]
        tree_dict = {}
        ReconInput.build_tree_dictionary(ReconInput.build_tree(dfs_list), "Top", tree_dict, tree_type)
        real_distances = tree.depths()
        real_distance_dict = {}
        for clade in real_distances:
            name = clade.name
            real_distance_dict[name] = dist
        return tree_dict, real_distance_dict

    @staticmethod
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
            left_tree = ReconInput.build_tree(left_list)
            right_tree = ReconInput.build_tree(right_list)
            return (root_name, left_tree, right_tree)

    @staticmethod
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
            ReconInput.build_tree_dictionary(left_tree, root, D, tree_type)
            ReconInput.build_tree_dictionary(right_tree, root, D, tree_type)

    @staticmethod
    def parse_phi(pairs):
        """
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