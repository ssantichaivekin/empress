# recongraph_tools.py  --  was previously named DP.py
# Ran Libeskind-Hadas, June 2015
# The DP algorithm for reconciling pairs of trees
# Altered and expanded by Carter Slocum and Annalise Schweickart
# Altered and expanded by Andrew Ramirez and Eli Zupke

# A tree is represented as a dictionary of key-value pairs where a key is an
# edge name and the value is a tuple of the form
# (start vertex, end vertex, left child edge name, right child edge name)
# An edge name may be None.  The "dummy" edge leading to the root of the
# parasite tree, denoted e^P in the technical report, must be named "pTop".
# The final DTL reconciliation graph is represented as a dictionary, with
# keys representing mapping nodes, and the associated values corresponding
# to events that can occur at each mapping node in an MPR, as well as other small
# values/information (see docstring of DP for more info on these values).

# Edited by Annalise Schweickart and Carter Slocum, July 2015 to return
# the DTL reconciliation graph that uses frequency scoring, as well as the
# number of reconciliations of the host and parasite trees.

# Edited by Andrew Ramirez and Eli Zupke in late June 2017 to return the number of MPRs for a given data set
# with an improved time efficiency relative to previous methods, usually by a factor of greater than or
# equal to 2. Also, smaller functionality was added in early July, including the ability to calculate the
# mean and median numbers of event nodes per mapping node.

import sys
from typing import Tuple, Iterator

from numpy import mean
from numpy import median as md

from empress.reconcile import reconcile_main_input
from empress.input_reader import _ReconInput

Infinity = float('inf')


def preorder(tree: dict, root_edge_name: Tuple) -> Iterator:
    """
    :param tree <tree> - host or parasite tree (see description above)
    :param root_edge_name <str> - the name associated with the root of the given tree
    :yield: list of edges in the given tree in preorder (high to low edges).
    """

    value = tree[root_edge_name]
    _, _, left_child_edge_name, right_child_edge_name = value

    # Base case
    if left_child_edge_name is None:  # Then right_child_edge_name == None also
        yield root_edge_name
    else:  # Recursive call
        yield root_edge_name
        yield from preorder(tree, left_child_edge_name)
        yield from preorder(tree, right_child_edge_name)


def postorder(tree: dict, root_edge_name: Tuple) -> Iterator:
    """ The parameters of this function are the same as that of preorder above, except it
    yields the edge list in postorder. """

    value = tree[root_edge_name]
    _, _, left_child_edge_name, right_child_edge_name = value

    # Base case
    if left_child_edge_name is None:  # then right_child_edge_name == None also
        yield root_edge_name
    else:  # Recursive call
        yield from postorder(tree, left_child_edge_name)
        yield from postorder(tree, right_child_edge_name)
        yield root_edge_name


def contemporaneous(host_1, host_1_parent, host_2, host_2_parent, distances):
    """
    :param host_1: the first host node
    :param host_1_parent: its parent
    :param host_2: the second host node
    :param host_2_parent: its parent
    :param distances: the distance dictionary for the host tree
    :return: bool of whether the two lineages overlap in time
    """
    start_1 = distances[host_1_parent]
    end_1 = distances[host_1]
    start_2 = distances[host_2_parent]
    end_2 = distances[host_2]
    # They must overlap unless one comes completely before the other
    if end_1 < start_2:
        return False
    if end_2 < start_1:
        return False
    return True


