"""
render_test.py
Tester for render function
"""

from sample_data import host_dict3, parasite_dict3, recon_dict3
from recon_viewer import render

render(host_dict3, parasite_dict3, recon_dict3, show_internal_labels=True, show_freq=False)