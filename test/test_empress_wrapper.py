import empress
import unittest
import os
import matplotlib.pyplot as plt


class TestEmpressWrappers(unittest.TestCase):
    example_input_path = "./examples/test-size5-no924.newick"

    example_strong_consistent_reconciliation = empress.ReconciliationWrapper(
        reconciliation={('n0', 'm4'): [('D', ('n1', 'm4'), ('n2', 'm4'))],
                        ('n1', 'm4'): [('C', (None, None), (None, None))],
                        ('n2', 'm4'): [('D', ('n3', 'm4'), ('n4', 'm4'))],
                        ('n3', 'm4'): [('C', (None, None), (None, None))],
                        ('n4', 'm4'): [('C', (None, None), (None, None))]},
        root=('n0', 'm4'),
        recon_input=empress.ReconInput(
            host_tree={'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
                       ('m0', 'm1'): ('m0', 'm1', None, None),
                       ('m0', 'm2'): ('m0', 'm2', ('m2', 'm3'), ('m2', 'm4')),
                       ('m2', 'm3'): ('m2', 'm3', None, None),
                       ('m2', 'm4'): ('m2', 'm4', None, None)},
            host_distances=None,
            parasite_tree={'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
                           ('n0', 'n1'): ('n0', 'n1', None, None),
                           ('n0', 'n2'): ('n0', 'n2', ('n2', 'n3'), ('n2', 'n4')),
                           ('n2', 'n3'): ('n2', 'n3', None, None),
                           ('n2', 'n4'): ('n2', 'n4', None, None)},
            parasite_distances=None,
            phi=None,
        ),
        dup_cost=None,
        trans_cost=None,
        loss_cost=None,
        total_cost=None,
    )

    example_inconsistent_reconciliation = empress.ReconciliationWrapper(
        reconciliation={('n0', 'm4'): [('T', ('n4', 'm4'), ('n2', 'm2'))],
                        ('n2', 'm2'): [('T', ('n5', 'm2'), ('n3', 'm1'))],
                        ('n3', 'm1'): [('S', ('n1', 'm3'), ('n6', 'm4'))],
                        ('n1', 'm3'): [('C', (None, None), (None, None))],
                        ('n4', 'm4'): [('C', (None, None), (None, None))],
                        ('n5', 'm2'): [('C', (None, None), (None, None))],
                        ('n6', 'm4'): [('C', (None, None), (None, None))]},
        root=('n0', 'm4'),
        recon_input=empress.ReconInput(
            host_tree={'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
                       ('m0', 'm1'): ('m0', 'm1', ('m1', 'm3'), ('m1', 'm4')),
                       ('m1', 'm3'): ('m1', 'm3', None, None),
                       ('m1', 'm4'): ('m1', 'm4', None, None),
                       ('m0', 'm2'): ('m0', 'm2', None, None)},
            host_distances=None,
            parasite_tree={'pTop': ('Top', 'n0', ('n0', 'n4'), ('n0', 'n2')),
                           ('n0', 'n4'): ('n0', 'n4', None, None),
                           ('n0', 'n2'): ('n0', 'n2', ('n2', 'n5'), ('n2', 'n3')),
                           ('n2', 'n5'): ('n2', 'n5', None, None),
                           ('n2', 'n3'): ('n2', 'n3', ('n3', 'n1'), ('n3', 'n6')),
                           ('n3', 'n1'): ('n3', 'n1', None, None),
                           ('n3', 'n6'): ('n3', 'n6', None, None)},
            parasite_distances=None,
            phi=None,
        ),
        dup_cost=None,
        trans_cost=None,
        loss_cost=None,
        total_cost=None,
    )

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
        filename = "./test_draw_cost_regions.png"
        fig.savefig(filename)
        os.path.exists(filename)

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

    def test_strong_consistency_reconciliation_draw(self):
        fig = self.example_strong_consistent_reconciliation.draw()
        self.assertTrue(isinstance(fig, plt.Figure))
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        filename = "./test_strong_consistency_reconciliation_draw.png"
        fig.savefig(filename)
        os.path.exists(filename)

    def test_inconsistent_reconciliation_draw(self):
        fig = self.example_inconsistent_reconciliation.draw()
        self.assertTrue(isinstance(fig, plt.Figure))
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        filename = "./test_inconsistent_reconciliation_draw.png"
        fig.savefig(filename)
        os.path.exists(filename)

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

        filename = "./test_cluster_pdv_histogram_draw.png"
        fig.savefig(filename)
        os.path.exists(filename)

    def test_cluster_reconciliation_draw(self):
        # TODO: move to visualization test
        # https://github.com/ssantichaivekin/eMPRess/issues/83
        recon_input = empress.read_input(self.example_input_path)
        recongraph = empress.reconcile(recon_input, 1, 1, 1)
        clusters = recongraph.cluster(3)
        fig, axs = plt.subplots(1, len(clusters))
        for i in range(len(clusters)):
            median = clusters[i].median()
            median.draw_on(axs[i])

        filename = "./test_cluster_reconciliation_draw.png"
        fig.savefig(filename)
        os.path.exists(filename)


if __name__ == '__main__':
    unittest.main()
