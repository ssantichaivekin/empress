# median.py
# Written July 2017 by Andrew Ramirez and Eli Zupke

# DATA STRUCTURE QUICK REFERENCE:
#
#
#   DTL or Median Reconciliation graph:
#       { mapping_node: [event1, event2, ... eventn, number], ...}
#   Event:
#       ('event_type', child_mapping_node1, child_mapping_node2)
#
#   Mapping node (case indicates capitalization standards):
#       ('gene_node', 'SPECIES_NODE')
#   or in loss or contemporary event nodes:
#       (None, None)
#
#
#   (edge) trees:
#       {('R','N'): ('R','N', ('N','C1'), ('N','C2')) ...}
#       aka:
#       {root_edge: (root_edge[0], root_edge[1], child1_edge, child2_edge) ...}
#
#   vertex_trees:
#       {'N':('C1','C2') ...}
#

import optparse
from operator import itemgetter

import numpy as np

from empress.reconcile import recongraph_tools, diameter

def mapping_node_sort(ordered_gene_node_list, ordered_species_node_list, mapping_node_list):
    """
    :param ordered_gene_node_list: an ordered dictionary of the gene nodes, where each key is a node
    and the corresponding values are children of that node in the gene tree. Note that the order (pre-
    or post-) in which this tree is passed determines the final order - a preorder gene node list will
    return mapping nodes sorted in preorder. The species and gene orderings must match.
    :param ordered_species_node_list: same as for the gene node list above, except for the species tree
    :param mapping_node_list: a list of all mapping nodes within a given reconciliation graph
    :return: the given mapping nodes except sorted in the order corresponding to the order in which
    the species and gene nodes are passed in (see description of ordered_gene_node_list for more on this).
    The returned mapping node list is sorted first by gene node and then by species node
    """

    # In order to sort the mapping nodes, we need a way to convert them into numbers. These two lookup tables allow
    # us to achieve a lexicographical ordering with gene nodes more significant than species nodes.
    gene_level_lookup = {}
    species_level_lookup = {}

    # By multiplying the gene node keys by the number of species nodes, we can ensure that a mapping node with a later
    # gene node always comes before one with a later species node, because a gene node paired with the last species
    # node will be one level less than the next gene node paired with the first species node.
    gene_multiplier = len(ordered_species_node_list)

    for i1, gene_node in enumerate(ordered_gene_node_list):
        gene_level_lookup[gene_node] = i1 * gene_multiplier

    for i2, species_node in enumerate(ordered_species_node_list):
        species_level_lookup[species_node] = i2

    # The lambda function looks up the level of both the gene node and the species nodes and adds them together to
    # get a number to give to the sorting algorithm for that mapping node. The gene node is weighted far more heavily
    # than the species node to make sure it is always more significant.
    sorted_list = sorted(mapping_node_list, key=lambda node: gene_level_lookup[node[0]] + species_level_lookup[node[1]])

    return sorted_list


def generate_scores(preorder_mapping_node_list, dtl_recon_graph, gene_root, normalize=True):
    """
    Computes frequencies for every event
    :param preorder_mapping_node_list: A list of all mapping nodes in DTLReconGraph in double preorder
    :param dtl_recon_graph: The DTL reconciliation graph that we are scoring
    :param gene_root: The root of the gene tree
    :return: 0. A file structured like the DTLReconGraph, but with the lists of events replaced
                with dicts, where the keys are the events and the values are the scores of those events, and
             1. The number of MPRs in DTLReconGraph.
    """

    # Initialize the dictionary that will store mapping node and event counts (which also acts as a memoization
    # dictionary)
    counts = dict()

    # Initialize the very start count, for the first call of countMPRs
    count = 0

    # Loop over all given minimum cost reconciliation roots
    for mapping_node in preorder_mapping_node_list:
        if mapping_node[0] == gene_root:

            # This will also populate the counts dictionary with the number of MPRs each event and mapping node is in
            count += count_mprs(mapping_node, dtl_recon_graph, counts)

    # Initialize the scores dict. This dict contains the frequency score of each mapping node
    scores = dict()
    for mapping_node in preorder_mapping_node_list:
        scores[mapping_node] = 0.0

    # This entry is going to be thrown away, but it seems neater to just let calculateScoresOfChildren
    # add scores to an unused entry than to check to see if they are (None, None) in the first place.
    scores[(None, None)] = 0.0

    # The scored graph is like the DTLReconGraph, except instead of individual events being in a list, they are the
    # keys of a dictionary where the values are the frequency scores of those events. So, event_scores takes event
    # nodes as keys and (after being filled below) has the frequencies of those events in MPRs as the values
    event_scores = {}

    for mapping_node in preorder_mapping_node_list:

        # If we are at the root of the gene tree, then we need to initialize the score entry
        if mapping_node[0] == gene_root:
            scores[mapping_node] = counts[mapping_node]
        # This fills up the event scores dictionary
        calculate_scores_for_children(mapping_node, dtl_recon_graph, event_scores, scores, counts)

    if normalize:
        # Normalize all of the event_scores by the number of MPRs
        # so that each score is a percentage
        for mapping_node in preorder_mapping_node_list:
            for event in dtl_recon_graph[mapping_node]:
                    event_scores[event] = event_scores[event] / float(count)

    return event_scores, count