def DP(tree_data: _ReconInput, dup_cost: float, transfer_cost: float, loss_cost: float) -> Tuple[dict, float, int, list]:
    """
    :param tree_data <_ReconInput> object - See newickFormatReader (data comes from getInput)
    :param dup_cost <float> - cost of a duplication event
    :param transfer_cost <float> - cost of a transfer event
    :param loss_cost <float> - cost of a loss event
    :return: the DTL reconciliation graph in the form of a dictionary, the total cost of the best reconciliation,
    the number of maximum parsimony reconciliations, and the roots for a reconciliation graph that could produce a
    Maximum Parsimony Reconciliation.

    Note that the DTL reconciliation graph
    is returned as a dictionary with mapping nodes for keys, and values
    corresponding to lists which include all valid event nodes for a given
    mapping node for the MPR.
    """
    host_dict = tree_data.host_dict
    host_distances = tree_data.host_distances
    parasite_dict = tree_data.parasite_dict
    tip_mapping = tree_data.tip_mapping

    # A, C, O, and best_switch are all defined in tech report. Keys are edges and values are as defined in tech report
    A = {}
    C = {}
    O = {}
    best_switch = {}

    # Keeps track of events and children. Keys are vertex pairs and values are event representations in a tuple
    events_dict = {}

    # Dictionary to keep track of minimum reconciliation cost for each (vp, vh)
    min_cost = {}

    # Keeps track of which vertex mappings 'gave' O its cost for the corresponding edges
    o_best = {}

    # Keeps track of switch locations. Keys are edges, values are edges to send the key edges to for transfers
    best_switch_locations = {}

    # Following logic taken from tech report, we loop over all ep and eh
    for ep in postorder(parasite_dict, "pTop"):

        # Get the parasite tree info in the format
        # (vp top, vp bottom, edge of child 1, edge of child 2)
        _, vp, ep1, ep2 = parasite_dict[ep]

        # If there's no child 1, there's no child 2 and vp is a tip
        if ep1 is None:
            vp_is_a_tip = True
            p_child1 = None
            p_child2 = None
        else:
            vp_is_a_tip = False

            # Save end node names for the parasite's children
            p_child1 = ep1[1]
            p_child2 = ep2[1]

        # Begin looping over host edges
        for eh in postorder(host_dict, "hTop"):

            # Similar format to that of the parasite tree above
            _, vh, eh1, eh2 = host_dict[eh]

            # Initialize entries for this iteration of ep and eh
            events_dict[(vp, vh)] = []
            o_best[(vp, vh)] = []

            # Same logic as for the parasite tree above
            if eh1 is None:
                vh_is_a_tip = True
                h_child1 = None
                h_child2 = None
            else:
                vh_is_a_tip = False

                # Save end node names for the host's children
                h_child1 = eh1[1]
                h_child2 = eh2[1]

            # Compute A(ep, eh)
            if vh_is_a_tip:

                # Check if the tips map to one another
                if vp_is_a_tip and tip_mapping[vp] == vh:

                    # The cost of matching mapped tips (thus, their edges) is 0
                    A[(ep, eh)] = 0

                    # Create a contemporary event
                    A_min = [("C", (None, None), (None, None))]
                else:
                    # Non-matched tips can't reconcile

                    A[(ep, eh)] = Infinity
                    A_min = [Infinity]
            else:

                # Compute Co and create event list to add to events_dict
                if not vp_is_a_tip:

                    # Calculate cospeciation cost assuming the cost is 0
                    co_ep_eh = min(C[(ep1, eh1)] + C[(ep2, eh2)],
                                   C[(ep1, eh2)] + C[(ep2, eh1)])
                    co_min = []  # List to keep track lowest cost speciation
                    if co_ep_eh == C[(ep2, eh1)] + C[(ep1, eh2)]:
                        co_min.append(("S", (p_child2, h_child1),
                                       (p_child1, h_child2)))
                    if co_ep_eh == C[(ep1, eh1)] + C[(ep2, eh2)]:
                        co_min.append(("S", (p_child1, h_child1),
                                       (p_child2, h_child2)))
                else:
                    co_ep_eh = Infinity
                    co_min = [Infinity]

                # Compute L and create event list to add to events_dict
                loss_ep_eh = loss_cost + min(C[(ep, eh1)], C[(ep, eh2)])
                loss_min = []  # List to keep track of lowest cost loss

                # Check which (or maybe both) option produces the minimum
                if loss_ep_eh == loss_cost + C[(ep, eh1)]:
                    loss_min.append(("L", (vp, h_child1), (None, None)))
                if loss_ep_eh == loss_cost + C[(ep, eh2)]:
                    loss_min.append(("L", (vp, h_child2), (None, None)))

                # Determine which event occurs for A[(ep, eh)]
                A[(ep, eh)] = min(co_ep_eh, loss_ep_eh)

                # Record event occurring for A[(ep, eh)] (as A_min) by seeing which
                # event(s) produces least cost
                if co_ep_eh < loss_ep_eh:
                    A_min = co_min
                elif loss_ep_eh < co_ep_eh:
                    A_min = loss_min
                else:
                    A_min = loss_min + co_min

            # Compute C(ep, eh)
            # First, compute D
            if not vp_is_a_tip:

                # Calculate the cost of a duplication event
                dup_ep_eh = dup_cost + C[(ep1, eh)] + C[(ep2, eh)]

                # List to keep track of lowest cost duplication event
                dup_list = ("D", (p_child1, vh), (p_child2, vh))
            else:
                dup_ep_eh = Infinity
                dup_list = [Infinity]

            # Next, Compute T and create event list to add
            # to events_dict using best_switch_locations
            if not vp_is_a_tip:
                switch_list = []  # List to keep track of lowest cost switch

                # Calculate the cost of a switch/transfer event
                switch_ep_eh = transfer_cost + min(C[(ep1, eh)] + best_switch[(ep2, eh)],
                                                   C[(ep2, eh)] + best_switch[(ep1, eh)])

                # If ep2 switching has the lowest cost or equal to the other
                if (C[(ep1, eh)] + best_switch[(ep2, eh)]) <= (C[(ep2, eh)] +
                                                               best_switch[(ep1, eh)]):

                    # Search for the optimal switch location by searching through the best switch
                    # locations for the given child and vh pair
                    for location in best_switch_locations[(p_child2, vh)]:
                        # Proposed new landing site
                        current_loc = location[1]
                        # Append the proposed event to the list of possible switches
                        switch_list.append(("T", (p_child1, vh), (p_child2,
                                                                  current_loc)))
                # If ep1 switching has the lowest cost or equal to the other
                elif (C[(ep2, eh)] + best_switch[(ep1, eh)]) <= (C[(ep1, eh)] +
                                                                 best_switch[(ep2, eh)]):

                    # Search for the optimal switch location by searching through the best switch
                    # locations for the given child and vh pair
                    for location in best_switch_locations[(p_child1, vh)]:
                        # Proposed new landing site
                        current_loc = location[1]

                        # Append the proposed event to the list of possible switches
                        switch_list.append(("T", (p_child2, vh),
                                            (p_child1, current_loc)))

            else:  # vp is a tip
                switch_ep_eh = Infinity
                switch_list = [Infinity]

            # Compute C[(ep, eh)] and add the event or events with that cost
            # to the dictionary events_dict
            C[(ep, eh)] = min(A[(ep, eh)], dup_ep_eh, switch_ep_eh)

            # Add the minimum costs for the current edges to the min_cost dict
            min_cost[(vp, vh)] = C[(ep, eh)]

            # Find which events produce the optimal cost for these edges and add to eventDict
            if C[(ep, eh)] == dup_ep_eh:
                events_dict[(vp, vh)].append(dup_list)
            if C[(ep, eh)] == switch_ep_eh:
                events_dict[(vp, vh)].extend(switch_list)
            if C[(ep, eh)] == A[(ep, eh)]:
                events_dict[(vp, vh)].extend(A_min)

            # Calculate O for eh's children
            # Remove all 'impossible' events from the options
            if min_cost[(vp, vh)] == Infinity:
                del min_cost[(vp, vh)]
                del events_dict[(vp, vh)]

            # Compute o_best[(vp, vh)], the source of O(ep, eh)
            if vh_is_a_tip:
                O[(ep, eh)] = C[(ep, eh)]
                o_best[(vp, vh)] = [(vp, vh)]
            else:

                # Compute O(ep, eh) if vh is not a tip
                O[(ep, eh)] = min(C[(ep, eh)], O[(ep, eh1)], O[(ep, eh2)])

                # o_min helps us easily find which value (between C, O for child 1, and O for child 2) produces
                # O for this edge. Knowing what its indices represent, we search through to see which produce O
                o_min = [ind for ind, elem in enumerate([C[(ep, eh)], O[(ep, eh1)], O[(ep, eh2)]])
                         if elem == O[(ep, eh)]]

                # Corresponds to C
                if 0 in o_min:
                    o_best[(vp, vh)].append((vp, vh))

                # Corresponds to the O table for each child
                if 1 in o_min:
                    o_best[(vp, vh)].extend(o_best[(vp, h_child1)])
                if 2 in o_min:
                    o_best[(vp, vh)].extend(o_best[(vp, h_child2)])

        # Compute best_switch values
        best_switch[(ep, "hTop")] = Infinity
        best_switch_locations[(vp, host_dict["hTop"][1])] = [(None, None)]
        for eh in preorder(host_dict, "hTop"):

            # Redefine the host information for this new loop
            _, vh, eh1, eh2 = host_dict[eh]

            # Is vh a tip?
            if eh1 is None:  # Then eh2 == None too and vh is a tip!
                vh_is_a_tip = True
                h_child1 = None
                h_child2 = None
            else:
                vh_is_a_tip = False
                h_child1 = host_dict[eh][2][1]
                h_child2 = host_dict[eh][3][1]

            # Find best cost for a switch to occur (best_switch)
            # and the location to which the edge switches (best_switch_locations)
            if not vh_is_a_tip:

                # Initialize lists for switch locations
                best_switch_locations[(vp, h_child1)] = []
                best_switch_locations[(vp, h_child2)] = []

                # Compute the switch costs
                best_switch[(ep, eh1)] = min(best_switch[(ep, eh)], O[(ep, eh2)])
                best_switch[(ep, eh2)] = min(best_switch[(ep, eh)], O[(ep, eh1)])

                # Add best switch locations for child 1
                if best_switch[(ep, eh1)] == best_switch[(ep, eh)] and \
                        best_switch_locations[(vp, vh)] != [(None, None)]:
                    best_switch_locations[(vp, h_child1)].extend(
                        best_switch_locations[(vp, vh)])
                if best_switch[(ep, eh1)] == O[(ep, eh2)] and \
                        o_best[(vp, h_child2)] != [(None, None)]:
                    best_switch_locations[(vp, h_child1)].extend(
                        o_best[(vp, h_child2)])

                # Add best switch locations for child 2
                if best_switch[(ep, eh2)] == best_switch[(ep, eh)] and \
                        best_switch_locations[(vp, vh)] != [(None, None)]:
                    best_switch_locations[(vp, h_child2)].extend(
                        best_switch_locations[(vp, vh)])
                if best_switch[(ep, eh2)] == O[(ep, eh1)] and \
                        o_best[(vp, h_child1)] != [(None, None)]:
                    best_switch_locations[(vp, h_child2)].extend(
                        o_best[(vp, h_child1)])

    # Create the list of minimum cost mapping nodes involving root of parasite tree
    tree_min = find_best_roots(parasite_dict, min_cost)

    # Build the reconciliation graph as a dictionary, with keys as mapping nodes and values as event nodes
    dtl_recon_graph = build_dtl_recon_graph(tree_min, events_dict, {})

    mpr_count = count_mprs_wrapper(tree_min, dtl_recon_graph)

    # The total cost of the best reconciliation
    best_cost = min_cost[tree_min[0]]

    # Returns the graph, the optimal cost, the number of MPRs, and the roots that could produce an MPR
    return dtl_recon_graph, best_cost, mpr_count, tree_min


