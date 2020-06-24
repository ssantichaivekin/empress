#!/usr/bin/env python

# empress_cli.py
# Cat Ngo, April 2020
# Updated 6/1/2020 by RLH

import argparse
from pathlib import Path

from empress import input_reader
from empress.reconcile import recongraph_tools
from empress.cluster import cluster_main
from empress.histogram import histogram_main
from empress.xscape import costscape

def process_arg():
    """ Returns args parse object that contains all parameters needed to run a functionality
    :return args - the object that contains all necessary params for the desired functionality to run
    """
    parser = argparse.ArgumentParser()

    ### Path to newick file ###
    parser.add_argument("--host", metavar="<host_file>", required=True,
                        help="The path to the file with the input host tree.")
    parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                        help="The path to the file with the input parasite tree.")
    parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                        help="The path to the file with the tip mapping.")
    
    # subparsers to encode for each functionality 
    subparsers = parser.add_subparsers(dest='functionality',help='Functions empress can run')
    
    ### Parser for costscape ###
    costscape_parser = subparsers.add_parser('costscape', help="Run costscape")
    costscape_parser.add_argument("-dl", metavar="<duplication_low>", default = 1, 
        type=float, help="Duplication low value for costcape")
    costscape_parser.add_argument("-dh", metavar="<duplication_high>", default = 5, 
        type=float, help="Duplication high value for costcape")
    costscape_parser.add_argument("-tl", metavar="<transfer_low>", default = 1, 
        type=float, help="Transfer low value for costcape")
    costscape_parser.add_argument("-th", metavar="<transfer_high>", default = 5, 
        type=float, help="Transfer high value for costcape")
    costscape_parser.add_argument("--outfile", metavar="<output_file>", default = "",
        help="Name of output file, ending in .pdf")
    costscape_parser.add_argument("--log", action= "store_true",
        help="Set display to log scale")
    costscape_parser.add_argument("--display", action= "store_true",
        help="Display output on screen")
    
    ### Parser for reconcile ###
    reconcile_parser = subparsers.add_parser('reconcile', help="Run reconcile")
    reconcile_parser.add_argument("-d", type=float, metavar="<duplication_cost>", 
        default = 2, help="Duplication cost")
    reconcile_parser.add_argument("-t", type=float, metavar="<transfer_cost>", 
        default = 3, help="Transfer cost")
    reconcile_parser.add_argument("-l", type=float, metavar="<loss_cost>", 
        default = 1, help="Loss cost")

    ### Param for clumpr ###
    clumpr_parser = subparsers.add_parser('clumpr', help="Run clumpr")
    clumpr_parser.add_argument("-d", type=float, metavar="<duplication_cost>", 
        default = 2, help="Duplication cost")
    clumpr_parser.add_argument("-t", type=float, metavar="<transfer_cost>", 
        default = 3, help="Transfer cost")
    clumpr_parser.add_argument("-l", type=float, metavar="<loss_cost>", 
        default = 1, help="Loss cost")
    clumpr_parser.add_argument("-k", type=int, metavar="<number_of_clusters>", help="Number of clusters")
    clumpr_parser.add_argument("--medians", action="store_true", required=False,
        help="Whether or not to print out medians for each cluster")
    # Specifies how far down to go when finding splits
    depth_or_n = clumpr_parser.add_mutually_exclusive_group(required=True)
    depth_or_n.add_argument("--depth", type=int, metavar="<tree_depth>",
        help="How far down to split the graph before clustering")
    depth_or_n.add_argument("--nsplits", type=int, metavar="<tree_depth>",
        help="Find at least n splits before combining the splits into clusters")
    # What visualizations to produce
    vis_type = clumpr_parser.add_mutually_exclusive_group(required=False)
    vis_type.add_argument("--pdv-vis", action="store_true",
        help="Visualize the resulting clusters using the Pairwise Distance")
    vis_type.add_argument("--support-vis", action="store_true",
        help="Visualize the resulting clusters using event supports")
    # Which objective function to use
    score = clumpr_parser.add_mutually_exclusive_group(required=True)
    score.add_argument("--pdv", action="store_true",
        help="Use the weighted average distance to evaluate clusters")
    score.add_argument("--support", action="store_true",
        help="Use the weighted average event support to evaluate clusters")

    ### Parser for Histogram ###
    histogram_parser = subparsers.add_parser('histogram', help="Run histogram")
    histogram_parser.add_argument("-d", type=float, metavar="<duplication_cost>", 
        default = 2, help="Duplication cost")
    histogram_parser.add_argument("-t", type=float, metavar="<transfer_cost>", 
        default = 3, help="Transfer cost")
    histogram_parser.add_argument("-l", type=float, metavar="<loss_cost>", 
        default = 1, help="Loss cost")
    histogram_parser.add_argument("--histogram", metavar="<filename>", default="unset",     
        nargs="?", help="Output the histogram at the path provided. \
        If no filename is provided, outputs to a filename based on the input .newick file.")
    histogram_parser.add_argument("--xnorm", action="store_true",
        help="Normalize the x-axis so that the distances range between 0 and 1.")
    histogram_parser.add_argument("--ynorm", action="store_true",
        help="Normalize the y-axis so that the histogram is a probability distribution.")
    histogram_parser.add_argument("--omit_zeros", action="store_true",
        help="Omit the zero column of the histogram, which will always be the total number of reconciliations.")
    histogram_parser.add_argument("--cumulative", action="store_true",
        help="Make the histogram cumulative.")
    histogram_parser.add_argument("--csv", metavar="<filename>", default="unset", nargs="?",
        help="Output the histogram as a .csv file at the path provided. \
        If no filename is provided, outputs to a filename based on the input .newick file.")
    # Statistics to print
    histogram_parser.add_argument("--stats", action="store_true",
        help="Output statistics including the total number of MPRs, the diameter of MPR-space, and the average distance between MPRs.")
    # Time it?
    histogram_parser.add_argument("--time", action="store_true",
        help="Time the diameter algorithm")
    args = parser.parse_args()
    if args.functionality == "histogram":
        fname = Path(args.filename)
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
    

def main():
    args = process_arg()
    recon_input = input_reader.ReconInput.from_files(args.host_file, args.parasite_file, args.mapping_file)
    if args.functionality == "costscape":
        costscape.solve(recon_input, args.dl, args.dh, args.tl, args.th, args)
    elif args.functionality == "reconcile":
        recongraph_tools.reconcile_noninter(recon_input, args.d, args.t, args.l)
    elif args.functionality == "histogram":
        histogram_main.compute_pdv(args.filename, recon_input, args.d, args.t, args.l, args)
    elif args.functionality == "clumpr":
        cluster_main.perform_clustering(recon_input, args.d, args.t, args.l, args.k, args)


if __name__ == "__main__": main()
