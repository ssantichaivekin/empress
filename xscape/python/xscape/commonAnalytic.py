# commonAnalytic.py

from shapely.geometry import *
from CostVector import *
import random

def getRegions(CVlist, switchMin, switchMax, lossMin, lossMax,
               restrict=True):
    regions = {}

    # bounding box
    boundingbox = [(lossMin, switchMin), (lossMin, switchMax), \
                   (lossMax, switchMax), (lossMax, switchMin)]
    bb = Polygon(boundingbox)

    # find region for each event count vector
    # Let x and y denote the loss and transfer costs (relative to duplication cost).
    # A cost vector cv has cost = cv.d + cv.l * x + cv.s * y.
    # For cv1 to be optimal, then for each cv2 (s.t. cv2 != cv1), it must be that
    #     cv1.d + cv1.l * x + cv1.s * y <= cv2.d + cv2.l * x + cv2.s * y
    # that is
    #     y <= x * (cv2.l - cv1.l)/(cv1.s - cv2.s) + (cv2.d - cv1.d)/(cv1.s - cv2.s)
    for cv1 in CVlist:
        region = bb
        for cv2 in CVlist:
            if cv2 == cv1:
                continue    # skip comparison

            if cv1.s == cv2.s:  # vertical line defines the half-space
                xint = 1.0*(cv2.d - cv1.d)/(cv1.l - cv2.l)  # x-intercept
                
                # the variable "below" is True iff half-space is to left of line
                below = cv1.l - cv2.l > 0
                
                # test if half-space is to left or right of the line
                if below:      # below
                    lowestx = min(xint, lossMin)
                    poly = [(xint, switchMin), (xint, switchMax),
                            (lowestx, switchMax), (lowestx, switchMin)]
                else:          # above
                    highestx = max(xint, lossMax)
                    poly = [(xint, switchMin), (xint, switchMax),
                            (highestx, switchMax), (highestx, switchMin)]    
            else:
                m = 1.0*(cv2.l - cv1.l)/(cv1.s - cv2.s)  # slope
                b = 1.0*(cv2.d - cv1.d)/(cv1.s - cv2.s)  # y-intercept
                
                # the variable "below" is True iff half-space is below line
                below = cv1.s - cv2.s > 0
                
                if m == 0:      # horizontal line defines the half-space
                    # test if half-space is below or above the line
                    if below:  # below
                        lowesty = min(b, switchMin)
                        poly = [(lossMin, b), (lossMax, b),
                                (lossMax, lowesty), (lossMin, lowesty)]
                    else:      # above
                        highesty = max(b, switchMax)
                        poly = [(lossMin, b), (lossMax, b),
                                (lossMax, highesty), (lossMin, highesty)]
                else:           # "slanted" line defines the half-space
                    # y-coord of intersection with left/right edge of boundingbox 
                    lefty = m * lossMin + b
                    righty = m * lossMax + b
                    
                    # test if half-space is below or above the line
                    if below:  # below
                        lowesty = min(switchMin, lefty, righty)
                        poly = [(lossMin, lefty), (lossMax, righty),
                                (lossMax, lowesty), (lossMin, lowesty)]
                    else:      # above
                        highesty = max(switchMax, lefty, righty)
                        poly = [(lossMin, lefty), (lossMax, righty),
                                (lossMax, highesty), (lossMin, highesty)]
                
            # update region
            P = Polygon(poly)
            region = region.intersection(P)

        # keep region?
        keep = True
        if restrict:
            if (region.is_empty) or (not region.intersects(bb)):
                keep = False
            
        # update dictionary
        if keep:
            regions[str(cv1)] = region

    return regions


def buildColors(numRegions):
    
    fixedColors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), \
                   (0.8, 0, 0.8), (0.0, 0.0, 0.5), (0.1, 0.8, 0.4), \
                   (0.4, 0.1, 1), (0.4, 0.6, 0), (0.4, 0, 0.6), (0, 0.4, 0.6)]
    colorMap = {}
    for i in range(numRegions):
        if i < len(fixedColors):
            colorMap[i] = fixedColors[i]
        else:
            colorMap[i] = (random.uniform(0, 1), \
                           random.uniform(0, 1), \
                           random.uniform(0, 1))
    return colorMap

