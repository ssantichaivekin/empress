
import DTLReconGraph
import HistogramAlg
import Diameter
import HistogramDisplay

import argparse
from pathlib import Path
import time
import math

def process_args():
    """
    Parse the command line arguments.
    :return <namespace> the parsed arguments.
    """
    # Required arguments - input file, D T L costs
    parser = argparse.ArgumentParser("")
    parser.add_argument("--input", metavar="<filename>", required=True,
        help="The path to a .newick file with the input trees and tip mapping.")
    parser.add_argument("-d", type=int, metavar="<duplication_cost>", required=True,
        help="The relative cost of a duplication.")
    parser.add_argument("-t", type=int, metavar="<transfer_cost>", required=True,
        help="The relative cost of a transfer.")
    parser.add_argument("-l", type=int, metavar="<loss_cost>", required=True,
        help="The relative cost of a loss.")
    # Histogram options
    # nargs "?" means that it will search for an argument if there is one, but not take it if there isn't
    # The current setup means that histogram will be set to "unset" if --histogram is not present
    # set to None if --histogram is present with no argument,
    # and set to the argument if there is an argument.
    parser.add_argument("--histogram", metavar="<filename>", default="unset", nargs="?",
        help="Output the histogram at the path provided. \
        If no filename is provided, outputs to a filename based on the input .newick file.")
    parser.add_argument("--xnorm", action="store_true",
        help="Normalize the x-axis so that the distances range between 0 and 1.")
    parser.add_argument("--ynorm", action="store_true",
        help="Normalize the y-axis so that the histogram is a probability distribution.")
    parser.add_argument("--omit_zeros", action="store_true",
        help="Omit the zero column of the histogram, which will always be the total number of reconciliations.")
    parser.add_argument("--cumulative", action="store_true",
        help="Make the histogram cumulative.")
    parser.add_argument("--csv", metavar="<filename>", default="unset", nargs="?",
        help="Output the histogram as a .csv file at the path provided. \
        If no filename is provided, outputs to a filename based on the input .newick file.")
    # Statistics to print
    parser.add_argument("--stats", action="store_true",
        help="Output statistics including the total number of MPRs, the diameter of MPR-space, and the average distance between MPRs.")
    # Time it?
    parser.add_argument("--time", action="store_true",
        help="Time the diameter algorithm.")
    args = parser.parse_args()
    fname = Path(args.input)
    cost_suffix = ".{}-{}-{}".format(args.d, args.t, args.l)
    # If args is unset, use the original .newick file path but replace .newick with .pdf
    if args.histogram is None:
        args.histogram = str(fname.with_suffix(cost_suffix + ".pdf"))
    # If it wasn't set by the arg parser, then set it to None (the option wasn't present)
    elif args.histogram == "unset":
        args.histogram = None
    #TODO: check that the specified path has a matplotlib-compatible extension?
    # Do the same for .csv
    if args.csv is None:
        args.csv = str(fname.with_suffix(cost_suffix + ".csv"))
    elif args.csv == "unset":
        args.csv = None
    # If it was user-specified, check that it has a .csv extension
    else:
        c = Path(args.csv)
        assert c.suffix == ".csv"
    return args

def calc_histogram(newick, d, t, l, time_it, normalize=False, zero_loss=False):
    """
    Compute the PDV from a .newick file.
    :param newick <string> - The newick file to reconcile
    :param d <float> - the cost of a duplication
    :param t <float> - ^^ transfer
    :param l <float> - ^^ loss
    :param time_it <bool> - collect timing info
    :param normalize <bool> - normalize the histogram by the size of the gene tree
    :param zero_loss <bool> - ignore loss events
    :return diameter_alg_hist <Histogram> - the PDV for the given .newick
    :return elapsed <float> - the time it took to compute the PDV
        None if time_it is False.
    """
    # From the newick tree create the reconciliation graph
    edge_species_tree, edge_gene_tree, dtl_recon_graph, mpr_count, best_roots \
        = DTLReconGraph.reconcile(newick, d, t, l)

    # If we want to know the number of MPRs
    #print(mpr_count)

    # Reformat the host and parasite tree to use it with the histogram algorithm
    gene_tree, gene_tree_root, gene_node_count = Diameter.reformat_tree(edge_gene_tree, "pTop")
    species_tree, species_tree_root, species_node_count \
        = Diameter.reformat_tree(edge_species_tree, "hTop")

    if time_it:
        start = time.time()
    # Calculate the histogram via histogram algorithm
    diameter_alg_hist = HistogramAlg.diameter_algorithm(
        species_tree, gene_tree, gene_tree_root, dtl_recon_graph, dtl_recon_graph,
        False, zero_loss)
    if time_it:
        end = time.time()
        elapsed = end - start
    else:
        elapsed = None

    if normalize:
        # Number of internal gene tree nodes
        gene_tree_nodes = int(math.ceil(len(gene_tree) / 2.0))
        diameter_alg_hist = diameter_alg_hist.xscale(1.0/(2*gene_tree_nodes))
    return diameter_alg_hist, elapsed

def transform_hist(hist, omit_zeros, xnorm, ynorm, cumulative):
    """
    Transform the given histogram in various ways
    :param hist <Histogram> - the histogram to transform
    :param omit_zeros <bool> - omit the zero column of the histogram
    :param xnorm <bool> - normalize the x-values of the histogram to [0,1]
    :param ynorm <bool> - normalize the y-values of the histogram to [0,1]
    :param cumulative <bool> - make the histogram cumulative
    :return hist_cum <Histogram> - the transformed histogram
    :return width <float> - the bin-width that should be used when plotting the histogram
    """
    # Omit zeroes
    if omit_zeros:
        hist_zero = HistogramDisplay.omit_zeros(hist)
    else:
        hist_zero = hist
    # Normalize the x values
    if xnorm:
        width = 1 / float(max(hist_zero.keys()))
        hist_xnorm = HistogramDisplay.normalize_xvals(hist_zero)
    else:
        width = 1
        hist_xnorm = hist_zero
    # Normalize the y values
    if ynorm:
        hist_ynorm = HistogramDisplay.normalize_yvals(hist_xnorm)
    else:
        hist_ynorm = hist_xnorm
    # Cumulative
    if cumulative:
        hist_cum = HistogramDisplay.cumulative(hist_ynorm)
    else:
        hist_cum = hist_ynorm
    return hist_cum, width

def main(args):
    """
    Compute the PDV and other information and save them / output them
    :param args <namespace> - the CLI arguments
    """
    hist, elapsed = calc_histogram(args.input, args.d, args.t, args.l, args.time)
    hist = hist.histogram_dict
    if args.time:
        print(("Time spent: {}".format(elapsed)))
    # Calculate the statistics (with zeros)
    if args.stats:
        n_mprs = hist[0]
        diameter, mean, std = HistogramDisplay.compute_stats(hist)
        print(("Number of MPRs: {}".format(n_mprs)))
        print(("Diameter of MPR-space: {}".format(diameter)))
        print(("Mean MPR distance: {} with standard deviation {}".format(mean, std)))
    hist_new, width = transform_hist(hist, args.omit_zeros, args.xnorm, args.ynorm, args.cumulative)
    # Make the histogram image
    if args.histogram is not None:
        HistogramDisplay.plot_histogram(args.histogram, hist, width, Path(args.input).stem, args.d, args.t, args.l)
    if args.csv is not None:
        HistogramDisplay.csv_histogram(args.csv, hist)

if __name__ == "__main__":
    args = process_args()
    main(args)

