'''
This demo demonstrates how you would use the reconciliation graph visualizer
written by me and Dennis.
'''

import DTLReconGraph # for creating a reconciliation graph
import ReconciliationVisualization # for visualization

# Since we currently have no way of storing reconciliation graph in a file,
# we generate it every time when we run the algorithm
# create a reconciliation graph from file
result = DTLReconGraph.reconcile("./newickSample/size5/test-size5-no700.newick", 2, 4, 2)
# the result is a five-tuple host, paras, graph, num_recon, best_roots
# we only want the reconciliation graph, which is the third item
# in the tuple
host, paras, graph, num_recon, best_roots = result
# this visualize the graph and save it at './sampleVis700.png'
ReconciliationVisualization.visualizeAndSave(graph, './sampleVis700.png')

