"""
Display histogram of pairwise distances between MPRs

Yi-Chieh Wu
May 6, 2020
"""

# python libraries
import argparse
from pathlib import Path
import sys

# empress libraries
import empress
from empress import commands
from empress.newickFormatReader import getInput
from empress.clumpr import ClusterMain

#==========================================================

def run():
    #=============================
    # parser

    parser = argparse.ArgumentParser(
        usage="%(prog)s clumpr [options]",
        description="Cluster MPRs",
        formatter_class=commands.CustomHelpFormatter,
        add_help=False)
    parser.add_argument("-h", "--help",
                        action="help",
                        help=argparse.SUPPRESS)

    parser.add_argument("-fn","--filename", dest="filename",
                        metavar="<filename>",
                        required=True,
                        help="The path to the file with the input trees and tip mapping.")

    parser.add_argument("-d", dest="dupcost",
                        metavar="<dup_cost>",
                        type=float, default=empress.DUP_COST,
                        help="duplication cost")
    parser.add_argument("-t", dest="transcost",
                        metavar="<transfer_cost>",
                        type=float, default=empress.TRANS_COST,
                        help="transfer cost")
    parser.add_argument("-l", dest="losscost",
                        metavar="<loss_cost>",
                        type=float, default=empress.LOSS_COST,
                        help="loss cost")

    parser.add_argument("-k", dest="k",
                        metavar="<number_of_clusters>",
                        type=int, default=empress.NUM_CLUSTERS,
                        help="Number of clusters")
    parser.add_argument("--medians", dest="medians",
                        action="store_true",
                        help="Set to print medians for each cluster")

    depth_or_n = parser.add_mutually_exclusive_group(required=True)
    depth_or_n.add_argument("--depth", dest="depth",
                            metavar="<tree_depth>",
                            type=int,
                            help="How far down graph to consider event splits")
    depth_or_n.add_argument("--nmprs", dest="nmprs",
                            metavar="<tree_depth>",
                            type=int,
                            help="Number of MPRs to consider")

    vis_type = parser.add_mutually_exclusive_group(required=False)
    vis_type.add_argument("--pdv-vis", dest="pdv_vis",
                          action="store_true",
                          help="Visualize resulting clusters using pairwise distance")
    vis_type.add_argument("--support-vis", dest="support_vis",
                          action="store_true",
                          help="Visualize resulting clusters using event supports")

    score = parser.add_mutually_exclusive_group(required=True)
    score.add_argument("--pdv", action="store_true",
                       help="use weighted average distance to evaluate clusters")
    score.add_argument("--support", action="store_true",
                       help="use weighted average event support to evaluate clusters")

    args = parser.parse_args(sys.argv[2:])

    #=============================
    # process

    newick_data = getInput(args.filename)
    ClusterMain.perform_clustering(newick_data,
                                   args.dupcost, args.transcost, args.losscost,
                                   args.k, args)
