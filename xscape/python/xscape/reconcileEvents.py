# reconcileEvents.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013
# memoized Pareto tree reconciliation software for untimed trees

# A tree is represented as a dictionary of key-value pairs where a key is an
# edge name and the value is a tuple of the form
# (start vertex, end vertex, left child edge name, right child edge name)
# An edge name may be None.  The "dummy" edge leading to the root of the
# parasite tree must be named "pTop".

# python libraries
from collections import *
import copy

# xscape libraries
from common import *
from CostVector import *

# The three dictionaries below correspond to the A, C, and Best DP tables
# described in the technical report.

Amemo = {}
Cmemo = {}
Bestmemo = {}

# The Ancestors and Descendants dictionaries are precomputed in the reconcile
# function and allow the switch function to determine the valid landing sites
# for a switch.

Ancestors = {}
Descendants = {}

# The switchLo, switchHi, lossLo, and lossHi values are the user-specified
# low and high ranges for the switch and loss costs, relative to the unit
# cost of duplication.  They are shown here only for clarity.  

switchLo = None
switchHi = None
lossLo = None
lossHi = None

# The CVevents global dictionary has keys that are tuples of the form
# (ep, eh, eventType c, d, s, l) and values that are all the events in 
# that solution of the form (ep', eh', eventTypeString) associated with 
# ep on eh with cost vector <c, d, s, l>
CVevents = defaultdict(set)
CVallEvents = defaultdict(set)
CandidateCVlist = list()

# looking at union OR intersection of events?
class Config:     # to get around immutable globals
    pass
CONFIG = Config()
CVseen = defaultdict(bool) # Initially all values are False by default
CVcommonEvents = defaultdict(set)

# This is the main function for this file.  It seeks to find the best
# reconciliation for the parasite tree, rooted at every possible edge of the
# host tree.
def reconcileEvents(parasiteTree, hostTree, phi, smin, smax, lmin, lmax):
    ''' Takes dictionary representations of the parasite tree, host tree
        and phi as input and returns a list of the Pareto optimal solutions. '''
    
    global switchLo, switchHi, lossLo, lossHi
    switchLo = smin; switchHi = smax; lossLo = lmin; lossHi = lmax

    ancestorsAndDescendants(hostTree) # Set the Ancestors and Descendants
    
    solutions = []
    for eh in hostTree:
        solutions.extend(C(parasiteTree, hostTree, phi, "pTop", eh))
    return(paretoFilter(solutions))

# The A and C functions implement the A and C DPs in the HMC Tech Report
# "Faster Dynamic Programming Algorithms for the Cophylogeny Reconstruction
# Problem" available at www.cs.hmc.edu/~hadas/jane/TechReportCS-2011-1.pdf
# This implementation uses memoization rather than DP.

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

            cospeciation1 = merge(C(parasiteTree, hostTree, phi, \
                                    epLeftChild, ehLeftChild), \
                                  C(parasiteTree, hostTree, phi, \
                                    epRightChild, ehRightChild), \
                                  ep, eh, epLeftChild, ehLeftChild, \
                                  epRightChild, ehRightChild, "cospeciation")

            cospeciation2 = merge(C(parasiteTree, hostTree, phi, \
                                    epLeftChild, ehRightChild), \
                                  C(parasiteTree, hostTree, phi, \
                                    epRightChild, ehLeftChild), \
                                  ep, eh, epLeftChild, ehRightChild, \
                                  epRightChild, ehLeftChild, "cospeciation")

            cospeciation = cospeciation1 + cospeciation2
            
        # Loss
        loss1 = lossmerge(ep, eh, ehLeftChild, \
                     C(parasiteTree, hostTree, phi, ep, ehLeftChild))
                       
        loss2 = lossmerge(ep, eh, ehRightChild, \
                     C(parasiteTree, hostTree, phi, ep, ehRightChild))

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
        
        duplicate = merge(C(parasiteTree, hostTree, phi, epLeftChild, eh), \
                          C(parasiteTree, hostTree, phi, epRightChild, eh), \
                            ep, eh, epLeftChild, eh, \
                            epRightChild, eh, "duplication")
    
        switch = []
        leftCVlist = C(parasiteTree, hostTree, phi, epLeftChild, eh)
        rightPairs = allSwitches(parasiteTree, hostTree, phi, epRightChild, eh)
        for (switchEdge, rightCVlist) in rightPairs:
            switch.extend(merge(leftCVlist, rightCVlist, \
                                ep, eh, epLeftChild, eh, epRightChild, \
                                switchEdge, "switch"))
            
        leftCVlist = C(parasiteTree, hostTree, phi, epRightChild, eh)
        rightPairs = allSwitches(parasiteTree, hostTree, phi, epLeftChild, eh)
        for (switchEdge, rightCVlist) in rightPairs:
            switch.extend(merge(leftCVlist, rightCVlist, \
                                ep, eh, epRightChild, eh, epLeftChild, \
                                switchEdge, "switch"))
               
    output = paretoFilter(passThrough + duplicate + switch)
    Cmemo[(ep, eh)] = output

    return output

