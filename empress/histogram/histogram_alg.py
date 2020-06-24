# Modification on the original diameter algorithm to support getting the histogram of the whole graph.

from itertools import product

from empress.histogram.Histogram import Histogram
from empress.histogram.histogram_brute_force import BFVerifier

# def reformat_tree(tree, root):
#     """A recursive function that changes the format of a (species or gene) tree from edge to vertex, as described
#     above. It returns the tree (in postorder), the root of the tree, and the number of nodes in the tree. The base
#     case of this function is when there are no children for a given root.
#     :param tree:        A tree in edge format
#     :param root:        The root of that tree
#     :return:            0: The new vertex based tree,
#                         1: The root of that tree, and
#                         2: The number of nodes in that tree. """

#     # This line catches the "xTop" handle and replaces
#     new_root = root[1] if isinstance(root, tuple) else tree[root][1]

#     child1 = tree[root][2][1] if tree[root][2] is not None else None  # These lines handle the leaves, where
#     child2 = tree[root][3][1] if tree[root][3] is not None else None  # there is None in the place of a tuple

#     # This is the tree that we will be returning. We will add the subtrees of our children first, then add this node.
#     new_vertex_tree = OrderedDict()  # This has to be an OrderedDict, otherwise we can't guarantee it's in postorder

#     # This is the number of nodes in the subtree rooted at each of our children
#     # We actually don't need to calculate this here at all, since the count will just be the length of new_vertex_tree
#     child1_count = 0
#     child2_count = 0

#     if child1 is not None:  # If this node has children, then we need to add their children's subtrees to the dict
#         child1_tree, _, child1_count = reformat_tree(tree, tree[root][2])
#         new_vertex_tree.update(child1_tree)
#     if child2 is not None:
#         child2_tree, _, child2_count = reformat_tree(tree, tree[root][3])
#         new_vertex_tree.update(child2_tree)
#     new_vertex_tree.update({new_root: (child1, child2)})  # We add this node last, to ensure postorderness.

#     return new_vertex_tree, new_root, (child1_count + child2_count + 1)


def intersect_cost(event):
    """
    The cost added if both reconciliations being looked at share a particular event
    :param event <tuple>   - the event being shared
    :return <int>          - the cost
    """
    return 0


def cost(event, zero_loss):
    """
    The cost added if exactly one of the reconciliations being looked at share a particular event
    :param event <tuple>      - the event being shared
    :param zero_loss <bool>   - whether loss events should have cost = 0
    :return <int>             - the cost
    """

    if zero_loss and event[0] == 'L':
        return 0
    return 1


def calculate_ancestral_table(species_tree):
    """
    :param species_tree <dict> - a species tree, in vertex format and postorder,
    represented as an OrderedDict (output from reformat_tree)
    :return - A nested dictionary. The first dictionary has vertices in the
    tree as keys and the values are dictionaries. These dictionaries have
    as keys vertices of the tree (again) and values which are strings,
    representing how the first index relates to the second (see below
    for info on what certain strings mean). It creates these dictionaries
    by traversing the tree.
    """

    # Initialize the ancestral table which we will be returning
    ancestral_table = dict()

    # Helper dict to help us determine if two nodes are ancestrally related
    descendants = dict()

    # Get all of the vertices in the tree
    vertices = [vertex for vertex in species_tree]

    # Initialize all entries to incomparable to make following calculations easier
    for A, B in list(product(vertices, vertices)):  # Cartesian product of all of the vertices

        # Check if we need to make a dictionary for the first vertex
        if A not in ancestral_table:
            ancestral_table[A] = dict()

        # Set all identical pairs to equal while we're in this loop - check for equality here
        if A == B:
            ancestral_table[A][B] = 'eq'

        else:

            # Set all other pairs to incomparable
            ancestral_table[A][B] = 'in'

    # Now loop over all vertex pairs checking for ancestral connections
    for v in vertices:

        # Save the vertices that represent the children into variables
        child1 = species_tree[v][0]
        child2 = species_tree[v][1]

        # Check for leaf nodes
        if child1 is None and child2 is None:
            descendants[v] = []  # Empty list --> no descendants

        else:

            # The descendants of a node are the direct children and those children's children, and so on
            descendants[v] = descendants[child1] + descendants[child2] + [child1] + [child2]

            # Assign relationship between a node and its descendants, and vice versa
            for descendant in descendants[v]:
                ancestral_table[v][descendant] = 'an'
                ancestral_table[descendant][v] = 'des'

    return ancestral_table