def calculate_mean_med_event_nodes_per_mapping_node(dtl_recon_graph: dict) -> Tuple[float, float, list]:
    """
    :param dtl_recon_graph: a DTL Maximum Parsimony Reconciliation graph, as outputted by DP
    :return: the mean and median number of event nodes per mapping node in the given reconciliation,
    as well as just a list of the data points used in calculating the median
    """

    # Initialize the list that will store the data
    data = list()

    # Search through all keys in the dict/graph - i.e., the mapping nodes
    for map_node in dtl_recon_graph:
        data.append(len(dtl_recon_graph[map_node]))

    mean_event_nodes_per_mapping_node = mean(data)
    median_event_nodes_per_mapping_node = md(data)

    return mean_event_nodes_per_mapping_node, median_event_nodes_per_mapping_node, data


def count_mprs_wrapper(mapping_node_list: list, dtl_recon_graph: dict) -> int:
    """
    :param mapping_node_list: output from findBestRoots, a list of mapping
    nodes for the root of the parasite tree that could produce a MPR.
    See findBestRoots for more info on this input.
    :param dtl_recon_graph: the output from buildDTLReconGraph. See that
    function for more info on this input.
    :return: this function uses the helper function countMPRs to loop over
    all of the minimum cost parasite root mappings and sum their MPR counts
    to find the total number of MPRs for the given DTLReconGraph. This
    number is returned as an integer
    """

    # Initialize the memo
    memo = dict()

    # Initialize the very start count, for the first call of countMPRs
    count = 0

    # Loop over all given minimum cost reconciliation roots
    for mappingNode in mapping_node_list:
        count += count_mprs(mappingNode, dtl_recon_graph, memo)

    return count


