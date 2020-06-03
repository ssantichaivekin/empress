#=============================================================================
# constants

INF = float('inf')

#=============================================================================
# functions

def frange(low, high, numSteps, log=True):
    ''' Return a list of numSteps+1 floating point numbers between low and high
        with uniform step size. '''
    if (not log):
        return [low + (1.0/numSteps) * i * (high-low) for i in range(numSteps+1)]
    else:
##        http://docs.scipy.org/doc/numpy/reference/generated/numpy.logspace.html
##        import math
##        import numpy as np
##        base = 10  # does not matter
##        return np.logspace(math.log(low, base), math.log(high, base), numSteps+1, base=base)
        import math
        base = 10  # does not matter
        low = math.log(low, base)
        high = math.log(high, base)
        y = [low + (1.0/numSteps) * i * (high-low) for i in range(numSteps+1)]
        return [base**x for x in y]

def getBestCV(CVlist, x, y):
    ''' Takes a list, called CVlist, of CostVectors as input, a loss cost (x),
        and a switch cost (y) as input and returns the index into the CVlist,
        the best CV, and the best cost over all solutions in the CVlist.'''
    bestIndex = None                # Best index found so far
    bestCV = None                   # Best CV found so far
    bestCost = INF                  # Best cost found so far
    for i,cv in enumerate(CVlist):
        d, l, s = cv.d, cv.l, cv.s  # Extract d, l, s
        cost = d + l*x + s*y        # Compute the cost 
        if cost < bestCost:         # Update best index and cost
            bestIndex = i
            bestCV = cv
            bestCost = cost
    return bestIndex, bestCV, bestCost

