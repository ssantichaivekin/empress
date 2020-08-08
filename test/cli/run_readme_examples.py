"""Run cli examples from readme"""

import subprocess
import sys

readme_commands = {
    "empress cli help": "pipenv run python empress_cli.py --help",
    "cost-regions help": "pipenv run python empress_cli.py cost-regions --help",
    "cost-regions example": "pipenv run python empress_cli.py cost-regions examples/heliconius_host.nwk "
                            "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping "
                            "-tl 0.5 -th 10 -dl 0.5 -dh 10 --outfile costscape-example-img.pdf --log",
    "reconcile example": "pipenv run python empress_cli.py reconcile examples/heliconius_host.nwk "
                         "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping "
                         "-d 4 -t 2 -l 0",
    "distance pair histogram example": "pipenv run python empress_cli.py histogram examples/heliconius_host.nwk "
                                       "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping "
                                       "--csv histogram_example_output_csv.csv "
                                       "--histogram-pdf histogram_example_output_img.pdf --ynorm",
    "cluster example": "pipenv run python empress_cli.py cluster examples/heliconius_host.nwk "
                       "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping "
                       "3 --median --n-splits 4 --support",
    "tanglegram example": "python empress_cli.py tanglegram examples/heliconius_host.nwk "
                          "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping",
    "p-value example": "python empress_cli.py p-value examples/heliconius_host.nwk "
                       "examples/heliconius_parasite.nwk examples/heliconius_mapping.mapping "
                       "-d 4 -t 2 -l 1 --n-samples 200",
}

n_failed_tests = 0
for command_info, command in readme_commands.items():
    print("Running", command_info)
    print("$", command)
    completed_process = subprocess.run(command.split())
    if completed_process.returncode != 0:
        n_failed_tests += 1

if n_failed_tests == 0:
    print("All tests passed")
else:
    print(n_failed_tests, "tests failed")
    # Exit with error code to fail ci
    sys.exit(1)
