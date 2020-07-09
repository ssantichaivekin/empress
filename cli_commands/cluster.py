import argparse
import empress
from empress.cluster import cluster_main
import cli_commands._shared_utils


def add_cluster_to_parser(cluster_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(cluster_parser)
    cluster_parser.add_argument("n_clusters", type=int, metavar="<number_of_clusters>", help="Number of clusters")

    cli_commands._shared_utils.add_dtl_costs_to_parser(cluster_parser)

    cluster_parser.add_argument("--medians", action="store_true", required=False,
                                help="whether or not to print out medians for each cluster")

    # Specifies how far down to go when finding splits
    depth_or_n = cluster_parser.add_mutually_exclusive_group(required=True)
    depth_or_n.add_argument("--depth", type=int, metavar="<tree_depth>",
                            help="how far down to split the graph before clustering")
    depth_or_n.add_argument("--n-splits", type=int, metavar="<tree_depth>",
                            help="find at least n splits before combining the splits into clusters")

    # What visualizations to produce
    vis_type = cluster_parser.add_mutually_exclusive_group(required=False)
    vis_type.add_argument("--pdv-vis", action="store_true",
                          help="visualize the resulting clusters using the Pairwise Distance")
    vis_type.add_argument("--support-vis", action="store_true",
                          help="visualize the resulting clusters using event supports")

    # Which objective function to use
    score = cluster_parser.add_mutually_exclusive_group(required=True)
    score.add_argument("--pdv", action="store_true",
                       help="use the weighted average distance to evaluate clusters")
    score.add_argument("--support", action="store_true",
                       help="use the weighted average event support to evaluate clusters")


def run_cluster(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    cluster_main.perform_clustering(recon_input, args.dup_cost, args.trans_cost, args.loss_cost, args.n_clusters, args)
