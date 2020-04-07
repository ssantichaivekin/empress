import argparse

from newickFormatReader import getInput
from clumpr import HistogramMain, DTLReconGraph
from xscape.bin import costscape

def process_arg():
    parser = argparse.ArgumentParser("")
    parser.add_argument("-fn","--filename", metavar="<filename>", required=True,
        help="The path to a .newick file with the input trees and tip mapping.")
    parser.add_argument("-rec", "--reconcile", type = bool, dest=reconcile, 
        action= "store_true", help="Flag to run DTL Reconciliation")
    parser.add_argument("-cos", "--costscape", type = bool, dest=costscape, 
        action= "store_true", help="Flag to run Costscape")
    parser.add_argument("-his", "--histogram", type = bool, dest=histogram, 
        action= "store_true", help="Flag to run Pair Distance Histogram")
    parser.add_argument("-clu", "--clumpr", type = bool, dest=clumpr, 
        action= "store_true", help="Flag to run Cluster MPR")
    return parser.parse_args()
    

def main():
    args = process_arg()
    newick_data = getInput(args.filename)
    if parser.costscape:
        costscape.main(newick_data)
    if parser.histogram:
        HistogramMain.main(args.filename, newick_data)
    if parser.rec:
        DTLReconGraph.main(newick_data)


if __name__ == "__main__": main()