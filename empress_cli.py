#!/usr/bin/env python3

# empress_cli.py
# Cat Ngo, April 2020
# Updated 6/1/2020 by RLH

import argparse

import cli_commands.cluster
import cli_commands.cost_regions
import cli_commands.histogram
import cli_commands.reconcile


def main():
    parser = argparse.ArgumentParser(
        description="Empress tool for duplication-transfer-loss maximum parsimony reconciliation.",
        epilog="Show help for each command by running `python empress_cli.py <command> --help`",
    )

    # Create subparsers and setup the subparsers
    subparsers = parser.add_subparsers(dest='command', help='Commands empress can run')

    cost_regions_parser = subparsers.add_parser(
        'cost_regions',
        description="Find cost regions that give same maximum parsimony reconciliations.",
        help="find cost regions that give same maximum parsimony reconciliations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # print default value
    )
    cli_commands.cost_regions.add_cost_regions_to_parser(cost_regions_parser)

    reconcile_parser = subparsers.add_parser(
        'reconcile',
        description="Find maximum parsimony reconciliations given duplication, transfer, and loss costs.",
        help="find maximum parsimony reconciliations given duplication, transfer, and loss costs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.reconcile.add_reconcile_to_parser(reconcile_parser)

    histogram_parser = subparsers.add_parser(
        'histogram',
        description="Find pairwise distance histogram of all reconciliations given duplication, transfer, and loss costs.",
        help="find pairwise distance histogram of all reconciliations given duplication, transfer, and loss costs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.histogram.add_histogram_to_parser(histogram_parser)

    cluster_parser = subparsers.add_parser(
        'cluster',
        description="Find cluster of reconciliations with similar properties given duplication, transfer, and loss costs.",
        help="find cluster of reconciliations with similar properties given duplication, transfer, and loss costs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.cluster.add_cluster_to_parser(cluster_parser)

    # Determine which command we should run and run it
    args = parser.parse_args()

    if args.command == "cost_regions":  # argparse automatically converts "-" to "_"
        cli_commands.cost_regions.run_cost_regions(args)
    elif args.command == "reconcile":
        cli_commands.reconcile.run_cost_regions(args)
    elif args.command == "histogram":
        cli_commands.histogram.run_cost_regions(args)
    elif args.command == "cluster":
        cli_commands.cluster.run_cost_regions(args)


if __name__ == "__main__":
    main()