def is_leaf(u, vertex_tree):
    """
    :param u <str>              - the node to test
    :param vertex_tree <dict>   - the vertex tree that contains the node
    :return <bool>              - a boolean value representing whether the given node is a leaf of the given tree
    """
    return vertex_tree[u] == (None, None)


def is_exit_event(event):
    """
    :param event <tuple>   - an event to check
    :return <bool>         - whether said event is an exit event
    """
    return event[0] not in ('C', 'L')


# Modified : use Histogram instead of value
def calculate_hist_both_exit(zero_loss, enter_table, u, gene_tree, uA, dtl_recon_graph_a, uB, dtl_recon_graph_b):
    """
    This function computes the histogram of a 'double exit', where both mapping nodes exit immediately
    :param zero_loss <bool>           - a boolean value representing whether loss events should count for distance
    :param enter_table <dict>         - the enter table, which we use here
    :param u <str>                    - the gene node whose group we're in
    :param gene_tree <dict>           - the gene tree in vertex format
    :param uA <str>                   - the 'a' mapping node
    :param dtl_recon_graph_a <dict>   - the 'a' DTL reconciliation graph
    :param uB <str>                   - the 'b' mapping node
    :param dtl_recon_graph_b <dict>   - the 'b' DTL reconciliation graph
    :return <Histogram>               - the Histogram object of both mapping nodes exiting
    """
    hist_both_exit = Histogram(None)

    # Test to see if u is a leaf
    if is_leaf(u, gene_tree):
        if uA == uB and ('C', (None, None), (None, None)) in dtl_recon_graph_a[uA]:
            hist_both_exit = Histogram(0)
    else:
        uA_exit_events = [event for event in dtl_recon_graph_a[uA] if isinstance(event, tuple) and is_exit_event(event)]
        uB_exit_events = [event for event in dtl_recon_graph_b[uB] if isinstance(event, tuple) and is_exit_event(event)]
        for e_a in uA_exit_events:
            child1 = e_a[1][0]
            child2 = e_a[2][0]
            # A1 and A2 are the species nodes of the two mapping nodes of e_a
            A1 = e_a[1][1]
            A2 = e_a[2][1]
            for e_b in uB_exit_events:
                # If the events are shared, only need the first ordering (the second will overcount)
                if uA == uB and e_b > e_a:
                    continue
                # B1 and B2 are the species nodes of the two mapping nodes of e_b
                # We need to account for the case that the children of u are in opposite order between the two events
                if child1 == e_b[1][0]:
                    B1 = e_b[1][1]
                    B2 = e_b[2][1]
                else:
                    B1 = e_b[2][1]
                    B2 = e_b[1][1]
                # Now, we need to turn the species nodes into the correct mapping nodes
                u1A = (child1, A1)
                u1B = (child1, B1)
                u2A = (child2, A2)
                u2B = (child2, B2)
                # If the histogram of this iteration's double exit is better than the old one, then the old one will
                # supersede this one
                left_entry = enter_table[child1][u1A][u1B]
                right_entry = enter_table[child2][u2A][u2B]
                # Techically n_choices encodes the number of choices beyond the first.
                n_choices = 0
                # 1 choice means either a choice about both children but not the event, or about the event and only one child.
                if (uA == uB and e_a == e_b) or (u1A == u1B or u2A == u2B):
                    n_choices = 1
                # 2 choices means a choice about both children AND the event.
                if u1A == u1B and u2A == u2B and e_a != e_b:
                    n_choices = 2
                # Do the convolution between left and right, then shift based on the difference of the events
                this_hist = left_entry.product_combine(right_entry, n_choices)
                if e_a != e_b:
                    this_hist = this_hist << (cost(e_a, zero_loss) + cost(e_b, zero_loss))
                else:
                    this_hist = this_hist << intersect_cost(0)
                # Final histogram is the sum over all event pairs
                hist_both_exit = hist_both_exit + this_hist
    return hist_both_exit


