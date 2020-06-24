# This file is not run by unittest by default
# Run this file to generate drawing examples

import empress
import matplotlib.pyplot as plt
from pathlib import Path
from draw import common

common.create_output_folder()

example_input_path = "./examples/test-size5-no924.newick"

# Wrapper draw examples and tests

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

def test_recongraph_draw():
    recon_input = empress.read_input(example_input_path)
    recongraph = empress.reconcile(recon_input, 1, 1, 1)
    fig = recongraph.draw()
    fig.savefig(Path(common.output_path).joinpath("test_recongraph_draw.png"))

test_recongraph_draw()

def test_recongraph_draw_graph():
    # Draw reconciliation graph to file
    recon_input = empress.read_input(example_input_path)
    recongraph = empress.reconcile(recon_input, 1, 1, 1)
    recongraph.draw_graph_to_file(Path(common.output_path).joinpath("test_recongraph_draw_graph.png"))

test_recongraph_draw_graph()

def test_strong_consistency_reconciliation_draw():
    fig = example_strong_consistent_reconciliation.draw()
    fig.savefig(Path(common.output_path).joinpath("test_strong_consistency_reconciliation_draw.png"))

test_strong_consistency_reconciliation_draw()

def test_inconsistent_reconciliation_draw():
    fig = example_inconsistent_reconciliation.draw()
    fig.savefig(Path(common.output_path).joinpath("test_inconsistent_reconciliation_draw.png"))

test_inconsistent_reconciliation_draw()


def test_cluster_reconciliation_draw():
    recon_input = empress.read_input(example_input_path)
    recongraph = empress.reconcile(recon_input, 1, 1, 1)
    clusters = recongraph.cluster(3)
    fig, axs = plt.subplots(1, len(clusters))
    for i in range(len(clusters)):
        median_recon = clusters[i].median()
        median_recon.draw_on(axs[i])

    fig.savefig(Path(common.output_path).joinpath("test_cluster_reconciliation_draw.png"))

test_cluster_reconciliation_draw()

def test_cluster_pdv_histogram_draw():
    recon_input = empress.read_input(example_input_path)
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

    fig.savefig(Path(common.output_path).joinpath("test_cluster_pdv_histogram_draw.png"))

test_cluster_pdv_histogram_draw()

def test_stats_1():
    recon_input = empress.read_input(example_input_path)
    recongraph = empress.reconcile(recon_input, 1, 1, 1)
    fig = recongraph.draw_stats()
    fig.savefig(Path(common.output_path).joinpath("test_stats_1.png"))

test_stats_1()