def count_mprs(mapping_node, dtl_recon_graph, counts):
    """
    :param mapping_node: an individual mapping node that maps a node
    for the parasite tree onto a node of the host tree, in the format
    (p, h), where p is the parasite node and h is the host node
    :param dtl_recon_graph: A DTL reconciliation graph (see data structure quick reference at top of file)
    :param counts: a dictionary representing the running memo that is passed
    down recursive calls of this function. At first it is just an empty
    dictionary (see above function), but as it gets passed down calls, it collects
    keys of mapping nodes or event nodes and values of MPR counts. This memo improves runtime
    of the algorithm
    :return: the number of MPRs spawned below the given mapping node in the graph
    """

    # Search the counts dictionary for previously calculated results (this is the memoization)
    if mapping_node in counts:
        return counts[mapping_node]

    # Base case, occurs if being called on a child produced by a loss or contemporary event
    if mapping_node == (None, None):
        return 1

    # Initialize a variable to keep count of the number of MPRs
    count = 0

    # Loop over all event nodes corresponding to the current mapping node
    for eventNode in dtl_recon_graph[mapping_node]:

        # Save the children produced by the current event
        mapping_child1 = eventNode[1]
        mapping_child2 = eventNode[2]

        # Add the product of the counts of both children (over all children) for this event to get the parent's count
        counts[eventNode] = count_mprs(mapping_child1, dtl_recon_graph, counts) * count_mprs(mapping_child2,
                                                                                             dtl_recon_graph, counts)
        count += counts[eventNode]

    # Save the result in the counts
    counts[mapping_node] = count

    return count


def calculate_scores_for_children(mapping_node, dtl_recon_graph, event_scores, mapping_scores, counts):
    """
    This function calculates the frequency score for every mapping node that is a child of an event node that is a
    child of the given mapping node, and stores them in scoredGraph.
    :param mapping_node: The mapping node that is the parent of the two scores we will compute
    :param dtl_recon_graph: The DTL reconciliation graph (see data structure quick reference at top of file)
    :param event_scores: The scored DTL reconciliation graph (see data structure quick reference at top of file)
    :param mapping_scores: The score for each mapping node (which will ultimately be thrown away) that this function
    helps build up
    :param counts: The counts generated in countMPRs (from the bottom-up). Note that the counts are filled during a
    bottom-up traversal, and the scores are filled in during a top-down traversal after the counts
    :return: Nothing, but scoredGraph is built up.
    """

    assert mapping_scores[mapping_node] != 0, "Sorting error! Ensure that parents are calculated before children"

    # This multiplier results in  counts[event_node] / counts[mapping_node] for each event node, which is the % of
    # this mapping node's scores (scores[mapping_node]) that it gives to each event node.
    multiplier = float(mapping_scores[mapping_node]) / counts[mapping_node]

    # Iterate over every event
    for event_node in dtl_recon_graph[mapping_node]:

        event_scores[event_node] = multiplier * counts[event_node]

        # Save the children produced by the current event
        mapping_child1 = event_node[1]
        mapping_child2 = event_node[2]
        mapping_scores[mapping_child1] += event_scores[event_node]
        mapping_scores[mapping_child2] += event_scores[event_node]


