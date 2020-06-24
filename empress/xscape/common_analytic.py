# common_analytic.py
# Updated 6/1/2020: loss = 1, x-axis is duplication, y-axis is transfer

import random

from shapely.geometry import Polygon

from empress.xscape.CostVector import CostVector

def getRegions(CVlist, transferMin, transferMax, dupMin, dupMax,
               restrict=True):
    regions = {}

    # bounding box
    boundingbox = [(dupMin, transferMin), (dupMin, transferMax), \
                   (dupMax, transferMax), (dupMax, transferMin)]
    bb = Polygon(boundingbox)

    # find region for each event count vector
    # Let x and y denote the duplication and transfer costs (relative to duplication cost).
    # A cost vector cv has cost = cv.d * x + cv.l * 1 + cv.s * y.
    # For cv1 to be optimal, then for each cv2 (s.t. cv2 != cv1), it must be that
    #     cv1.d * x + cv1.l * 1 + cv1.s * y <= cv2.d * x + cv2.l * 1 + cv2.s * y
    # that is
    #     y <= x * (cv2.d - cv1.d)/(cv1.s - cv2.s) + (cv2.l - cv1.l)/(cv1.s - cv2.s)
    for cv1 in CVlist:
        keep = True     # Keep this region for now
        region = bb
        for cv2 in CVlist:
            if cv2 == cv1:
                continue    # skip comparison

            if cv1.s == cv2.s:  # vertical line defines the half-space
                xint = 1.0*(cv2.l - cv1.l)/(cv1.d - cv2.d)  # x-intercept
                
                # the variable "below" is True iff half-space is to left of line
                below = cv1.d - cv2.d > 0
                
                # test if half-space is to left or right of the line
                if below:      # below
                    lowestx = min(xint, dupMin)
                    poly = [(xint, dupMin), (xint, dupMax),
                            (lowestx, transferMax), (lowestx, transferMin)]
                else:          # above
                    highestx = max(xint, dupMax)
                    poly = [(xint, transferMin), (xint, transferMax),
                            (highestx, transferMax), (highestx, transferMin)]    
            else:
                m = 1.0*(cv2.d - cv1.d)/(cv1.s - cv2.s)  # slope
                b = 1.0*(cv2.l - cv1.l)/(cv1.s - cv2.s)  # y-intercept
                
                # the variable "below" is True iff half-space is below line
                below = cv1.s - cv2.s > 0
                
                if m == 0:      # horizontal line defines the half-space
                    # test if half-space is below or above the line
                    if below:  # below
                        lowesty = min(b, transferMin)
                        poly = [(dupMin, b), (dupMax, b),
                                (dupMax, lowesty), (dupMin, lowesty)]
                    else:      # above
                        highesty = max(b, transferMax)
                        poly = [(dupMin, b), (dupMax, b),
                                (dupMax, highesty), (dupMin, highesty)]
                else:           # "slanted" line defines the half-space
                    # y-coord of intersection with left/right edge of boundingbox 
                    lefty = m * dupMin + b
                    righty = m * dupMax + b
                    
                    # test if half-space is below or above the line
                    if below:  # below
                        lowesty = min(transferMin, lefty, righty)
                        poly = [(dupMin, lefty), (dupMax, righty),
                                (dupMax, lowesty), (dupMin, lowesty)]
                    else:      # above
                        highesty = max(transferMax, lefty, righty)
                        poly = [(dupMin, lefty), (dupMax, righty),
                                (dupMax, highesty), (dupMin, highesty)]
                
            # update region
            P = Polygon(poly)
            region = region.intersection(P)

            # Shapely does strange things when intersecting
            # a Polygon of zero area with another Polygon.
            # If P is a Polygon of zero area, the region should
            # be considered empty and thus not kept.
            if P.area == 0.0:   
                keep = False
                break

        # keep region?
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

