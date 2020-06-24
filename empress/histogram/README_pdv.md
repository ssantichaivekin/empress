The main program for computing the Pairwise Distance Vector for a reconciliation is `HistogramMain.py`. For computing aggregate statistics for an entire data set, use `HistogramNormal.py`

## How to use `HistogramMain.py`

`HistogramMain` computes the Pairwise Distance Vector for a given `.newick` file. The pairwise distance vector is a histogram where the x-axis is distance, and the y-axis is the number of MPR pairs at that distance. It is useful for determining the shape of MPR-space. A bimodal PDV can indicate the presence of multiple clusters, which would mean that a single MPR is not likely to represent MPR-space.

### CLI

* `--input` takes the path to a `.newick` file with the trees and the tip mapping. If no filename is specified for output, this file name (and path) will be used to generate paths for output files.

* `-d`, `-t`, `-l` specify the duplication, transfer, and loss costs respectively.

* `--histogram` specifies whether to generate a histogram. If a filename is provided, the histogram will be saved to that filename. Otherwise, a name related to the input filename is used. By default, the format is `.pdf`, but if the provided filename has a different extension, it will be saved as that format.

* `--xnorm` normalizes the x-axis of the PDV so that the distances range between 0 and 1 (normalized to the diameter of MPR-space).

* `--ynorm` normalizes the y-axis of the PDV so that the bar height is the frequency of MPR pairs at each distance rather than the number.

* `-omit_zeros` takes out zeroes from the PDV (which are always MPRs compared with themselves)

* `--cumulative` reports the number of MPRs at distance less than or equal to x rather than just equal to x.

* `--csv` saves the PDV to a `.csv` file. If a filename is provided, it will be saved there. Otherwise, a name related to the input filename is used. The CSV has two columns - the first column is the x-value in the histogram, and the second column is the y-value.

* `--stats` outputs various statistics about MPR-space.

* `--time` times and reports the running time of the PDV algorithm.

## How to use `HistogramNormal.py`

`HistogramNormal` computes aggregate statistics about an entire data set. It computes timing information for each file as well as some timing statistics. It also reports aggregate statistics about the histograms. Finally, it computes normality statistics on each file and sorts the files by normality of their PDV. All of these are printed out, so the standard usage is to pipe the output to a file for later analysis. As a note on the normality statistics, the distribution of distances for a roughly spherical MPR-space is not actually normal, but will score above a bimodal or otherwise strange PDV on standard normality statistics. Thus, sorting by the normality score is a good heuristic for finding which `.newick` files yield strange PDVs and which are more standard.

### CLI

* `--input` takes the path to a __folder__ of `.newick` files. It ignores non-`.newick` files in the specified path.

* `-d`, `-t`, `-l` as above.

* `--timeout` is how long a single tree file can run before timing out (in seconds).

* `--min-mprs` is the minimum number of MPRs a reconciliation must have to use it in aggregate statistics.

