import empress
import unittest
import os


class TestEmpressWrappers(unittest.TestCase):
    example_host = "./examples/test_size5_no924_host.nwk"
    example_parasite = "./examples/test_size5_no924_parasite.nwk"
    example_mapping = "./examples/test_size5_no924_mapping.mapping"

    def test_read_input(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        self.assertTrue(isinstance(recon_input, empress.ReconInputWrapper))

    def test_compute_cost_regions(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        cost_regions = recon_input.compute_cost_regions(0.5, 10, 0.5, 10)
        self.assertTrue(isinstance(cost_regions, empress.CostRegionsWrapper))

    def test_draw_cost_regions(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        cost_regions = recon_input.compute_cost_regions(0.5, 10, 0.5, 10)
        fig = cost_regions.draw()
        filename = "./test_draw_cost_regions.png"
        fig.savefig(filename)
        os.path.exists(filename)

    def test_reconcile(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        recongraph = recon_input.reconcile(1, 1, 1)
        self.assertTrue(isinstance(recongraph, empress.ReconGraphWrapper))
        self.assertTrue(isinstance(recongraph.n_recon, int))
        # the testing recongraph should be designed to have multiple MPRs for DTL = 111
        self.assertGreater(recongraph.n_recon, 1)

    def test_median(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        recongraph = recon_input.reconcile(1, 1, 1)
        median_reconciliation = recongraph.median()
        self.assertTrue(isinstance(median_reconciliation, empress.ReconciliationWrapper))

    def test_clusters(self):
        recon_input = empress.ReconInputWrapper.from_files(self.example_host, self.example_parasite, self.example_mapping)
        recongraph = recon_input.reconcile(1, 1, 1)
        clusters = recongraph.cluster(3)
        self.assertTrue(isinstance(clusters, list))
        total_recon = 0
        for cluster in clusters:
            self.assertTrue(isinstance(cluster, empress.ReconGraphWrapper))
            total_recon += cluster.n_recon
        # n_recon ~ number of reconciliation graphs
        self.assertEqual(total_recon, recongraph.n_recon)


if __name__ == '__main__':
    unittest.main()
