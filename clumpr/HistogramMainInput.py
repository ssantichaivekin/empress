# HistogramMainInput.py
# Adrian Garcia, March 2020
# Main input function for HistogramMain

def getInput(filename):
    """ 
    :param filename: the path to a .newick file with the input trees and tip mapping.
    :return: dictionary of arguments where key is parameter name and value is parameter value.
    """
    
    inputs = {}
    # Get input file name and try to open it
    while True:
        duplication = input("Enter relative cost of a duplication event: ")
        try:
            inputs["d"] = int(duplication)
            break
        except ValueError:
            print("Duplication cost must be integer number. Please try again.")
    
    while True:
        transfer = input("Enter relative cost of a transfer event: ")
        try:
            inputs["t"] = int(transfer)
            break
        except ValueError:
            print("Transfer cost must be integer number. Please try again.")
    
    while True:
        loss = input("Enter relative cost of a loss event: ")
        try:
            inputs["l"] = int(loss)
            break
        except ValueError:
            print("Loss cost must be integer number. Please try again.")

    inputs.update(getOptionalInput())

    cost_suffix = ".{}-{}-{}".format(duplication, transfer, loss)
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

def getOptionalInput():
    """ 
    :return: dictionary of arguments where key is parameter name and value is parameter value.
    """
    inputs = {}
    string_params = ("histogram", "time")
    bool_params = ("xnorm", "ynorm", "omit_zeros", "cumulative", "stats", "time")
    for param in string_params:
        inputs[param] = "unset"
    for param in bool_params:
        inputs[param] = True

    print("Enter additional input in the form <parameter name> <value>")
    print("Enter 'Done' when you have no additional input to enter.")
    print("Enter '?' if you would like to see additional input options.")
    while True:
        user_input = input().split()
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
    
    return inputs
        
def print_usage():
    """
    Print information on all optional parameter inputs.
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
