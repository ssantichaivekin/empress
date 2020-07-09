import argparse

def add_recon_input_args_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--host", metavar="<host_file>", required=True,
                        help="file path to the host tree")
    parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                        help="file path to the parasite tree")
    parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                        help="file path to the tip mapping")

def add_dtl_costs_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-d", "--dup-cost", type=float, metavar="<duplication_cost>",
                        default=2, help="cost incurred on each duplication event")
    parser.add_argument("-t", "--trans-cost", type=float, metavar="<transfer_cost>",
                        default=3, help="cost incurred on  each transfer event")
    parser.add_argument("-l", "--loss-cost", type=float, metavar="<loss_cost>",
                        default=1, help="cost incurred on each loss event")
