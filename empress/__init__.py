"""
Wraps empress functionalities
"""
from matplotlib import pyplot as plt
from typing import List, Iterable
from abc import ABC, abstractmethod
from empress.xscape.CostVector import CostVector

#==========================================================
# global

DUP_COST = 2
TRANS_COST = 3
LOSS_COST = 1

DUP_LOW = 1
DUP_HIGH = 5
TRANS_LOW = 1
TRANS_HIGH = 5

NUM_CLUSTERS = 3

#==========================================================

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
        pass

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
    def __init__(self, info):
        """
        Will look into this more.
        """
        pass

    def draw_on(self, axes: plt.Axes):
        pass

def read_input(fname: str) -> ReconInputWrapper:
    """
    Read parasite tree, host tree, and tip mapping from fname.
    Returns ReconInputWrapper which wraps the three info.
    """
    pass

def compute_cost_region(recon_input: ReconInputWrapper) -> CostRegionWrapper:
    """
    Compute the cost polygon of recon_input. The cost polygon can be used
    to create a figure that separate costs into different regions.
    """
    pass

def reconcile(recon_input: ReconInputWrapper, dup_cost: int, trans_cost: int, loss_cost: int) -> ReconGraphWrapper:
    """
    Given recon_input (which has parasite tree, host tree, and tip mapping info)
    and the cost of the three events, computes and returns a reconciliation graph.
    """
    pass
