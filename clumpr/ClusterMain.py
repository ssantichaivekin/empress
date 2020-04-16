import ClusterUtil
import ReconciliationVisualization as RV
import HistogramDisplay
import DTLMedian
import ClusterMainInput

import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ideas
# - Correlate normality with improvement
# - Correlate improvement with depth / no. of graphs before clustering
# - Correlate improvement with the number of clusters
# - Just a histogram of the improvements for each tree
# - Normality distance (i.e. Normality statistic instead of average for the PDV)
#   - How does this correlate with improvements in the other metrics?
# - Generally, for each metric how does it improve the other metrics
#   - Ex. correlate PDV improvement with Support improvement for clusterings created
#       using the PDV (or support) distance.
# - Use "increases average improvement the most" rather than "smallest distance between pairs"
#   for deciding which to merge
#   - is this the same?

# Improvement vs. number of clusters, but improvement is vs. 1 cluster only

# The width parameter is unused -- it's here to maintain compatibility with HistogramDisplay.plot_histogram
def plot_support_histogram(plot_file, hist_def, width, tree_name, d, t, l, max_x=None, max_y=None, title=True):
    hist, bins = hist_def
    width = bins[1] - bins[0]
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align="center", width=width)
    # Set max y
    if max_y is not None:
        plt.ylim(top=max_y)
    if max_x is not None:
        plt.xlim(right=max_x)
    plt.xlabel("Event Support")
    plt.ylabel("Number of Events")
    if title:
        plt.title("{} with costs D:{}, T:{}, L:{}".format(tree_name, d, t, l))
    plt.savefig(plot_file, bbox_inches="tight")
    plt.clf()

# My attempt at leveraging the fact that we want to generate the plots in the same
# manner regardless of which type of plot to use...
def vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, newick_data):
    get_hist = mk_get_hist(species_tree, gene_tree, gene_root)
    cost_suffix = ".{}-{}-{}".format(args["d"], args["t"], args["l"])
    p = Path(newick_data)
    orig_p = str(p.with_suffix(cost_suffix + ".pdf"))
    orig_h = get_hist(recon_g)
    max_x, max_y = get_max(orig_h)
    plot_f(orig_p, orig_h, 1, Path(newick_data).stem, args["d"], args["t"], args["l"], max_x, max_y, False)
    for i, g in enumerate(cluster_gs):
        g_i = "-{}cluster{}".format(args["k"], i)
        g_p = str(p.with_suffix("." + g_i + cost_suffix + ".pdf"))
        g_h = get_hist(g)
        plot_f(g_p, g_h, 1, Path(newick_data).stem + g_i, args["d"], args["t"], args["l"], max_x, max_y, False)

def support_vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, newick_data):
    mk_get_hist = ClusterUtil.mk_get_support_hist
    plot_f = plot_support_histogram
    def get_max(l):
        h, b = l
        return 1, np.amax(h)
    vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, newick_data)

def pdv_vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, newick_data):
    mk_get_hist = ClusterUtil.mk_get_pdv_hist
    plot_f = HistogramDisplay.plot_histogram
    def get_max(l):
        return max(l.keys()), max(l.values())
    vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, newick_data)

def mk_get_median(gene_tree, species_tree, gene_root, best_roots):
    def get_median(graph):
        median_graph, n_meds, median_roots = DTLMedian.get_median_graph(
                graph, gene_tree, species_tree, gene_root, best_roots)
        med_counts = DTLMedian.get_med_counts(median_graph, median_roots)
        random_median = DTLMedian.choose_random_median_wrapper(median_graph, median_roots, med_counts)
        return random_median
    return get_median

def main(filename, newick_data, relev_params=None):
    """
    :param filename: the path to a .newick file with the input trees and tip mapping.
    :param newick_data: output to newickFormatReader.getInput().
    :param relev_params: relevant params.
    """

    if (relev_params == None):
        relev_params = {}

    args = ClusterMainInput.getInput(Path(filename), relev_params)
    # Choose the distance metric
    if args["support"]:
        mk_score = ClusterUtil.mk_support_score
    elif args["pdv"]:
        mk_score = ClusterUtil.mk_pdv_score
    else:
        assert False
    # Get the recon graph + other info
    gene_tree, species_tree, gene_root, recon_g, mpr_count, best_roots = \
        ClusterUtil.get_tree_info(newick_data, args["d"],args["t"],args["l"])

    # Visualize the graphs
    #RV.visualizeAndSave(recon_g, "original.png")
    #gs = ClusterUtil.full_split(recon_g, gene_root, args["depth"])
    #for i, g in enumerate(gs):
    #    RV.visualizeAndSave(g, "{}.png".format(i))
    
    mpr_counter = ClusterUtil.mk_count_mprs(gene_root)
    # Make the distance metric for these specific trees
    score = mk_score(species_tree, gene_tree, gene_root)
    # Actually perform the clustering
    if args["depth"] is not None:
        graphs,scores,_ = ClusterUtil.cluster_graph(recon_g, gene_root, score, args["depth"], args["k"], 200)
    elif args["nmprs"] is not None:
        graphs,scores,_ = ClusterUtil.cluster_graph_n(recon_g, gene_root, score, args["nmprs"], mpr_count, args["k"], 200)
    else:
        assert False
    # Visualization
    if args["pdv_vis"]:
        pdv_vis(species_tree, gene_tree, gene_root, recon_g, graphs, args, newick_data)
    if args["support_vis"]:
        support_vis(species_tree, gene_tree, gene_root, recon_g, graphs, args, newick_data)
    if args["medians"]:
        get_median = mk_get_median(gene_tree, species_tree, gene_root, best_roots)
        for i, g in enumerate(graphs):
            m = get_median(g)
            print(("Median for Cluster {}:".format(i)))
            # TODO: print to a better file format?
            print(m)
    # Statistics
    one_score = ClusterUtil.get_score_nodp([recon_g], score, mpr_counter)
    k_score = ClusterUtil.get_score_nodp(graphs, score, mpr_counter)
    improvement = ClusterUtil.calc_improvement(k_score, one_score)
    print(("Old score: {}".format(one_score)))
    print(("New score: {}".format(k_score)))
    print(("Improvement:  {}".format(improvement)))

# Debug
def main2():
    args = process_args()
    gene_tree, species_tree, gene_root, recon_g, mpr_count = \
        ClusterUtil.get_tree_info(newick_data, args["d"],args["t"],args["l"])
    RV.visualizeAndSave(recon_g, "original.png")
    gs = ClusterUtil.full_split(recon_g, gene_root, args["depth"])
    for i, g in enumerate(gs):
        RV.visualizeAndSave(g, "{}.png".format(i))
