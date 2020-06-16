"""
render_test1.py
Tester for render function
"""
import os
from pathlib import Path
import shutil
import unittest

from empress.clumpr.recon_vis import recon_viewer


class TestReconViewer(unittest.TestCase):
    """
    Test the Reconciliation render function.
    """
    generated_dir_path = "./temp_test_recon_viewer"

    def setUp(self) -> None:
        os.mkdir(self.generated_dir_path)

    def tearDown(self) -> None:
        shutil.rmtree(self.generated_dir_path)

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

    def test_render_1(self):
        fig = recon_viewer.render(self.host_dict1, self.parasite_dict1, self.recon_dict1,
                                  show_internal_labels=True, show_freq=True)
        filepath = Path(self.generated_dir_path).joinpath("recon_test_1.png")
        fig.save(filepath)
        # look at an example by stopping here in the debugger and look at the filepath location
        self.assertTrue(os.path.exists(filepath))

    def test_render_2(self):
        fig = recon_viewer.render(self.host_dict1, self.parasite_dict1, self.recon_dict2,
                                  show_internal_labels=True, show_freq=True)
        filepath = Path(self.generated_dir_path).joinpath("recon_test_2.png")
        fig.save(filepath)
        # look at an example by stopping here in the debugger and look at the filepath location
        self.assertTrue(os.path.exists(filepath))

if __name__ == '__main__':
    unittest.main()
