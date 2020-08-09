# HMC Empress Codebase for Spring 2020 Research

## Overview
Empress supports the following functionality:
* DTL Reconciliation - `reconcile`
* Costscape - `costscape`
* Pair-distance Histogram - `histogram`
* Cluster MPR - `clumpr`

## Install empress 

The empress developer team seeks to provide users with a smooth and straightforward installation experience. We are packaging empress as an application that can be installed and run with one click. We will provide links below when the installers become available. If you cannot find an installer for your platform, please use the [Install empress for development](#install-empress-for-development) instruction below.

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
Empress uses python version 3.7 and has not been set up to run on higher versions. You can check whether you have `python3.7` installed on your computer by typing the following command in the terminal:
```bash
python3.7 --version
```
If the command gives you a python version (say, `3.7.8`) it means you have `python3.7` installed. If it says `command not found`, please follow the steps below to install `python3.7`.

If you don't have `python3.7` installed in your computer, you can download the installer from [python.org website](https://www.python.org/downloads/release/python-378/). For macOS, choose the macOS 64-bit installer. For Windows, choose the Windows x86-64 executable installer.  There is currently no python 3.7 installer for linux on python.org. Alternatively, you can download python3.7 from [Anaconda website](https://www.anaconda.com/products/individual#Downloads) or from your favorite package manager tool such as `apt-get`.

### Install pipenv package manager
Empress uses [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) as its package manager to install dependencies. You can install pipenv using the terminal and typing in the command:
```bash
pip3 install pipenv  # use python3 pip to install pipenv
```

### Download empress repository
If you have `git` installed, you can download empress by typing in the terminal
```bash
cd folder-you-want-to-install  # go to the folder you want to download empress to
git clone https://github.com/ssantichaivekin/empress.git
```

If you don't have `git` installed, you can [click on this link to download the zip file](https://github.com/ssantichaivekin/empress/archive/master.zip). Name the zip file `empress` instead of `empress-master` and unzip it into the location of your choice.

### Use pipenv to install dependencies
Go to terminal, run:
```bash
cd empress  # go to the empress folder you downloaded from last step
pipenv install  # create virtual environment and install dependencies
pipenv shell  # enter the virtual environment with dependencies installed
```
Every time you restart the terminal, make sure you run `pipenv shell` before running empress script.

## Run graphical user interface (gui)
Make sure you have already run `pipenv shell` in the empress folder. (Note that empress will not work if you run `pipenv shell` outside of the empress folder and then change the directory to the empress folder afterward.)

In the empress folder, type:
```bash
python empress_gui.py
```

## Run empress command line interface (cli)

To see help, run:
```bash
python empress_cli.py --help
```

To see help with using a given command, run:
```bash
python empress_cli.py <command> --help
```

On the command line, the structure of the inputs is:    
```bash
python empress_cli.py <command> hostfile parasitefile mappingfile <additional-arguments>
```

For example, to run cost-regions with default parameters, you run:
```bash
python empress_cli.py cost-regions hostfile parasitefile mappingfile <additional-arguments>
```

Note that to run cluster, there is an additional positional input: the number of clusters:
```bash
python empress_cli.py cluster hostfile parasitefile mappingfile number_of_clusters <additional-arguments>
```

For specific parameters of each functionality, consult the list below:

## List of Parameters

### Cost-Regions
* `-dl <duplication_low>`, `--duplication-low <duplication_low>`:  duplication low floating point value for cost regions viewer window (default: 1.0)
* `-dh <duplication_high>`, `--duplication-high <duplication_high>`: duplication high floating point value for cost regions viewer window (default: 5.0)
* `-tl <transfer_low>`, `--transfer-low <transfer_low>`: transfer low floating point value for cost regions viewer window (default: 1.0)
* `-th <transfer_high>`, `--transfer-high <transfer_high>`: transfer high floating point value for cost regions viewer window (default: 5.0)
* `--outfile <output_file>` : path to output file ending with .pdf, (default: generated filename at same location as the host file)
* `--log` : set both axes to use log scale (default: False)

For example, the following example runs Cost-Regions with duplication low value of 0.5, duplication high value of 10, transfer low value of 0.5, 
and transfer high value of 10, that saves to a file called `costscape-example-img.pdf` at the current location with axes displayed in log scale.
```bash
$ python empress_cli.py cost-regions examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                     examples/heliconius_mapping.mapping -tl 0.5 -th 10 -dl 0.5 -dh 10 \
                                     --outfile costscape-example-img.pdf --log
```

### DTL Reconciliation
* `-d <duplication_cost>`, `--dup-cost <duplication_cost>`: floating point cost incurred on each duplication event (default: 2.0)
* `-t <transfer_cost>`, `--trans-cost <transfer_cost>`: floating point cost incurred on each transfer event (default: 3.0)
* `-l <loss_cost>`, `--loss-cost <loss_cost>`: floating point cost incurred on each loss event (default: 1.0)
* `--csv <filename>` : output the reconciliation as a .csv file at the path provided. If no filename is provided, outputs to a filename based on the input host file
* `--graph` : instead of outputting a random median, output the entire reconciliation graph (default: False)

For example, to run DTL Reconciliation with duplication cost of 4, transfer cost of 2 and lost cost of 1, you run
```bash
$ python empress_cli.py reconcile examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                  examples/heliconius_mapping.mapping -d 4 -t 2 -l 1
```
Outputs a `.csv` file that enumerates the events and mappings for a median MPR. Each row of this table has an entry corresponding to a mapping between a parasite node and a gene node, and an event associated with that node. It has the folloing items in order: parasite node, host node, event type, node frequency, event frequency. The node frequency is the frequency with which that parasite is mapped to that host among all MPRs. The event frequency is the frequency with which that specific event occurs.

### Pairwise Distance Histogram
* `-d <duplication_cost>`, `--dup-cost <duplication_cost>`: floating point cost incurred on each duplication event (default: 2.0)
* `-t <transfer_cost>`, `--trans-cost <transfer_cost>`: floating point cost incurred on each transfer event (default: 3.0)
* `-l <loss_cost>`, `--loss-cost <loss_cost>`: floating point cost incurred on each loss event (default: 1.0)
* `--histogram-pdf <filename>`:  output the histogram pdf image at the path provided. If no filename is provided, outputs to a filename based on the input host file
* `--xnorm`: normalize the x-axis so that the distances range (default: False)
* `--ynorm`: normalize the y-axis so that the histogram is a probability distribution (default: False)
* `--omit-zeros`:  omit the zero column of the histogram, which will always be the total number of reconciliations (default: False)
* `--cumulative`:  make the histogram cumulative (default: False)
* `--csv <filename>`: output the histogram as a .csv file at the path provided. If no filename is provided, outputs to a filename based on the input host file (default: unset)
* `--stats`: output statistics including the total number of MPRs, the diameter of MPR-space, and the average distance between MPRs (default: False)
* `--time`: time the diameter algorithm (default: False)

For example, to run Pairwise Distance Histogram that outputs a csv file at `histogram_example_output_csv.csv`, outputs a histogram to `histogram_example_output_img.pdf` and normalizes the y-axis, you run
```bash
$ python empress_cli.py histogram examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                  examples/heliconius_mapping.mapping --csv histogram_example_output_csv.csv 
-                                 -histogram-pdf histogram_example_output_img.pdf --ynorm
```
CSV output has rows with two values each. The first value on each row is the distance (measured using the symmetric set difference between the event sets), and the second value is the number of MPR pairs that are that far apart from each other.

### Clustering
* `-d <duplication_cost>`, `--dup-cost <duplication_cost>`: floating point cost incurred on each duplication event (default: 2.0)
* `-t <transfer_cost>`, `--trans-cost <transfer_cost>`: floating point cost incurred on each transfer event (default: 3.0)
* `-l <loss_cost>`, `--loss-cost <loss_cost>`: floating point cost incurred on each loss event (default: 1.0)
* `--median`: whether or not to print out medians for each cluster (default: False)
* `--depth <tree_depth>`: how far down to split the graph before clustering 
* `--n-split <splits>` : find at least n splits before combining the splits
* `--pdv-vis` : visualize the resulting clusters using the Pairwise Distance (default: False)
* `--support-vis` : visualize the resulting clusters using event supports (default: False)
* `--pdv` : use the weighted average distance to evaluate clusters (default: False)
* `--support` : use the weighted average event support to evaluate clusters (default: False)

For example, to find at least 8 distinct parts of reconciliation-space before merging them into clusters, use `--n-splits 8`. The clusters are merged based on a cluster-distance that is calculated either using the average event support or the pairwise distance. To use the event support use `--support`. Finally, to get the median reconciliation of each of the three clusters, use `--median`. Putting it all together, the full command is
```bash
$ python empress_cli.py cluster examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                examples/heliconius_mapping.mapping 3 --median --n-splits 8 --support
```

### P-Value Histogram
* `-d <duplication_cost>`, `--dup-cost <duplication_cost>`: floating point cost incurred on each duplication event (default: 2.0)
* `-t <transfer_cost>`, `--trans-cost <transfer_cost>`: floating point cost incurred on each transfer event (default: 3.0)
* `-l <loss_cost>`, `--loss-cost <loss_cost>`: floating point cost incurred on each loss event (default: 1.0)
* `--outfile`: output the p-value test drawing at the path provided. If no filename is provided, outputs to a filename based on the input host file.
* `--n-samples` : the number of random tip mappings to sample (default: 100)

This tests the hypothesis that the optimal cost was obtained by a random tip mapping by sampling random tip mappings and checking the cost. The output is a histogram that shows the distribution of scores from random mappings, the score from the known mapping, and the p-value.
```bash
$ python empress_cli.py p-value examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                examples/heliconius_mapping.mapping -d 4 -t 2 -l 1 --n-samples 200
```

### Tanglegram
* `--outfile` : output the tanglegram drawing at the path provided. If no filename is provided, outputs to a filename based on the input host file.

View a tanglegram of the given files, showing the tip mapping.
```bash
$ python empress_cli.py tanglegram examples/heliconius_host.nwk examples/heliconius_parasite.nwk \
                                   examples/heliconius_mapping.mapping
```