def calculate_incomparable_enter_hist(zero_loss, enter_table, u, uA, uA_loss_events, uB, uB_loss_events,
                                       hist_both_exit):
    """
    Returns the enter table entry for [uA][uB] with the assumption that A is on a different part of the species
    tree from B
    :param zero_loss <bool>             - whether losses should not count
    :param enter_table <dict>           - the DP table we are computing part of
    :param u <str>                      - the gene node whose group we are in
    :param uA <str>                     - the first mapping node to compare
    :param uA_loss_events <list>        - a list of the loss events on that mapping node
    :param uB <str>                     - the second mapping node to compare
    :param uB_loss_events <list>        - a list of the loss events on that mapping node
    :param hist_both_exit <Histogram>   - the histogram of the double-exit that was previously calculated for uA and uB
    :return <Histogram>                 - the enter table entry for [uA][uB]
    """
    hists = [hist_both_exit]
    lost_hists = []

    # We add up all of the hists for both uA's and uB's loss events.
    for event in uA_loss_events:
        a_child = event[1][1]
        hists.append(enter_table[u][(u, a_child)][uB] << cost(event, zero_loss))
    for event in uB_loss_events:
        b_child = event[1][1]
        hists.append(enter_table[u][uA][(u, b_child)] << cost(event, zero_loss))
    # The previous histograms will overcount the possibility of taking a loss in both children.
    # Since enter[u][(u, a_child)][(u, b_child)] is counted by both
    # enter[u][uA][(u, b_child)] and enter[u][(u, a_child)][uB]
    # Here we compute enter[u][(u, a_child)][(u, b_child)] in order to subtract it off
    for loss_event_A, loss_event_B in product(uA_loss_events, uB_loss_events):
        a_child = loss_event_A[1][1]
        b_child = loss_event_B[1][1]
        loss_cost = cost(loss_event_A, zero_loss) + cost(loss_event_B, zero_loss)
        lost_hists.append(enter_table[u][(u, a_child)][(u, b_child)] << loss_cost)
    return Histogram.sum(hists) - Histogram.sum(lost_hists)


def calculate_equal_enter_hist(zero_loss, enter_table, u, uA, uA_loss_events, uB, uB_loss_events,
                                hist_both_exit, exit_table_a, exit_table_b):
    """
    Returns the enter table entry for [uA][uB] with the assumption that uA equals uB (but they might have different
    loss events leading from them!)
    :param zero_loss <bool>             - whether losses should not count
    :param enter_table <dict>           - the DP table we are computing part of
    :param u <str>                      - the gene node whose group we are in
    :param uA <str>                     - the first mapping node to compare
    :param uA_loss_events <list>        - a list of the loss events on that mapping node
    :param uB <str>                     - the second mapping node to compare
    :param uB_loss_events <list>        - a list of the loss events on that mapping node
    :param hist_both_exit <Histogram>   - the histogram of the double-exit that was previously calculated for uA and uB
    :param exit_table_a <dict>          - the a exit table, which contains information about the single exit events for
                                          the mapping nodes' children
    :param exit_table_b <dict>          - the b exit table, which contains information about the single exit events for
                                          the mapping nodes' children
    :return <Histogram>                 - the enter table entry for [uA][uB]  
    """
    # If uA does not equal uB, then something's gone horribly wrong.
    assert uA == uB, "calculate_equal_enter_hist called on values of uA and uB that are not equal"

    # Build up a list of the possible histograms of this pair of mapping nodes, so that we can find the maximum later.
    hists = [hist_both_exit]

    for a_event in uA_loss_events:
        a_child = a_event[1][1]
        for b_event in uB_loss_events:
            b_child = b_event[1][1]
            # Only the first ordering matters ((a, b) and (b, a) will both appear, but we should not treat them as distinct)
            if a_child < b_child:
                hists.append(enter_table[u][(u, a_child)][(u, b_child)] << 2)
            # If they are the same, then the same loss was used so there is no shift.
            elif a_child == b_child:
                hists.append(enter_table[u][(u, a_child)][(u, b_child)])

    # Only need to iterate through uA_loss_events since if they are equal then uB_loss_events = uA_loss_events.
    for event in uA_loss_events:
        a_child = event[1][1]
        hists.append(exit_table_b[u][uB][(u, a_child)] << cost(event, zero_loss))
    return Histogram.sum(hists)


