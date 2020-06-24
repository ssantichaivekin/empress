# histogram_main_input.py
# Adrian Garcia, March 2020
# Main input function for HistogramMain
from pathlib import Path

def getInput(filename, d, t, l, args):
    """ 
    Get additional input from user for computing and saving the PDV
    :param filename <str> - the path to a .newick file with the input trees and tip mapping
    :param d <float> - the cost of a duplication
    :param t <float> - ^^ transfer
    :param l <float> - ^^ loss
    :param args <dict str->str> - dictionary that contains all parameters needed 
    to compute, save, and/or output the PDV
    :return inputs <dict str->str> - all input from user for computing and saving the PDV
    """
    
    inputs = {}
    inputs.update(args)
    getOptionalInput(inputs)

    cost_suffix = ".{}-{}-{}".format(d, t, l)
    # If args is unset, use the original .newick file path but replace .newick with .pdf
    if inputs["histogram"] is None:
        inputs["histogram"] = str(filename.with_suffix(cost_suffix + ".pdf"))
    # If it wasn't set by the arg parser, then set it to None (the option wasn't present)
    elif inputs["histogram"] == "unset":
        inputs["histogram"] = None
    #TODO: check that the specified path has a matplotlib-compatible extension?
    # Do the same for .csv
    if inputs["csv"] is None:
        inputs["csv"] = str(filename.with_suffix(cost_suffix + ".csv"))
    elif inputs["csv"] == "unset":
        inputs["csv"] = None
    # If it was user-specified, check that it has a .csv extension
    else:
        c = Path(inputs["csv"])
        assert c.suffix == ".csv"
    return inputs

def getOptionalInput(inputs):
    """ 
    Add additional arguments to 'inputs' dictionary
    :param inputs <dict str->str> - dictionary that contains given parameters to
    compute, save, and/or output the PDV
    :return None - inputs is simply updated with new information
    """
    string_params = ("histogram", "time", "csv")
    bool_params = ("xnorm", "ynorm", "omit_zeros", "cumulative", "stats", "time")

    for param in string_params:
        if param not in inputs:
            inputs[param] = "unset"
    for param in bool_params:
        if param not in inputs:
            inputs[param] = True

    print("Enter additional input in the form <parameter name> <value>")
    print("Enter 'Done' when you have no additional input to enter.")
    print("Enter '?' if you would like to see additional input options.")
    while True:
        user_input = input(">> ").split()
        param = user_input[0]
        value = None
        if len(user_input) > 1:
            value = " ".join(user_input[1:])

        if param == "Done":
            break
        elif param == "?":
            print_usage()
        elif param in bool_params:
            if value[0] in ('y', 'Y', 'n', 'N'):
                inputs[param] = value[0] in ('y', 'Y')
            else:
                print("Value must begin with Y, y, N, or n.  Please try again.")
        elif param in string_params:
            inputs[param] = value
        else:
            print("That is not a valid parameter name. Please try again.")
        
def print_usage():
    """
    Print information on all optional parameter inputs
    """
    data = [
        ("histogram", ("Output the histogram at the path provided. "
        "If no filename is provided, outputs to a filename based on the input .newick file.")),
        ("xnorm", "Normalize the x-axis so that the distances range between 0 and 1."),
        ("ynorm", "Normalize the y-axis so that the histogram is a probability distribution."),
        ("omit_zeros", ("Omit the zero column of the histogram, "
        "which will always be the total number of reconciliations.")),
        ("cumulative", "Make the histogram cumulative."),
        ("csv", ("Output the histogram as a .csv file at the path provided. "
        "If no filename is provided, outputs to a filename based on the input .newick file.")),
        ("stats", ("Output statistics including the total number of MPRs, "
        "the diameter of MPR-space, and the average distance between MPRs.")),
        ("time", "Time the diameter algorithm.")
    ]
    col_width = max(len(x) for x,y in data) + 2
    for name, hint in data:
        print(name.ljust(col_width) + " " + hint)