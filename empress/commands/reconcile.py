"""
Reconcile gene tree to species tree

Yi-Chieh Wu
May 6, 2020
"""

# python libraries
import argparse
import sys

# empress libraries
import empress
from empress import commands
from empress.newickFormatReader import getInput
from empress.clumpr import DTLReconGraph

#==========================================================

def run():
    #=============================
    # parser

    parser = argparse.ArgumentParser(
        usage="%(prog)s reconcile [options]",
        description="Find an MPR",
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

    args = parser.parse_args(sys.argv[2:])

    #=============================
    # process

    newick_data = getInput(args.filename)
    DTLReconGraph.reconcile_noninter(newick_data,
                                     args.dupcost, args.transcost, args.losscost)
