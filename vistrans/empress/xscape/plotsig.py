# plotsig.py
# Ran Libeskind-Hadas, October 2013
# Plots significance over cost space using a matplotlib/pyplot

# python libraries
import random
import collections

# matplotlib libraries
from matplotlib import pyplot as plt

# xscape libraries
from empress.xscape.common import frange, getBestCV
from empress.xscape.CostVector import CostVector

def plotsig(CVlist, randomTrialsCVlist,
            switchMin, switchMax, lossMin, lossMax, steps, outfile,
	    log=True, display=False):
    ''' Plots the experimental p-values for in green (p-value <= 0.01),
        yellow (0.01 < p-value <= 0.05), and red (0.05 < p-value) '''
    numTrials = len(randomTrialsCVlist)

    if log:
        plt.xscale('log')
        plt.yscale('log')
    plt.axis([lossMin, lossMax, switchMin, switchMax])
    plt.xlabel("Loss cost relative to duplication")
    plt.ylabel("Transfer cost relative to duplication")

    greenCounter = 0
    yellowCounter = 0
    redCounter = 0
    totalSamples = 0

    # process
    pts = collections.defaultdict(list)  # key = pColor
    for x in frange(lossMin, lossMax, steps, log=log):
        for y in frange(switchMin, switchMax, steps, log=log):
            totalSamples += 1
            junkIndex, junkCV, bestOriginal = getBestCV(CVlist, x, y)
            counter = 0
            for trialCVlist in randomTrialsCVlist:
                junkIndex, junkCV, bestThisTrial = getBestCV(trialCVlist, x, y)
                if bestOriginal <  bestThisTrial: counter += 1
            pValue = 1.0 - 1.0 * counter / numTrials
            if pValue < 0.01:
                pColor = (0, 1, 0)       # Very significant = green
                greenCounter += 1
            elif 0.01 <= pValue < 0.05:   
                pColor = (1, 1, 0)       # Significant = yellow
                yellowCounter += 1
            else:
                pColor = (1, 0, 0)       # Not significant = red
                redCounter += 1
            pts[pColor].append((x,y))

    # plot
    for pColor, p in pts.items():
        x, y = list(zip(*p))
        plt.plot(x, y, "o", color=pColor)

    # statistics
    print("Using ", str(numTrials), " trials")
    print("  Percentage green (p-value < 0.01): %.2f" % \
          (100.0 * greenCounter / totalSamples))
    print("  Percentage yellow (0.01 <= p-value < 0.05): %.2f" % \
          (100.0 * yellowCounter / totalSamples))
    print("  Percentage red (0.05 <= p-value): %.2f" % \
          (100.0 * redCounter / totalSamples))   

    plt.title("Sigscape:  " + outfile)

    if outfile != "":
        plt.savefig(outfile, format="pdf")
    if display:
        plt.show()
    
