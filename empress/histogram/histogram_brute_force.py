'''
Implements brute force algorithm to calculate the diameter
and histogram of a reconciliation graph. I use this to compare
the results from the DP algorithm.

Author: Santi Santichaivekin
'''

from empress.histogram.Histogram import Histogram

def event_node_type(event_node):
    '''
    Returns type 'S', 'T', 'D', L', or 'C'
    'S': speciation
    'D': duplication
    'T': transfer
    'L': loss
    'C': end event
    :param event_node <tuple>   - the event node being inspected
    :return <str>               - type of the event node
    '''
    return event_node[0]

def first_child(event_node):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # returns a mapping node
    assert(event_node[1][0] and event_node[1][1])
    return event_node[1]

def second_child(event_node):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # ['C', (None, None), (None, None), 1.0]
    # returns a mapping node
    # do not use on null entities
    assert(event_node[2][0] and event_node[2][1])
    return event_node[2]

def BF_enumerate_partial_MPRs(recongraph, mapping_node) :
    '''
    Given a reconciliation graph and a mapping node, enumerate all
    the MPRs in the reconciliation graph starting at the mapping node.
    '''
    for event_node in recongraph[mapping_node]:
        if event_node_type(event_node) in ['S', 'T', 'D']:
            for left_mapping_dict in BF_enumerate_partial_MPRs(recongraph, first_child(event_node)):
                for right_mapping_dict in BF_enumerate_partial_MPRs(recongraph, second_child(event_node)):
                    recon_tree = {}
                    recon_tree[mapping_node] = [event_node]
                    recon_tree.update(left_mapping_dict)
                    recon_tree.update(right_mapping_dict)
                    yield recon_tree
        elif event_node_type(event_node) == 'L':
            for child_mapping_dict in BF_enumerate_partial_MPRs(recongraph, first_child(event_node)):
                recon_tree = {}
                recon_tree[mapping_node] = [event_node]
                recon_tree.update(child_mapping_dict)
                yield recon_tree
        elif event_node_type(event_node) == 'C':
            recon_tree = {}
            recon_tree[mapping_node] = [event_node]
            yield recon_tree

def BF_enter_hist(recongraph, uA, uB):
    '''
    Given a reconciliation graph and two mapping nodes,
    find the histogram that embodies the different pairs 
    of partial MPRs between uA and uB.
    '''
    if uA == uB:
        hist_dict = {}
        recon_trees = list(BF_enumerate_partial_MPRs(recongraph, uA))
        for recon_tree_i in range(0, len(recon_trees)):
            for recon_tree_j in range(recon_tree_i+1):
                recon_tree_A = recon_trees[recon_tree_i]
                recon_tree_B = recon_trees[recon_tree_j]
                diff_count = recon_trees_diff(recon_tree_A, recon_tree_B)
                if diff_count not in hist_dict:
                    hist_dict[diff_count] = 0
                hist_dict[diff_count] += 1
        return Histogram(hist_dict)
    else: # uA != uB
        hist_dict = {}
        uA_recon_trees = list(BF_enumerate_partial_MPRs(recongraph, uA))
        uB_recon_trees = list(BF_enumerate_partial_MPRs(recongraph, uB))
        for recon_tree_A in uA_recon_trees:
            for recon_tree_B in uB_recon_trees:
                diff_count = recon_trees_diff(recon_tree_A, recon_tree_B)
                if diff_count not in hist_dict:
                    hist_dict[diff_count] = 0
                hist_dict[diff_count] += 1
        return Histogram(hist_dict)

def BF_exit_hist(recongraph, uA, uB):
    return NotImplementedError("Brute force exit calculation not yet implemented")

def BF_enumerate_MPRs(recongraph, roots) :
    '''
    Given a reconciliation graph, enumerate every reconciliation trees in the graph.
    Note that reconciliation trees are just like reconciliation graph, but each mapping
    node can only have one event node child.
    '''
    for root in roots:
        for recon_tree in BF_enumerate_partial_MPRs(recongraph, root):
            yield recon_tree, root

def recon_trees_diff(recon_tree_A, recon_tree_B):
    '''
    Return the symmetric set difference between
    the two trees.
    '''
    diff_count = 0
    for mapping_node_key in recon_tree_A:
        if mapping_node_key not in recon_tree_B :
            diff_count += 1
        elif recon_tree_A[mapping_node_key] != recon_tree_B[mapping_node_key] :
            diff_count += 1
    
    for mapping_node_key in recon_tree_B:
        if mapping_node_key not in recon_tree_A :
            diff_count += 1
        elif recon_tree_A[mapping_node_key] != recon_tree_B[mapping_node_key] :
            diff_count += 1
    
    return diff_count

def count_mpr_pairs(hist) :
    '''
    Total number of reconciliation pairs in the histogram.
    Note that this include self-pair (a, a).
    '''
    total = 0
    hist_dict = hist.histogram_dict
    for key in hist_dict :
        if key >= 1:
            total += hist_dict[key]
    return total

def calculate_n_pairs(m) :
    '''
    If there is m diffeerent MPRs in the reconciliation
    graph, there should be m*(m-1)/2 different pairs in
    the graph.
    '''
    return m*(m-1)/2

def BF_find_histogram(recongraph, roots) :
    '''
    Given a reconciliation graph, find the histogram of the graph via enumreating
    all of its reconciliation trees.
    '''
    hist_dict = {}
    recon_trees = [recon_tree for recon_tree, root in BF_enumerate_MPRs(recongraph, roots)]
    for recon_tree_i in range(0, len(recon_trees)):
        for recon_tree_j in range(recon_tree_i+1):
            recon_tree_A = recon_trees[recon_tree_i]
            recon_tree_B = recon_trees[recon_tree_j]
            diff_count = recon_trees_diff(recon_tree_A, recon_tree_B)
            if diff_count not in hist_dict:
                hist_dict[diff_count] = 0
            hist_dict[diff_count] += 1
    
    return Histogram(hist_dict)

def BF_find_diameter(recongraph, roots) :
    '''
    Given a reconciliation graph, find the diameter for the graph via enumerating
    all of its reconcilation trees.
    '''
    hist_dict = BF_find_histogram(recongraph, roots).histogram_dict
    return max(hist_dict.keys())

class BFVerifier:
    '''
    The brute force verifier is initialized once with the
    reconciliation graph. Then, you can verify the histogram
    algorithm by calling the verifier.
    '''
    def __init__(self, recongraph, error_func=None):
        # The error function is a two argument function
        # lambda (alg_hist, bf_hist, message) that deals with the error
        self.recongraph = recongraph
        def print_hist_diff(alg_hist, bf_hist, message):
            print(message)
            print("Histogram from Brute Force:", bf_hist)
            print("Histogram from Algorithm  :", alg_hist)
        self.error_func = print_hist_diff
    
    def verify_enter(self, uA, uB, alg_enter_hist):
        bf_hist = BF_enter_hist(self.recongraph, uA, uB)
        if alg_enter_hist != bf_hist:
            message = "Failed enter %s %s" % (str(uA), str(uB))
            self.error_func(alg_enter_hist, bf_hist, message)
    
    def verify_exit(self, uA, uB, alg_exit_hist):
        bf_hist = BF_exit_hist(self.recongraph, uA, uB)
        if alg_exit_hist != bf_hist:
            message = "Failed exit %s %s" % (str(uA), str(uB))
            self.error_func(alg_exit_hist, bf_hist, message)
