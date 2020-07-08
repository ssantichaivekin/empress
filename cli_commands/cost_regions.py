import argparse
import empress
from empress.xscape import costscape


def add_cost_regions_to_parser(cost_regions_parser: argparse.ArgumentParser):
    # Read input files
    cost_regions_parser.add_argument("--host", metavar="<host_file>", required=True,
                                     help="The path to the host tree file.")
    cost_regions_parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                                     help="The path to the parasite tree file.")
    cost_regions_parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                                     help="The path to the tip mapping file.")

    # Read cost_regions information
    cost_regions_parser.add_argument("-dl", "--duplication_low", metavar="<duplication_low>", default=1,
                                     type=float, help="Duplication low value for cost regions viewer window")
    cost_regions_parser.add_argument("-dh", "--duplication_high", metavar="<duplication_high>", default=5,
                                     type=float, help="Duplication high value for cost regions viewer window")
    cost_regions_parser.add_argument("-tl", "--transfer_low", metavar="<transfer_low>", default=1,
                                     type=float, help="Transfer low value for cost regions viewer window")
    cost_regions_parser.add_argument("-th", "--transfer_high", metavar="<transfer_high>", default=5,
                                     type=float, help="Transfer high value for cost regions viewer window")
    cost_regions_parser.add_argument("--outfile", metavar="<output_file>", default="",
                                     help="Name of output file, ending in .pdf")
    cost_regions_parser.add_argument("--log", action="store_true",
                                     help="Set display to log scale")
    cost_regions_parser.add_argument("--display", action="store_true",
                                     help="Display output on screen")


def run_cost_regions(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    costscape.solve(recon_input, args.duplication_low, args.duplication_high, args.transfer_low, args.transfer_high,
                    args)
