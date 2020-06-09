import unittest
import os
import itertools
import shutil
from empress import newickFormatReader
from empress.topo_sort import recon_builder
from empress.clumpr import DTLReconGraph
from empress.clumpr import HistogramAlgTools
from empress.clumpr.script02_gen_newick_trees import generateNewickTestsMultipleSizes

class TestReconBuilder(unittest.TestCase):
    """
    Test the build_trees_with_temporal_order function from ReconBuilder.
    The first two test examples are temporally consistent, and next
    two test examples are temporally inconsistent. The last test genereates
    examples that might be temporally consistent or inconsistent.
    """

    size_range = [5] # range of sizes of the tree examples we want to generate
    generated_dir_path = "./temp_newick_samples" # directory for generated examples
    num_examples_to_test = 5 # number of examples to run in the last test

    def setUp(self):
        """
        Generate newick tests of certain sizes
        """
        generateNewickTestsMultipleSizes(self.size_range, self.generated_dir_path)

    def check_topological_order(self, temporal_graph, ordering_dict):
        """
        Helper function for checking the ordering_dict orders the nodes in temporal_graph
        in topological order
        """
        for node_tuple in temporal_graph:
            for node_tuple_child in temporal_graph[node_tuple]:
                is_child_leaf = node_tuple_child not in ordering_dict
                # leaves are not ordered
                if is_child_leaf:
                    continue
                self.assertTrue(ordering_dict[node_tuple] < ordering_dict[node_tuple_child])

    def check_temporally_consistent(self, host_tree, parasite_tree, reconciliation):
        """
        Helper function for checking a temporally consistent reconciliation has a
        topological order for the host and parasite nodes, and build_temporal_graph
        function instantiates the tree objects correctly and indicates the reconciliation
        is temporally consistent
        """
        temporal_graph = recon_builder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
        ordering_dict = recon_builder.topological_order(temporal_graph)
        self.assertIsNotNone(ordering_dict)
        self.check_topological_order(temporal_graph, ordering_dict)

        host, parasite, if_consistent = recon_builder.build_trees_with_temporal_order(host_tree,
                                                                    parasite_tree, reconciliation)
        self.assertIsNotNone(host)
        self.assertIsNotNone(parasite)
        self.assertTrue(if_consistent)

    def check_temporally_inconsistent(self, host_tree, parasite_tree, reconciliation):
        """
        Helper function for checking a temporally inconsistent reconciliation does not have
        a topological order for the host and parasite nodes, and build_temporal_graph
        function returns None, None, False
        """
        temporal_graph = recon_builder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
        ordering_dict = recon_builder.topological_order(temporal_graph)
        self.assertIsNone(ordering_dict)

        host, parasite, if_consistent = recon_builder.build_trees_with_temporal_order(host_tree,
                                                                    parasite_tree, reconciliation)
        self.assertIsNone(host)
        self.assertIsNone(parasite)
        self.assertFalse(if_consistent)

    def test_detect_consistency_1(self):
        """
        Test build_trees_with_temporal_order on a temporally consistent reconciliation
        """
        # a temporally consistent reconciliation with simple topological order
        host_tree = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
        ('m0', 'm1'): ('m0', 'm1', None, None),
        ('m0', 'm2'): ('m0', 'm2', ('m2', 'm3'), ('m2', 'm4')),
        ('m2', 'm3'): ('m2', 'm3', None, None),
        ('m2', 'm4'): ('m2', 'm4', None, None)}

        parasite_tree = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
        ('n0', 'n1'): ('n0', 'n1', None, None),
        ('n0', 'n2'): ('n0', 'n2', ('n2', 'n3'), ('n2', 'n4')),
        ('n2', 'n3'): ('n2', 'n3', None, None),
        ('n2', 'n4'): ('n2', 'n4', None, None)}

        reconciliation = { ('n0', 'm4'): [('D', ('n1', 'm4'), ('n2', 'm4'))],
        ('n1', 'm4'): [('C', (None, None), (None, None))],
        ('n2', 'm4'): [('D', ('n3', 'm4'), ('n4', 'm4'))],
        ('n3', 'm4'): [('C', (None, None), (None, None))],
        ('n4', 'm4'): [('C', (None, None), (None, None))]}

        self.check_temporally_consistent(host_tree, parasite_tree, reconciliation)

    def test_detect_consistency_2(self):
        """
        Test build_trees_with_temporal_order on another temporally consistent reconciliation
        """
        # a temporally consistent reconciliation with more complicated topological order
        host_tree = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
        ('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
        ('m0', 'm4'): ('m0', 'm4', ('m4', 'm5'), ('m4', 'm6')),
        ('m1', 'm2'): ('m1', 'm2', None, None),
        ('m1', 'm3'): ('m1', 'm3', None, None),
        ('m4', 'm5'): ('m4', 'm5', None, None),
        ('m4', 'm6'): ('m4', 'm6', None, None)}

        parasite_tree = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
        ('n0', 'n1'): ('n0', 'n1', ('n1', 'n5'), ('n1', 'n6')),
        ('n0', 'n2'): ('n0', 'n2', ('n2', 'n3'), ('n2', 'n4')),
        ('n1', 'n5'): ('n1', 'n5', None, None),
        ('n1', 'n6'): ('n1', 'n6', None, None),
        ('n3', 'n7'): ('n3', 'n7', None, None),
        ('n3', 'n8'): ('n3', 'n8', None, None),
        ('n2', 'n3'): ('n2', 'n3', ('n3', 'n7'), ('n3', 'n8')),
        ('n2', 'n4'): ('n2', 'n4', None, None),}

        reconciliation = { ('n0', 'm0'): [('S', ('n1', 'm1'), ('n2', 'm4'))],
        ('n1', 'm1'): [('S', ('n5', 'm2'), ('n6', 'm3'))],
        ('n2', 'm4'): [('T', ('n4', 'm4'), ('n3', 'm1'))],
        ('n4', 'm4'): [('L', ('n4', 'm6'), (None, None))],
        ('n4', 'm6'): [('C', (None, None), (None, None))],
        ('n3', 'm1'): [('S', ('n7', 'm2'), ('n8', 'm3'))],
        ('n7', 'm2'): [('C', (None, None), (None, None))],
        ('n8', 'm3'): [('C', (None, None), (None, None))],
        ('n5', 'm2'): [('C', (None, None), (None, None))],
        ('n6', 'm3'): [('C', (None, None), (None, None))]}

        self.check_temporally_consistent(host_tree, parasite_tree, reconciliation)

    def test_detect_inconsistency_1(self):
        """
        Test build_trees_with_temporal_order on a temporally inconsistent reconciliation
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

        self.check_temporally_inconsistent(host_tree, parasite_tree, reconciliation)

    def test_detect_inconsistency_2(self):
        """
        Test build_trees_with_temporal_order on another type of temporally inconsistent reconciliation
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

        self.check_temporally_inconsistent(host_tree, parasite_tree, reconciliation)

    def test_topological_order(self):
        """
        Test topological_order by generating host and parasite trees of different sizes and going through
        each reconciliaiton in the reconciliaiton graph to see if the order generated by topological_order
        is a topological order. We skip the reconciliations that are temporally inconsistent.
        """
        count = 0
        for tree_size in self.size_range:
            tree_size_Folder = '%s/size%d' % (self.generated_dir_path, tree_size)
            for newick in os.listdir(tree_size_Folder):
                if count >= self.num_examples_to_test: break
                if newick.startswith('.'): continue
                recon_input =  newickFormatReader.getInput(os.path.join(tree_size_Folder, newick))
                host_tree = recon_input.host_tree
                parasite_tree = recon_input.parasite_tree
                for d, t, l in itertools.product(range(1, 5), repeat=3):
                    recon_graph, _, _, best_roots = DTLReconGraph.DP(recon_input, d, t, l)
                    for reconciliation, _ in HistogramAlgTools.BF_enumerate_MPRs(recon_graph, best_roots):
                        temporal_graph = recon_builder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
                        ordering_dict = recon_builder.topological_order(temporal_graph)
                        # if there is no temporal inconsistency
                        if ordering_dict != None:
                            self.check_topological_order(temporal_graph, ordering_dict)
                count += 1

    def tearDown(self):
        """
        Clean up the generated tests
        """
        shutil.rmtree(self.generated_dir_path)

if __name__ == '__main__':
    unittest.main()
