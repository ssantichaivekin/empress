import unittest

import empress
from empress.miscs import input_generator

class TestInputGenerator(unittest.TestCase):
    """
    Test that the input generator generates valid ReconInputWrapper
    """

    def test_generate_all_input(self):
        inputs = input_generator.generate_all_recon_input(4)
        for recon_input in inputs:
            self.assertTrue(recon_input.is_complete())
            try:
                recon_input.reconcile(1, 1, 1)
            except Exception as e:
                self.fail("recon_input.reconcile fail on recon_input: %s" % e)

    def test_generate_random_input(self):
        for _ in range(10):
            recon_input = input_generator.generate_random_recon_input(20)
            self.assertTrue(recon_input.is_complete())
            try:
                recon_input.reconcile(1, 1, 1)
            except Exception as e:
                self.fail("recon_input.reconcile fail on recon_input: %s" % e)


if __name__ == '__main__':
    unittest.main()
