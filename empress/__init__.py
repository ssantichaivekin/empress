"""
Wraps empress functionalities
"""
import matplotlib.pyplot as plt
from typing import List
from abc import ABC, abstractmethod

from empress.xscape.CostVector import CostVector
from empress import newickFormatReader
from empress.xscape.reconcile import reconcile as xscape_reconcile
from empress.xscape.plotcostsAnalytic import plot_costs_to_axis as xscape_plot_costs_to_axis


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


class ReconInputWrapper:
    def __init__(self, parasite_tree: dict, host_tree: dict, tip_mapping: dict):
        self._parasite_tree = parasite_tree
        self._host_tree = host_tree
        self._tip_mapping = tip_mapping


class ReconciliationWrapper(Drawable):
    # TODO: Replace dict with Reconciliation type
    # https://github.com/ssantichaivekin/eMPRess/issues/30
    def __init__(self, reconciliation: dict):
        self._reconciliation = reconciliation

    def draw_on(self, axes: plt.Axes):
        pass


class ReconGraphWrapper(Drawable):
    # TODO: Replace dict with ReconGraph type
    # https://github.com/ssantichaivekin/eMPRess/issues/30
    def __init__(self, recongraph: dict):
        self._recongraph = recongraph

    def find_median(self) -> ReconciliationWrapper:
        """
        Find and return one median of self
        """
        pass

    def draw_on(self, axes: plt.Axes):
        pass

    def cluster(self, n) -> List['ReconGraphWrapper']:
        """
        Cluster self into n reconciliation graphs
        """
        pass


class CostRegionWrapper(Drawable):
    def __init__(self, cost_vectors, switch_min, switch_max, loss_min, loss_max):
        """
        Will look into this more.
        """
        self._cost_vectors = cost_vectors
        self._switch_min = switch_min
        self._switch_max = switch_max
        self._loss_min = loss_min
        self._loss_max = loss_max
        pass

    def draw_on(self, axes: plt.Axes, log=False):
        xscape_plot_costs_to_axis(axes, self._cost_vectors, self._switch_min, self._switch_max,
                                  self._loss_min, self._loss_max, log=False)


def read_input(fname: str) -> ReconInputWrapper:
    """
    Read parasite tree, host tree, and tip mapping from fname.
    Returns ReconInputWrapper which wraps the three info.
    """
    host_tree, parasite_tree, tip_mapping = newickFormatReader.getInput(fname)
    recon_input = ReconInputWrapper(parasite_tree, host_tree, tip_mapping)
    return recon_input


def compute_cost_region(recon_input: ReconInputWrapper, switch_low: float, switch_high: float,
                         lost_low: float, lost_high: float) -> CostPolygonWrapper:
    """
    Compute the cost polygon of recon_input. The cost polygon can be used
    to create a figure that separate costs into different regions.
    """
    parasite_tree = recon_input._parasite_tree
    host_tree = recon_input._host_tree
    tip_mapping = recon_input._tip_mapping
    cost_vectors = xscape_reconcile(parasite_tree, host_tree, tip_mapping, switch_low, switch_high, lost_low, lost_high)
    return CostPolygonWrapper(cost_vectors, switch_low, switch_high, lost_low, lost_high)


def reconcile(recon_input: ReconInputWrapper, dup_cost: int, trans_cost: int, loss_cost: int) -> ReconGraphWrapper:
    """
    Given recon_input (which has parasite tree, host tree, and tip mapping info)
    and the cost of the three events, computes and returns a reconciliation graph.
    """
    pass
