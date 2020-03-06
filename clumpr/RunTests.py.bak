# RunTests.py
# Written July 2017 by Eli Zupke and Andrew Ramirez
# This file contains the ability to actually calculate the diameter or median diameter of single or multiple files.
# It contains the best CLI and is the only file that should be really used on the command line.

import Diameter
import csv
import time
import DTLReconGraph
import DTLMedian
import os
import numpy as np

# Used for command line arguments:
import sys
import re
import traceback
import optparse

import ReconGraphFileInterchange


def write_to_csv(csv_file, costs, filename, mpr_count, gene_node_count, species_node_count,
                 DTLReconGraph_time_taken, properties):
    """Takes a large amount of information about a diameter solution and appends it as one row to the provided csv file.
    :param csv_file:                    The csv file to write to
    :param costs:                       A string representing the costs used to calculate the DTL recon graph
    :param filename:                    The name of the file that was reconciled
    :param mpr_count:                   The number of MPRS found
    :param gene_node_count:             The total number of nodes in the gene tree
    :param species_node_count:          The total number of nodes in the species tree
    :param DTLReconGraph_time_taken:    The amount of time that DTLReconGraph took to run
    :param properties:                  A list of tuples, where each tuple represents one property of the graph that was
                                         computed (for example, diameter), and has the following format:
                                         0: Name of the property
                                         1: Property computed
                                         2 (optional, and creates complimentary header): Time taken
    """
    file_exists = os.path.isfile(csv_file)
    # If they only supply one argument, let's correct it for them.
    if isinstance(properties, tuple):
        properties = [properties]

    with open(csv_file, 'a') as output_file:
        writer = csv.writer(output_file)

        # Write the headers if we need to.
        if not file_exists:
            header = ["File Name", "Date Completed", "Costs", "MPR Count", "Gene Node Count", "Species Node Count",
                      "DTLReconGraph Computation Time"]
            for property in properties:
                header += [property[0]]

                # This property may associated timing data, which should be included
                if len(property) == 3:
                    header += ["{0} Computation Time".format(property[0])]
            writer.writerow(header)
        numbers = [filename, time.strftime("%c"), costs, mpr_count, gene_node_count, species_node_count,
                   DTLReconGraph_time_taken]
        for property in properties:
            numbers += [property[1]]

            # This property may associated timing data, which should be included
            if len(property) == 3:
                numbers += [property[2]]
        writer.writerow(numbers)


def find_median_and_count(gene_tree, gene_tree_root, species_tree, dtl_recon_graph, best_roots):
    """
    Finds the entire median reconciliation graph, and counts the number of reconciliations.
    :param gene_tree:       The gene tree, in vertex format
    :param gene_tree_root:  The vertex root of the gene tree
    :param species_tree:    The species tree, in vertex format
    :param dtl_recon_graph: The entire DTL mpr reconciliation graph
    :param best_roots:      best_roots, a list of mapping nodes that can be the root of MPRs (as returned from
                             DTLReconGraph.reconcile)
    :return:                An entry in the results list for the count AND the median reconciliation
    """
    start_time = time.clock()
    preorder_mapping_node_list = DTLMedian.mapping_node_sort(gene_tree, species_tree, dtl_recon_graph.keys())

    # Find the dictionary for frequency scores for the given mapping nodes and graph, as well as the given gene root
    scoresDict = DTLMedian.generate_scores(list(reversed(preorder_mapping_node_list)), dtl_recon_graph, gene_tree_root)

    median_reconciliation, n_meds, _ = DTLMedian.compute_median(dtl_recon_graph, scoresDict[0],
                                                                preorder_mapping_node_list,
                                                                best_roots)
    median_time_taken = time.clock() - start_time
    return [("Median Count", n_meds, median_time_taken)], median_reconciliation


def find_worst_median_distance(species_tree, gene_tree, gene_tree_root, dtl_recon_graph, median_reconciliation, debug):
    """
    Finds the furthest distance from a median MPR to any other MPR.
    :param gene_tree:               The gene tree, in vertex format
    :param gene_tree_root:          The vertex root of the gene tree
    :param species_tree:            The species tree, in vertex format
    :param dtl_recon_graph:         The entire DTL mpr reconciliation graph
    :param median_reconciliation:   A DTL reconciliation graph containing every possible median
    :param debug:                   Whether or not to print debug tables
    :return:                        An entry to be added to the results list containing the Worst Median Distance
    """
    start_time = time.clock()
    worst_median_distance = Diameter.diameter_algorithm(species_tree, gene_tree, gene_tree_root,
                                                        median_reconciliation, dtl_recon_graph, debug, False)
    worst_median_distance_time_taken = time.clock() - start_time
    return [("Worst Median Distance", worst_median_distance, worst_median_distance_time_taken)]


