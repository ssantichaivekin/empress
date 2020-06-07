#!/usr/bin/env python

# empress.py
# Cat Ngo, April 2020
# Updated 6/1/2020 by RLH
# Updated 6/5/2020 by YJW

# python libraries
import argparse
import importlib
import sys

# empress libraries
import empress
from empress import commands

#==========================================================
# parser

def parse_command():
    """parse command"""

    parser = argparse.ArgumentParser(
        usage="%(prog)%s [ -h | --help] <command> [<args>]",
        
        description=
"""\
%(prog)s is a phylogenetic program for DTL reconciliation.

These empress commands used in various situations:

clumpr      Cluster MPRs
costscape   Find MPR landscapes across ranges of event costs
reconcile   Find an MPR
histogram   Display histogram of pairwise distances between MPRs

See '%(prog)s <command> -h' to read about a specific subcommand.
""",

    epilog=
"""\
""",

    formatter_class=argparse.RawDescriptionHelpFormatter,

    add_help=False)

    parser.add_argument("-h", "--help", action="help",
                        help=argparse.SUPPRESS)
    parser.add_argument("command", help=argparse.SUPPRESS)

    # display help if no command
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        parser.exit(1)

    args = parser.parse_args(sys.argv[1:2]) # exclude rest of args
    if args.command not in commands.__all__:
        parser.error("'${args.command}' is not an empress command. See 'empress.py --help'")
    return args.command


#==========================================================
# main function

def main():
    """main"""

    # parse arguments
    command = parse_command()

    # run sub-command
    mod = importlib.import_module(f"empress.commands.{command}")
    mod.run()

if __name__ == "__main__":
    sys.exit(main())
