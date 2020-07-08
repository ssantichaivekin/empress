import argparse
import empress
from empress.reconcile import recongraph_tools


def add_reconcile_to_parser(reconcile_parser: argparse.ArgumentParser):
    # Read input files
    reconcile_parser.add_argument("--host", metavar="<host_file>", required=True,
                                  help="The path to the host tree file.")
    reconcile_parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                                  help="The path to the parasite tree file.")
    reconcile_parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                                  help="The path to the tip mapping file.")

    # Read dtl costs
    reconcile_parser.add_argument("-d", type=float, metavar="<duplication_cost>",
                                  default=2, help="Duplication cost")
    reconcile_parser.add_argument("-t", type=float, metavar="<transfer_cost>",
                                  default=3, help="Transfer cost")
    reconcile_parser.add_argument("-l", type=float, metavar="<loss_cost>",
                                  default=1, help="Loss cost")


def run_cost_regions(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    recongraph_tools.reconcile_noninter(recon_input, args.d, args.t, args.l)
