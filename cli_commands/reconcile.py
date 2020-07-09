import argparse

import empress
from empress.reconcile import recongraph_tools
import cli_commands._shared_utils


def add_reconcile_to_parser(reconcile_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(reconcile_parser)
    cli_commands._shared_utils.add_dtl_costs_to_parser(reconcile_parser)

def run_reconcile(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    recongraph_tools.reconcile_noninter(recon_input, args.dup_cost, args.trans_cost, args.loss_cost)
