import argparse
from pathlib import Path
from matplotlib import pyplot as plt

import empress
import cli_commands._shared_utils

def add_tanglegram_to_parser(tanglegram_parser: argparse.ArgumentParser):
    cli_commands._shared_utils.add_recon_input_args_to_parser(tanglegram_parser)
    tanglegram_parser.add_argument("--outfile", metavar="<filename>",
                                help="Output the tanglegram at the path provided. If no filename is "
                                "provided, outputs to a filename based on the input host file.")

def run_tanglegram(args):
    recon_input = empress.ReconInputWrapper.from_files(args.host, args.parasite, args.mapping)
    suffix = ".tanglegram"
    if args.outfile is None:
        host_filepath = Path(args.host)
        outfile = host_filepath.with_suffix(suffix + ".pdf")
    else:
        outfile = args.outfile
    fig = recon_input.draw()
    fig.savefig(outfile)
    plt.close(fig)
