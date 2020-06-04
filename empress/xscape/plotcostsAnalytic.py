# plotcostsAnalytic.py
# Ran Libeskind-Hadas, October 2013
# Plots the cost space using a matplotlib/pyplot
# Updated June 2020 to plot costs relative to loss rather than to duplication

import matplotlib
from matplotlib.axes import Axes

matplotlib.use('tkagg')  # need this so plt.show() works
import matplotlib.pyplot as plt
from shapely.geometry import *
from .CostVector import *
from .commonAnalytic import *


def plot_costs_to_axis(axes: Axes, cost_vectors, switch_min, switch_max, loss_min,
                       loss_max, log=False):
    if log:
        axes.set_xscale('log')
        axes.set_yscale('log')
    axes.set_xlim(loss_min, loss_max)
    axes.set_ylim(switch_min, switch_max)
    axes.set_xlabel("Loss cost relative to duplication")
    axes.set_ylabel("Transfer cost relative to duplication")

    n_regions = len(cost_vectors)
    color_map = buildColors(n_regions)

    regions = getRegions(cost_vectors, switch_min, switch_max, loss_min, loss_max)
    for cost_vector in cost_vectors:
        cost_vector_str = str(cost_vector)
        if cost_vector_str not in regions:
            continue
        region = regions[cost_vector_str]

        color = color_map[cost_vectors.index(cost_vector)]
        label = cost_vector_str

        if isinstance(region, Polygon):  # non-degenerate
            coords = list(region.exterior.coords)
            axes.add_patch(plt.Polygon(coords, color=color, label=label))
        elif isinstance(region, LineString):  # degenerate
            coords = list(region.coords)
            axes.plot([coords[0][0], coords[1][0]],
                      [coords[0][1], coords[1][1]],
                      linewidth=4,
                      color=color, label=label)
        elif isinstance(region, Point):  # degenerate
            coords = list(region.coords)
            axes.plot(coords[0][0], coords[0][1],
                      'o', markersize=4,
                      color=color, label=label)
        else:  # non-degenerate (collection)
            try:
                area = 0
                for r in region:
                    if isinstance(r, Polygon):  # non-degenerate
                        coords = list(r.exterior.coords)
                        axes.add_patch(plt.Polygon(coords, color=color, label=label))
                    elif isinstance(r, LineString):  # degenerate
                        coords = list(r.coords)
                        axes.plot([coords[0][0], coords[1][0]],
                                  [coords[0][1], coords[1][1]],
                                  linewidth=4,
                                  color=color, label=label)
                    elif isinstance(r, Point):  # degenerate
                        coords = list(r.coords)
                        axes.plot(coords[0][0], coords[0][1],
                                  'o', markersize=4,
                                  color=color, label=label)
                    else:
                        raise Exception(
                            "cost vector (%s) has invalid subregion (%s)" % (str(cost_vector), str(type(r))))
                    area += r.area
            except:
                raise Exception("cost vector (%s) has invalid region (%s)" % (str(cost_vector), str(type(region))))

    leg = axes.legend()
    for i in range(len(leg.legendHandles)):  # adjust legend marker thickness
        leg.legendHandles[i].set_linewidth(2.0)
    axes.set_title("Costscape")

def plotcosts(CVlist, switchMin, switchMax, lossMin, lossMax, outfile,
              log=True, display=False):
    ''' Plots the cost space for the given CVlist of CostVectors.  The x-axis
        represents loss cost (relative to unit cost for duplication) and
        the y-axis represents switch cost (relative to unit cost for
        duplication).  The x-range is from lossMin to lossMax and the
        y-range is from switchMin to switchMax.'''

    if log:
        plt.xscale('log')
        plt.yscale('log')
    plt.axis([lossMin, lossMax, switchMin, switchMax])
    plt.xlabel("Loss cost relative to duplication")
    plt.ylabel("Transfer cost relative to duplication")

    # color map
    numRegions = len(CVlist)
    colorMap = buildColors(numRegions)

    # plot regions
    regions = getRegions(CVlist, switchMin, switchMax, lossMin, lossMax)
    for cv in CVlist:
        cv_str = str(cv)
        if cv_str not in regions:
            continue
        region = regions[cv_str]

        # output
        print("Cost vector ", cv)
        color = colorMap[CVlist.index(cv)]
        label = cv_str
        if isinstance(region, Polygon):  # non-degenerate
            coords = list(region.exterior.coords)
            plt.gca().add_patch(plt.Polygon(coords,
                                            color=color, label=label))
            print("  Polygon vertices: ", coords)
            print("  Polygon area: ", region.area)
        elif isinstance(region, LineString):  # degenerate
            coords = list(region.coords)
            plt.plot([coords[0][0], coords[1][0]],
                     [coords[0][1], coords[1][1]],
                     linewidth=4,
                     color=color, label=label)
            print("  Line vertices: ", coords)
        elif isinstance(region, Point):  # degenerate
            coords = list(region.coords)
            plt.plot(coords[0][0], coords[0][1],
                     'o', markersize=4,
                     color=color, label=label)
            print("  Point vertex: ", coords)
        else:  # non-degenerate (collection)
            try:
                area = 0
                for r in region:
                    if isinstance(r, Polygon):  # non-degenerate
                        coords = list(r.exterior.coords)
                        plt.gca().add_patch(plt.Polygon(coords,
                                                        color=color, label=label))
                        print("  Polygon vertices: ", coords)
                        print("  Polygon area: ", r.area)
                    elif isinstance(r, LineString):  # degenerate
                        coords = list(r.coords)
                        plt.plot([coords[0][0], coords[1][0]],
                                 [coords[0][1], coords[1][1]],
                                 linewidth=4,
                                 color=color, label=label)
                        print("  Line vertices: ", coords)
                    elif isinstance(r, Point):  # degenerate
                        coords = list(r.coords)
                        plt.plot(coords[0][0], coords[0][1],
                                 'o', markersize=4,
                                 color=color, label=label)
                        print("  Point vertex: ", coords)
                    else:
                        raise Exception("cost vector (%s) has invalid subregion (%s)" % (str(cv), str(type(r))))
                    area += r.area
                    print("  Total area: ", area)
            except:
                raise Exception("cost vector (%s) has invalid region (%s)" % (str(cv), str(type(region))))

    # legend
    leg = plt.legend()
    for i in range(len(leg.legendHandles)):  # adjust legend marker thickness
        leg.legendHandles[i].set_linewidth(2.0)
    plt.title("Costscape:  " + outfile)

    if outfile != "":
        plt.savefig(outfile, format="pdf")
    if display:
        plt.show()

