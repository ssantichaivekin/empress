"""
render_test1.py
Tester for render function
"""

from sample_data import host_dict1, parasite_dict1, recon_dict1
from recon_viewer import render

render(host_dict1, parasite_dict1, recon_dict1, show_internal_labels=True, show_freq=True)
