import time
import math
from pathlib import Path

from empress.histogram import histogram_alg, histogram_display
from empress.reconcile import recongraph_tools, diameter

def calc_histogram(tree_data, d, t, l, time_it, normalize=False, zero_loss=False):
    """
    Compute the PDV from a .newick file
    :param tree_data <ReconInput> - Output of newickFormatReader.getInput()
    :param d <float> - the cost of a duplication
    :param t <float> - ^^ transfer
    :param l <float> - ^^ loss
    :param time_it <bool> - collect timing info
    :param normalize <bool> - normalize the histogram by the size of the gene tree
    :param zero_loss <bool> - ignore loss events
    :return diameter_alg_hist <Histogram> - the PDV for the given .newick
    :return elapsed <float> - the time it took to compute the PDV
        None if time_it is False
    """
    # From the newick tree create the reconciliation graph
    edge_species_tree, edge_gene_tree, dtl_recon_graph, mpr_count, best_roots \
        = recongraph_tools.reconcile(tree_data, d, t, l)

    # If we want to know the number of MPRs
    #print(mpr_count)

    # Reformat the host and parasite tree to use it with the histogram algorithm
    gene_tree, gene_tree_root, gene_node_count = diameter.reformat_tree(edge_gene_tree, "pTop")
    species_tree, species_tree_root, species_node_count \
        = diameter.reformat_tree(edge_species_tree, "hTop")

    if time_it:
        start = time.time()
    # Calculate the histogram via histogram algorithm
    diameter_alg_hist = histogram_alg.diameter_algorithm(
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
        hist_zero = histogram_display.omit_zeros(hist)
    else:
        hist_zero = hist
    # Normalize the x values
    if xnorm:
        width = 1 / float(max(hist_zero.keys()))
        hist_xnorm = histogram_display.normalize_xvals(hist_zero)
    else:
        width = 1
        hist_xnorm = hist_zero
    # Normalize the y values
    if ynorm:
        hist_ynorm = histogram_display.normalize_yvals(hist_xnorm)
    else:
        hist_ynorm = hist_xnorm
    # Cumulative
    if cumulative:
        hist_cum = histogram_display.cumulative(hist_ynorm)
    else:
        hist_cum = hist_ynorm
    return hist_cum, width

def compute_pdv(filename, tree_data, d, t, l, args):
    """
    Compute the PDV and other information and save them / output them
    :param filename - the path to a .newick file with the input trees and tip mapping
    :param tree_data <ReconInput> - Output of newickFormatReader.getInput()
    :param d <float> - the cost of a duplication
    :param t <float> - ^^ transfer
    :param l <float> - ^^ loss
    :param args <ArgumentParser> - object that contains all parameters needed 
    to compute, save, and/or output the PDV
    """
    # if args.interactive:
    #     # converts args to dictionary first
    #     args = vars(args)
    #     args = HistogramMainInput.getInput(Path(filename), d, t, l, args)
    hist, elapsed = calc_histogram(tree_data, d, t, l, args.time)
    hist = hist.histogram_dict
    if args.time:
        print("Time spent: {}".format(elapsed))
    # Calculate the statistics (with zeros)
    if args.stats:
        n_mprs = hist[0]
        diameter, mean, std = histogram_display.compute_stats(hist)
        print("Number of MPRs: {}".format(n_mprs))
        print("Diameter of MPR-space: {}".format(diameter))
        print("Mean MPR distance: {} with standard deviation {}".format(mean, std))
    hist_new, width = transform_hist(hist, args.omit_zeros, args.xnorm, args.ynorm, args.cumulative)
    # Make the histogram image
    if args.histogram is not None:
        histogram_display.plot_histogram(args.histogram, hist, width, Path(args.host).stem, args.d, args.t, args.l)
    if args.csv is not None:
        histogram_display.csv_histogram(args.csv, hist)

