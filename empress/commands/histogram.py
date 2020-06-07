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
from empress.clumpr import HistogramMain

#==========================================================

def run():
    #=============================
    # parser

    parser = argparse.ArgumentParser(
        usage="%(prog)s histogram [options]",
        description="Display histogram of pairwise distances between MPRs",
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

    parser.add_argument("--histogram",
                        metavar="<filename>", default="unset",     
                        nargs="?",
                        help=\
"""Output the histogram at the path provided.
If no filename is provided, outputs to a filename based on the input .newick file.""")
    parser.add_argument("--xnorm",
                        action="store_true",
                        help="Normalize x-axis so that distances range between 0 and 1.")
    parser.add_argument("--ynorm",
                        action="store_true",
                        help="Normalize y-axis so that histogram is probability distribution.")
    parser.add_argument("--omit_zeros",
                        action="store_true",
                        help="Omit zero column of histogram, which will always be the number of reconciliations.")
    parser.add_argument("--cumulative",
                        action="store_true",
                        help="Make the histogram cumulative.")
    parser.add_argument("--csv",
                        metavar="<filename>", default="unset", nargs="?",
                        help=\
"""Output the histogram as a .csv file at the path provided.
If no filename is provided, outputs to a filename based on the input .newick file.""")
    
    parser.add_argument("--stats",
                        action="store_true",
                        help="Output statistics including the total number of MPRs, the diameter of MPR-space, and the average distance between MPRs.")

    parser.add_argument("--time",
                        action="store_true",
                        help="Time the diameter algorithm")

    args = parser.parse_args(sys.argv[2:])

    #=============================
    # process

    fname = Path(args.filename)
    cost_suffix = ".{}-{}-{}".format(args.dupcost, args.transcost, args.losscost)
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
