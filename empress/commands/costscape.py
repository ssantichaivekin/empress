"""
Find MPR landscapes across ranges of event costs

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
from empress.xscape import costscape

#==========================================================

def run():
    #=============================
    # parser

    parser = argparse.ArgumentParser(
        usage="%(prog)s costscape [options]",
        description="Find MPR landscapes across ranges of event costs",
        formatter_class=commands.CustomHelpFormatter,
        add_help=False)
    parser.add_argument("-h", "--help",
                        action="help",
                        help=argparse.SUPPRESS)

    parser.add_argument("-fn","--filename", dest="filename",
                        metavar="<filename>",
                        required=True,
                        help="The path to the file with the input trees and tip mapping.")

    parser.add_argument("-dl", dest="duplow",
                        metavar="<dup_low>",
                        type=float, default=empress.DUP_LOW, 
                        help="duplication low value")
    parser.add_argument("-dh", dest="duphigh",
                        metavar="<dup_high>",
                        type=float, default=empress.DUP_HIGH,
                        help="duplication high value")
    parser.add_argument("-tl", dest="translow",
                        metavar="<trans_low>",
                        type=float, default=empress.TRANS_LOW,
                        help="transfer low value")
    parser.add_argument("-th", dest="transhigh",
                        metavar="<trans_high>",
                        type=float, default=empress.TRANS_HIGH, 
                        help="transfer high value")

    parser.add_argument("-o", "--outfile", dest="outfile",
                        metavar="<output_file>",
                        default=None,
                        help="output filename")
    parser.add_argument("--log", dest="log",
                        action= "store_true",
                        help="Set display to log scale")

    args = parser.parse_args(sys.argv[2:])

    #=============================
    # process

    newick_data = getInput(args.filename)
    costscape.solve(newick_data,
                    args.duplow, args.duphigh,
                    args.translow, args.transhigh,
                    args.outfile, args.log)
