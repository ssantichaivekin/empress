# reconcile.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013

# Memoized Pareto tree reconciliation dynamic programming solver for 
# untimed trees.

# Implements the dynamic programming algorithm described in HMC Tech Report
# "Faster Dynamic Programming Algorithms for the Cophylogeny Reconstruction
# Problem" available at www.cs.hmc.edu/~hadas/jane/TechReportCS-2011-1.pdf
# This implementation uses memoization rather than DP.

# A tree is represented as a dictionary of key-value pairs where a key is an
# edge name and the value is a tuple of the form
# (start vertex, end vertex, left child edge name, right child edge name)
# An edge name may be None.  The "dummy" edge leading to the root of the
# parasite tree, denoted e^P in the technical report, must be named "pTop".

# python libraries
from collections import *

# xscape libraries
from common import *
from CostVector import *

# The three dictionaries below correspond to the A, C, and Best DP tables
# described in the technical report.  These are set to None here but initialized
# in the reconcile function.  They need to be reset before each run since
# they change for each sigscape randomization trial.

Amemo = None
Cmemo = None
Bestmemo = None

# The Ancestors and Descendants dictionaries are precomputed in the reconcile
# function and allow the switch function to determine the valid landing sites
# for a switch. 

Ancestors = None
Descendants = None

# The switchLo, switchHi, lossLo, and lossHi values are the user-specified
# low and high ranges for the switch and loss costs, relative to the unit
# cost of duplication.  They are shown here only for clarity.  

switchLo = None
switchHi = None
lossLo = None
lossHi = None

# This is the main function for this file.  It seeks to find the best
# reconciliation for the parasite tree, rooted at every possible edge of the
# host tree.
def reconcile(parasiteTree, hostTree, phi, smin, smax, lmin, lmax):
    ''' Takes dictionary representations of the parasite tree, host tree
        and phi as input and returns a list of the Pareto optimal solutions. '''
            
    global switchLo, switchHi, lossLo, lossHi
    global Amemo, Cmemo, Bestmemo
    global Ancestors, Descendants
    Amemo = {}; Cmemo = {}; Bestmemo = {}  # These need to be reset on each run
    Ancestors = {}; Descendants = {}
    
    switchLo = smin; switchHi = smax; lossLo = lmin; lossHi = lmax
    
    ancestorsAndDescendants(hostTree) # Set the Ancestors and Descendants
        
    solutions = []
    for eh in hostTree:
        solutions.extend(C(parasiteTree, hostTree, phi, "pTop", eh))
    return paretoFilter(solutions)

def A(parasiteTree, hostTree, phi, ep, eh):
    ''' The A table for the dynamic program. '''
    
    global Amemo
    
    if (ep, eh) in Amemo: return Amemo[(ep, eh)]

    if tipEdge(eh, hostTree):
        if tipEdge(ep, parasiteTree) and \
           phi[endVertex(ep, parasiteTree)] == endVertex(eh, hostTree):
            return [CostVector(0, 0, 0, 0, 1)]
        else:
            return [CostVector(INF, INF, INF, INF, 0)]
    else:
        ehLeftChild = leftChildEdge(eh, hostTree)
        ehRightChild = rightChildEdge(eh, hostTree)

        # Cospeciation
        if tipEdge(ep, parasiteTree):
            cospeciation = [CostVector(INF, INF, INF, INF, 0)]
        else:
            epLeftChild = leftChildEdge(ep, parasiteTree)
            epRightChild = rightChildEdge(ep, parasiteTree)

            cospeciation1 = CostVector(1, 0, 0, 0, 1) * \
              merge(C(parasiteTree, hostTree, phi, epLeftChild, ehLeftChild), \
                    C(parasiteTree, hostTree, phi, epRightChild, ehRightChild))

            cospeciation2 = CostVector(1, 0, 0, 0, 1) * \
              merge(C(parasiteTree, hostTree, phi, epLeftChild, ehRightChild), \
                    C(parasiteTree, hostTree, phi, epRightChild, ehLeftChild)) \

            cospeciation = cospeciation1 + cospeciation2
            
        # Loss
        loss1 = CostVector(0, 0, 0, 1, 1) * \
                C(parasiteTree, hostTree, phi, ep, ehLeftChild)

        loss2 = CostVector(0, 0, 0, 1, 1) * \
                C(parasiteTree, hostTree, phi, ep, ehRightChild)

        loss = loss1 + loss2
        
        output = paretoFilter(cospeciation + loss) 
        Amemo[(ep, eh)] = output
        return output
        
def C(parasiteTree, hostTree, phi, ep, eh):
    ''' The C table for the dynamic program. '''
    
    global Cmemo
    
    if (ep, eh) in Cmemo: return Cmemo[(ep, eh)]
    
    # Option 1:  Pass through
    passThrough = A(parasiteTree, hostTree, phi, ep, eh)
    
    if tipEdge(ep, parasiteTree):   # The options below don't apply to tips
        return passThrough

    else:
        epLeftChild = leftChildEdge(ep, parasiteTree)
        epRightChild = rightChildEdge(ep, parasiteTree)
    
        # Option 2:  Duplicate here
        duplicate = CostVector(0, 1, 0, 0, 1) * \
                    merge(C(parasiteTree, hostTree, phi, epLeftChild, eh), \
                          C(parasiteTree, hostTree, phi, epRightChild, eh)) 
    
        # Option 3:  Switch here

        switch1 = CostVector(0, 0, 1, 0, 1) * \
                  merge(C(parasiteTree, hostTree, phi, epLeftChild, eh), \
                        switches(parasiteTree, hostTree, phi, epRightChild, eh))

        switch2 = CostVector(0, 0, 1, 0, 1) * \
                  merge(C(parasiteTree, hostTree, phi, epRightChild, eh), \
                        switches(parasiteTree, hostTree, phi, epLeftChild, eh))

        switch = switch1 + switch2
        
    output = paretoFilter(passThrough + duplicate + switch) 
    Cmemo[(ep, eh)] = output
    return output

