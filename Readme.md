# HMC eMPRess Codebase for Spring 2020 Research

## Overview
eMPRess supports the following functionality:
* DTL Reconciliation - `reconcile`
* Costscape - `costscape`
* Pair-distance Histogram - `histogram`
* Cluster MPR - `clumpr`

## Installing Dependencies
The package uses [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) to install dependencies. Please refer to the Pipenv website on how to install pipenv.

On the command line, run:
```bash
pipenv install # create virtual environment and install dependencies
pipenv shell # enter the virtual environment with dependencies installed
```
Every time you restart the terminal, make sure you run `pipenv shell` before running empress script.

## Running eMPRess

To see help, run:
```bash
python empress_cli.py --help
```

On the command line, the structure of the inputs are:    
```bash
python empress_cli.py <command> hostfile parasitefile mappingfile 
```

For example, to run Costscape with default parameters, you run:
```bash
python empress_cli.py cost_regions hostfile parasitefile mappingfile 
```

For specific parameters of each functionality, consult the list below:

## List of Parameters
Note: value in parenthesis denotes default value, asterisk denotes boolean flags
### Costscape
* `-dl` : Duplication low value (1)
* `-dh` : Duplication high value (5)
* `-tl` : Transfer low value (1)
* `-th` : Transfer high value (5)
* `--outfile` : Name of output file. Must end in .pdf ("")
* `--log` : Set graph to log scale*
* `--display` : Display graph to screen*


For example, the following example runs Costscape with duplication low value of 0.5, duplication high value of 10, transfer low value of 0.5, 
and transfer high value of 10, that saves to a file called `foo.pdf` display it in log scale.
```bash
$ python empress_cli.py cost_regions examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                     examples/heliconius_mapping.mapping -tl 0.5 -th 10 -dl 0.5 -dh 10 \
                                     --outfile costscape-example-img.pdf --log
```

### DTL Reconciliation
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)

For example, to run DTL Reconciliation with duplication cost of 4, transfer cost of 2 and lost cost of 0, you run
```bash
$ python empress_cli.py reconcile examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                  examples/heliconius_mapping.mapping -d 4 -t 2 -l 0
```

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

For example, to run Pair-distance Histogram that outputs a csv file at `foo.csv`, outputs a histogram to `bar.pdf` and normalizes the y-axis, you run
```bash
$ python empress_cli.py histogram examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                  examples/heliconius_mapping.mapping -csv foo.csv --histogram bar.pdf --ynorm
```

### Cluster MPR
* `-d` : Duplication cost (2)
* `-t` : Transfer cost (3)
* `-l` : Lost cost (1)
* `-k` : Number of clusters
* `--median` : Print out medians of each cluster
* `--depth` : How far down to split the graph before clustering
* `--nsplits` : As an alternative to passing the depth directly, split the reconciliation graph into at least n distinct pieces before merging
* `--pdv-vis` : Visualize the resulting clusters using the PDV*
* `--support-vis` : Visualize the resulting clusters using a histogram of the event supports*
* `--pdv` : Use the weighted average distance to evaluate clusters*
* `--support` : Use the weighted average event support to evaluate clusters*

For example, to find at least 8 distinct parts of reconciliation-space before merging them into clusters, use `--nsplits 8`. To merge those splits into three clusters, use `-k 3`. The clusters are merged based on a cluster-distance that is calculated either using the average event support or the pairwise distance. To use the event support use `--support`. Finally, to get the median reconciliation of each of the three clusters, use `--median`. Putting it all together, the full command is
```bash
$ python empress_cli.py cluster examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                examples/heliconius_mapping.mapping clumpr 3 --median --n-splits 8 --support
```