def calculate_ancestral_enter_hist(zero_loss, is_swapped, enter_table, u, uA, uA_loss_events, uB, uB_loss_events,
                                    hist_both_exit, exit_table_a, exit_table_b):
    """
    Returns the enter table entry for [uA][uB] with the assumption that A is an ancestor of B (if is_swapped is
    false) or that B is an ancestor of A (if is_swapped is true). In both cases, it will compute the single exit
    table entry of the pair (with the ancestor going first, of course).
    :param zero_loss <bool>             - whether losses should not count
    :param is_swapped <bool>            - whether B is an ancestor of A (instead of the assumed A is an ancestor of B)
    :param enter_table <dict>           - the DP table we are computing part of
    :param u <str>                      - the gene node whose group we are in
    :param uA <str>                     - the first mapping node to compare
    :param uA_loss_events <list>        - a list of the loss events on that mapping node
    :param uB <str>                     - the second mapping node to compare
    :param uB_loss_events <list>        - a list of the loss events on that mapping node
    :param hist_both_exit <Histogram>   - the histogram of the double-exit that was previously calculated for uA and uB
    :param exit_table_a <dict>          - the a exit table, which contains information about the single exit events for
                                          the mapping nodes' children
    :param exit_table_b <dict>          - the b exit table, which contains information about the single exit events for
                                          the mapping nodes' children
    :return <Histogram>                 - the enter table entry for [uA][uB]
    """

    # In both cases, we will need to tally up the histograms of any loss events on the descendant. Hists will hold those
    # values, and the histograms of a double exit.
    hists = [hist_both_exit]

    # We check to see if which mapping node is the ancestor is swapped from uA an uB to uB an uA. We can't just
    # swap the arguments in that case unfortunately, because enter_table requires the two arguments be entered in the
    # correct direction.
    if not is_swapped:
        # uA is an ancestor to uB
        # Tally up the histograms of the descendant's (uB's) loss events
        for event in uB_loss_events:
            b_child = event[1][1]
            # Add the histogram of taking this loss (the exit_table's entry for the mapping node that this loss
            # leads to, plus the cost of a loss)
            hists += [exit_table_a[u][uA][(u, b_child)] << cost(event, zero_loss)]

        # Initialize the ancestor's (uA) entry in exit_table, if need be.
        if uA not in exit_table_a[u]:
            exit_table_a[u][uA] = {}
        exit_table_a[u][uA][uB] = Histogram.sum(hists)

        enter_hists = [exit_table_a[u][uA][uB]]
        for event in uA_loss_events:
            a_child = event[1][1]
            # Double the nonzero entries if one node is the direct child of the other through the loss event.
            # This occurs because order matters when considering a pair of sub-reconciliations rooted at the child.
            # Either of those sub-reconciliations may be given the loss event and used as the sub-reconciliation
            # rooted at the parent.
            if (u, a_child) == uB:
                event_enter = enter_table[u][(u, a_child)][uB].double_nonzero_entry()
            else:
                event_enter = enter_table[u][(u, a_child)][uB]
            enter_hists += [event_enter << cost(event, zero_loss)]
        return Histogram.sum(enter_hists)
    else:
        # uB is an ancestor to uA
        # Tally up the histograms of the descendant's (uA's) loss events
        for event in uA_loss_events:
            a_child = event[1][1]
            # Add the histograms of taking this loss (the exit_table's entry for the mapping node that this loss
            # leads to, plus the cost of a loss)
            hists += [exit_table_b[u][uB][(u, a_child)] << cost(event, zero_loss)]

        # Initialize the ancestor's (uB) entry in exit_table, if need be.
        if uB not in exit_table_b[u]:
            exit_table_b[u][uB] = {}
        exit_table_b[u][uB][uA] = Histogram.sum(hists)
        
        enter_hists = [exit_table_b[u][uB][uA]]
        for event in uB_loss_events:
            b_child = event[1][1]
            if uA == (u, b_child):
                event_enter = enter_table[u][uA][(u, b_child)].double_nonzero_entry()
            else:
                event_enter = enter_table[u][uA][(u, b_child)]
            enter_hists += [event_enter << cost(event, zero_loss)]
        return Histogram.sum(enter_hists)