def merge(CVlist1, CVlist2):
    ''' Given two lists of CostVectors, returns a new list of CostVectors, each
        of which is the sum of a pair of vectors from the two given lists.'''
    output = []
    for v in CVlist1:
        for w in CVlist2:
            output.append(v+w)
    return output

def switches(parasiteTree, hostTree, phi, ep, eh):
    ''' Returns the list of all CostVectors in which the given parasite edge ep
        switches to all possible host edges. '''
        
    global Bestmemo
    global Ancestors, Descendants
    
    if (ep, eh) in Bestmemo: return Bestmemo[(ep, eh)]
    output = []
    for switchEdge in hostTree:     # for every possible host edge
        if switchEdge != eh and switchEdge not in Ancestors[eh] and \
           switchEdge not in Descendants[eh]:
            output.extend(C(parasiteTree, hostTree, phi, ep, switchEdge))
    Bestmemo[(ep, eh)] = output
    return output

def paretoFilter(CVlist):
    ''' Returns the Pareto front for the given list of CostVectors. '''
    CVlist = CVfilter(CVlist)
    uniqueCVlist = coalesceDuplicates(CVlist)
    uniqueCVlist.sort(CostVector.lex)
    if len(uniqueCVlist) == 1: return uniqueCVlist
    lexlist = [uniqueCVlist[0]]
    for i in range(1, len(uniqueCVlist)):
        predecessor = uniqueCVlist[i-1]
        current = uniqueCVlist[i]
        if predecessor.d < current.d or predecessor.s < current.s:
            lexlist.append(current)
    output = []
    for v in lexlist:
        if minimal(v, CVlist): output.append(v)
    return output        

def CVfilter(CVlist):
    ''' Filter the CVlist to a subset that removes those cost vectors that
        cannot be optimal in the given cost range. '''
        
    global switchLo, switchHi, lossLo, lossHi 
    
    if CVlist == []: return []
    else:
        LUB = min([cv.d + cv.s * switchHi + cv.l * lossHi for cv in CVlist])
        output = []
        for cv in CVlist:
            mincost = cv.d + cv.l * lossLo + cv.s * switchLo 
            if mincost <= LUB:
                output.append(cv)
        return output
            
def coalesceDuplicates(CVlist):
    ''' Takes a cost vector list as input and returns a list with duplicates
        removed and with event counts updated accordingly. '''
    counts = {}
    for cv in CVlist:
        cvtup = cv.toTupleCDSL()
        count = cv.count
        if cvtup not in counts:
            counts[cvtup] = count
        else:
            counts[cvtup] = counts[cvtup] + count
    output = []
    for entry in counts:
        entryWithCounts = entry + (counts[entry],)
        output.append(tupleToCV(entryWithCounts))
    return output

def tupleToCV(entry):
    return CostVector(entry[0], entry[1], entry[2], entry[3], entry[4])

def minimal(v, CVlist):
    ''' Returns True if v is a minimal element of the CostVector list. '''
    for w in CVlist:
        if w < v: return False
    return True

def descendants(edge, tree):
    ''' returns the list of descendant edges of the given edge in the
        given tree.'''
    if tipEdge(edge, tree): return []
    else: return [leftChildEdge(edge, tree), rightChildEdge(edge, tree)] + \
                  descendants(leftChildEdge(edge, tree), tree) + \
                  descendants(rightChildEdge(edge, tree), tree)
                  
def ancestorsAndDescendants(tree):
    ''' Returns a two dictionaries D and A, where D[e] is the list
        of descendant edges of e and A[e] is the list of ancestral edges
        of e. '''
    global Ancestors, Descendants
    
    # First, compute all the descendants
    for e in tree:
        Descendants[e] = descendants(e, tree)
    # Next, compute ancestors 
    for e in tree: Ancestors[e] = []  # initialize A dictionary      
    for e in tree:
        for d in Descendants[e]: # d descendant of e => e ancestor of d
            Ancestors[d].append(e)
        
def tipEdge(edge, tree):
    ''' returns True if the edge terminates at a tip  '''
    return leftChildEdge(edge, tree) == None  # This edge has no edge children
    
def startVertex(edge, tree):
    ''' returns the start vertex of an edge '''
    return tree[edge][0]

def endVertex(edge, tree):
    ''' returns the end vertex of an edge '''
    return tree[edge][1]

def leftChildEdge(edge, tree):
    ''' returns the left child edge of the given edge '''
    return tree[edge][2]

def rightChildEdge(edge, tree):
    ''' returns the right child edge of the given edge '''
    return tree[edge][3]
