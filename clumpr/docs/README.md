Welcome to the HMC CompBio DTL Reconciliation project! This code is for Python version 2.7.
Using this code, you can generate DTL reconciliations, compute the DTL reconciliation graph, and run various other computations on the reconciliation graph. Each piece of functionality has its own README:

* [Generate Reconciliation Graphs](README_graphs.md)
* [Calculate Diameters and Medians](README_diameter.md)
* [Compute the Pairwise Distance Vector](README_pdv.md)
* [Cluster MPR-space](README_cluster.md)

Dependencies (see `Pipfile`)
* `numpy`
* `Biopython` - interacting with `.newick` and other tree formats.
* `networkx` - drawing reconciliation graphs
* `pydot` - drawing reconciliation graphs
* `coverage` - unit testing
