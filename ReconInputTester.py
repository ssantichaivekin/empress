# ReconInputTester.py

import ReconInput

R = ReconInput.ReconInput()
R.read_host("gopher.nwk")
print(R.read_host("gopher.nwk"))
R.read_parasite("louse.nwk")
R.read_mapping("gopherlouse.mapping")
print(R.complete())
assert R.complete()
