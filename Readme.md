# HMC eMPRess Codebase for Spring 2020 Research

## Overview
eMPRess (in Python 3.7.4) supports the following functionality:
* DTL Reconciliation
* Costscape
* Pair distance Histogram
* Cluster MPR

## Running eMPRess

On the command line, the structure of the inputs are:    
* `python3.7 empress.py -fn < path to newick file> [--costscape --reconcile -- histogram --clumpr]`

For example, to run Costscape, you can do:
* `python3.7 empress.py -fn examples/heliconius.newick --costscape`

## Dependencies
eMPRess runs in Python 3.7.4 and requires the following packages:
* matplotlib
* biopython
* numpy
* networkx