def find_median_diameter(species_tree, gene_tree, gene_tree_root, median_reconciliation, debug):
    """
    Finds the diameter of the medioid space
    :param gene_tree:               The gene tree, in vertex format
    :param gene_tree_root:          The vertex root of the gene tree
    :param species_tree:            The species tree, in vertex format
    :param median_reconciliation:   The entire DTL median reconciliation graph
    :param median_reconciliation:   A DTL reconciliation graph containing every possible median
    :param debug:                   Whether or not to print debug tables
    :return:                        An entry to be added to the results list containing the Worst Median Distance
    """
    start_time = time.clock()
    median_diameter = Diameter.diameter_algorithm(species_tree, gene_tree, gene_tree_root,
                                                  median_reconciliation, median_reconciliation, debug, False)
    worst_median_diameter_time_taken = time.clock() - start_time
    return [("Median Diameter", median_diameter, worst_median_diameter_time_taken)]


def find_median_cluster(filename, log, costs, gene_tree, gene_tree_root, species_tree, dtl_recon_graph, best_roots,
                        cluster_size):
    """
    Finds the maximum distance from a randomly selected median reconciliation a set number of times, and records
     each diameter in a special log file. The average and standard deviation of the found distances (among other things)
     of the entire cluster are returned, ready to be added to the results dictionary.
    :param filename:            The name of the file that we're reconciling (so that we can name the special log file
                                 the same).
    :param log:                 The name of the regular log file (so that we can name the folder we're putting the
                                special log files in the same)
    :param costs:               A string, representing the DTL costs.
    :param gene_tree:           The gene tree, in vertex format
    :param gene_tree_root:      The vertex root of the gene tree
    :param species_tree:        The species tree, in vertex format
    :param dtl_recon_graph:     The entire DTL mpr reconciliation graph
    :param best_roots:          best_roots, a list of mapping nodes that can be the root of MPRs (as returned from
                                 DTLReconGraph.reconcile)
    :param cluster_size:        The number of medians we should compute per cluster
    :return:                    An entry (to be added to the results list) containing information about the cluster.
    """
    start_time = time.clock()

    _, file_log_name = os.path.split(filename)
    file_log_name, _ = os.path.splitext(file_log_name)
    file_log_path = os.path.splitext(log)[0] + "/" + file_log_name + ".csv"

    preorder_mapping_node_list = DTLMedian.mapping_node_sort(gene_tree, species_tree, dtl_recon_graph.keys())
    scoresDict = DTLMedian.generate_scores(list(reversed(preorder_mapping_node_list)), dtl_recon_graph,
                                           gene_tree_root)
    median_recon, n_meds, med_roots = DTLMedian.compute_median(dtl_recon_graph, scoresDict[0],
                                                               preorder_mapping_node_list,
                                                               best_roots)
    med_counts = dict()
    for root in med_roots:
        DTLMedian.count_mprs(root, median_recon, med_counts)

    # Save previously seen median reconciliations
    old_medians = dict()

    random_median_diameters = []
    # Every time this loop repeats, we calculate another random median and find its diameter

    for i in range(0, cluster_size):
        # TODO: Move inner loop to own function
        start_sub_time = time.clock()

        random_median = DTLMedian.choose_random_median_wrapper(median_recon, med_roots, med_counts)
        median_hash = hash(str(random_median))

        end_random_time = time.clock() - start_sub_time
        start_sub_time = time.clock()

        random_median_diameter = None  # Initialize this entry for the dict

        if median_hash in old_medians:
            # We've already computed the diameter for this, so we can save some time by re-using the old values
            random_median_diameter = old_medians[median_hash]
            end_sub_time = 0
        else:
            random_median_diameter = Diameter.diameter_algorithm(species_tree, gene_tree, gene_tree_root,
                                                                 random_median, dtl_recon_graph, False, False)
            old_medians[median_hash] = random_median_diameter

            end_sub_time = time.clock() - start_sub_time

        sub_results = [("Random Median", median_hash, end_random_time),
                       ("Random Median Distance", random_median_diameter, end_sub_time)]

        # Store this diameter so that we can do maths to it
        random_median_diameters += [random_median_diameter]

        if log is not None:
            write_to_csv(file_log_path, costs, filename, n_meds, -1, -1,
                         -1, sub_results)

    avg = np.average(random_median_diameters)
    std_dev = np.std(random_median_diameters)

    random_median_diameter_time_taken = time.clock() - start_time
    return [("Random Median Distance Average", avg, random_median_diameter_time_taken),
            ("Random Median Distance Standard Deviation", std_dev),
            ("Best Random Median Distance", min(random_median_diameters)),
            ("Worst Random Median Distance", max(random_median_diameters)),
            ("Unique Median Count", len(old_medians))]