def make_group_dict(gene_tree, dtl_recon_graph, postorder_species_nodes):
    """
    Returns a group dictionary of a particular dtl_recon_graph, that contains the mapping nodes in each gene node
    :param gene_tree <dict>                 - the vertex-based gene tree
    :param dtl_recon_graph <dict>           - the dtl reconciliation graph we are using
    :param postorder_species_nodes <list>   - a list of the species nodes in post order
    :return <dict>                          - a dict keyed by gene node, where the values are the lists of mapping nodes for that
                                              gene node
    """
    postorder_group = {}
    for u in gene_tree:
        # First we make the dictionary only contain nodes that have this gene node
        postorder_group[u] = [mapping for mapping in dtl_recon_graph if mapping[0] == u]
        # Then we sort the dictionary into postorder, using the species node's index in the postorder species list as a
        # guide.
        postorder_group[u] = sorted(postorder_group[u], key=lambda mapping: postorder_species_nodes.index(mapping[1]))
    return postorder_group


def diameter_algorithm(species_tree, gene_tree, gene_tree_root, dtl_recon_graph_a, dtl_recon_graph_b, debug, zero_loss, verify=False):
    """
    This function finds the diameter of a reconciliation graph, as measured by the largest symmetric set difference
     of any two reconciliation trees inside of a reconciliation graph. While you can get standard diameter behaviour
     by making dtl_recon_graph_a equal dtl_recon_graph_b, arbitrary restrictions may be placed on which nodes are
     selected by choosing different graphs, for example by limiting one of the graphs to a single reconciliation tree
     to find that tree's distance to the furthest reconciliation.
    :param species_tree <dict>        - the species tree (in vertex form)
    :param gene_tree <dict>           - the gene tree (in vertex form)
    :param gene_tree_root <str>       - the root of the gene tree
    :param dtl_recon_graph_a <dict>   - one of the two DTL reconcilation graphs to make the diameter from
    :param dtl_recon_graph_b <dict>   - the other reconciliation graph. Both must share the same species and gene trees.
    :param debug <bool>               - whether or not to print out pretty tables
    :param zero_loss <bool>           - whether losses should count at all
    :param verify <bool>              - whether to verify the calculations using brute force
    :return <Histogram>               - the diameter of the reconciliation
    """

    # Use debugging
    #assert(dtl_recon_graph_a == dtl_recon_graph_b)
    if verify:
        verfier = BFVerifier(dtl_recon_graph_a)

    postorder_gene_nodes = list(gene_tree.keys())
    postorder_species_nodes = list(species_tree.keys())
    postorder_group_a = make_group_dict(gene_tree, dtl_recon_graph_a, postorder_species_nodes)
    postorder_group_b = make_group_dict(gene_tree, dtl_recon_graph_b, postorder_species_nodes)

    ancestral_table = calculate_ancestral_table(species_tree)

    if debug:
        print_table_nicely(ancestral_table, ", ", "Ancestral", "literal")

    exit_table_a = {}
    exit_table_b = {}

    enter_table = {}

    for u in postorder_gene_nodes:
        enter_table[u] = {}
        exit_table_a[u] = {}
        exit_table_b[u] = {}

        # Loop over every pair of mapping nodes in group(u)
        for uA in postorder_group_a[u]:
            enter_table[u][uA] = {}
            for uB in postorder_group_b[u]:

                hist_both_exit = calculate_hist_both_exit(zero_loss, enter_table, u, gene_tree, uA, dtl_recon_graph_a,
                                                            uB, dtl_recon_graph_b)

                # Look up ancestry string in the precomputed table (indexed by the species nodes of the mapping nodes)
                ancestry = ancestral_table[uA[1]][uB[1]] 

                uA_loss_events = [event for event in dtl_recon_graph_a[uA] if isinstance(event, tuple) and event[0] == 'L']
                uB_loss_events = [event for event in dtl_recon_graph_b[uB] if isinstance(event, tuple) and event[0] == 'L']

                # To compute the proper single exit entry, we must know how the two nodes relate to each other. See the
                # header for a more complete explanation on this data structure.
                if ancestry == 'in':
                    hist = calculate_incomparable_enter_hist(zero_loss, enter_table, u, uA, uA_loss_events, uB,
                                                               uB_loss_events, hist_both_exit)
                elif ancestry == 'eq':
                    hist = calculate_equal_enter_hist(zero_loss, enter_table, u, uA, uA_loss_events, uB,
                                                        uB_loss_events, hist_both_exit, exit_table_a, exit_table_b)
                # The only difference between the 'des' and 'an' cases are whether the nodes should be swapped
                elif ancestry == 'des':
                    hist = calculate_ancestral_enter_hist(zero_loss, True, enter_table, u, uA, uA_loss_events, uB,
                                                            uB_loss_events, hist_both_exit, exit_table_a, exit_table_b)
                elif ancestry == 'an':
                    hist = calculate_ancestral_enter_hist(zero_loss, False, enter_table, u, uA, uA_loss_events, uB,
                                                            uB_loss_events, hist_both_exit, exit_table_a, exit_table_b)
                else:
                    raise ValueError("Invalid ancestry type '{0}', check calculate_ancestral_table().".format(ancestry))
                if verify:
                    verfier.verify_enter(uA, uB, hist)
                enter_table[u][uA][uB] = hist
                if debug:
                    print("{0} -{1}-> {2}, Double-equal\t{3}\Hist:{4}".format(uA, ancestry, uB, hist_both_exit,
                                                                                hist))

        if debug:
            print_table_nicely(enter_table[u], ", ", "EnterTable({0})".format(u))

    if debug:
        print("Exit Table A: {0}".format(exit_table_a))
        print("")
        print("Exit Table B: {0}".format(exit_table_b))
    # Now, the diameter of this reconciliation will be the maximum entry on the enter table.
    result = Histogram(None)
    for uA in enter_table[gene_tree_root]:
        for uB in enter_table[gene_tree_root][uA]:
            if uB > uA :
                continue
            entry = enter_table[gene_tree_root][uA][uB]
            result = result + entry
    return result


