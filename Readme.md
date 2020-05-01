# HMC eMPRess Codebase for Spring 2020 Research

## Overview
eMPRess (in Python 3.7.4) supports the following functionality:
* DTL Reconciliation - `reconcile`
* Costscape - `costscape`
* Pair-distance Histogram - `histogram`
* Cluster MPR - `clumpr`

## Running eMPRess

On the command line, the structure of the inputs are:    
* `python3.7 empress.py -fn <path to tree data file> <functionality>`

For example, to run Costscape with default parameters, you run:
* `python3.7 empress.py -fn examples/heliconius.newick costscape`

For specific parameters of each functionality, consult the list below:

## List of Parameters
Note: value in paranthesis denotes default value, asterik denotes boolean flags
### Costscape
* `-tl` : Transfer low value (1)
* `-th` : Transfer high value (5)
* `-ll` : Loss low value (1)
* `-lh` : Loss high value (5)
* `--outfile` : Name of output file. Must end in .pdf ("")
* `--log` : Set graph to log scale*
* `--display` : Display graph to screen*

For example, to run Costscape with switch low value of 2 and switch high value of 10 that saves to a file called `foo.pdf` display it in log scale, you run
* `python3.7 empress.py -fn examples/heliconius.newick costscape -sl 2 -sh 10 --outfile foo.pdf --log`

### DTL Reconciliation
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)

For example, to run DTL Reconciliation with duplication cost of 4, transfer cost of 2 and lost cost of 0, you run
* `python3.7 empress.py -fn examples/heliconius.newick costscape reconcile -d 4 -t 2 -l 0`

### Pair distance Histogram
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)
* `--histogram` : Name of output file. If no filename is provided, outputs to a filename based on the input tree data file
* `--xnorm` : Normalize the x-axis so that the distances range between 0 and 1*
* `--ynorm` : Normalize the y-axis so that the distances range between 0 and 1*
* `--omit-zeros` : Omit the zero column of the histogram, which will always be the total number of reconciliations*
* `--cumulative` : Make the histogram cumulative*
* `--csv` : Output the histogram as a .csv file at the path provided. If no filename is provided, outputs to a filename based on the input tree data file*
* `--stats` : Output statistics including the total number of MPRs, the diameter of MPR-space, and the average distance between MPRs*
* `--time` : Time the diameter algorithm*

For example, to run Pair-distance Histogram that outputs the histogram to `foo.pdf` and normalizes the y-axis, you run
* `python3.7 empress.py -fn examples/heliconius.newick histogram --histogram foo.pdf --y-axis`

### Cluster MPR
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)
* `-k` : Number of clusters
* `--median` : Print out medians of each cluster
* `--depth` : How far down the graph to consider event splits
* `--nmprs` : How many MPRs to consider
* `--pdv-vis` : Visualize the resulting clusters using the PDV*
* `--support-vis` : Visualize the resulting clusters using a histogram of the event supports*
* `--pdv` : Use the weighted average distance to evaluate clusters*
* `--support` : Use the weighted average event support to evaluate clusters*

For example, to run Cluster MPR that prints out the medians of each cluster with 4 MPRs using the weighted average event support, you run 
* `python3.7 empress.py -fn examples/heliconius.newick clumpr --median --nmprs 4 --support`

## Dependencies
eMPRess runs in Python 3.7.4 and requires the following packages:
* matplotlib
* biopython
* numpy
* networkx
