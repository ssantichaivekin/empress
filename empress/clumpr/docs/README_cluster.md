The main program for computing a clustering of the MPR-space is `ClusterMain.py`. To compute aggregate statistics over an entire data set, use `ClusterAgg.py`

## How to use `ClusterMain.py`

`ClusterMain` computes multiple reconciliation graphs for a given `.newick` file. It starts with the original reconciliation graph obtained in the usual way, then splits this graph at a given depth level and merges those graphs until the desired number of clusters remain, each time merging the graphs that optimizes some objective function. Currently, two objectives are available: event support and pairwise distance. If event support is chosen, the clustering algorithm will attempt to maximize the averages event support of the clusters (weighted by the number of MPRs in each). Pairwise distance means that it minimizes the weighted average of the pairwise distance among the clusters.

### CLI

* `--input` specifies the input file, which should be a `.newick` file. If visualization is used, the visualization files will be saved to files with matching names to the input file in the same folder as it.

* `-d`, `-t`, `-l` specify the duplication, transfer, and loss costs.

* `-k` is the number of final desired clusters.

* `--support` or `--pdv` specifies the objective function, the average event support or average pairwise distance respectively.

* `--depth` or `--nmprs` specify how to choose the depth. `--depth` explicitly specifies how far down to go whereas `--nmprs` specifies a number of splits to start with, and goes down to the first depth level that yields at least that many splits. When comparing statistics across multiple data, using `--nmprs` gives a more fair comparison since the initial choices of events may be placed farther down in one of the graphs. When looking at a single `.newick` file, the approach that makes the most sense is to explicitly increase depth until the improvement flatlines, at which point the important events have probably been separated by the algorithm.

* `--pdv-vis` or `--support-vis` specify a visualization type. If neither is used, no visualization will be generated. `--pdv-vis` generates the Pairwise Distance Vector for the original reconciliation graph and for each of the clusters found. `--support-vis` generates a histogram of event supports for the original recon graph and each cluster.

* `--medians` prints out a random (uniformly sampled) median reconciliation for each cluster. The format is specified in a comment at the top of `DTLMedian.py` :(

## How to use `ClusterAgg.py`

`ClusterAgg` generates aggregate statistics and plots regarding clustering for an entire set of `.newick` files.

### CLI

* `--input` is a path to a __folder__ of `.newick` files, or a path to a pre-computed data file (generated using `--output`). If a folder, it will automatically look for only `.newick` files, so it does not matter if there are any extraneous files in the folder.

* `-d`, `-t`, `-l` as above

* `k` as above

* `--support` or `--pdv` as above

* `--depth` or `--nmprs` as above

* `--output` specifies a file to store the output. This is useful when generating multiple types of plot from the same data, debugging the script, or when looking at certain characteristics of the data. Note that the saved data for a given analysis only works with that analysis. Output files should be named accordingly so that it is easy to remember which data belongs with which analysis.

Note that some of these parameters may not be used in certain of the tests. For example `--nmprs` is ignored when doing the sensitivity to N analysis because that test analyzes the clustering for multiple values of N.

#### Analyses

* `--s1s2` clusters according to a single objective function and then evaluates on both so that the two evaluations can be correlated. This serves as a way to measure the similarity between two objective functions: If theimprovement from one objective is highly correlated with the improvement from the other objective, then each objective can largely substitute for the other.

* `--ni` determines the sensitivity to the value of N, the number of initial clusters. This is useful for understanding what the best value of N is.

* `--ki` shows how improvement changes with the value of K, the number of final clusters. This data can be useful for determining a good value of K.

* `--absolute` is a flag that can optionally be included with `--ki`. Instead of showing the relative improvement (which compares k+1 clusters to k clusters at each value of k), it shows absolute improvement (which compares k clusters to the original unclustered reconciliation graph).

* `--mpri` shows how improvement (1 cluster to 2 clusters) varies with the number of MPRs.

* `--time` determines aggregate timing information and computes how the running time varies with the number of MPRs.

## How to Add an Objective

To add a new objective function (we will refer to the objective by name as X for now), four things need to be done:

* Add a `mk_X_score` function to `ClusterUtil.py`. For reference, use the `mk_support_score` and `mk_pdv_score` functions in that file. It should take in the species tree, gene tree, and gene root as parameters, and return a function that takes a graph and returns a number. The clustering algorithm uses gradient descent, so make sure that X is "good" when minimized. If X is good when maximized (like event support), you can use the negative.

* Add a `calc_improvement_X` to `ClusterUtil.py`. For reference, use `calc_improvement_pdv` or `calc_improvement_support` from the same file. In general, if X is maximized, then this will be the ratio of the score for the larger number of clusters to the score for the smaller number of clusters. If it is to be minimized, then it will be the opposite ratio. If this is how improvement of X is defined, you may use one of the existing functions, but you may also make this more complicated if you have some other idea of what constitutes an increase in X.

* Add a command line option for X to the `parse_args` function in `ClusterAgg.py` and/or `ClusterMain.py`. Add it to the `score` mutually exclusive group.

* Edit the `choose_*` family of functions in `ClusterAgg.py`. These functions set up graph titles, filenames, etc. for each objective function. For `ClusterMain`, edit the top of `main` where `mk_score` is set to use your `mk_X_score` from `ClusterUtil.py` when the command line option you created is set.

