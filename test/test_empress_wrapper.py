# TODO: To be converted to automated tests
# https://github.com/ssantichaivekin/eMPRess/issues/32
"""
An example of how we will use the empress wrapper
"""
import empress
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter

# Read Reconciliation Input
recon_input = empress.read_tree("./example/heliconius.newick")

# Display Costscape Window where we can click on x/y axis
class TkinterCostRegionPage:
    """Put this class in your app"""
    def __init__(self):
        # or put these lines in your class
        cost_poly = empress.compute_cost_region(recon_input)
        fig = cost_poly.draw()
        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()

# Compute ReconGraph
recongraph = empress.reconcile(recon_input, 1, 3, 2)

# Save Histogram
recongraph.draw_to_file("./histogram_example.pdf")

# Display Histogram
class TkinterHistogramPage:
    """Put this class in your app"""
    def __init__(self):
        # or put these lines in your class
        fig = recongraph.draw()
        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()

# Get a random median from ReconGraph
recon = recongraph.find_median()

# Display one Reconciliation
class TkinterReconPage:
    """Put this class in your app"""
    def __init__(self):
        # or put these lines in your class
        fig = recon.draw()
        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()

# Save Reconciliation drawing
recon.draw_to_file("./recon_example.pdf")

# Display Histogram of different clusters (by creating multiple matplotlib axes)
class TkinterMultiHistogramPage:
    """Put this class in your app"""
    def __init__(self):
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

        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()

        # if you want to save the figure somewhere
        fig.savefig("./histogram_multi_example.pdf")
