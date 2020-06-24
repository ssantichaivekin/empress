Welcome to the HMC CompBio DTL Reconciliation project! This code is for Python version 3.6
Using this code, you can generate DTL reconciliations, compute the DTL reconciliation graph, and run various other computations on the reconciliation graph. Each piece of functionality has its own README:

* [Generate Reconciliation Graphs](reconcile/README_graphs.md)
* [Calculate Diameters and Medians](reconcile/README_diameter.md)
* [Compute the Pairwise Distance Vector](histograms/README_pdv.md)
* [Cluster MPR-space](clustering/README_cluster.md)

Dependencies (see `Pipfile`)
* `numpy`
* `Biopython` - interacting with `.newick` and other tree formats.
* `networkx` - drawing reconciliation graphs
* `pydot` - drawing reconciliation graphs
* `coverage` - unit testing
