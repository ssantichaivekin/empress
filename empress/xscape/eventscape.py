#!/usr/bin/env python

# eventcape.py
# Ran Libeskind-Hadas, Jessica Yi-Chieh Wu, Mukul Bansal, November 2013

# python libraries
import time
from collections import *
from operator import itemgetter
import csv

# xscape libraries
try:
    from empress import xscape
except ImportError:
    import sys
    sys.path.append('..')
    import empress.xscape
from empress.xscape import getInput
from empress.xscape import reconcile


def main():
    global CandidateCVlist
    
    print("Eventscape %s" % xscape.PROGRAM_VERSION_TEXT)
    hostTree, parasiteTree, phi, switchLo, switchHi, lossLo, lossHi, outfile = \
        getInput.getInput(outputExtension ="csv")

    while True:
        merge_type = input("[U]nion or [I]ntersection? ")
        if merge_type == "U" or merge_type == "I":
            break
        print("Invalid input.  Please try again.")
    CONFIG.intersection = merge_type == "I"
        
    print("Reconciling trees...")
    startTime = time.time()
    
    print("  Preprocessing...")
    preCVlist = reconcile.reconcile(parasiteTree, hostTree, phi, \
                                    switchLo, switchHi, lossLo, lossHi)
    CandidateCVlist.extend(restrict(preCVlist, \
                                    switchLo, switchHi, lossLo, lossHi))
    print("  Solving...")
    CVlist = reconcileEvents(parasiteTree, hostTree, phi, \
                             switchLo, switchHi, lossLo, lossHi)
    endTime = time.time()
    elapsedTime = endTime- startTime
    print("Elapsed time %.2f seconds" % elapsedTime)
    output(outfile, CVlist, hostTree, switchLo, switchHi, lossLo, lossHi,
           root=parasiteTree["pTop"][1])
    print("Output written to file ", outfile)

def restrict(CVlist, switchLo, switchHi, lossLo, lossHi, regions=None):
    restrictedList = []
    
    if regions is None:
        regions = getRegions(CVlist, switchLo, switchHi, lossLo, lossHi)
    for cv in CVlist:
        if str(cv) in regions:
            if cv not in restrictedList:
                restrictedList.append(cv)
    
    return restrictedList
      
def output(outfile, CVlist, hostTree, switchMin, switchMax, lossMin, lossMax,
           root="Root", regions=None):
    intersection = CONFIG.intersection
    if not intersection:
        global CVallEvents
    else:
        global CVcommonEvents
    
    if regions is None:
        regions = getRegions(CVlist, switchMin, switchMax, lossMin, lossMax)
    ofile = open(outfile, "w")
    writer = csv.writer(ofile, delimiter = ",")
    optimalCVlist = restrict(CVlist, switchMin, switchMax, lossMin, lossMax,
                             regions=regions)
     
    allEvents = set()  # set of all events in optimal solutions in the cost space
    if not intersection:
        allEventsThisCV = defaultdict(set)  # set of all events in this Pareto CV
    for cv in optimalCVlist:
        outputRow = [cv]
        thisCV = cv.toTupleCDSL()

        if not intersection:
            for eh in hostTree:
                key = ("pTop", eh) + thisCV
                events = CVallEvents[key]
                allEventsThisCV[thisCV] |= events
                allEvents |= events
                for event in events:
                    outputRow.append(displayVersion(event, root))
        else:
            events = CVcommonEvents[thisCV]
            allEvents |= events
            for event in events:
                outputRow.append(displayVersion(event, root))
                
        writer.writerow(outputRow)

    eventsWithCounts = []
    if not intersection:
        eventsDict = allEventsThisCV
    else:
        eventsDict = CVcommonEvents
    for event in allEvents:
        eventcount = 0
        for bestCV in optimalCVlist:
            if event in eventsDict[bestCV.toTupleCDSL()]:
                eventcount += 1
        eventsWithCounts.append((event, eventcount))
    eventsWithCounts.sort(key = itemgetter(1), reverse = True)
    maxCounts = len(optimalCVlist)
    for count in range(maxCounts, 0, -1):
        row = ["Events in " + str(count) + " regions"]
        row.extend([displayVersion(event[0], root) for event in eventsWithCounts \
                    if event[1] == count])
        writer.writerow(row)
 
def displayVersion(event, root="Root", sep=" "):
    if event[0] == "pTop": parasiteNode = root
    else: parasiteNode = event[0][1]
    hostNode = event[1][1]
    eventType = event[2]
    if eventType.startswith("loss"):
        eventType = "loss" + sep + eval(eventType[5:].split()[1].strip(")"))
    if eventType.startswith("switch"):
        eventType = "switch" + sep + eval(eventType[10:].split()[1].strip(")"))
    return parasiteNode + sep + hostNode + sep + eventType 
           
if __name__ == '__main__': main()
    
