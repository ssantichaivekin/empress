import argparse
from pathlib import Path

import empress
from empress.histogram import histogram_main


def add_histogram_to_parser(histogram_parser: argparse.ArgumentParser):
    # Read input files
    histogram_parser.add_argument("--host", metavar="<host_file>", required=True,
                                     help="The path to the host tree file.")
    histogram_parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                                     help="The path to the parasite tree file.")
    histogram_parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                                     help="The path to the tip mapping file.")

    # Read duplication/transfer/loss information
    histogram_parser.add_argument("-d", type=float, metavar="<duplication_cost>",
                                  default=2, help="Duplication cost")
    histogram_parser.add_argument("-t", type=float, metavar="<transfer_cost>",
                                  default=3, help="Transfer cost")
    histogram_parser.add_argument("-l", type=float, metavar="<loss_cost>",
                                  default=1, help="Loss cost")

    histogram_parser.add_argument("--histogram", metavar="<filename>", default="unset",
                                  nargs="?", help="Output the histogram at the path provided. If no filename is "
                                                  "provided, outputs to a filename based on the input host file.")
    histogram_parser.add_argument("--xnorm", action="store_true",
                                  help="Normalize the x-axis so that the distances range between 0 and 1.")
    histogram_parser.add_argument("--ynorm", action="store_true",
                                  help="Normalize the y-axis so that the histogram is a probability distribution.")
    histogram_parser.add_argument("--omit_zeros", action="store_true",
                                  help="Omit the zero column of the histogram, which will always be the total number "
                                       "of reconciliations.")
    histogram_parser.add_argument("--cumulative", action="store_true",
                                  help="Make the histogram cumulative.")
    histogram_parser.add_argument("--csv", metavar="<filename>", default="unset", nargs="?",
                                  help="Output the histogram as a .csv file at the path provided. If no filename is "
                                       "provided, outputs to a filename based on the input host file.")

    # Statistics to print
    histogram_parser.add_argument("--stats", action="store_true",
                                  help="Output statistics including the total number of MPRs, the diameter of "
                                       "MPR-space, and the average distance between MPRs.")

    # Time it
    histogram_parser.add_argument("--time", action="store_true",
                                  help="Time the diameter algorithm")


def run_cost_regions(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    fname = Path(args.host)
    cost_suffix = ".{}-{}-{}".format(args.d, args.t, args.l)
    # If args is unset, use the original .newick file path but replace .newick with .pdf
    if args.histogram is None:
        args.histogram = str(fname.with_suffix(cost_suffix + ".pdf"))
    # If it wasn't set by the arg parser, then set it to None (the option wasn't present)
    elif args.histogram == "unset":
        args.histogram = None
    # TODO: check that the specified path has a matplotlib-compatible extension?
    # Do the same for .csv
    if args.csv is None:
        args.csv = str(fname.with_suffix(cost_suffix + ".csv"))
    elif args.csv == "unset":
        args.csv = None
    # If it was user-specified, check that it has a .csv extension
    else:
        c = Path(args.csv)
        assert c.suffix == ".csv"

    histogram_main.compute_pdv(args.host, recon_input, args.d, args.t, args.l, args)
