# plotcosts.py
# Ran Libeskind-Hadas, October 2013
# Plots the cost space using a matplotlib/pyplot

# python libraries
import random
import collections

# matplotlib libraries
from matplotlib import pyplot as plt

# xscape libraries
from empress.xscape.common import frange, getBestCV
from empress.xscape.CostVector import CostVector

def plotcosts(CVlist, switchMin, switchMax, dupMin, dupMax, steps, outfile,
              log=True, display=False):
    ''' Plots the cost space for the given CVlist of CostVectors.  The x-axis
        represents dup cost (relative to unit cost for loss) and
        the y-axis represents switch cost (relative to unit cost for
        duplication).  The x-range is from dupMin to dupMax and the
        y-range is from switchMin to switchMax.  Draws steps dots in each
        dimension. '''
    numVectors = len(CVlist)
    colorMap = buildColors(numVectors)

    print("New version")
    plotted = []    # Store list of CVlist indices that are optimal in our range
    if log:
        plt.xscale('log')
        plt.yscale('log')
    plt.axis([dupMin, dupMax, switchMin, switchMax])
    plt.xlabel("Duplication cost relative to loss")
    plt.ylabel("Transfer cost relative to loss")
    
    # process
    pts = collections.defaultdict(list)  # key = bestIndex
    for x in frange(dupMin, dupMax, steps, log=log):
        for y in frange(switchMin, switchMax, steps, log=log):
            bestIndex, junkCV, junkCost = getBestCV(CVlist, x, y)  # Find index of best CV
            if not bestIndex in plotted:
                plotted.append(bestIndex)
            #plt.plot(x, y, "o", color = colorMap[plotted.index(bestIndex)])
            pts[bestIndex].append((x,y))

    # plot
    for bestIndex, p in pts.iteritems():
        x, y = zip(*p)
        plt.plot(x, y, "o", color = colorMap[plotted.index(bestIndex)])

    # legend
    for i in plotted:   # Generate labels for plotted CV
        plt.plot(dupMin, switchMin, color = colorMap[plotted.index(i)], \
                       label = str(CVlist[i]))
    leg = plt.legend()
    for i in range(len(leg.legendHandles)):  # Adjust legend marker thickness
        leg.legendHandles[i].set_linewidth(5.0)
    plt.title("Costscape:  " + outfile)

    if outfile != "":
        plt.savefig(outfile, format="pdf")
    if display:
        plt.show()

def buildColors(numVectors):
    fixedColors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), \
                   (0.8, 0, 0.8), (0.0, 0.0, 0.5), (0.1, 0.8, 0.4), (0.4, 0.1, 1), \
                   (0.4, 0.6, 0), (0.4, 0, 0.6), (0, 0.4, 0.6)]
    colorMap = {}
    for i in range(numVectors):
        if i < len(fixedColors):
            colorMap[i] = fixedColors[i]
        else:
            colorMap[i] = (random.uniform(0, 1), \
                           random.uniform(0, 1), \
                           random.uniform(0, 1))
    return colorMap
