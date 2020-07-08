def add_cost_regions_to_parser(cost_regions_parser: argparse.ArgumentParser):
    # Read input files
    cost_regions_parser.add_argument("--host", metavar="<host_file>", required=True,
                                     help="The path to the host tree file.")
    cost_regions_parser.add_argument("--parasite", metavar="<parasite_file>", required=True,
                                     help="The path to the parasite tree file.")
    cost_regions_parser.add_argument("--mapping", metavar="<mapping_file>", required=True,
                                     help="The path to the tip mapping file.")

    # Read duplication/transfer/loss information
    cluster_parser.add_argument("-d", type=float, metavar="<duplication_cost>",
                                default=2, help="Duplication cost")
    cluster_parser.add_argument("-t", type=float, metavar="<transfer_cost>",
                                default=3, help="Transfer cost")
    cluster_parser.add_argument("-l", type=float, metavar="<loss_cost>",
                                default=1, help="Loss cost")