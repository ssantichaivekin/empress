# input.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013
# Main input function for xscape tools

# xscape libraries
from .common import *
from .newickFormatReader import *

def getInput(outputExtension, allowEmptyOutfile=False):
    """ outputExtension is the output file extension (e.g, pdf or csv) """
    
    # Get input file name and try to open it
    # while True:
    #     fileName = input("Enter .newick input file name: ")
    #     if fileName.endswith(".newick"):
    #         try:
    #             fileHandle = open(fileName, 'r')
    #             break
    #         except IOError:
    #             print("Error reading file.  Please try again.")
    #     else:
    #         print("File name must end in .newick.  Please try again.")
    
    # hostTree, parasiteTree, phi = newickFormatReader(fileHandle)
    # fileHandle.close()

    # Get output file name
    while True:
        if allowEmptyOutfile:
            outfile = input("Enter ." + outputExtension + " name for output file (or Return): ")
            if outfile == "": break
        else:
            outfile = input("Enter ." + outputExtension + " name for output file: ")
        if outfile.endswith(outputExtension):
            break
        else:
            print("File name must end in ." + outputExtension + ".  Please try again.")   
    
    # Get parameter value ranges            
    switchLo = floatInput("Enter transfer low value: ", min_val=0)
    switchHi = floatInput("Enter transfer high value: ", min_val=switchLo)
    lossLo = floatInput("Enter loss low value: ", min_val=0)
    lossHi = floatInput("Enter loss high value: ", min_val=lossLo)
    
    #return hostTree, parasiteTree, phi, switchLo, switchHi, lossLo, lossHi, outfile
    return switchLo, switchHi, lossLo, lossHi, outfile

def floatInput(prompt, min_val=-INF, max_val=INF):
    return numericInput(prompt, "float", min_val, max_val)

def intInput(prompt, min_val=-INF, max_val=INF):
    return numericInput(prompt, "int", min_val, max_val)

def numericInput(prompt, data_type, min_val=-INF, max_val=INF):
    ''' Query user for input and by displaying the prompt string and then
        return that input as either a float or an int, depending on whether
        the given dataType is "float" or "int" '''
    while True:
        try:
            if data_type == "float":
                val = float(input(prompt))
            elif data_type == "int":
                val = int(input(prompt))
            else:
                raise Exception("invalid data_type")
            
            if (val < min_val) or (val > max_val):
                print("Input falls outside valid range.  Please try again.")
            return val
        except ValueError:
            print("Non-numeric input.  Please try again.")

def boolInput(prompt):
    '''Query user for Y/N input'''
    while True:
        val = input(prompt)
        if val[0] in ['y', 'Y', 'n', 'N']:
            break
        else:
            print("Input must begin with Y, y, N, or N.  Please try again.")
    return val[0] == 'Y' or val[0] == 'y' 

