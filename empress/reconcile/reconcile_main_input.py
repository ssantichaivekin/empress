# reconcile_main_input.py
# Parker Andrews and Alberto Garcia, March 2020
# Main input function for recongraph_tools.py

def get_inputs():
    """ 
    :return: Duplication, Transfer, and Loss Values in that order
    """    
    while True:
        duplication = input("Enter relative cost of a duplication event: ")
        try:
            duplication = int(duplication)
            break
        except ValueError:
            print("Duplication cost must be integer number. Please try again.")
    
    while True:
        transfer = input("Enter relative cost of a transfer event: ")
        try:
            transfer = int(transfer)
            break
        except ValueError:
            print("Transfer cost must be integer number. Please try again.")
    
    while True:
        loss = input("Enter the relative cost of a loss event")
        try:
            loss = int(loss)
            break
        except ValueError:
            print("Loss cost must be integer number. Please try again.")

    return duplication, transfer, loss
