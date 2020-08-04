import argparse
from pathlib import Path

def add_recon_input_args_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("host", metavar="<host_file>",
                        help="file path to the host tree")
    parser.add_argument("parasite", metavar="<parasite_file>",
                        help="file path to the parasite tree")
    parser.add_argument("mapping", metavar="<mapping_file>",
                        help="file path to the tip mapping")

def add_dtl_costs_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-d", "--dup-cost", type=float, metavar="<duplication_cost>",
                        default=2, help="cost incurred on each duplication event")
    parser.add_argument("-t", "--trans-cost", type=float, metavar="<transfer_cost>",
                        default=3, help="cost incurred on  each transfer event")
    parser.add_argument("-l", "--loss-cost", type=float, metavar="<loss_cost>",
                        default=1, help="cost incurred on each loss event")

def set_csv_path(args, command_str):
    fname = Path(args.parasite)
    cost_suffix = ".{}.{}-{}-{}".format(command_str, args.dup_cost, args.trans_cost, args.loss_cost)
    if args.csv is None:
        args.csv = fname.with_suffix(cost_suffix + ".csv")
    # If args.csv was set, make sure it's a .csv file
    else:
        p = Path(args.csv)
        assert p.suffix == ".csv"
