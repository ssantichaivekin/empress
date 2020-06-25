import unittest

from empress import input_reader


class TestInputReader(unittest.TestCase):
    example_host_file = "./examples/test_size5_no924_host.nwk"
    example_parasite_file = "./examples/test_size5_no924_parasite.nwk"
    example_mapping_file = "./examples/test_size5_no924_mapping.mapping"
    example_invalid_mapping_file = "./examples/test_size5_no924_invalid_mapping.mapping"

    example_host = {'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
                     ('m0', 'm1'): ('m0', 'm1', None, None),
                     ('m0', 'm2'): ('m0', 'm2', None, None)}

    example_parasite = {'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
                         ('n0', 'n1'): ('n0', 'n1', None, None),
                         ('n0', 'n2'): ('n0', 'n2', None, None)}

    example_valid_mapping = {'n1': 'm1', 'n2': 'm2'}

    def test_init_empty(self):
        recon_input = input_reader.ReconInput()
        self.assertTrue(isinstance(recon_input, input_reader.ReconInput))
        self.assertIsNone(recon_input.host_tree)
        self.assertIsNone(recon_input.parasite_tree)
        self.assertIsNone(recon_input.phi)

    def test_init_success(self):
        recon_input = input_reader.ReconInput(self.example_host, None, self.example_parasite, None,
                                              self.example_valid_mapping)
        self.assertTrue(recon_input.is_complete())

    def test_init_invalid_parasite_tip_error(self):
        # parasite n0 is not a tip
        invalid_mapping = {'n0': 'm1', 'n2': 'm2'}
        self.assertRaises(input_reader.ReconInputError, input_reader.ReconInput,
                          self.example_host, None, self.example_parasite, None, invalid_mapping)

    def test_init_invalid_host_tip_error(self):
        # host m0 is not a tip
        invalid_mapping = {'n1': 'm0', 'n2': 'm2'}
        self.assertRaises(input_reader.ReconInputError, input_reader.ReconInput,
                          self.example_host, None, self.example_parasite, None, invalid_mapping)

    def test_read_success(self):
        recon_input = input_reader.ReconInput()
        recon_input.read_host(self.example_host_file)
        recon_input.read_parasite(self.example_parasite_file)
        recon_input.read_mapping(self.example_mapping_file)
        self.assertTrue(recon_input.is_complete())

    def test_read_invalid_tip_error(self):
        recon_input = input_reader.ReconInput()
        recon_input.read_host(self.example_host_file)
        recon_input.read_parasite(self.example_parasite_file)
        self.assertRaises(input_reader.ReconInputError, recon_input.read_mapping, self.example_invalid_mapping_file)

    def test_from_files_success(self):
        recon_input = input_reader.ReconInput.from_files(self.example_host_file, self.example_parasite_file, self.example_mapping_file)
        self.assertTrue(recon_input.is_complete())

    def test_from_files_type_error(self):
        self.assertRaises(input_reader.ReconInputError, input_reader.ReconInput.from_files,
                          self.example_host_file, 12345, self.example_mapping_file)

    def test_from_files_file_not_found_error(self):
        self.assertRaises(input_reader.ReconInputError, input_reader.ReconInput.from_files,
                          self.example_host_file, self.example_parasite_file, "./this-file-does-not-exist")


if __name__ == '__main__':
    unittest.main()