# HMC Empress Codebase for Spring 2020 Research

## Overview
Empress supports the following functionality:
* DTL Reconciliation - `reconcile`
* Costscape - `costscape`
* Pair-distance Histogram - `histogram`
* Cluster MPR - `clumpr`

## Install empress 

Empress developer team wishes users a smooth and straightforward installation experience. We are packaging empress as an application that can be installed and run with one click. We will provide a link below when the installers becomes available. If you cannot find an installer for your platform, please use the [Install empress for development](#install-empress-for-development) instruction below.

Graphical User Interface:
- macOS: unavailable
- linux: unavailable
- windows: unavailable

Command Line Interface:
- macOS: unavailable
- linux: unavailable
- windows: unavailable

## Install empress for development

### Install python
Empress uses python version 3.7 and has not been set up to run on higher versions. If you don't have python3.7 installed in your computer, you can download the installer from [python.org website](https://www.python.org/downloads/release/python-378/). For macOS, choose the macOS 64-bit installer. For Windows, choose the Windows x86-64 executable installer. I could not find the installer for linux on python.org. Alternatively, you could download python3.7 from [Anaconda website](https://www.anaconda.com/products/individual#Downloads) or from your favorite package manager tool such as `apt-get`.

### Install pipenv package manager
Empress uses [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) as its package manager to install dependencies. You can install pipenv by going to the terminal and type in the command:
```bash
pip3 install pipenv  # use python3 pip to install pipenv
```

### Download empress repository
If you have `git` installed, you can download empress by typing in terminal
```bash
cd folder-you-want-to-install  # go to the folder you want to downlaod empress to
git clone https://github.com/ssantichaivekin/empress.git
```

If you don't have `git` installed, you can [click on this link to download the zip file](https://github.com/ssantichaivekin/empress/archive/master.zip). Name the zip file `empress` instead of `empress-master` and unzip it to a location you want.

### Use pipenv to install dependencies
Go to terminal, run:
```bash
cd empress  # go to the empress folder you downloaded from last step
pipenv install  # create virtual environment and install dependencies
pipenv shell  # enter the virtual environment with dependencies installed
```
Every time you restart the terminal, make sure you run `pipenv shell` before running empress script.

## Run graphical user interface (gui)
Make sure you have already run `pipenv shell` in the empress folder. Note this empress will not work if you run `pipenv shell` outside of empress folder and then changing directory to empress folder afterward.

In the empress folder, type:
```bash
python empress_gui.py
```

## Run empress command line interface (cli)

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
python empress_cli.py cost-regions hostfile parasitefile mappingfile 
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
$ python empress_cli.py cost-regions examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
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