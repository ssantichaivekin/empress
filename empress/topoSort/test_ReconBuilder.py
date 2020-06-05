import unittest
import os
import itertools
import shutil
from empress import newickFormatReader
from empress.topoSort import ReconBuilder
from empress.clumpr import DTLReconGraph
from empress.clumpr import HistogramAlgTools
from empress.clumpr.script02_gen_newick_trees import generateNewickTestsMultipleSizes

class TestReconBuilder(unittest.TestCase):
    """
    Test the build_trees_with_temporal_order function from ReconBuilder
    """
    @classmethod
    def setUp(self):
        """
        generate newick tests of certain sizes
        """
        size_range = [5]
        generated_dir_path = "./newickSample"
        generateNewickTestsMultipleSizes(size_range, generated_dir_path)

    @staticmethod
    def build_ordering_dict(host_tree, parasite_tree, reconciliation):
        """
        build the ordering dictionary given a host_tree, a parasite_tree, and a reconciliation.
        """
        temporal_graph = ReconBuilder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
        ordering_dict = ReconBuilder.topological_order(temporal_graph)
        return ordering_dict

    @staticmethod
    def check_topological_order(temporal_graph, ordering_dict):
        """
        Check the ordering_dict orders the nodes in temporal_graph in topological order
        """
        for node_tuple in temporal_graph:
            for node_tuple_child in temporal_graph[node_tuple]:
                is_child_leaf = node_tuple_child not in ordering_dict
                # leaves are not ordered
                if is_child_leaf:
                    continue
                assert(ordering_dict[node_tuple] < ordering_dict[node_tuple_child])

    @classmethod
    def test_detect_inconsistency_1(self):
        """
        test topological_order recognizes an inconsistent reconciliation
        """
        # a reconciliation with temporal inconsistency
        host_tree = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
        ('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
        ('m0', 'm4'): ('m0', 'm4', ('m4', 'm5'), ('m4', 'm6')),
        ('m1', 'm2'): ('m1', 'm2', None, None),
        ('m1', 'm3'): ('m1', 'm3', None, None),
        ('m4', 'm5'): ('m4', 'm5', None, None),
        ('m4', 'm6'): ('m4', 'm6', None, None)}

        parasite_tree = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n5')),
        ('n0', 'n1'): ('n0', 'n1', ('n1', 'n2'), ('n1', 'n3')),
        ('n1', 'n3'): ('n1', 'n3', ('n3', 'n4'), ('n3', 'n6')),
        ('n1', 'n2'): ('n1', 'n2', None, None),
        ('n3', 'n4'): ('n3', 'n4', None, None),
        ('n0', 'n5'): ('n0', 'n5', None, None),
        ('n3', 'n6'): ('n3', 'n6', None, None),}

        reconciliation = { ('n0', 'm1'): [('T', ('n1', 'm1'), ('n5', 'm5'))],
        ('n1', 'm1'): [('L', ('n1', 'm2'), (None, None))],
        ('n1', 'm2'): [('T', ('n2', 'm2'), ('n3', 'm4'))],
        ('n2', 'm2'): [('C', (None, None), (None, None))],
        ('n4', 'm5'): [('C', (None, None), (None, None))],
        ('n5', 'm5'): [('C', (None, None), (None, None))],
        ('n6', 'm6'): [('C', (None, None), (None, None))],
        ('n3', 'm4'): [('S', ('n4', 'm5'), ('n6', 'm6'))]}

        ordering_dict = TestReconBuilder.build_ordering_dict(host_tree, parasite_tree, reconciliation)
        assert(ordering_dict == None)

    @classmethod
    def test_detect_inconsistency_2(self):
        """
        test topological_order recognizes another type of inconsistent reconciliation
        """
        # a reconciliation with another type of temporal inconsistency
        host_tree = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
        ('m0', 'm1'): ('m0', 'm1', ('m1', 'm3'), ('m1', 'm4')),
        ('m1', 'm3'): ('m1', 'm3', None, None),
        ('m1', 'm4'): ('m1', 'm4', None, None),
        ('m0', 'm2'): ('m0', 'm2', None, None)}

        parasite_tree = { 'pTop': ('Top', 'n0', ('n0', 'n4'), ('n0', 'n2')),
        ('n0', 'n4'): ('n0', 'n4', None, None),
        ('n0', 'n2'): ('n0', 'n2', ('n2', 'n5'), ('n2', 'n3')),
        ('n2', 'n5'): ('n2', 'n5', None, None),
        ('n2', 'n3'): ('n2', 'n3', ('n3', 'n1'), ('n3', 'n6')),
        ('n3', 'n1'): ('n3', 'n1', None, None),
        ('n3', 'n6'): ('n3', 'n6', None, None)}

        reconciliation = { ('n0', 'm4'): [('T', ('n4', 'm4'), ('n2', 'm2'))],
        ('n2', 'm2'): [('T', ('n5', 'm2'), ('n3', 'm1'))],
        ('n3', 'm1'): [('S', ('n1', 'm3'), ('n6', 'm4'))],
        ('n1', 'm3'): [('C', (None, None), (None, None))],
        ('n4', 'm4'): [('C', (None, None), (None, None))],
        ('n5', 'm2'): [('C', (None, None), (None, None))],
        ('n6', 'm4'): [('C', (None, None), (None, None))]}

        ordering_dict = TestReconBuilder.build_ordering_dict(host_tree, parasite_tree, reconciliation)
        assert(ordering_dict == None)

    @classmethod
    def test_topological_order(self):
        """
        test topological_order by generating host and parasite trees of different sizes and going through
        each reconciliaiton in the reconciliaiton graph to see if the order generated by topological_order
        is a topological order
        """
        size_range = [5]
        generated_dir_path = "./newickSample"
        count = 0
        for tree_size in size_range:
            tree_size_Folder = '%s/size%d' % (generated_dir_path, tree_size)
            for newick in os.listdir(tree_size_Folder):
                if count >= 5: break # we only test 5 examples
                if newick.startswith('.'): continue
                recon_input =  newickFormatReader.getInput(os.path.join(tree_size_Folder, newick))
                host_tree = recon_input.host_tree
                parasite_tree = recon_input.parasite_tree
                for d, t, l in itertools.product(range(1, 5), repeat=3):
                    recon_graph, _, _, best_roots = DTLReconGraph.DP(recon_input, d, t, l)
                    for reconciliation, _ in HistogramAlgTools.BF_enumerate_MPRs(recon_graph, best_roots):
                        temporal_graph = ReconBuilder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
                        ordering_dict = ReconBuilder.topological_order(temporal_graph)
                        # if there is no temporal inconsistency
                        if ordering_dict != None:
                            TestReconBuilder.check_topological_order(temporal_graph, ordering_dict)
                count += 1

    @classmethod
    def tearDown(self):
        """
        clean up the generated tests
        """
        generated_dir_path = "./newickSample"
        if os.path.isdir(generated_dir_path):
            shutil.rmtree(generated_dir_path)

if __name__ == '__main__':
    unittest.main()
