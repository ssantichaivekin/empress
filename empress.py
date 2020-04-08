#!/usr/bin/env python

# empress.py
# Cat Ngo, April 2020

import argparse

from newickFormatReader import getInput
from clumpr import HistogramMain, DTLReconGraph, ClusterMain
from xscape import costscape

def process_arg():
    parser = argparse.ArgumentParser("")
    parser.add_argument("-fn","--filename", required=True,
        help="The path to a .newick file with the input trees and tip mapping.")
    parser.add_argument("-rec", "--reconcile", dest='reconcile', 
        action= "store_true", help="Flag to run DTL Reconciliation")
    parser.add_argument("-cos", "--costscape", dest='costscape', 
        action= "store_true", help="Flag to run Costscape")
    parser.add_argument("-his", "--histogram", dest='histogram', 
        action= "store_true", help="Flag to run Pair Distance Histogram")
    parser.add_argument("-clu", "--clumpr", dest='clumpr', 
        action= "store_true", help="Flag to run Cluster MPR")
    return parser.parse_args()
    

def main():
    args = process_arg()
    newick_data = getInput(args.filename)
    if args.costscape:
        costscape.main(newick_data)
    if args.reconcile:
        DTLReconGraph.main(newick_data)
    if args.histogram:
        HistogramMain.main(args.filename, newick_data)
    if args.clumpr:
        ClusterMain.main(args.filename,newick_data)


if __name__ == "__main__": main()