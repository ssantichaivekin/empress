#!/usr/bin/env python

# costscape.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013
# Updated 6/1/2020 by RLN:  Changed so that loss fixed at 1, x-axis is duplication, y-axis is transfer

# python libraries
import time

# xscape libraries
from empress import xscape
from empress.xscape import reconcile
from empress.xscape import plotcosts_analytic as plotcosts

def solve(newick_data, transferMin, transferMax, dupMin, dupMax, optional):
    print("Costscape %s" % xscape.PROGRAM_VERSION_TEXT)
    hostTree = newick_data.host_dict
    parasiteTree = newick_data.parasite_dict
    tip_mapping = newick_data.tip_mapping
    if optional.outfile == "":
        display = True
    else:
        display = optional.display

    print("Reconciling trees...")
    startTime = time.time()
    CVlist = reconcile.reconcile(parasiteTree, hostTree, tip_mapping, \
                                 transferMin, transferMax, dupMin, dupMax)
    endTime = time.time()
    elapsedTime = endTime- startTime
    print("Elapsed time %.2f seconds" % elapsedTime)
    plotcosts.plotcosts(CVlist, transferMin, transferMax, dupMin, dupMax, \
                        optional.outfile, \
                        optional.log, display)
    if optional.outfile != "":
        print("Output written to file: ", optional.outfile)
