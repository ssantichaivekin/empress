import argparse
from pathlib import Path
from matplotlib import pyplot as plt
import cli_commands._shared_utils
import empress

def add_p_value_to_parser(p_value_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(p_value_parser)
    cli_commands._shared_utils.add_dtl_costs_to_parser(p_value_parser)
    p_value_parser.add_argument("--outfile", metavar="<filename>",
                                help="Output the p-value test at the path provided. If no filename is "
                                "provided, outputs to a filename based on the input host file.")

def run_p_value(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    cost_suffix = ".pvalue.{}-{}-{}".format(args.dup_cost, args.loss_cost, args.trans_cost)
    if args.outfile is None:
        host_filepath = Path(args.host)
        outfile = host_filepath.with_suffix(cost_suffix + ".pdf")
    else:
        outfile = args.outfile
    recongraph = recon_input.reconcile(args.dup_cost, args.trans_cost, args.loss_cost)
    fig = recongraph.draw_stats()
    fig.savefig(outfile)
    plt.close(fig)
