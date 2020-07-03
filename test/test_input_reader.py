import unittest
import os

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
        recon_input = input_reader._ReconInput()
        self.assertTrue(isinstance(recon_input, input_reader._ReconInput))
        self.assertIsNone(recon_input.host_dict)
        self.assertIsNone(recon_input.parasite_dict)
        self.assertIsNone(recon_input.tip_mapping)

    def test_init_success(self):
        recon_input = input_reader._ReconInput(self.example_host, None, self.example_parasite, None,
                                               self.example_valid_mapping)
        self.assertTrue(recon_input.is_complete())

    def test_init_invalid_parasite_tip_error(self):
        # parasite n0 is not a tip
        invalid_mapping = {'n0': 'm1', 'n2': 'm2'}
        self.assertRaises(input_reader.ReconInputError, input_reader._ReconInput,
                          self.example_host, None, self.example_parasite, None, invalid_mapping)

    def test_init_invalid_host_tip_error(self):
        # host m0 is not a tip
        invalid_mapping = {'n1': 'm0', 'n2': 'm2'}
        self.assertRaises(input_reader.ReconInputError, input_reader._ReconInput,
                          self.example_host, None, self.example_parasite, None, invalid_mapping)

    def test_read_success(self):
        recon_input = input_reader._ReconInput()
        recon_input.read_host(self.example_host_file)
        recon_input.read_parasite(self.example_parasite_file)
        recon_input.read_mapping(self.example_mapping_file)
        self.assertTrue(recon_input.is_complete())

    def test_read_invalid_tip_error(self):
        recon_input = input_reader._ReconInput()
        recon_input.read_host(self.example_host_file)
        recon_input.read_parasite(self.example_parasite_file)
        self.assertRaises(input_reader.ReconInputError, recon_input.read_mapping, self.example_invalid_mapping_file)

    def test_from_files_success(self):
        recon_input = input_reader._ReconInput.from_files(self.example_host_file, self.example_parasite_file, self.example_mapping_file)
        self.assertTrue(recon_input.is_complete())

    def test_from_files_type_error(self):
        self.assertRaises(input_reader.ReconInputError, input_reader._ReconInput.from_files,
                          self.example_host_file, 12345, self.example_mapping_file)

    def test_from_files_file_not_found_error(self):
        self.assertRaises(input_reader.ReconInputError, input_reader._ReconInput.from_files,
                          self.example_host_file, self.example_parasite_file, "./this-file-does-not-exist")

    def test_write_to_file(self):
        recon_input = input_reader._ReconInput(self.example_host, None, self.example_parasite, None,
                                               self.example_valid_mapping)
        host_save_path = "./temp_host.tree"
        parasite_save_path = "./temp_parasite.tree"
        tip_mapping_save_path = "./temp_mapping.mapping"

        recon_input.save_to_files(host_save_path, parasite_save_path, tip_mapping_save_path)

        os.path.exists(host_save_path)
        os.path.exists(parasite_save_path)
        os.path.exists(tip_mapping_save_path)

        result_input = input_reader._ReconInput.from_files(host_save_path, parasite_save_path, tip_mapping_save_path)
        self.assertEqual(self.example_host, result_input.host_dict)
        self.assertEqual(self.example_parasite, result_input.parasite_dict)
        self.assertEqual(self.example_valid_mapping, result_input.tip_mapping)

        os.remove(host_save_path)
        os.remove(parasite_save_path)
        os.remove(tip_mapping_save_path)


if __name__ == '__main__':
    unittest.main()
