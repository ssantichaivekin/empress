"""
Wraps empress functionalities
"""
from typing import Dict
import matplotlib
# the tkagg backend is for pop-up windows, and will not work in environments
# without graphics such as a remote server. Refer to issue #49
try:
    matplotlib.use("tkagg")
except ImportError:
    print("Using Agg backend: will not be able to create pop-up windows.")
    matplotlib.use("Agg")
from matplotlib import pyplot as plt
from typing import List
from abc import ABC, abstractmethod

from empress.xscape.CostVector import CostVector
from empress.input_reader import _ReconInput
from empress.xscape.reconcile import reconcile as xscape_reconcile
from empress.xscape.plotcosts_analytic import plot_costs_on_axis as xscape_plot_costs_on_axis
from empress.reconcile import recongraph_tools
from empress.reconcile import recongraph_visualization
from empress.reconcile import median
from empress.reconcile import diameter
from empress.reconcile import statistics
from empress.histogram import histogram_display
from empress.histogram import histogram_alg
from empress.cluster import cluster_util
from empress.recon_vis import recon_viewer
from empress.recon_vis import tanglegram

def _find_roots(old_recon_graph) -> list:
    not_roots = set()
    for mapping in old_recon_graph:
        for event in old_recon_graph[mapping]:
            etype, left, right = event
            if etype in 'SDT':
                not_roots.add(left)
                not_roots.add(right)
            elif etype == 'L':
                child = left
                not_roots.add(child)
            elif etype == 'C':
                pass
            else:
                raise ValueError('%s not in "SDTLC' % etype)
    roots = []
    for mapping in old_recon_graph:
        if mapping not in not_roots:
            roots.append(mapping)
    return roots

class Drawable(ABC):
    """
    Implements a default draw method
    """

    @abstractmethod
    def draw_on(self, axes: plt.Axes):
        """
        Draw self on matplotlib Axes
        """
        pass

    def draw(self) -> plt.Figure:
        """
        Draw self as matplotlib Figure.
        """
        figure, ax = plt.subplots(1, 1)
        self.draw_on(ax)
        return figure

    def draw_to_file(self, fname):
        """
        Draw self and save it as image at path fname.
        """
        figure = self.draw()
        figure.savefig(fname)


class ReconciliationWrapper(Drawable):
    # TODO: Replace dict with Reconciliation type
    # https://github.com/ssantichaivekin/eMPRess/issues/30
    def __init__(self, reconciliation: dict, root: tuple, recon_input: _ReconInput, dup_cost, trans_cost, loss_cost,
                 total_cost: float, event_scores: Dict[tuple, float] = None):
        self.recon_input = recon_input
        self.dup_cost = dup_cost
        self.trans_cost = trans_cost
        self.loss_cost = loss_cost
        self.total_cost = total_cost
        self._reconciliation = reconciliation
        self.root = root
        self.event_scores = event_scores

    def draw_on(self, axes: plt.Axes):
        recon_viewer.render(self.recon_input.host_dict, self.recon_input.parasite_dict, self._reconciliation,
                            axes=axes)

