# Tree.py
# Defines classes related to host and parasite nodes and trees

from enum import Enum

class TreeType(Enum):
    HOST = 1
    PARASITE = 2

# The Node class defines a node of a tree
class Node:
    def __init__(self, name):
        self.name = name            # String; name of this host or parasite
        self.left_node = None       # Node:  left child Node or None
        self.right_node = None      # Node:  right child Node or None
        self.parent_node = None     # Node:  parent Node or None
        self.layout = None          # NodeLayout object: layout of this node

    # The @property decorator allows this to be called as .is_leaf rather than .is_leaf()
    @property
    def is_leaf(self):
        return self.left_node is None and self.right_node is None

    # The @property decorator allows this to be called as .is_root rather than .is_root()
    @property
    def is_root(self):
        return self.parent_node is None

    def __repr__(self):
        return str(self.name)
    
class NodeLayout:
    def __init__(self):
        self.row = None         # float: logical position of this Node in rendering

        # The self.col can be generated from a topological ordering of the temporal constraint graph
        self.col = None         # float: logical position of this Node in rendering 
 
        self.x = None           # int: x-coordinate for rendering
        self.y = None           # int: y-coordinate for rendering

# The Tree type defines a tree
class Tree:
    def __init__(self):
        self.root_node = None       # Node:  Root Node of the Tree 
        self.tree_type = None       # TreeType: HOST or PARASITE 

    def leaf_list(self):
        """ Returns list of leaf Nodes from left to right. """
        return self._leaf_list_helper(self.root_node)

    def _leaf_list_helper(self, node):
        if node.is_leaf: return [node]
        else:
            list1 = self._leaf_list_helper(node.left_node)
            list2 = self._leaf_list_helper(node.right_node)
            list1.extend(list2)
            return list1


    def postorder_list(self):
        """ returns list of all Nodes in postorder """
        return self._postorder_list_helper(self.root_node)

    def _postorder_list_helper(self, node):
        if node.is_leaf: return [node]
        else:
            list1 = self._postorder_list_helper(node.left_node)
            list2 = self._postorder_list_helper(node.right_node)
            list1.extend(list2)
            list1.append(node)
            return list1


    
        



