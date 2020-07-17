import empress.recon_vis.recon_viewer
from empress.miscs import input_generator

from empress.recon_vis.recon_viewer import render

host_leaves = parasite_leaves = 20
recon_input = input_generator.generate_random_recon_input(host_leaves, parasite_leaves)
recongraph = recon_input.reconcile(1, 1, .0001)
reconciliation = recongraph.median()

render(recon_input.host_dict, recon_input.parasite_dict, reconciliation._reconciliation, reconciliation.event_frequencies, show_internal_labels=True, show_freq=True).show()