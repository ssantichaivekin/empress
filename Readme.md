# HMC eMPRess Codebase for Spring 2020 Research

## Overview
eMPRess (in Python 3.7.4) supports the following functionality:
* DTL Reconciliation - `reconcile`
* Costscape - `costscape`
* Pair distance Histogram - `histogram`
* Cluster MPR - `clumpr`

## Running eMPRess

On the command line, the structure of the inputs are:    
* `python3.7 empress.py -fn <path to newick file> <functionality>`

For example, to run Costscape with default parameters, you run:
* `python3.7 empress.py -fn examples/heliconius.newick costscape`

For specific parameters of each functionality, consult the list below:

## List of Parameters
Note: value in paranthesis denotes default value
### Costscape
* `-sl` : Switch low value (1)
* `-sh` : Switch high value (5)
* `-tl` : Transfer low value (1)
* `-th` : Transfer high value (5)
* `--outfile` : Name of output file. Must end in .pdf ("")
* `--log` : Set graph to log scale
* `--display` : Display graph to screen 

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
* `--histogram` : Name of output file

### Cluster MPR
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)
* `-k` : Number of clusters
* `--median` : Print out medians of each cluster

[NOTE: Currently not comprehensive for histogram and clumpr, but you can run -h flag for more info]

## Dependencies
eMPRess runs in Python 3.7.4 and requires the following packages:
* matplotlib
* biopython
* numpy
* networkx