class ReconGraphWrapper(Drawable):
    # TODO: Replace dict with ReconGraph type
    # https://github.com/ssantichaivekin/eMPRess/issues/30
    def __init__(self, recongraph: dict, roots: list, n_recon: int, recon_input: _ReconInput, dup_cost, trans_cost,
                 loss_cost, total_cost: float, event_scores: Dict[tuple, float] = None):
        self.recon_input = recon_input
        self.dup_cost = dup_cost
        self.trans_cost = trans_cost
        self.loss_cost = loss_cost
        self.recongraph = recongraph
        self.total_cost = total_cost
        self.n_recon = n_recon
        self.roots = roots
        self.event_scores = event_scores

    def draw_on(self, axes: plt.Axes):
        """
        Draw Pairwise Distance Histogram on axes
        """
        # Reformat the host and parasite tree to use it with the histogram algorithm
        parasite_tree, parasite_tree_root, parasite_node_count = diameter.reformat_tree(self.recon_input.parasite_dict, "pTop")
        host_tree, host_tree_root, host_node_count \
            = diameter.reformat_tree(self.recon_input.host_dict, "hTop")
        hist = histogram_alg.diameter_algorithm(
            host_tree, parasite_tree, parasite_tree_root, self.recongraph, self.recongraph,
            False, False)
        histogram_display.plot_histogram_to_ax(axes, hist.histogram_dict)

    def draw_graph_to_file(self, fname):
        """
        Draw self and save it as image at path fname.
        """
        recongraph_visualization.visualize_and_save(self.recongraph, fname)

    def stats(self, num_trials: int = 50):
        _, costs, p = statistics.stats(self.recon_input, self.dup_cost, self.trans_cost, self.loss_cost, num_trials)
        return costs, p

    def draw_stats_on(self, ax: plt.Axes):
        costs, p = self.stats()
        statistics.draw_stats(ax, self.total_cost, costs, p)

    def draw_stats(self):
        figure, ax = plt.subplots(1, 1)
        self.draw_stats_on(ax)
        return figure

    def median(self) -> ReconciliationWrapper:
        """
        Return one of the best ReconciliationWrapper that best represents the
        reconciliation graph. The function internally uses random and is not deterministic.
        """
        postorder_parasite_tree, parasite_tree_root, _ = diameter.reformat_tree(self.recon_input.parasite_dict, "pTop")
        postorder_host_tree, _, _ = diameter.reformat_tree(self.recon_input.host_dict, "hTop")

        # Compute the median reconciliation graph
        median_reconciliation, n_meds, roots_for_median = median.get_median_graph(
            self.recongraph, postorder_parasite_tree, postorder_host_tree, parasite_tree_root, self.roots)

        med_counts_dict = median.get_med_counts(median_reconciliation, roots_for_median)

        random_median = median.choose_random_median_wrapper(median_reconciliation, roots_for_median, med_counts_dict)
        median_root = _find_roots(random_median)[0]
        return ReconciliationWrapper(random_median, median_root, self.recon_input, self.dup_cost, self.trans_cost,
                                     self.loss_cost, self.total_cost, self.event_scores)

    def cluster(self, n) -> List['ReconGraphWrapper']:
        """
        Cluster self into list of n ReconGraphWrapper.
        """
        if n > self.n_recon:
            raise Exception("Cannot cluster %d Reconciliation into %d clusters" % (self.n_recon, n))

        parasite_tree, host_tree, parasite_root, recon_g, mpr_count, best_roots = \
            cluster_util.get_tree_info(self.recon_input, self.dup_cost, self.trans_cost, self.loss_cost)

        score = cluster_util.mk_pdv_score(host_tree, parasite_tree, parasite_root)

        graphs, scores, _ = cluster_util.cluster_graph(self.recongraph, parasite_root, score, 4, n, 200)
        new_graphs = []
        for graph in graphs:
            roots = _find_roots(graph)
            n = recongraph_tools.count_mprs_wrapper(roots, graph)
            new_graphs.append(
                ReconGraphWrapper(graph, roots, n, self.recon_input, self.dup_cost, self.trans_cost, self.loss_cost,
                                  self.total_cost, self.event_scores))
        return new_graphs

    def set_event_frequencies(self):
        """
        Set self.event_scores,
        event_scores is a dictionary that maps events nodes to their frequencies in all the optimal reconciliations
        indicated by the recongraph
        """
        postorder_parasite_tree, parasite_tree_root, _ = diameter.reformat_tree(self.recon_input.parasite_dict, "pTop")
        postorder_host_tree, _, _ = diameter.reformat_tree(self.recon_input.host_dict, "hTop")
        postorder_mapping_node_list = median.mapping_node_sort(postorder_parasite_tree, postorder_host_tree,
                                                    list(self.recongraph.keys()))
        event_scores = median.generate_scores(postorder_mapping_node_list[::-1], self.recongraph, parasite_tree_root)[0]
        self.event_scores = event_scores

class CostRegionsWrapper(Drawable):
    def __init__(self, cost_vectors, transfer_min, transfer_max, dup_min, dup_max):
        """
        CostRegionsWrapper wraps all information required to display a cost region plot.
        """
        self._cost_vectors = cost_vectors
        self._transfer_min = transfer_min
        self._transfer_max = transfer_max
        self._dup_min = dup_min
        self._dup_max = dup_max

    def draw_on(self, axes: plt.Axes, log=False):
        xscape_plot_costs_on_axis(axes, self._cost_vectors, self._transfer_min, self._transfer_max,
                                  self._dup_min, self._dup_max, log=False)

class ReconInputWrapper(_ReconInput, Drawable):
    def __init__(self, *args, **kwargs):
        _ReconInput.__init__(self, *args, **kwargs)

    def draw_on(self, ax: plt.Axes):
        """
        This draws the tanglegram.
        """
        tanglegram.render(self.host_dict, self.parasite_dict, self.tip_mapping, True, ax)

    def compute_cost_regions(self, transfer_min: float, transfer_max: float,
                         dup_min: float, dup_max: float) -> CostRegionsWrapper:
        """
        Compute the cost polygon of self. The cost polygon can be used
        to create a figure that separate costs into different regions.
        """
        parasite_dict = self.parasite_dict
        host_dict = self.host_dict
        tip_mapping = self.tip_mapping
        cost_vectors = xscape_reconcile(parasite_dict, host_dict, tip_mapping, transfer_min, transfer_max, dup_min, dup_max)
        return CostRegionsWrapper(cost_vectors, transfer_min, transfer_max, dup_min, dup_max)

    def reconcile(self, dup_cost: int, trans_cost: int, loss_cost: int) -> ReconGraphWrapper:
        """
        Given self (which has parasite tree, host tree, and tip mapping info)
        and the cost of the three events, computes and returns a reconciliation graph.
        """
        graph, total_cost, n_recon, roots = recongraph_tools.DP(self, dup_cost, trans_cost, loss_cost)
        recongraph = ReconGraphWrapper(graph, roots, n_recon, self, dup_cost, trans_cost, loss_cost, total_cost)
        recongraph.set_event_frequencies()
        return recongraph