def merge(CVlist1, CVlist2, ep, eh, epChild1, ehChild1, epChild2, \
          ehChild2, eventType):
    ''' Given two lists of CostVectors, returns a new list of CostVectors, each
        of which is the sum of a pair of vectors from the two given lists.'''
    global CVevents
    global CVallEvents
    global CandidateCVlist

    intersection = CONFIG.intersection
    if intersection:
        global CVseen
        global CVcommonEvents
        
    output = []
    for v in CVlist1:
        for w in CVlist2:
            if eventType == "cospeciation":
                newCV = CostVector(1, 0, 0, 0, 1) + v + w
            elif eventType == "duplication":
                newCV = CostVector(0, 1, 0, 0, 1) + v + w
            else:   # eventType == "switch":
                newCV = CostVector(0, 0, 1, 0, 1) + v + w
            keepnewCV = True
            for cv in CandidateCVlist:
                if cv < newCV: 
                    keepnewCV = False
                    break
    
            if keepnewCV:
                output.append(newCV)
                vsoln = (epChild1, ehChild1) + v.toTupleCDSL()
                wsoln = (epChild2, ehChild2) + w.toTupleCDSL()
                if eventType == "switch": eventType = "switch to "+str(ehChild2)
                nswe = (ep, eh, eventType) + newCV.toTupleCDSL()
                ns = (ep, eh) + newCV.toTupleCDSL()
                CVevents[nswe].add(nswe)
                CVevents[nswe] = CVevents[nswe].\
                                 union(CVallEvents[vsoln]).\
                                 union(CVallEvents[wsoln])
                CVallEvents[ns] = CVallEvents[ns].union(CVevents[nswe])

                if intersection:
                    key = newCV.toTupleCDSL()
                    if CVseen[key]:
                        CVcommonEvents[key] = CVcommonEvents[key].\
                                              intersection(CVevents[nswe])
                    else:
                        CVcommonEvents[key] = CVevents[nswe]
                        CVseen[key] = True
    return output

def lossmerge(ep, eh, ehChild, CVlist):
    global CVevents
    global CVallEvents
    global CandidateCVlist

    intersection = CONFIG.intersection
    if intersection:
        global CVseen
        global CVcommonEvents
    
    output = []
    for v in CVlist:
        newCV = CostVector(0, 0, 0, 1, 1) + v
        keepnewCV = True
        for cv in CandidateCVlist:
            if cv < newCV: 
                keepnewCV = False
                break
    
        if keepnewCV:
            output.append(newCV)
            vsoln = (ep, ehChild) + v.toTupleCDSL()
            nswe = (ep, eh, "loss "+str(ehChild)) + newCV.toTupleCDSL()
            ns = (ep, eh) + newCV.toTupleCDSL()
            CVevents[nswe].add(nswe)
            CVevents[nswe] = CVevents[nswe].union(CVallEvents[vsoln])
            CVallEvents[ns] = CVallEvents[ns].union(CVevents[nswe])

            if intersection:
                key = newCV.toTupleCDSL()
                if CVseen[key]:
                    CVcommonEvents[key] = CVcommonEvents[key].\
                                              intersection(CVevents[nswe])
                else:
                    CVcommonEvents[key] = CVevents[nswe]
                    CVseen[key] = True
    return output
    
def allSwitches(parasiteTree, hostTree, phi, ep, eh):
    ''' Returns the list of all CostVectors in which the given parasite edge ep
        switches to all possible host edges. '''
    global Bestmemo
    if (ep, eh) in Bestmemo: return Bestmemo[(ep, eh)]
    output = []
    for switchEdge in hostTree:     # for every possible host edge
        if switchEdge != eh and switchEdge not in Ancestors[eh] and \
           switchEdge not in Descendants[eh]:
            output.append((switchEdge, \
                               C(parasiteTree, hostTree, phi, ep, switchEdge)))
    Bestmemo[(ep, eh)] = output
    return output

def paretoFilter(CVlist):
    ''' Returns the Pareto front for the given list of CostVectors. '''
    CVlist = CVfilter(CVlist)
    if CVlist == []: return []
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
        LUB = min([cv.d + cv.l * lossHi + cv.s * switchHi for cv in CVlist])
        output = []
        for cv in CVlist:
            mincost = cv.d + cv.l * lossLo + cv.s * switchLo 
            if mincost <= LUB:
                output.append(cv)
        return output
            
def coalesceDuplicates(CVlist):
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
