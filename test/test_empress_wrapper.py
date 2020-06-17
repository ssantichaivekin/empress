# TODO: To be converted to automated tests
# https://github.com/ssantichaivekin/eMPRess/issues/32
import empress
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk

# Read Reconciliation Input
recon_input = empress.read_input("./examples/test-size5-no924.newick")

cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)
cost_regions.draw_to_file('./examples/cost_poly.png')

# Compute ReconGraph
recongraph = empress.reconcile(recon_input, 1, 1, 1)
print(recongraph.n_recon)

# Draw Reconciliation Graph to file
recongraph.draw_graph_to_file("./recongraph_example.pdf")
recongraph.draw_to_file("./recongraph_hist_example.pdf")

# Find median
median_reconciliation = recongraph.median()

# Get Reconciliation figure object for visualization
# Note that you can use this for tkinter
fig = median_reconciliation.draw()
# Save Reconciliation visualization to file
median_reconciliation.draw_to_file("./recon_draw_example.png")

# Separate one ReconGraph to three ReconGraph
# clusters is a list of ReconGraph
clusters = recongraph.cluster(3)

# Draw three histograms on one figure
# fig: plt.Figure
fig, axs = plt.subplots(1, len(clusters))
for i in range(len(clusters)):
    clusters[i].draw_on(axs[i])
# Note that you could also display this figure in tkinter
fig.savefig("./figure_of_three_his_example.png")

# Read this example and see whether you get what it does
fig, axs = plt.subplots(3, 3)
# first row -- one cluster
recongraph.draw_on(axs[0, 0])
# second row -- two clusters
clusters_2 = recongraph.cluster(2)
clusters_2[0].draw_on(axs[1, 0])
clusters_2[1].draw_on(axs[1, 1])
# third row -- three clusters
clusters_3 = recongraph.cluster(3)
clusters_3[0].draw_on(axs[2, 0])
clusters_3[1].draw_on(axs[2, 1])
clusters_3[2].draw_on(axs[2, 2])

fig.savefig("./multi_pdv_histogram_example.pdf")






# Save Reconciliation drawing
# recon.draw_to_file("./recon_example.pdf")
#
# # Display Histogram of different clusters (by creating multiple matplotlib axes)
# class TkinterMultiHistogramPage:
#     """Put this class in your app"""
#     def __init__(self):
#         fig, axs = plt.subplots(3, 3)
#         # first row -- one cluster
#         recongraph.draw_on(axs[0, 0])
#
#         # second row -- two clusters
#         clusters_2 = recongraph.cluster(2)
#         clusters_2[0].draw_on(axs[1, 0])
#         clusters_2[1].draw_on(axs[1, 1])
#
#         # third row -- three clusters
#         clusters_3 = recongraph.cluster(3)
#         clusters_3[0].draw_on(axs[2, 0])
#         clusters_3[1].draw_on(axs[2, 1])
#         clusters_3[2].draw_on(axs[2, 2])
#
#         canvas = FigureCanvasTkAgg(fig)
#         canvas.draw()
#
#         # if you want to save the figure somewhere
#         fig.savefig("./histogram_multi_example.pdf")