def run_single_calculation(filename, D, T, L, log=None, debug=False, verbose=True, zero_loss=False, median=False,
                           worst_median=False, median_cluster=0, median_diameter=False, save_graph=False,
                           save_median_graph=False):
    """This function computes the diameter of space of MPRs in a DTL reconciliation problem,
     as measured by the symmetric set distance between the events of the two reconciliations of the pair
      that has the highest such difference.


      :param filename:      The path to the newick tree file to reconcile
      :param D:             The cost for duplication events
      :param T:             The cost for transfer events
      :param L:             The cost for loss events
      :param log:           The csv file to output results to (will create it if it does not exist)
      :param debug:         Whether to print out all of the tables
      :param verbose:       Whether we should print our results to the screen
      :param zero_loss:     Whether we should also calculate the regular diameter when losses don't cost anything?
      :param median:        Whether we should count the number of medians (and find the median reconciliation graph)
      :param worst_median:  Whether we should find the distance to furthest MPR of the worst median
      :param median_cluster: The number of random medians we should find the distance to furthest MPR is (or 0 for not
                              doing that.
      :param median_diameter: Whether we should calculate the diameter of median-space.
      :param save_graph:    Whether we should save the dtl recon graph as a SIF file to be viewed (or possibly
                             reimported)
      :return:              Nothing, but we output results to a csv file, or the screen"""

    # These statements check to make sure that all arguments were entered correctly.
    assert isinstance(log, (str, unicode)) or log is None
    assert isinstance(filename, (str, unicode))
    assert isinstance(D, (int, float))
    assert isinstance(T, (int, float))
    assert isinstance(L, (int, float))
    assert isinstance(debug, bool)

    # Record the time that DTLReconGraph starts
    start_time = time.clock()

    # Get everything we need from DTLReconGraph
    edge_species_tree, edge_gene_tree, dtl_recon_graph, mpr_count, best_roots = DTLReconGraph.reconcile(filename, D, T,
                                                                                                        L)

    # The gene tree needs to be in node format, not edge format, so we find that now.
    # (This also puts the gene_tree into postorder, as an ordered dict)
    gene_tree, gene_tree_root, gene_node_count = Diameter.reformat_tree(edge_gene_tree, "pTop")

    species_tree, species_tree_root, species_node_count = Diameter.reformat_tree(edge_species_tree, "hTop")

    # And record the amount of time DTLReconGraph + cleaning up the graph took
    DTLReconGraph_time_taken = time.clock() - start_time

    if verbose:
        print "Reconciliation Graph Made in \033[33m\033[1m{0} seconds\033[0m".format(DTLReconGraph_time_taken)

    if save_graph:
        file_graph_name = os.path.split(filename)[1]
        file_graph_name = "graphs/"+ os.path.splitext(file_graph_name)[0] + "_graph.sif"
        ReconGraphFileInterchange.save_recon_graph(dtl_recon_graph, file_graph_name)
        test_graph = ReconGraphFileInterchange.load_recon_graph(file_graph_name)
        if dtl_recon_graph != test_graph:
            print "MPR DTL reconciliation graph was saved improperly!"

    # This list will contain all of the results we want recorded, as tuples.
    results = []

    start_time = time.clock()

    # Now we draw the rest of the owl
    diameter = Diameter.diameter_algorithm(species_tree, gene_tree, gene_tree_root, dtl_recon_graph, dtl_recon_graph,
                                           debug, False)

    # And record how long it took to compute the diameter.
    diameter_time_taken = time.clock() - start_time
    results += [("Diameter", diameter, diameter_time_taken)]

    # Each one of these if statements is controlled by one option on the command line. The results from each test are
    # stored as tuples in the results list, which is passed to the write_to_csv function.
    if zero_loss:
        start_time = time.clock()
        zl_diameter = Diameter.diameter_algorithm(species_tree, gene_tree, gene_tree_root, dtl_recon_graph,
                                                  dtl_recon_graph, debug, True)
        zl_diameter_time_taken = time.clock() - start_time
        results += [("Zero Loss Diameter", zl_diameter, zl_diameter_time_taken)]

    median_reconciliation = {}
    if median or worst_median or median_diameter or save_median_graph:
        new_result, median_reconciliation = find_median_and_count(gene_tree, gene_tree_root, species_tree,
                                                                  dtl_recon_graph, best_roots)
        results += new_result

    if save_median_graph:
        file_graph_name = os.path.split(filename)[1]
        file_graph_name = "graphs/" + os.path.splitext(file_graph_name)[0] + "_med_graph.sif"
        ReconGraphFileInterchange.save_recon_graph(median_reconciliation, file_graph_name)
        test_graph = ReconGraphFileInterchange.load_recon_graph(file_graph_name)
        if median_reconciliation != test_graph:
            print "Median DTL reconciliation graph was saved improperly!"
    if median_diameter:
        assert median_reconciliation != {}, "Can't compute median-space diameter without knowing the median reconciliation!"
        results += find_median_diameter(species_tree, gene_tree, gene_tree_root, median_reconciliation, debug)
    if worst_median:
        assert median_reconciliation != {}, "Can't compute worst median without knowing the median reconciliation!"
        results += find_worst_median_distance(species_tree, gene_tree, gene_tree_root, dtl_recon_graph,
                                              median_reconciliation,
                                              debug)

    if median_cluster > 0:
        costs = "D: {0} T: {1} L: {2}".format(D, T, L)
        results += find_median_cluster(filename, log, costs, gene_tree, gene_tree_root, species_tree, dtl_recon_graph,
                                       best_roots, median_cluster)

    if verbose:
        print "Results:"
        for result in results:
            print "\t{0}:\t\033[33m\033[1m{1}\033[0m".format(result[0], result[1])

    # Now, we write our results to a csv file.
    if log is not None:
        costs = "D: {0} T: {1} L: {2}".format(D, T, L)
        write_to_csv(log + ".csv", costs, filename, mpr_count, gene_node_count, species_node_count,
                     DTLReconGraph_time_taken,
                     results)

    # And we're done.
    return


