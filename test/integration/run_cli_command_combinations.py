import itertools
import subprocess
import argparse

cli_filename = "empress_cli.py"
example_host = "examples/heliconius_host.nwk"
example_parasite = "examples/heliconius_parasite.nwk"
example_mapping = "examples/heliconius_mapping.mapping"

list_of_commands = ["cost-regions", "reconcile", "histogram", "cluster"]
options_for_reconcile = ["-d", "-t", "-l"]
options_for_cost_regions = ["-dl", "-tl", "-dh", "-th", "--log", "--outfile"]
options_for_histogram = ["-d", "-t", "-l", "--histogram", "--xnorm", "--ynorm", "--omit-zeros", "--cumulative",
                         "--csv", "--stats", "--time"]
options_for_cluster = ["-d", "-t", "-l", "--medians", "--depth", "--n-splits", "--pdv-vis", "--support-vis",
                       "--pdv", "--support"]

# copied from https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def input_value(option):
    """Compute an input value for the optional argument"""
    if option in ["-d", "-t", "-l"]:
        # default value d: 2, t: 3, l:1
        return "3"
    elif option in ["-dl", "-tl"]:
        # default value for this option is 1
        return "2"
    elif option in ["-dh","-th"]:
        # default value for this option is 5
        return "10"
    elif option == "--csv":
        return "test_cli_output_csv.csv"
    elif option == "--histogram":
        return "test_cli_output_histogram.pdf"
    elif option == "--outfile":
        return "test_cli_output_cost_regions.pdf"
    elif option in ["--depth", "--n-splits"]:
        return "2"
    else:
        return None

def run_command(command: str, n_tests: int, fail_fast = True):
    """
    :param command: the functionality to test
    :param n_tests: upper limit on number of tests to run for the command
    :param fail_fast: return upon first failure
    """
    print("Testing", command)
    n_failed_tests = 0

    if command == "cost-regions":
        options_for_command = options_for_cost_regions
    elif command == "reconcile":
        options_for_command = options_for_reconcile
    elif command == "histogram":
        options_for_command = options_for_histogram
    elif command == "cluster":
        options_for_command = options_for_cluster
        num_clusters = "3"
    else:
        raise RuntimeError("command [%s] not recognized" % command)

    total_combinations = list(powerset(options_for_command))[:n_tests]

    for selected_options in total_combinations:
        # example command : python empress_cli.py reconcile <host_file> <parasite_file> <mapping_file>
        command_args = ["python", cli_filename, command, example_host, example_parasite, example_mapping]
        for option in selected_options:
            command_args.append(option)
            if input_value(option) is not None:
                command_args.append(input_value(option))
        if command == "cluster":
            # cluster has an additional positional argument <number_of_clusters>
            command_args.append(num_clusters)
            # select only one from "--pdv" and "--support"
            if "--pdv" in selected_options and "--support" in selected_options:
                continue
            if "--pdv" not in selected_options and "--support" not in selected_options:
                continue
            # we cannot select both "--pdv-vis" and "--support-vis"
            if "--pdv-vis" in selected_options and "--support-vis" in selected_options:
                continue
            # we must select only one from "--depth" and "--n-splits"
            if "--depth" in selected_options and "--n-splits" in selected_options:
                continue
            if "--depth" not in selected_options and "--n-splits" not in selected_options:
                continue
        # Run the command, if pass, pass silently. Print the commands that fail
        completed_process = subprocess.run(command_args, capture_output=True)
        if completed_process.returncode != 0:
            if n_failed_tests == 0:
                print("Failed Test(s):")
            print("$", *command_args)
            output_str = completed_process.stdout.decode('utf-8').strip()
            if output_str:
                print(output_str)
            error_str = completed_process.stderr.decode('utf-8').strip()
            if error_str:
                print(error_str)
            n_failed_tests += 1
            if fail_fast:
                break

    if n_failed_tests == 0:
        print("All %s %d/%d tests passed" % (command, len(total_combinations), len(total_combinations)))
    elif not fail_fast:
        print("%d/%d %s tests failed" % (n_failed_tests, len(total_combinations), command))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="empress_cli tester for generating and running combination or arguments")
    parser.add_argument("tests_per_group", type=int)
    args = parser.parse_args()

    run_command("cost-regions", args.tests_per_group)
    run_command("reconcile", args.tests_per_group)
    run_command("histogram", args.tests_per_group)
    run_command("cluster", args.tests_per_group)
