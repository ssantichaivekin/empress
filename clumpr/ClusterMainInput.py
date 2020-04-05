# ClumsterMainInput.py
# Dave Makhervaks, March 2020
# Main input function for ClumperMain

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

    while True:
        cluster = input("Enter how many clusters to create: ")
        try:
            inputs["k"] = int(cluster)
            break
        except ValueError:
            print("Cluster number must be integer number. Please try again.")

   
    inputs.update(getMutuallyExclusiveInput())
    inputs.update(getOptionalInput())

    cost_suffix = ".{}-{}-{}".format(duplication, transfemdr, loss)
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

def getMutuallyExclusiveInput():
    """ 
    :return: dictionary of arguments where key is parameter name and value is parameter value.
    """
    inputs = {}
    # Specifies how far down to go when finding splits
    while True:
        # requires, d or n!
        depth_or_n = input("Please type 'd' if you want to enter depth, or 'n' for nmprs")
        if (depth_or_n not in ('d', 'n')):
            print("Please enter 'd' or 'n'")
        else:
            break

    if (depth_or_n == 'd'):
        while True:
            depth = input("How far down the graph to consider even splits.")
            try:
                inputs["depth"] = int(depth)
                break
            except ValueError:
                print("Depth must be an integer number. Please try again.")
    else:
        while True:
            nmprs = input("How many MPRs to consider.")
            try:
                inputs["nmprs"] = int(nmprs)
                break
            except ValueError:
                print("NMPRs must be an integer number. Please try again.")

    # What visualizations to produce
    while True:
        # does not require visualization
        vis_type = input("Please type 'p' for visualizing using PDV, 'h' for histograms, and 'n' for none.")
        if (vis_type not in ('p','h','n')):
            print("Please enter 'p', 'h', or 'n'")
        else:
            break

    if (vis_type == 'p'):
        inputs["pdv-vis"] = True
    elif (vis_type == 'h'):
        inputs["support-vis"] = True
        
    
    # Which objective function to use
    while True:
        # requires, p or s!
        score = input("Please type 'p' for using weighted average distance to evaluate clusters, or 's' for using weighted event support")
        if (score not in ('p','s')):
            print("Please enter 'p' or 's'")
        else:
            break

    if (score == 'p'):
        inputs["pdv"] = True
    else:
        inputs["support"] = True

    return inputs

def getOptionalInput():
    """ 
    :return: dictionary of arguments where key is parameter name and value is parameter value.
    """
    inputs = {}
    valid_params = ["medians"]
    for param in valid_params:
        inputs[param] = None

    print("Enter additional input in the form <parameter name> <value>")
    print("Enter 'Done' when you have no additional input to enter.")
    print("Enter '?' if you would like to see additional input options.")
    while True:
        user_input = input().split()
        if user_input[0] == "Done":
            break
        elif user_input[0] == "?":
            print_usage()
        elif user_input[0] in valid_params:
            inputs[user_input[0]] = True
        else:
            print("That is not a valid parameter name. Please try again.")
    
    return inputs
        
def print_usage():
    """
    Print information on all optional parameter inputs.
    """
    data = [
        ("medians", "Whether or not to print out medians for each cluster."),
    ]
    col_width = max(len(x) for x,y in data) + 2
    for name, hint in data:
        print(name.ljust(col_width) + " " + hint)