def count_mprs(mapping_node: tuple, dtl_recon_graph: dict, memo: dict) -> int:
    """
    :param mapping_node: an individual mapping node that maps a node
    for the parasite tree onto a node of the host tree, in the format
    (p, h), where p is the parasite node and h is the host node
    :param dtl_recon_graph: a DTLReconGraph, output from buildDTLReconGraph
    (see that function for more info on the format of this input)
    :param memo: a dictionary representing the running memo that is passed
    down recursive calls of this function. At first it is just an empty
    dictionary (see above function), but as it gets passed down calls, it collects
    keys of mapping nodes and values of MPR counts. This memo improves runtime
    of the algorithm
    :return: the number of MPRs spawned below the given mapping node in the graph
    """

    # Search the memo dictionary for previously calculated results
    if mapping_node in memo:
        return memo[mapping_node]

    # Base case, occurs if being called on a child produced by a loss or contemporary evet
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
        count += count_mprs(mapping_child1, dtl_recon_graph, memo) * count_mprs(mapping_child2, dtl_recon_graph, memo)

    # Save the result in the memo
    memo[mapping_node] = count

    return count


def find_best_roots(parasite_dict: dict, min_cost_dict: dict) -> list:
    """
    :param parasite_dict: parasite tree in the format described at the
    top of this file
    :param min_cost_dict: a dictionary - keys representing mappings of
    parasite vertices onto host vertices (p, h) and values representing
    the minimum cost for a reconciliation based on that mapping. In DP,
    this dictionary was called minCost
    :return: returns a list of all of the mapping nodes involving the
    parasite root that can produce a MPR
    """
    tree_tops = []
    for key in min_cost_dict:
        if key[0] == parasite_dict['pTop'][1]:
            tree_tops.append(key)
    tree_min = []
    min_score = min([min_cost_dict[root] for root in tree_tops])
    for pair in tree_tops:
        if min_cost_dict[pair] == min_score:
            tree_min.append(pair)
    return tree_min


