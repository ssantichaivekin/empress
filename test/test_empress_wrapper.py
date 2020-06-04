# TODO: To be converted to automated tests
# https://github.com/ssantichaivekin/eMPRess/issues/32
import empress
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk

# Read Reconciliation Input
recon_input = empress.read_input("./examples/heliconius.newick")

cost_region = empress.compute_cost_region(recon_input, 0.5, 10, 0.5, 10)
cost_region.draw_to_file('./examples/cost_poly.png')

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        fig = cost_region.draw()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

root = tk.Tk()
app = Application(master=root)
app.mainloop()

# Functions below are still untested

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