def compute_median(dtl_recon_graph, event_scores, postorder_mapping_nodes, mpr_roots):
    """
    :param dtl_recon_graph: A dictionary representing a DTL Recon Graph.
    :param event_scores: A dictionary with event nodes as keys and values corresponding to the frequency of
    that events in MPR space for the recon graph
    :param postorder_mapping_nodes: A list of the mapping nodes in a possible MPR, except sorted first in
    postorder by species node and postorder by gene node
    :param mpr_roots: A list of mapping nodes that could act as roots to an MPR for the species and
    gene trees in question, output from the findBestRoots function in recongraph_tools.py
    :return: A new dictionary which is has the same form as a DTL reconciliation graph except every
    mapping node only has one event node, along with the number of median reconciliations for the given DTL
    reconciliation graph, as well as the root of the median MPR for the given graph. Thus, this graph will
    represent a single reconciliation: the median reconciliation.
    """

    # Note that for a symmetric median reconciliation, each frequency must have 0.5 subtracted from it

    # Initialize a dict that will store the running total frequency sum incurred up to the given mapping node,
    # and the event node that directly gave it that frequency sum. Keys are mapping nodes, values are tuples
    # consisting of a list of event nodes that maximize the frequency - 0.5 sum score for the lower level,
    # and the corresponding running total frequency - 0.5 sum up to that mapping node
    sum_freqs = dict()

    # Loop over all mapping nodes for the gene tree
    for map_node in postorder_mapping_nodes:

        # Contemporaneous events need to be caught from the get-go
        if dtl_recon_graph[map_node] == [('C', (None, None), (None, None))]:
            sum_freqs[map_node] = ([('C', (None, None), (None, None))], 0.5)  # C events have freq 1, so 1 - 0.5 = 0.5
            continue  # Contemporaneous events should be a lone event in a list, so we move to the next mapping node

        # Get the events for the current mapping node and their running (frequency - 0.5) sums, in a list
        events = list()
        for event in dtl_recon_graph[map_node]:

            # Note that 'event' is of the form: ('event ID', 'Child 1', 'Child 2'), so the 0th element is the event
            # ID and the 1st and 2nd elements are the children produced by the event
            if event[0] == 'L':  # Losses produce only one child, so we only need to look to one lower mapping node
                events.append((event, sum_freqs[event[1]][1] + event_scores[event] - 0.5))
            else:  # Only other options are T, S, and D, which produce two children
                events.append((event, sum_freqs[event[1]][1] + sum_freqs[event[2]][1] + event_scores[event] - 0.5))

        # Find and save the max (frequency - 0.5) sum
        max_sum = max(events, key=itemgetter(1))[1]

        # Initialize list to find all events that gives the current mapping node the best (freq - 0.5) sum
        best_events = list()

        # Check to see which event(s) produce the max (frequency - 0.5) sum
        for event in events:
            if event[1] == max_sum:
                best_events.append(event[0])

        # Help out the garage collector by discarding the now-useless non-optimal events list
        del events

        # Save the result for this mapping node so it can be used in higher mapping nodes in the graph
        sum_freqs[map_node] = (best_events[:], max_sum)

    # Get all possible roots of the graph and their running frequency scores, in a list, for later use
    possible_root_combos = [(root, sum_freqs[root][1]) for root in mpr_roots]

    # Find the best frequency - 0.5 sum for all of the potential roots for the median
    best_sum = max(possible_root_combos, key=itemgetter(1))[1]

    # Find all of the root combos for a median by filtering out the roots that don't give the best freq - 0.5 sum
    best_root_combos = list([x for x in possible_root_combos if x[1] == best_sum])

    # Extract just the roots from the previously filtered out list
    best_roots = [root[0] for root in best_root_combos]

    # Adjust the sum_freqs dictionary so we can use it with the buildDTLReconGraph function from recongraph_tools.py
    for map_node in sum_freqs:

        # We place the event tuples into lists so they work well with the diameter algorithm
        sum_freqs[map_node] = sum_freqs[map_node][0]  # Only use the events, no longer the associated frequency sum

    # Use the buildDTLReconGraph function from recongraph_tools.py to find the median recon graph
    # Note that build_dtl... requires a list of the best roots for a reconciliation graph, the events for each
    # mapping node that are viable for an MPR (in our case, the median), and an empty dicitonary to populate
    # as the final return value
    med_recon_graph = recongraph_tools.build_dtl_recon_graph(best_roots, sum_freqs, {})

    # Check to make sure the median is a subgraph of the DTL reconciliation
    assert check_subgraph(dtl_recon_graph, med_recon_graph), 'Median is not a subgraph of the recon graph!'

    # We can use this function to find the number of medians once we've got the final median recon graph
    n_med_recons = recongraph_tools.count_mprs_wrapper(best_roots, med_recon_graph)

    return med_recon_graph, n_med_recons, best_roots


