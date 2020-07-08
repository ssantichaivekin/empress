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
    parser = argparse.ArgumentParser("empress tool for duplication-transfer-loss maximum parsimony reconciliation")

    # Create subparsers and setup the subparsers
    subparsers = parser.add_subparsers(dest='command', help='Commands empress can run')

    cost_regions_parser = subparsers.add_parser('cost_regions',
                                                help="Find cost regions that give the same reconciliations")
    cli_commands.cost_regions.add_cost_regions_to_parser(cost_regions_parser)
    reconcile_parser = subparsers.add_parser('reconcile', help="Find the reconciliation graph given the dtl costs")
    cli_commands.reconcile.add_reconcile_to_parser(reconcile_parser)
    histogram_parser = subparsers.add_parser('cluster',
                                             help="Find pairwise distance histogram of reconciliation space")
    cli_commands.histogram.add_histogram_to_parser(histogram_parser)
    cluster_parser = subparsers.add_parser('cluster', help="Find cluster of reconciliations with same properties")
    cli_commands.cluster.add_cluster_to_parser(cluster_parser)

    # Determine which command we should run and run the correct command
    args = parser.parse_args()

    if args.command == "cost_regions":  # argparse - characters will be converted to _ characters
        cli_commands.cost_regions.run_cost_regions(args)
    elif args.command == "reconcile":
        cli_commands.reconcile.run_cost_regions(args)
    elif args.command == "histogram":
        cli_commands.histogram.run_cost_regions(args)
    elif args.command == "cluster":
        cli_commands.cluster.run_cost_regions(args)

if __name__ == "__main__":
    main()
