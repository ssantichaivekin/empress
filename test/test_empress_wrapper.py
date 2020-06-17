import empress
import unittest
import matplotlib.pyplot as plt

class TestEmpressWrappers(unittest.TestCase):

    example_input_path = "./examples/test-size5-no924.newick"

    def test_read_input(self):
        recon_input = empress.read_input(self.example_input_path)
        self.assertTrue(isinstance(recon_input, empress.newickFormatReader.ReconInput))

    def test_compute_cost_regions(self):
        recon_input = empress.read_input(self.example_input_path)
        cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)
        fig = cost_regions.draw()
        self.assertTrue(isinstance(fig, plt.Axes))

    def test_reconcile(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        self.assertTrue(isinstance(recongraph, empress.ReconGraphWrapper))
        self.assertTrue(isinstance(recongraph.n_recon, int))
        # the testing recongraph should be designed to have multiple MPRs for DTL = 111
        self.assertGreater(recongraph, 1)

    def test_draw_recongraph(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        fig = recongraph.draw()
        # Uncomment for examples:
        # recongraph.draw_graph_to_file("./recongraph_example.pdf")
        # recongraph.draw_to_file("./recongraph_hist_example.pdf")
        self.assertTrue(isinstance(fig, plt.Axes))

    def test_median(self):


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

# number of reconciliation graph
recongraph.n_recon

# Draw three histograms on one figure
# fig: plt.Figure
fig, axs = plt.subplots(1, len(clusters))
for i in range(len(clusters)):
    clusters[i].draw_on(axs[i])
# Note that you could also display this figure in tkinter
fig.savefig("./figure_of_three_his_example.png")

# Draw three Reconciliations on one figure
fig, axs = plt.subplots(1, len(clusters))
for i in range(len(clusters)):
    median = clusters[i].median()
    median.draw_on(axs[i])
# Note that you could also display this figure in tkinter
fig.savefig("./figure_of_three_medians_example.png")

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