def run_iterative_calculations(file_pattern, start, end, d, t, l, log=None, debug=False, verbose=True, loud=False,
                               zero_loss=False, median_count=False, worst_median=False, cluster=0,
                               median_diameter=False, save_graph=False, save_median_graph=False):
    """Iterates over a lot of input files and finds the diameter of all of them.
    :param file_pattern: A string contains the name of the files to be used, with the counting number replaced with #'s
    :param start:       Numbered file to start on
    :param end:         Numbered file to end with
    :param d:           Duplication event cost
    :param t:           Transfer event cost
    :param l:           Loss event cost
    :param log:         csv file to log results to
    :param debug:       Whether to print out every DP table made (not recommended)
    :return:
    """
    match = re.match("([^#]*)(#+)([^#]*)", file_pattern)
    if not match:
        print "Filepath '" + file_pattern + "' not understood. Please enter the path to your files, with repeated hash marks" \
                                            "(#'s) in place of sequential numbering."
        return
    fill = len(match.group(2))
    if fill < len(str(end - 1)) or fill < len(str(start)):
        print "Starting or ending number is larger than '{1}' supports ({0})!".format((10 ** fill) - 1, file_pattern)
        return
    print "Running {4} sequential jobs on files '{3}' with costs D = {0}, T = {1}, and L = {2}".format(d, t, l,
                                                                                                       file_pattern,
                                                                                                       end - start)
    for i in range(start, end):
        cur_file = "{0}{1}{2}".format(match.group(1), str(i).zfill(fill), match.group(3))
        if not os.path.exists(cur_file):
            print "(file '{0}' does not exist)".format(cur_file)
            continue

        print "Reconciling {0}".format(cur_file)

        try:
            run_single_calculation(cur_file, d, t, l, log, debug, verbose, zero_loss, median_count, worst_median,
                                   cluster, median_diameter, save_graph, save_median_graph)
        except (KeyboardInterrupt, SystemExit):
            print "\13Thank you for playing Wing Commander!"
            sys.exit()

        except:
            if loud:
                print "\07"
            if verbose:
                print traceback.print_exc(sys.exc_traceback)
            print "Could not reconcile file '{0}'. Continuing, but please make sure the file was formatted correctly!" \
                .format(cur_file)


