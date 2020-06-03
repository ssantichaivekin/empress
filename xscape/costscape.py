#!/usr/bin/env python

# costscape.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013

# python libraries
import time

# xscape libraries
try:
    import xscape
except ImportError:
    import sys
    print(sys.path)
    sys.path.append("..")
    import xscape
from xscape.commonAnalytic import *
from xscape.CostVector import *
from xscape import getInput
from xscape import reconcile
from xscape import plotcostsAnalytic as plotcosts

def solve(newick_data, switchLo, switchHi, lossLo, lossHi, optional):
    print("Costscape %s" % xscape.PROGRAM_VERSION_TEXT)
    hostTree = newick_data.host_tree
    parasiteTree = newick_data.parasite_tree
    phi = newick_data.phi
    if optional.outfile == "":
        display = True
    else:
        display = optional.display

    print("Reconciling trees...")
    startTime = time.time()
    CVlist = reconcile.reconcile(parasiteTree, hostTree, phi, \
                                 switchLo, switchHi, lossLo, lossHi)
    endTime = time.time()
    elapsedTime = endTime- startTime
    print("Elapsed time %.2f seconds" % elapsedTime)

    plotcosts.plotcosts(CVlist, switchLo, switchHi, lossLo, lossHi, \
                        optional.outfile, \
                        optional.log, display)
    if optional.outfile != "":
        print("Output written to file: ", optional.outfile)
    
if __name__ == '__main__': main()
