The main program for calculating diameters and medians is `DTLReconGraph.py`.

## How to use DTLReconGraph.py

### From the Command Line:

After typing `python DTLReconGraph.py`, enter the values for:

  * The name of the file in which the data are stored and
  * The costs of duplication, transfer, and loss, 
  
in that order. The data file should include: 
  * Two newick trees (formatted, for example, as ((C,D)B,E)A if A has children B and E and B has children C and D) on separate lines, with the species/host tree given first and the gene/parasite tree second, and
  * Mappings between all of the tips of the two trees (formatted, for example, c:C; d:D; e:E if c maps to C, d to D and e to E), with a different one on each line.

The output is:
  * Two Python dictionaries in the format {(parent, child):(parent, child, child 1 of child, child 2 of child):, ...}, where parent is a node in the tree, child is one of parent's children, and children 1 and 2 of child represent children of the child of parent (in other words, grandchildren of the parent) - one for each of the two trees used as input. This is essentially a dictionary representation of the two trees given as input;
  * A Python dictionary with mapping nodes as keys and lists of their event node children as values. This has the format {(gene node, species node): [(event string, resulting mapping node 1, resulting mapping node 2), minimum cost], ...}. The event string is 'D', 'T', 'L', 'C', or 'S', representing duplication, transfer, loss, contemporary event, and speciation, respectively. Lastly, the resulting mapping nodes are the mappings that are induced as a result of the given event;
  * The number of Maximum Parsimony Reconciliations for the given data set and costs, as an integer
  * A list of mapping nodes we could use to root the gene tree to produce a maximum parsimony reconciliation

### Via Interactive Mode:

`python -i DTLReconGraph.py` will access the code in interactive mode. From there, all major and helper functions will be available, however the two most important are DP and reconcile. 

#### DP

DP implements the algorithm given in the technical report titled "HMC CS Technical Report CS-2011-1: Faster Dynamic Programming Algorithms for the Cophylogeny Reconstruction Problem". Given host and parasite trees, tip mappings, and costs for duplication, transfer, and loss, DP returns the DTL maximum parsimony reconciliation graph as a dictionary, the total cost associated with the best reconciliation for the given D, T, and L costs, the number of reconciliations for the given trees and tip mappings, and a list of all possible mapping nodes for the root of the gene tree that could be used in an MPR (see the outputs discussed in the section on using this code from the command line for more detail on the output format).

#### Reconcile

Reconcile is the more practically useful function. Since the data are implemented as newick trees and mappings, reconcile utilizes a separate module that both handles getting the data from a file and reformatting the inputs. Reconcile reformats the species and gene trees to match the output format given in the section on running from the command line, and prints out these trees along with the reconciliation graph, the number of Maximum Parsimony Reconciliations, and a list of mappings of gene nodes onto species nodes that could produce an MPR.
