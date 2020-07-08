import argparse
import empress
from empress.cluster import cluster_main


def add_cluster_to_parser(cluster_parser: argparse.ArgumentParser):
    # Read input files
    cluster_parser.add_argument("--host", metavar="<host_file>", required=True,
                                help="The path to the file with the input host tree.")
    cluster_parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                                help="The path to the file with the input parasite tree.")
    cluster_parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                                help="The path to the file with the tip mapping.")

    # Read duplication/transfer/loss information
    cluster_parser.add_argument("-d", type=float, metavar="<duplication_cost>",
                                default=2, help="Duplication cost")
    cluster_parser.add_argument("-t", type=float, metavar="<transfer_cost>",
                                default=3, help="Transfer cost")
    cluster_parser.add_argument("-l", type=float, metavar="<loss_cost>",
                                default=1, help="Loss cost")

    cluster_parser.add_argument("-k", type=int, metavar="<number_of_clusters>", help="Number of clusters")

    cluster_parser.add_argument("--medians", action="store_true", required=False,
                                help="Whether or not to print out medians for each cluster")

    # Specifies how far down to go when finding splits
    depth_or_n = cluster_parser.add_mutually_exclusive_group(required=True)
    depth_or_n.add_argument("--depth", type=int, metavar="<tree_depth>",
                            help="How far down to split the graph before clustering")
    depth_or_n.add_argument("--nsplits", type=int, metavar="<tree_depth>",
                            help="Find at least n splits before combining the splits into clusters")

    # What visualizations to produce
    vis_type = cluster_parser.add_mutually_exclusive_group(required=False)
    vis_type.add_argument("--pdv-vis", action="store_true",
                          help="Visualize the resulting clusters using the Pairwise Distance")
    vis_type.add_argument("--support-vis", action="store_true",
                          help="Visualize the resulting clusters using event supports")

    # Which objective function to use
    score = cluster_parser.add_mutually_exclusive_group(required=True)
    score.add_argument("--pdv", action="store_true",
                       help="Use the weighted average distance to evaluate clusters")
    score.add_argument("--support", action="store_true",
                       help="Use the weighted average event support to evaluate clusters")


def run_cost_regions(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    cluster_main.perform_clustering(recon_input, args.d, args.t, args.l, args.k, args)
