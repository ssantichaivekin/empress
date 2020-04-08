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

def main(newick_data):
    print("Costscape %s" % xscape.PROGRAM_VERSION_TEXT)
    hostTree, parasiteTree, phi, = newick_data 
    switchLo, switchHi, lossLo, lossHi, outfile = \
        getInput.getInput(outputExtension = "pdf", allowEmptyOutfile=True)
    log = getInput.boolInput("Display in log coordinates? ")
    if outfile == "":
        display = True
    else:
        display = getInput.boolInput("Display to screen? ")

    print("Reconciling trees...")
    startTime = time.time()
    CVlist = reconcile.reconcile(parasiteTree, hostTree, phi, \
                                 switchLo, switchHi, lossLo, lossHi)
    endTime = time.time()
    elapsedTime = endTime- startTime
    print("Elapsed time %.2f seconds" % elapsedTime)

    plotcosts.plotcosts(CVlist, switchLo, switchHi, lossLo, lossHi, \
                        outfile, \
                        log, display)
    if outfile != "":
        print("Output written to file: ", outfile)
    
if __name__ == '__main__': main()