def event_to_string(event):
    return "{0}:{1}{2} {3}{4}".format(str(event[0]), str(event[1][0]), str(event[1][1]),
                                      str(event[2][0]), str(event[2][1]))


def print_table_nicely(table, deliminator, name="\t", dtype="map"):
    """
    Takes a table (a 2D dict keyed with tuples) and prints a nicely formatted table. Used for debugging and wall art.
    :param table <dict>        - the table we wish to print nicely. It is assumed that both the keys and values will fit within
                                 7 characters (room for one tab space), and that the table is filled completely.
    :param deliminator <str>   - what string to put in between the elements of the tuples
    :param name <str>          - what this table should be named (upper left)
    :param dtype <str>         - a string corresponding to the type of data. Valid values are 'event', 'literal', and 'map'.
    :return <None>             - nothing, but prints to the screen a lot
    """

    print("")
    if len(table) > 30:  # Don't spend too long displaying tables.
        print("Table '{1}' is {0}x{0}, which is bigger than the max size of 30.".format(len(table), name))
        return

    line = "\033[4m{0}\033[1m".format(name)  # Underline top row, bold column headers
    for column in table[list(table.keys())[0]]:
        if dtype == "event":
            line += "\t{0}".format(event_to_string(column))
        elif dtype == "literal":
            line += "\t{0}".format(column)
        else:
            line += "\t{0}{1}{2}".format(str(column[0]), deliminator, str(column[1]))
    print(line + "\033[0m")

    row_num = 0  # Used to alternate row colors

    for row in table:
        row_num += 1
        line_color = "\033[37m" if row_num % 2 == 0 else "\033[0m"

        line = line_color + "\t\033[4m\033[1m"  # Add bolding and underline to row headers
        if dtype == "event":
            line += "{0}".format(event_to_string(row))
        elif dtype == "literal":
            line += "{0}".format(row)
        else:
            line += "{0}{1}{2}".format(str(row[0]), deliminator, str(row[1]))
        line += "\033[0m\t" + line_color  # Remove bolding for entries, then return to line color
        for column in table[row]:
            if row == column:
                line += "\033[33m"  # Highlight diagonals
            line += str(table[row][column]) + "\t"
            if row == column:
                line += line_color
        print(line)
    print("\033[0m")  # Return to default color