def main():
    """Processes command line arguments"""
    usage = "usage: %prog [options] file d t l"
    p = optparse.OptionParser(usage=usage)
    p.add_option("-l", "--log", dest="logfile", help="writes a logfile in CSV format to LOGFILE", metavar="LOGFILE")
    p.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True,
                 help="suppresses (most) text output")
    p.add_option("-i", "--iterate", dest="count", action="store", nargs=2, help="calculates every file matching a "
                                                                                "pattern (defined in the file argument)"
                                                                                " with number MIN to MAX.",

                 metavar="MIN MAX", type=int)
    p.add_option("-L", "--loud", dest="loud", action="store_true", default=False,
                 help="print the bell character after each failed file when using the iterate flag")
    p.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                 help="prints out every DP table with size less"
                      "than 30x30")
    p.add_option("-z", "--zero-loss", dest="zero_loss", action="store_true", default=False,
                 help="calculate the zero-loss diameter of the file")
    p.add_option("-m", "--median-count", dest="median_count", action="store_true", default=False,
                 help="count the number of median reconciliations present")
    p.add_option("-M", "--median-diameter", dest="median_diameter", action="store_true", default=False,
                 help="find the diameter of the median reconciliation space")
    p.add_option("-w", "--worst-median", dest="worst_median", action="store_true", default=False,
                 help="find the largest possible distance from a median reconciliation to an MPR")
    p.add_option("-s", "--save-graph", dest="save_graph", action="store_true", default=False,
                 help="save the DTL reconciliation graph to an SIF file after it has been made.")
    p.add_option("-S", "--save-median-graph", dest="save_median_graph", action="store_true", default=False,
                 help="save the median DTL reconciliation graph to an SIF file after it has been made.")
    p.add_option("-c", "--cluster", dest="cluster", action="store", default=0,
                 help="find the distances to the furthest mpr of the specified number of random single medians (requires logging)")

    (options, args) = p.parse_args()
    if len(args) != 4:
        p.error("4 arguments must be provided: filename, d, t, and l")
    filename = args[0]
    d = float(args[1])
    t = float(args[2])
    l = float(args[3])
    log = options.logfile
    debug = options.debug
    verbose = options.verbose
    loud = options.loud
    cluster = int(options.cluster)
    zero_loss = options.zero_loss
    worst_median = options.worst_median
    median_diameter = options.median_diameter
    save_graph = options.save_graph
    save_median_graph = options.save_median_graph

    # Medians must be calculated if we use worst_median, so just add this in.
    median_count = options.median_count or worst_median

    if cluster > 0 and not log:
        p.error("you must specify a log file when doing cluster tests!")
    if cluster:
        cluster_log_folder = os.path.splitext(log)[0]
        if not os.path.exists(cluster_log_folder):
            os.makedirs(cluster_log_folder)
    if save_graph or save_median_graph:
        if not os.path.exists("graphs"):
            os.makedirs("graphs")
    if not (log or debug or verbose):
        p.error("some form of output must be specified! (-l or -d must be used when -q is used)")
    elif options.count is not None:
        rep = options.count
        run_iterative_calculations(filename, rep[0], rep[1], d, t, l, log, debug, verbose, loud, zero_loss,
                                   median_count, worst_median, cluster, median_diameter, save_graph, save_median_graph)
    else:
        run_single_calculation(filename, d, t, l, log, debug, verbose, zero_loss, median_count, worst_median,
                               cluster, median_diameter, save_graph, save_median_graph)


if __name__ == "__main__":
    main()
