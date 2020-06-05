# Statistics.py
# Computes statistics and creates cost histogram
# Ran Libeskind-Hadas, June 2020

# Performs Monte Carlo simulation to compute empirical p-value and histogram
# of solution costs.
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC379178/

from clumpr import DTLReconGraph
import random
import matplotlib
matplotlib.use('tkagg') # need this so plt.show() works
import matplotlib.pyplot as plt

from typing import List, Dict, Tuple

def trials(host_tree: dict, parasite_tree: dict, phi: dict, dup_cost: float, transfer_cost: float, loss_cost: float, num_trials: int) -> list:
    """
    :param host_tree: dictionary representation of host tree
    :param parasite_tree: dictionary of parasite tree
    :param phi: dictionary representation of parasite tip to host tip mapping
    :param dup_cost: float duplication cost
    :param transfer_cost: float transfer cost
    :param loss_cost: float loss cost
    :param num_trials: int number of trials in Monte Carlo simulation
    :return: list of floating point costs of reconciliations of the Monte Carlo samples
    """
   
    costs = list()  # List of costs of random trials
    parasites = phi.keys()
    hosts = list(phi.values())
    for t in range(num_trials):
        random_phi = create_random_phi(phi)
        for p in parasites:
            h = random.choice(hosts)
            random_phi[p] = h
        _, cost, _, _ = DTLReconGraph.DP(host_tree, parasite_tree, random_phi, dup_cost, transfer_cost, loss_cost)
        costs.append(cost)
    return costs

def create_random_phi(phi : dict) -> dict:
    """
    :param phi: dictionary representation of parasite tip to host tip mapping
    :return: a dictionary of parasite tips to host tips that preserves the degree of
        of the host tips in phi
    """
    random_phi = {}
    parasites = list(phi.keys())
    hosts = list(phi.values())
    unique_hosts = list(set(hosts))
    parasite_count = {}   # keys are hosts, values are the number of parasites on that host wrt phi
    # computer parasite_count values
    for p in parasites:
        h = phi[p]
        if h in parasite_count: parasite_count[h] += 1
        else: parasite_count[h] = 1
    for h in unique_hosts:
        parasite_samples = random.sample(parasites, parasite_count[h])
        for p in parasite_samples: 
            random_phi[p] = h
            parasites.remove(p)
    return random_phi

def plot_histogram(mpr_cost: int, costs: list):
    """
    :param mpr_cost: floating point cost of MPR for given host-parasite-phi and DTL costs
    :param costs: list of floating point costs of Monte Carlo samples
    :return: None.  Displays histogram.
    """
    plt.hist(costs, color = "blue", density = True)
    plt.hist(mpr_cost, color="red", rwidth=1)
    plt.show()

def stats(host_tree: dict, parasite_tree: dict, phi: dict, dup_cost: float, transfer_cost: float, \
    loss_cost: float, num_trials: int, mpr_cost: float = None) -> (float, list, float):
    """
    :param host_tree: dictionary representation of host tree
    :param parasite_tree: dictionary of parasite tree
    :param phi: dictionary representation of parasite tip to host tip mapping
    :param dup_cost: float duplication cost
    :param transfer_cost: float transfer cost
    :param loss_cost: float loss cost
    :param num_trials: int number of trials in Monte Carlo simulation
    :param mpr_cost: float cost of the mpr from the original dataset.  If None, we compute it here
    :return: tuple of three items:
        float cost of optimal MPR for given data
        list of floating point costs of reconciliations of the Monte Carlo samples
        float empirical p-value between 0 and 1
    """
    # If mpr_cost not passed in, we compute it here (only used for ease of testing)
    if mpr_cost is None:
        _, mpr_cost, _, _ = DTLReconGraph.DP(host_tree, parasite_tree, phi, dup_cost, \
            transfer_cost, loss_cost)
    costs = trials(host_tree, parasite_tree, phi, dup_cost, transfer_cost, loss_cost, num_trials)

    # Empirical p-value computed as (r+1)/(n+1) where n is the number of trials and r is the number of trials 
    # whose cost is less than or equal to the cost of the MPR for the actual data.
    r = len([score for score in costs if score <= mpr_cost])
    p = (r+1)/(num_trials + 1)
    return mpr_cost, costs, p