def build_dtl_recon_graph(best_roots: list, event_dict: dict, unique_dict: dict) -> dict:
    """
    :param best_roots: a list of minimum cost reconciliation roots - see findBestRoots
    for more info on the format of this input
    :param event_dict: a dictionary representing events and the corresponding children
    for each node - see eventDict in DP for more info on the format of this input
    :param unique_dict: a dictionary of unique vertex mappings, which initially
    starts empty and gets built up using eventDict and tupleList using recursion
    :return: the modified uniqueDict for this particular call of the function which,
    after all recursive calls are done, will be the final DTL reconciliation graph
    """

    for vertexPair in best_roots:
        if vertexPair not in unique_dict:
            unique_dict[vertexPair] = event_dict[vertexPair]
            for event in event_dict[vertexPair]:
                for location in event:
                    if type(location) is tuple and location != (None, None):
                        build_dtl_recon_graph([location], event_dict, unique_dict)
    return unique_dict


def reconcile(tree_data: _ReconInput, dup_cost: float, transfer_cost: float, loss_cost: float) -> Tuple[
    dict, dict, dict, int, list]:
    """
    :param tree_data <_ReconInput>: Output of newickFormatReader.getInput()
    :param dup_cost: the cost associated with a duplication event
    :param transfer_cost: the cost associated with a transfer event
    :param loss_cost: the cost associated with a loss event
    :return: the host tree used, the parasite tree used, the DTLReconGraph, the number of MPRs (as an int), and
    a list of the roots that could be used to produce an MPR for the given trees. See preceding functions
    for details on the format of the host and parasite trees as well as the DTLReconGraph
    """
    # Note: I have made modifications to the return statement to make diameter.py possible without re-reconciling.
    host = tree_data.host_dict
    paras = tree_data.parasite_dict
    graph, best_cost, num_recon, best_roots = DP(tree_data, dup_cost, transfer_cost, loss_cost)
    return host, paras, graph, num_recon, best_roots


# The remaining code handles the case of the user wanting to run reconcile from the command line

def usage():
    """
    :return: the usage statement associated with reconcile, and thus the main execution block
    """
    return ('usage: DTLReconGraph filename D_cost T_cost L_cost\n\t  filename: the name of the file that contains'
            ' the data \n\t  D_cost, T_cost, L_cost: costs for duplication, transfer, and loss events,'
            ' respectively')


# This should be called in empress_cli.py when the user wants to run reconcile
def reconcile_inter(tree_data: _ReconInput):
    """ 
    :param tree_data <_ReconInput>: Output of newickFormatReader.getInput()
    """
    duplication, transfer, loss = reconcile_main_input.get_inputs()
    result = reconcile(tree_data, duplication, transfer, loss)
    for i in range(len(result)):
        print((str(result[i]) + '\n'))


# This should be called in empress_cli.py when the user already supplied the DTL values
def reconcile_noninter(tree_data: _ReconInput, duplication: float, transfer: float, loss: float):
    """ 
    :param tree_data <_ReconInput> : Output of newickFormatReader.getInput()
    """
    result = reconcile(tree_data, duplication, transfer, loss)
    for i in range(len(result)):
        print((str(result[i]) + '\n'))

