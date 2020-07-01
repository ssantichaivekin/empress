"""
render_test1.py
Tester for render function
"""
from pathlib import Path
from draw import common

from empress.recon_vis import recon_viewer
import empress

common.create_output_folder()

host_dict1 = {'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
                  ('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
                  ('m0', 'm4'): ('m0', 'm4', None, None),
                  ('m1', 'm2'): ('m1', 'm2', None, None),
                  ('m1', 'm3'): ('m1', 'm3', None, None)}

parasite_dict1 = {'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n4')),
                  ('n0', 'n1'): ('n0', 'n1', ('n1', 'n2'), ('n1', 'n3')),
                  ('n0', 'n4'): ('n0', 'n4', None, None),
                  ('n1', 'n2'): ('n1', 'n2', None, None),
                  ('n1', 'n3'): ('n1', 'n3', None, None)}

recon_dict1 = {('n0', 'm0'): [('S', ('n1', 'm1'), ('n4', 'm4'))],
               ('n1', 'm1'): [('S', ('n2', 'm2'), ('n3', 'm3'))],
               ('n2', 'm2'): [('C', (None, None), (None, None))],
               ('n3', 'm3'): [('C', (None, None), (None, None))],
               ('n4', 'm4'): [('C', (None, None), (None, None))]}

recon_dict2 = {('n0', 'm1'): [('T', ('n1', 'm1'), ('n4', 'm4'))],
               ('n1', 'm1'): [('D', ('n2', 'm1'), ('n3', 'm1'))],
               ('n2', 'm1'): [('L', ('n2', 'm2'), (None, None))],
               ('n3', 'm1'): [('L', ('n3', 'm3'), (None, None))],
               ('n2', 'm2'): [('C', (None, None), (None, None))],
               ('n3', 'm3'): [('C', (None, None), (None, None))],
               ('n4', 'm4'): [('C', (None, None), (None, None))]}


def test_render_1():
    fig = recon_viewer.render(host_dict1, parasite_dict1, recon_dict1,
                              event_scores = None, show_internal_labels=True, show_freq=False)
    filepath = Path(common.output_path).joinpath("test_render_1.png")
    fig.save(filepath)

test_render_1()

def test_render_2():
    fig = recon_viewer.render(host_dict1, parasite_dict1, recon_dict2,
                              event_scores = None, show_internal_labels=True, show_freq=False)
    filepath = Path(common.output_path).joinpath("test_render_2.png")
    fig.save(filepath)

test_render_2()

def test_render_with_frequency_1():
    """
    render a reconciliation and displays the frequency of events in the reconciliation
    """
    example_host = "./examples/test_size5_no924_host.nwk"
    example_parasite = "./examples/test_size5_no924_parasite.nwk"
    example_mapping = "./examples/test_size5_no924_mapping.mapping"
    recon_input = empress.ReconInput.from_files(example_host, example_parasite, example_mapping)
    recon_wrapper = empress.reconcile(recon_input, 1, 1, 1)
    median_reconciliation = recon_wrapper.median()
    fig = recon_viewer.render(recon_input.host_dict, recon_input.parasite_dict,
            median_reconciliation._reconciliation, median_reconciliation.event_scores, show_internal_labels=True, show_freq=True)
    filepath = Path(common.output_path).joinpath("test_render_with_frequency_1.png")
    fig.save(filepath)

test_render_with_frequency_1()
