# plotcosts_analytic.py
# Ran Libeskind-Hadas, October 2013
# Plots the cost space using a matplotlib/pyplot

import sys
import matplotlib
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, LineString, Point

from empress.xscape.common_analytic import getRegions, buildColors


def plot_costs_on_axis(axes: Axes, cost_vectors, transfer_min, transfer_max, dup_min,
                       dup_max, title=None, log=False, verbose=False):
    if log:
        axes.set_xscale('log')
        axes.set_yscale('log')
    axes.set_xlim(dup_min, dup_max)
    axes.set_ylim(transfer_min, transfer_max)
    axes.set_xlabel("Duplication cost relative to loss")
    axes.set_ylabel("Transfer cost relative to loss")

    n_regions = len(cost_vectors)
    color_map = buildColors(n_regions)

    regions = getRegions(cost_vectors, transfer_min, transfer_max, dup_min, dup_max)
    for cost_vector in cost_vectors:
        if verbose:
            print("Cost vector ", cost_vector)
        cost_vector_str = str(cost_vector)
        if cost_vector_str not in regions:
            continue
        region = regions[cost_vector_str]

        color = color_map[cost_vectors.index(cost_vector)]
        label = cost_vector_str

        if isinstance(region, Polygon):  # non-degenerate
            coords = list(region.exterior.coords)
            axes.add_patch(plt.Polygon(coords, color=color, label=label))
            if verbose:
                print("  Polygon vertices: ", coords)
                print("  Polygon area: ", region.area)
        elif isinstance(region, LineString):  # degenerate
            coords = list(region.coords)
            axes.plot([coords[0][0], coords[1][0]],
                      [coords[0][1], coords[1][1]],
                      linewidth=4,
                      color=color, label=label)
            if verbose:
                print("  Line vertices: ", coords)
        elif isinstance(region, Point):  # degenerate
            coords = list(region.coords)
            axes.plot(coords[0][0], coords[0][1],
                      'o', markersize=4,
                      color=color, label=label)
            if verbose:
                print("  Point vertex: ", coords)
        else:  # non-degenerate (collection)
            try:
                area = 0
                legend_entry = False  # Add one only one legend entry per r in region
                for r in region:
                    if isinstance(r, Polygon):  # non-degenerate
                        coords = list(r.exterior.coords)
                        if not legend_entry:
                            axes.add_patch(plt.Polygon(coords, color=color, label=label))
                            legend_entry = True
                        else:
                            axes.add_patch(plt.Polygon(coords))  # legend entry has been added previously
                        if verbose:
                            print("  Polygon vertices: ", coords)
                            print("  Polygon area: ", r.area)
                    elif isinstance(r, LineString):  # degenerate
                        coords = list(r.coords)
                        if not legend_entry:
                            axes.plot([coords[0][0], coords[1][0]],
                                      [coords[0][1], coords[1][1]],
                                      linewidth=4,
                                      color=color, label=label)
                            legend_entry = True
                        else:
                            axes.plot([coords[0][0], coords[1][0]],
                                      [coords[0][1], coords[1][1]])
                        if verbose:
                            print("  Line vertices: ", coords)
                    elif isinstance(r, Point):  # degenerate
                        coords = list(r.coords)
                        if not legend_entry:
                            axes.plot(coords[0][0], coords[0][1],
                                      'o', markersize=4,
                                      color=color, label=label)
                        else:
                            axes.plot(coords[0][0], coords[0][1])  # legend entry has been added previously
                        if verbose:
                            print("  Point vertex: ", coords)
                    else:
                        raise Exception(
                            "cost vector (%s) has invalid subregion (%s)" % (str(cost_vector), str(type(r))))
                    area += r.area
                    if verbose:
                        print("  Total area: ", area)
            except:
                raise Exception("cost vector (%s) has invalid region (%s)" % (str(cost_vector), str(type(region))))

    leg = axes.legend()
    for i in range(len(leg.legendHandles)):  # adjust legend marker thickness
        leg.legendHandles[i].set_linewidth(2.0)
    axes.set_title("Costscape: %s" % title)

def plotcosts(CVlist, transfer_min, transfer_max, dup_min, dup_max, outfile,
              log=True, display=False, verbose=False):
    figure, ax = plt.subplots(1, 1)
    plot_costs_on_axis(ax, CVlist, transfer_min, transfer_max, dup_min, dup_max,
                       outfile, log, verbose)
    if outfile != "":
        plt.savefig(outfile, format="pdf")
    if display:
        plt.show()
