#!/usr/bin/env python

# sigscape.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013

# python libraries
import random
import sys
import time
from multiprocessing import Process, Queue  # For multiprocessing random trials

# xscape libraries
from empress import xscape
from empress.xscape import reconcile
from empress.xscape import plotsig


DOTS = 100  # DOTS data points per dimension;
            # Increase this value for higher resolution plottin

def getSeed(prompt):
    while True:
        try:
            s = input(prompt)
            if s == "":
                return None
            else:
                val = int(s)
            return val
        except ValueError:
            print("Non-numeric input.  Please try again.")

def seqTrials(parasiteTree, hostTree, tip_mapping, numTrials,
              switchLo, switchHi, lossLo, lossHi,
              verbose=True):
    ''' Perform numTrials randomization trials sequentially.  Although
        parTrials could be used to do this too, this function doesn't
        require the multiprocessing package and thus may be preferable
        to some users in some situation.'''
    parasiteTips, hostTips = getTipLists(parasiteTree, hostTree, tip_mapping)
    output = []
    for t in range(numTrials):
        if verbose:
            print(".", end=' ')      # Progress indicator!
        sys.stdout.flush()
        newPhi = randomizeTips(parasiteTips, hostTips)
        output.append(reconcile.reconcile(parasiteTree, hostTree, newPhi,
                                          switchLo, switchHi, lossLo, lossHi))
    
    if verbose:
        print()               # Newline
    return output

def parTrials(parasiteTree, hostTree, tip_mapping, numTrials,  \
              switchLo, switchHi, lossLo, lossHi, result,
              verbose=True):
    ''' Perform numTrials randomization trials in one process. '''
    parasiteTips, hostTips = getTipLists(parasiteTree, hostTree, tip_mapping)
    output = []
    for t in range(numTrials):
        if verbose:
            print(".", end=' ')      # Progress indicator!
            sys.stdout.flush()
        newPhi = randomizeTips(parasiteTips, hostTips)
        output.append(reconcile.reconcile(parasiteTree, hostTree, newPhi, \
                                          switchLo, switchHi, lossLo, lossHi))
    result.put(output)

def parallelTrials(parasiteTree, hostTree, tip_mapping, numTrials, numProcs, \
                   switchLo, switchHi, lossLo, lossHi):
    ''' This form of dumb parallelism is required to avoid overflowing
        buffers due to a Python bug. See the stackoverflow.com
        entry 11854519.  When that bug is fixed, the total number
        of trials can be divided over the given number of Procs.'''
        
    output = []
    result = Queue()
    for trial in range(0, numTrials, numProcs):
        procs = []
        for p in range(numProcs):
            proc = Process(target=parTrials, \
                       args = (parasiteTree, hostTree, tip_mapping, 1,\
                               switchLo, switchHi, lossLo, lossHi, result))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
        while not result.empty():
            output.extend(result.get())
    return output
    
def getTipLists(parasiteTree, hostTree, tip_mapping):
    ''' Return the lists of tips in the given parasite and host trees.'''
    parasiteTips = list(tip_mapping.keys())
    hostTips = []
    for p in parasiteTips:
        h = tip_mapping[p]
        if not h in hostTips: hostTips.append(h)
    return parasiteTips, hostTips

def randomizeTips(parasiteTips, hostTips):
    ''' Takes a list of parasiteTips and a list of hostTips as input and
        returns a random tip mapping dictionary that maps each parasite tip
        to a random host tip such that each host tip gets at least one \
        parasite tip mapped onto it.'''
    random.shuffle(hostTips)        # shuffle hostTips list in place
    random.shuffle(parasiteTips)    # shuffle parasiteTips list in place
    randomPhi = {}
    numPtips = len(parasiteTips)
    numHtips = len(hostTips)
    # Map parasite tips to host tips to ensure that every host tip has
    # an associated parasite tip.
    for i in range(0, numHtips):    
        randomPhi[parasiteTips[i]] = hostTips[i]
    # Map the remaining parasite tips at random to the hostTips
    for j in range(numHtips, numPtips):
        randomPhi[parasiteTips[j]] = random.choice(hostTips)
    return randomPhi
