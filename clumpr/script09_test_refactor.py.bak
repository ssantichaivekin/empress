'''
Test the correct of the current implementation of maximum distance reconciliation.
We do this by assuming that the DP algorithm generates a valid reconciliation graph,
then we use the diamater algorithm to find the max distance (diameter) among the 
reconciliation trees in that reconciliation graph. We then compare the max distance
which is calculated by the algorithm with the max distance that is computed by 
enumerating all the reconciliation trees in the graph, finding the pairwise distance
of each.
'''

import DTLReconGraph
import ReconciliationVisualization
import Diameter
import HistogramAlg
import HistogramAlgTools
from Histogram import Histogram
import itertools
import random
random.seed(1)

import os
import re
from sys import stdout

def get_tree_paths(tree_dir, min_size):
    paths = []
    for (dirpath, dirnames, fnames) in os.walk(tree_dir):
        for fname in fnames:
            fpath = os.path.join(dirpath, fname)
            # Parse the filename to get the size and the ID
            match_list = re.findall("(\d+)", fpath)
            i_list = [int(i) for i in match_list]
            assert len(i_list) == 3
            tree_size = i_list[0]
            # Skip trees that are smaller than the minimum specified size
            if tree_size < min_size:
                continue
            tree_id = i_list[2]
            paths.append((fpath, tree_size, tree_id))
    return paths

min_size = 7

# If you just want to look at and/or debug the output of only one file,
# then you should just set the tree_size, D, T, L, file_id, and just run
# the histogram algorithm once. (see the commented out code below)
if __name__ == '__main__' :
    # Find the path to each tree sample file
    tree_dir = "newickSample"
    tree_paths = get_tree_paths(tree_dir, min_size)
    n_trees = len(tree_paths)
    tree_index = 0
    for (tree_file, tree_size, tree_id) in tree_paths:
        tree_index += 1
        print(tree_file)
        stdout.write("Processing tree: %d / %d\r" % (tree_index, n_trees))
        stdout.flush()
        # Test different D, T, L values in {1, 2, 3, 4}
        for D, T, L in itertools.product([1, 2, 3, 4], repeat=3):
            # From the newick tree create the reconciliation graph
            edge_species_tree, edge_gene_tree, dtl_recon_graph, mpr_count, best_roots \
                = DTLReconGraph.reconcile(tree_file, D, T, L)

            # Sanity check: the mpr_count returned is equal to the count generated via brute force
            assert(mpr_count == sum(1 for _ in HistogramAlgTools.BF_enumerate_MPRs(dtl_recon_graph, best_roots)))

            # Calculate the histogram via brute force
            brute_force_hist = HistogramAlgTools.BF_find_histogram(dtl_recon_graph, best_roots)

            # Reformat the host and parasite tree to use it with the histogram algorithm
            gene_tree, gene_tree_root, gene_node_count = Diameter.reformat_tree(edge_gene_tree, "pTop")
            species_tree, species_tree_root, species_node_count \
                = Diameter.reformat_tree(edge_species_tree, "hTop")

            # Calculate the histogram via histogram algorithm
            diameter_alg_hist = HistogramAlg.diameter_algorithm(
                species_tree, gene_tree, gene_tree_root, dtl_recon_graph, dtl_recon_graph,
                False, False, verify=True)

            # If there is a mismatch, print the details and save the tree that causes
            # the error to a folder called errorTrees.
            if brute_force_hist != diameter_alg_hist :
                outname = './errorTrees/no%d-id%d-%d%d%d.png' % (tree_size, tree_id, D, T, L)
                ReconciliationVisualization.visualizeAndSave(dtl_recon_graph, outname)
                expected_n_pairs = HistogramAlgTools.calculate_n_pairs(mpr_count)
                brute_force_n_pairs = HistogramAlgTools.count_mpr_pairs(brute_force_hist)
                diag_force_n_pairs = HistogramAlgTools.count_mpr_pairs(diameter_alg_hist)
                print "ID = ", file_id, "DTL = ", D, T, L
                print "Expected pairs ", expected_n_pairs
                print "Brute Force: ", brute_force_hist, "pairs: ", brute_force_n_pairs
                print "Diameter Alg: ", diameter_alg_hist, "pairs: ", diag_force_n_pairs
                print ""


