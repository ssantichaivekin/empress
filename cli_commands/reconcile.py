import argparse

import empress
from empress.reconcile import recongraph_tools
import cli_commands._shared_utils


def add_reconcile_to_parser(reconcile_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(reconcile_parser)
    cli_commands._shared_utils.add_dtl_costs_to_parser(reconcile_parser)
    reconcile_parser.add_argument("--csv", metavar="<filename>", nargs=1,
            help="Output the reconciliation as a .csv file at the path provided. "
            "If no filename is provided, outputs to a filename based on the input host file.")
    reconcile_parser.add_argument("--graph", action="store_true",
            help="Instead of outputting a random median, output the entire reconciliation graph.")
    

def run_reconcile(args):
    if args.graph:
        command_str = "recon_graph"
    else:
        command_str = "recon"
    cli_commands._shared_utils.set_csv_path(args, command_str)
    print("Output to {}".format(args.csv))
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    recon_graph = recon_input.reconcile(args.dup_cost, args.trans_cost, args.loss_cost)
    if args.graph:
        recon_graph.export_csv(args.csv)
    else:
        median = recon_graph.median()
        median.export_csv(args.csv)
    print("Number of optimal reconciliations: {}".format(recon_graph.n_recon))
