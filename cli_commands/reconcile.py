import argparse

import empress
from empress.reconcile import recongraph_tools
import cli_commands._shared_utils


def add_reconcile_to_parser(reconcile_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(reconcile_parser)
    cli_commands._shared_utils.add_dtl_costs_to_parser(reconcile_parser)

def run_reconcile(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    recon_graph = recon_input.reconcile(args.dup_cost, args.trans_cost, args.loss_cost)
    recon_graph.export_csv("foo.csv")
    out = [recon_input.host_dict, recon_input.parasite_dict,
            recon_graph.recongraph, recon_graph.n_recon, recon_graph.roots]
    for o in out:
        print(o)
