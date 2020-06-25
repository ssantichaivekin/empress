from pathlib import Path
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from empress.cluster import cluster_util
from empress.histogram import histogram_display
from empress.reconcile import median

def plot_support_histogram(plot_file, hist_def, width, tree_name, d, t, l, max_x=None, max_y=None, title=True):
    """
    Creates Support visualization
    :param plot_file <str> - path of pdf file
    :param hist_def <tuple> - size 2, hist and bins
    :param width <float> - width of the plot
    :param tree_name <str> - name of the tree file
    :param d <float> - duplication cost
    :param t <float> - transfer cost
    :param l <float> - loss cost
    :max_x <float> - maximum x value
    :max_y <float> - maximum y value
    :title <str> - Title for the plot
    """
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

def vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, tree_data):
    """
    Creates Support visualization
    :param species_tree <OrderedDict> - the input species tree
    :param gene_tree <OrderedDict> - the input gene tree
    :param gene_root <str> - the value of the gene root
    :param recon_g <dict> - reconciliation graph
    :param cluster_gs <list> - list of cluster graphs, i.e. list of cluster dicts
    :param args <ArgumentParser>: args parse object that contains all parameters needed 
    :param mk_get_hist <func mk_get_support_hist>: retrieves support histograms
    :param plot_f <func plot_support_histogram>: plots support histograms
    :param get_max <func get_max>: retrieves max of key,value
    :param tree_data <str>: file location
    """
    get_hist = mk_get_hist(species_tree, gene_tree, gene_root)
    cost_suffix = ".{}-{}-{}".format(args.d, args.t, args.l)
    p = Path(tree_data)
    orig_p = str(p.with_suffix(cost_suffix + ".pdf"))
    orig_h = get_hist(recon_g)
    max_x, max_y = get_max(orig_h)
    plot_f(orig_p, orig_h, 1, Path(tree_data).stem, args.d, args.t, args.l, max_x, max_y, False)
    for i, g in enumerate(cluster_gs):
        g_i = "-{}cluster{}".format(args.k, i)
        g_p = str(p.with_suffix("." + g_i + cost_suffix + ".pdf"))
        g_h = get_hist(g)
        plot_f(g_p, g_h, 1, Path(tree_data).stem + g_i, args.d, args.t, args.l, max_x, max_y, False)

def support_vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, tree_data):
    """
    Creates Support visualization
    :param species_tree <OrderedDict> - the input species tree
    :param gene_tree <OrderedDict> - the input gene tree
    :param gene_root <str> - the value of the gene root
    :param recon_g <dict> - reconciliation graph
    :param cluster_gs <list> - list of cluster graphs, i.e. list of cluster dicts
    :param args <ArgumentParser>: args parse object that contains all parameters needed 
    :param tree_data <str>: file location
    """
    mk_get_hist = cluster_util.mk_get_support_hist
    plot_f = plot_support_histogram
    def get_max(l):
        h, b = l
        return 1, np.amax(h)
    vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, tree_data)

def pdv_vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, tree_data):
    """
    Creates pdv_vis
    :param species_tree <OrderedDict> - the input species tree
    :param gene_tree <OrderedDict> - the input gene tree
    :param gene_root <str> - the value of the gene root
    :param recon_g <dict> - reconciliation graph
    :param cluster_gs <list> - list of cluster graphs, i.e. list of cluster dicts
    :param args <ArgumentParser>: args parse object that contains all parameters needed 
    :param tree_data <str>: file location
    """
    mk_get_hist = cluster_util.mk_get_pdv_hist
    plot_f = histogram_display.plot_histogram
    def get_max(l):
        return max(l.keys()), max(l.values())
    vis(species_tree, gene_tree, gene_root, recon_g, cluster_gs, args, mk_get_hist, plot_f, get_max, tree_data)

def mk_get_median(gene_tree, species_tree, gene_root, best_roots):
    """
    Calculate the median
    :param gene_tree <OrderedDict> - the input gene tree
    :param species_tree <OrderedDict> - the input species tree
    :param gene_root <str> - the value of the gene root
    :param best_roots <list> - list of str of the best roots
    :return get_median <func get_median> - the function that calculates the median for a graph
    """
    def get_median(graph):
        """
        Returns the median
        :param graph <dict> - the input graph
        :return random_median <dict> - the median
        """
        median_graph, n_meds, median_roots = median.get_median_graph(
                graph, gene_tree, species_tree, gene_root, best_roots)
        med_counts = median.get_med_counts(median_graph, median_roots)
        random_median = median.choose_random_median_wrapper(median_graph, median_roots, med_counts)
        return random_median
    return get_median

def perform_clustering(tree_data, d, t, l, k, args):
    """
    :param tree_data <ReconInput>: Output of newickFormatReader.getInput()
    :param d <float>: cost of a duplication
    :param t <float>: cost of a transfer
    :param l <float>: cost of a loss
    :param k <float>: number of clusters
    :param args <ArgumentParser>: args parse object that contains all parameters needed 
    to run a functionality.
    """
    # if args.interactive:
    #     # converts args to dictionary first
    #     args = vars(args)
    #     args = ClusterMainInput.getInput(d, t, l, k, args)

    # Choose the distance metric
    if args.support:
        mk_score = cluster_util.mk_support_score
    elif args.pdv:
        mk_score = cluster_util.mk_pdv_score
    else:
        assert False
    # Get the recon graph + other info
    gene_tree, species_tree, gene_root, recon_g, mpr_count, best_roots = \
        cluster_util.get_tree_info(tree_data, d, t, l)

    # Visualize the graphs
    #RV.visualizeAndSave(recon_g, "original.png")
    #gs = ClusterUtil.full_split(recon_g, gene_root, args.depth)
    #for i, g in enumerate(gs):
    #    RV.visualizeAndSave(g, "{}.png".format(i))
    
    mpr_counter = cluster_util.mk_count_mprs(gene_root)
    # Make the distance metric for these specific trees
    score = mk_score(species_tree, gene_tree, gene_root)
    # Actually perform the clustering
    if args.depth is not None:
        graphs,scores,_ = cluster_util.cluster_graph(recon_g, gene_root, score, args.depth, k, 200)
    elif args.nsplits is not None:
        graphs,scores,_ = cluster_util.cluster_graph_n(recon_g, gene_root, score, args.nsplits, mpr_count, k, 200)
    else:
        assert False
    # Visualization
    if args.pdv_vis:
        pdv_vis(species_tree, gene_tree, gene_root, recon_g, graphs, args, args.filename)
    if args.support_vis:
        support_vis(species_tree, gene_tree, gene_root, recon_g, graphs, args, args.filename)
    if args.medians:
        get_median = mk_get_median(gene_tree, species_tree, gene_root, best_roots)
        for i, g in enumerate(graphs):
            m = get_median(g)
            print(("Median for Cluster {}:".format(i)))
            # TODO: print to a better file format?
            print(m)
    # Statistics
    one_score = cluster_util.get_score_nodp([recon_g], score, mpr_counter)
    k_score = cluster_util.get_score_nodp(graphs, score, mpr_counter)
    improvement = cluster_util.calc_improvement(k_score, one_score)
    print(("Old score: {}".format(one_score)))
    print(("New score: {}".format(k_score)))
    print(("Improvement:  {}".format(improvement)))
