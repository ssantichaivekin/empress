# statistics.py
# Computes statistics and creates cost histogram
# Ran Libeskind-Hadas, June 2020

# Performs Monte Carlo simulation to compute empirical p-value and histogram
# of solution costs.
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC379178/

import random
import matplotlib
from empress.input_reader import ReconInput
import matplotlib.pyplot as plt

from empress.reconcile import recongraph_tools

def _trials(recon_input: ReconInput, dup_cost: float, transfer_cost: float, loss_cost: float, num_trials: int) -> list:
    """
    :param recon_input <ReconInput> - class containing host tree, parasite tree, tip mapping
    :param dup_cost <float> - duplication cost
    :param transfer_cost <float> - transfer cost
    :param loss_cost <float> -loss cost
    :param num_trials <int> - number of trials in Monte Carlo simulation
    :return: list of floating point costs of reconciliations of the Monte Carlo samples
    """
   
    costs = list()  # List of costs of random trials
    parasites = recon_input.tip_mapping.keys()
    hosts = list(recon_input.tip_mapping.values())
    for t in range(num_trials):
        random_phi = _create_random_phi(recon_input.tip_mapping)
        for p in parasites:
            h = random.choice(hosts)
            random_phi[p] = h
        new_input = ReconInput(recon_input.host_dict, None, recon_input.parasite_dict, None, random_phi)
        _, cost, _, _ = recongraph_tools.DP(new_input, dup_cost, transfer_cost, loss_cost)
        costs.append(cost)
    return costs

def _create_random_phi(tip_mapping : dict) -> dict:
    """
    :param tip_mapping <dict> - dictionary representation of parasite tip to host tip mapping
    :return: a dictionary of parasite tips to host tips that preserves the degree of
        of the host tips in tip_mapping
    """
    random_phi = {}
    parasites = list(tip_mapping.keys())
    hosts = list(tip_mapping.values())
    unique_hosts = list(set(hosts))
    parasite_count = {}   # keys are hosts, values are the number of parasites on that host wrt tip_mapping
    # computer parasite_count values
    for p in parasites:
        h = tip_mapping[p]
        if h in parasite_count: parasite_count[h] += 1
        else: parasite_count[h] = 1
    for h in unique_hosts:
        parasite_samples = random.sample(parasites, parasite_count[h])
        for p in parasite_samples: 
            random_phi[p] = h
            parasites.remove(p)
    return random_phi

def draw_stats(ax: plt.Axes, mpr_cost: float, costs: list, pvalue: float = None):
    """
    :param ax <plt.Axes> - draw histogram on ax
    :param mpr_cost <float> - cost of MPR for given host-parasite-tip_mapping and DTL costs
    :param costs <list> -list of floating point costs of Monte Carlo samples
    """
    if pvalue is not None:
        ax.set_title("p-value = %f" % pvalue)
    ax.hist(costs, 10, color="blue", label="random")
    ax.axvline(mpr_cost, color="red", linewidth=2, label="this reconciliation")
    ax.set_xlabel("total cost")
    ax.set_ylabel("count")

def stats(recon_input: ReconInput, dup_cost: float, transfer_cost: float,
          loss_cost: float, num_trials: int) -> (float, list, float):
    """
    :param recon_input <ReconInput> - class containing host tree, parasite tree, tip mapping
    :param dup_cost <float> - duplication cost
    :param transfer_cost <float> - float transfer cost
    :param loss_cost <float> -loss cost
    :param num_trials <int> - int number of trials in Monte Carlo simulation
    :return: tuple of three items:
        float cost of optimal MPR for given data
        list of floating point costs of reconciliations of the Monte Carlo samples
        float empirical p-value between 0 and 1
    """
    _, mpr_cost, _, _ = recongraph_tools.DP(recon_input, dup_cost, transfer_cost, loss_cost)
    costs = _trials(recon_input, dup_cost, transfer_cost, loss_cost, num_trials)

    # Empirical p-value computed as (r+1)/(n+1) where n is the number of trials and r is the number of trials 
    # whose cost is less than or equal to the cost of the MPR for the actual data.
    r = len([score for score in costs if score <= mpr_cost])
    p = (r+1)/(num_trials + 1)
    return mpr_cost, costs, p


