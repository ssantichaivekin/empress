import unittest

import empress
from empress import input_reader
from empress.miscs import input_generator

class TestInputGenerator(unittest.TestCase):
    """
    Test that the input generator generates valid ReconInput
    """

    def test_generate_all_input_equal_size(self):
        n_leaves = 4
        inputs = input_generator.generate_all_recon_input(n_leaves, n_leaves)
        for recon_input in inputs:
            self.assertTrue(recon_input.is_complete())
            actual_n_host_leaves = len(input_reader.ReconInput._leaves_from_tree_dict(recon_input.host_dict))
            actual_n_parasite_leaves = len(input_reader.ReconInput._leaves_from_tree_dict(recon_input.parasite_dict))
            self.assertEqual(actual_n_host_leaves, n_leaves)
            self.assertEqual(actual_n_parasite_leaves, n_leaves)
            try:
                empress.reconcile(recon_input, 1, 1, 1)
            except Exception as e:
                self.fail("empress.reconcile fail on recon_input: %s" % e)

    def test_generate_all_input_unequal_size_1(self):
        test_n_leaves = [(3, 4), (4, 3)]
        for n_host_leaves, n_parasite_leaves in test_n_leaves:
            inputs = input_generator.generate_all_recon_input(n_host_leaves, n_parasite_leaves)
            for recon_input in inputs:
                self.assertTrue(recon_input.is_complete())
                actual_n_host_leaves = len(input_reader.ReconInput._leaves_from_tree_dict(recon_input.host_dict))
                actual_n_parasite_leaves = len(
                    input_reader.ReconInput._leaves_from_tree_dict(recon_input.parasite_dict))
                self.assertEqual(actual_n_host_leaves, n_host_leaves)
                self.assertEqual(actual_n_parasite_leaves, n_parasite_leaves)
                try:
                    empress.reconcile(recon_input, 1, 1, 1)
                except Exception as e:
                    self.fail("empress.reconcile fail on recon_input: %s" % e)

    def test_generate_random_input(self):
        n_host_leaves = 20
        for i in range(20):
            n_parasite_leaves = 20 - 10 + i
            recon_input = input_generator.generate_random_recon_input(n_host_leaves, n_parasite_leaves)
            self.assertTrue(recon_input.is_complete())
            actual_n_host_leaves = len(input_reader.ReconInput._leaves_from_tree_dict(recon_input.host_dict))
            actual_n_parasite_leaves = len(
                input_reader.ReconInput._leaves_from_tree_dict(recon_input.parasite_dict))
            self.assertEqual(actual_n_host_leaves, n_host_leaves)
            self.assertEqual(actual_n_parasite_leaves, n_parasite_leaves)
            try:
                empress.reconcile(recon_input, 1, 1, 1)
            except Exception as e:
                self.fail("empress.reconcile fail on recon_input: %s" % e)


if __name__ == '__main__':
    unittest.main()