def check_subgraph(recon_graph, subrecon):
    """
    :param recon_graph: A reconciliation graph
    :param subrecon: Another reconciliation graph, the one which is supposed to be a subgraph of "recon_graph"
    :return: a boolean value: True if the "subrecon" is really a subgraph of "recon_graph",
    False otherwise
    """

    # Loop over all mapping nodes contained in the median reconciliation graph
    for map_node in subrecon:

        # Loop over mapping nodes
        if map_node not in recon_graph:
            return False
        else:

            # Now events for a given mapping node
            for event in subrecon[map_node]:
                if event not in recon_graph[map_node]:
                    return False
    return True


def choose_random_median_wrapper(median_recon, med_roots, count_dict):
    """
    :param median_recon: the median reconciliation
    :param med_roots: the roots (root mapping nodes) for possible median reconciliations
    :param count_dict: a dictionary detailing how many medians can stem from an individual event
    node
    :return: a randomly, uniformly sampled median reconciliation graph
    """

    # Find the total amount of medians that can stem from the roots
    total_meds = 0.0
    for median_root in med_roots:
        total_meds += count_dict[median_root]

    # Create the choice list for the roots we can choose from, weighted to account for median
    # counts each root can produce
    # Note that numpy is so basic that we need to do a convoluted workaround to choose tuples from a list
    final_root = med_roots[np.random.choice(len(med_roots), p=[count_dict[med_root] / total_meds for med_root in
                                                               med_roots])]

    return choose_random_median(median_recon, final_root, count_dict)


def choose_random_median(median_recon, map_node, count_dict):
    """
    :param median_recon: the full median reconciliation graph, as returned by compute_median
    :param map_node: the current mapping node in the median reconciliation that we're trying
    to find a path from. In the first call, this mapping node will be one of the root mapping
    nodes for the median reconciliation graph, randomly selected
    :param count_dict: a dictionary that tells us how many total medians a given event node can spawn
    :return: a single-path reconciliation graph that is a sub-graph of the median. It is chosen
    randomly but randomly in such a way that event node choice will favor event nodes that lead
    to more MPRs so that the data aren't skewed
    """

    # Initialize the dictionary that will store the final single-path median that we choose
    random_submedian = dict()

    # Find the total number of medians we can get from the current mapping node
    total_meds = float(count_dict[map_node])

    # Use a convoluted numpy workaround to select tuples (events) from a list, taking into account
    # how many medians each event can produce
    next_event = median_recon[map_node][np.random.choice(len(median_recon[map_node]),
                                                         p=[count_dict[event] / total_meds for event in
                                                            median_recon[map_node]])]

    random_submedian.update({map_node: [next_event]})

    # Check for a loss
    if next_event[0] == 'L':
        random_submedian.update(choose_random_median(median_recon, next_event[1], count_dict))

    # Check for events that produce two children
    elif next_event[0] in ['T', 'S', 'D']:
        random_submedian.update(choose_random_median(median_recon, next_event[1], count_dict))
        random_submedian.update(choose_random_median(median_recon, next_event[2], count_dict))

    # Make sure our single path median is indeed a subgraph of the median
    assert check_subgraph(median_recon, random_submedian), 'The randomly chosen single-path median is not a subgraph ' \
                                                           'of the full median!'

    return random_submedian


def usage():
    """
    :return: the usage statement associated with running this file
    """

    return 'usage: DTLMedian filename dup_cost transfer_cost loss_cost [-r] [-n]'

def get_median_graph(recon_graph, postorder_gene_tree, postorder_species_tree, gene_tree_root, best_roots):
    # Get a list of the mapping nodes in preorder
    postorder_mapping_node_list = mapping_node_sort(postorder_gene_tree, postorder_species_tree,
                                                    list(recon_graph.keys()))
    # Find the dictionary for frequency scores for the given mapping nodes and graph, and the given gene root
    scores_dict = generate_scores(postorder_mapping_node_list[::-1], recon_graph, gene_tree_root)

    # Now find the median and related info
    median_graph, n_meds, roots_for_median = compute_median(recon_graph, scores_dict[0],
                                                                     postorder_mapping_node_list, best_roots)
    return median_graph, n_meds, roots_for_median

def get_med_counts(median_reconciliation, roots_for_median):
    # Initialize the dictionary that tells us how many medians can be spawned from a particular event node
    med_counts = dict()

    # Now fill it
    for root in roots_for_median:
        count_mprs(root, median_reconciliation, med_counts)
    return med_counts

