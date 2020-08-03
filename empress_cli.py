#!/usr/bin/env python3

# empress_cli.py
# Cat Ngo, April 2020
# Updated 6/1/2020 by RLH

import argparse

import cli_commands.cluster
import cli_commands.cost_regions
import cli_commands.histogram
import cli_commands.reconcile
import cli_commands.p_value

def main():
    parser = argparse.ArgumentParser(
        description="Empress tool for duplication-transfer-loss maximum parsimony reconciliation.",
        epilog="Show help for each command by running `python empress_cli.py <command> --help`",
    )

    # Create subparsers and setup the subparsers
    subparsers = parser.add_subparsers(dest='command', help='Commands empress can run', required=True)

    # Cost Regions
    cost_regions_description = "Find cost regions that give same maximum parsimony reconciliations."
    cost_regions_parser = subparsers.add_parser(
        'cost-regions', description=cost_regions_description, help=cost_regions_description.lower().rstrip('.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # print default value
    )
    cli_commands.cost_regions.add_cost_regions_to_parser(cost_regions_parser)

    # Reconcile
    reconcile_description = "Find maximum parsimony reconciliations given duplication, transfer, and loss costs."
    reconcile_parser = subparsers.add_parser(
        'reconcile', description=reconcile_description, help=reconcile_description.lower().rstrip('.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.reconcile.add_reconcile_to_parser(reconcile_parser)

    # Histogram
    histogram_description = "Find pairwise distance histogram of all reconciliations given duplication, transfer, " \
                            "and loss costs."
    histogram_parser = subparsers.add_parser(
        'histogram', description=histogram_description, help=histogram_description.lower().rstrip('.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.histogram.add_histogram_to_parser(histogram_parser)

    # Cluster
    cluster_description = "Find cluster of reconciliations with similar properties given duplication, transfer, " \
                          "and loss costs."
    cluster_parser = subparsers.add_parser(
        'cluster', description=cluster_description, help=cluster_description.lower().rstrip('.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # prints default values
    )
    cli_commands.cluster.add_cluster_to_parser(cluster_parser)

    # P Value
    p_value_description = "Test the hypothesis that the optimal reconciliation cost was obtained using " \
                          "a random mapping."
    p_value_parser = subparsers.add_parser(
            'p-value', description=p_value_description, help=p_value_description.lower().rstrip("."),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cli_commands.p_value.add_p_value_to_parser(p_value_parser)

    # Determine which command we should run and run it
    args = parser.parse_args()

    if args.command == "cost-regions":
        cli_commands.cost_regions.run_cost_regions(args)
    elif args.command == "reconcile":
        cli_commands.reconcile.run_reconcile(args)
    elif args.command == "histogram":
        cli_commands.histogram.run_histogram(args)
    elif args.command == "cluster":
        cli_commands.cluster.run_cluster(args)
    elif args.command == "p-value":
        cli_commands.p_value.run_p_value(args)


if __name__ == "__main__":
    main()
