
import itertools
import subprocess
import random

cli_filename = "empress_cli.py"
example_host = "examples/heliconius_host.nwk"
example_parasite = "examples/heliconius_parasite.nwk"
example_mapping = "examples/heliconius_mapping.mapping"

list_of_commands = ["cost-regions", "reconcile", "histogram", "cluster"]
options_for_reconcile = ["-d","-t","-l"]
options_for_cost_regions = ["-dl","-tl","-dh","-th","--log", "--outfile"]
options_for_histogram = ["-d","-t","-l","--histogram","--xnorm","--ynorm","--omit-zeros","--cumulative",\
                         "--csv", "--stats", "--time"]
options_for_cluster = ["-d","-t","-l","--medians","--depth","--n-splits","--pdv-vis","--support-vis",\
                       "--pdv", "--support"]

# copied from https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def input_value(option):
    """Compute an input value for the optional argument"""
    if option in ["-d","-t","-l"]:
        # default value d: 2, t: 3, l:1
        return str(random.choice(range(1, 10, 1)))
    elif option in ["-dl","-tl"]:
        # default value for this option is 1
        return str(random.choice(range(1, 5, 1)))
    elif option in ["-dh","-th"]:
        # default value for this option is 5
        return str(random.choice(range(5, 10, 1)))
    elif option == "--csv":
        return "test_cli_output_csv.csv"
    elif option == "--histogram":
        return "test_cli_output_histogram.pdf"
    elif option == "--outfile":
        return "test_cli_output_cost_regions.pdf"
    elif option in ["--depth", "--n-splits"]:
        return str(random.choice(range(1, 10, 1)))
    else:
        return ""

def run_command(command, max_combinations_to_test, reverse=False):
    """
    :param command <str>: the functionality to test
    :param max_combinations_to_test <int>: the maximum number of combinations of optional arguments to test
    :param reverse <bool>: if reverse is True, we test the combinations with the most # of elements first
                           if reverse is False, we test the combinations with the least # of elements first
    """
    if command == "cost-regions":
        options_for_command = options_for_cost_regions
    elif command == "reconcile":
        options_for_command = options_for_reconcile
    elif command == "histogram":
        options_for_command = options_for_histogram
    elif command == "cluster":
        options_for_command = options_for_cluster
        num_clusters = str(random.choice(range(1, 10, 1)))

    total_combinations = list(powerset(options_for_command))
    if reverse:
        total_combinations.reverse()

    num_combinations_tested = 0
    for selected_options in total_combinations:
        if num_combinations_tested >= max_combinations_to_test:
            break
        # example command : python empress_cli.py reconcile <host_file> <parasite_file> <mapping_file>
        command_string = "python {} {} {} {} {} ".format(cli_filename, command, example_host, \
                                                     example_parasite, example_mapping)
        if command == "cluster":
            # cluster has an additional positional argument <number_of_clusters>
            command_string += num_clusters + " "
            # we must select only one from "--pdv" and "--support"
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
        for option in selected_options:
            command_string += option + " " + input_value(option) + " "
        result = subprocess.check_call(command_string, stdin=None, stdout=None, stderr=None, shell=True)
        num_combinations_tested += 1
        print("command_string: ", command_string, " result code: ", result)

run_command("cost-regions", 5, True)
run_command("reconcile", 5, False)
run_command("histogram", 5, True)
run_command("cluster", 5, True)