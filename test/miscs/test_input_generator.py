import unittest

from empress.miscs import input_generator

class TestInputGenerator(unittest.TestCase):
    """
    Test that the input generator generates valid ReconInput
    """

    def test_generate_all_input(self):
        inputs = input_generator.generate_all_recon_input(4)
        for recon_input in inputs:
            self.assertTrue(recon_input.is_complete())

    def test_generate_random_input(self):
        for _ in range(10):
            recon_input = input_generator.generate_random_recon_input(100)
            self.assertTrue(recon_input.is_complete())


if __name__ == '__main__':
    unittest.main()
