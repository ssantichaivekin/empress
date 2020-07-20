# test_Tree.py
# Tests the Tree class and tree_format_converter.py
import unittest

from empress.recon_vis import tree
from empress.recon_vis.utils import dict_to_tree

# Edge-based format is the primary format used by eMPRess algorithms.  This is the format that input_reader.py
# constructs from a .newick input file.
# This format comprises  a dictionary in which each key is either the string "hTop" ("pTop") for the edge corresponding to 
# the handle of a host (parasite) tree or an edge tuple of the form (v1, v2) where v1 and v2 are strings denoting the
# name of the top and bottom vertices of that edge.  Values are 4-tuples of the form (v1, v2, edge1, edge2) where 
# edge1 and edge2 are the edge tuples for the branches emanating from (v1, v2).  If the branch terminates at a leaf
# then edge1 and edge2 are both None.

class TestTree(unittest.TestCase):
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
            ('m9', 'm10'): ('m9', 'm10', ('m10', 'melpomene_WestPA'), ('m10', 'rosina_WestCR')),
            ('m10', 'melpomene_WestPA'): ('m10', 'melpomene_WestPA', None, None),
            ('m10', 'rosina_WestCR'): ('m10', 'rosina_WestCR', None, None),
            ('m9', 'rosina_WestPA'): ('m9', 'rosina_WestPA', None, None),
            ('m8', 'm11'): ('m8', 'm11', ('m11', 'melpomene_EastC'), ('m11', 'cythera_WestE')),
            ('m11', 'melpomene_EastC'): ('m11', 'melpomene_EastC', None, None),
            ('m11', 'cythera_WestE'): ('m11', 'cythera_WestE', None, None)}

    def test_convert(self):
        host_converted = dict_to_tree(self.host, tree.TreeType.HOST)
        self.assertTrue(isinstance(host_converted, tree.Tree))

    def test_leaf_list(self):
        host_converted = dict_to_tree(self.host, tree.TreeType.HOST)
        leaves = host_converted.leaf_list()
        for leaf in leaves:
            self.assertTrue(isinstance(leaf, tree.Node))
            self.assertTrue(leaf.is_leaf())
        self.assertEqual(len(leaves), 12)

    def test_postorder_list(self):
        host_converted = dict_to_tree(self.host, tree.TreeType.HOST)
        nodes = host_converted.postorder_list()
        for node in nodes:
            self.assertTrue(isinstance(node, tree.Node))
        self.assertEqual(len(nodes), len(self.host))


if __name__ == '__main__':
    unittest.main()
