import argparse
from pathlib import Path

import empress
from empress.xscape import costscape
import cli_commands._shared_utils

def add_cost_regions_to_parser(cost_regions_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(cost_regions_parser)

    # Read cost_regions information
    cost_regions_parser.add_argument("-dl", "--duplication-low", metavar="<duplication_low>", default=1,
                                     type=float, help="duplication low value for cost regions viewer window")
    cost_regions_parser.add_argument("-dh", "--duplication-high", metavar="<duplication_high>", default=5,
                                     type=float, help="duplication high value for cost regions viewer window")
    cost_regions_parser.add_argument("-tl", "--transfer-low", metavar="<transfer_low>", default=1,
                                     type=float, help="transfer low value for cost regions viewer window")
    cost_regions_parser.add_argument("-th", "--transfer-high", metavar="<transfer_high>", default=5,
                                     type=float, help="transfer high value for cost regions viewer window")
    cost_regions_parser.add_argument("--outfile", metavar="<output_file>", default=None, required=True,
                                     help="name of output file, ending with .pdf")
    cost_regions_parser.add_argument("--log", action="store_true",
                                     help="set display to log scale")

def run_cost_regions(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    if args.outfile is None:
        host_filepath = Path(args.host)
        outfile = host_filepath.with_suffix(".cost-regions.pdf")
    else:
        outfile = args.outfile
    costscape.solve(recon_input, args.duplication_low, args.duplication_high, args.transfer_low, args.transfer_high,
                    outfile, args.log)
