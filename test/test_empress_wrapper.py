import empress
import unittest
import os
import matplotlib.pyplot as plt

class TestEmpressWrappers(unittest.TestCase):

    example_input_path = "./examples/test-size5-no924.newick"

    def test_read_input(self):
        recon_input = empress.read_input(self.example_input_path)
        self.assertTrue(isinstance(recon_input, empress.newickFormatReader.ReconInput))

    def test_compute_cost_regions(self):
        recon_input = empress.read_input(self.example_input_path)
        cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)
        self.assertTrue(isinstance(cost_regions, empress.CostRegionsWrapper))

    def test_draw_cost_regions(self):
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        recon_input = empress.read_input(self.example_input_path)
        cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)
        fig = cost_regions.draw()
        filename = "./cost_region_draw_example.png"
        fig.savefig(filename)
        os.path.exists(filename)
        os.remove(filename)

    def test_reconcile(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        self.assertTrue(isinstance(recongraph, empress.ReconGraphWrapper))
        self.assertTrue(isinstance(recongraph.n_recon, int))
        # the testing recongraph should be designed to have multiple MPRs for DTL = 111
        self.assertGreater(recongraph.n_recon, 1)

    def test_recongraph_draw(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        fig = recongraph.draw()
        self.assertTrue(isinstance(fig, plt.Figure))

    def test_recongraph_draw_graph(self):
        # Draw reconciliation graph to file
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        fig = recongraph.draw()
        self.assertTrue(isinstance(fig, plt.Figure))

    def test_median(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        median_reconciliation = recongraph.median()
        self.assertTrue(isinstance(median_reconciliation, empress.ReconciliationWrapper))

    def test_reconciliation_draw(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        median_reconciliation = recongraph.median()
        fig = median_reconciliation.draw()
        self.assertTrue(isinstance(fig, plt.Figure))

    def test_clusters(self):
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        clusters = recongraph.cluster(3)
        self.assertTrue(isinstance(clusters, list))
        total_recon = 0
        for cluster in clusters:
            self.assertTrue(isinstance(cluster, empress.ReconGraphWrapper))
            total_recon += cluster.n_recon
        # n_recon ~ number of reconciliation graphs
        self.assertEqual(total_recon, recongraph.n_recon)

    def test_cluster_pdv_histogram_draw(self):
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        clusters = recongraph.cluster(3)
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

        filename = "./temp_multi_pdv_histogram_example.png"
        fig.savefig(filename)
        os.path.exists(filename)
        os.remove(filename)

    def test_cluster_reconcile_draw(self):
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        clusters = recongraph.cluster(3)
        fig, axs = plt.subplots(1, len(clusters))
        for i in range(len(clusters)):
            median = clusters[i].median()
            median.draw_on(axs[i])

        filename = "./temp_three_medians_example.png"
        fig.savefig(filename)
        os.path.exists(filename)
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
