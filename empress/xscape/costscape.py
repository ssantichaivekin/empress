#!/usr/bin/env python

# costscape.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013
# Updated 6/1/2020 by RLN:  Changed so that loss fixed at 1, x-axis is duplication, y-axis is transfer

# python libraries
import time

# xscape libraries
from empress import xscape
from empress.xscape import reconcile
from empress.xscape import plotcostsAnalytic as plotcosts

def solve(newick_data, transferMin, transferMax, dupMin, dupMax,
          outfile=None, log=False):
    print("Costscape %s" % xscape.PROGRAM_VERSION_TEXT)
    hostTree = newick_data.host_tree
    parasiteTree = newick_data.parasite_tree
    phi = newick_data.phi
    if outfile is None:
        display = True
    else:
        display = False
    print(outfile, display)

    print("Reconciling trees...")
    startTime = time.time()
    CVlist = reconcile.reconcile(parasiteTree, hostTree, phi,
                                 transferMin, transferMax, dupMin, dupMax)
    endTime = time.time()
    elapsedTime = endTime- startTime

    print("Elapsed time %.2f seconds" % elapsedTime)
    plotcosts.plotcosts(CVlist, transferMin, transferMax, dupMin, dupMax,
                        outfile=outfile,
                        log=log, display=display)
    if outfile:
        print("Output written to file: ", outfile)
    
#if __name__ == '__main__':
#    main()
