import csv

from matplotlib import pyplot as plt

from empress.histogram import Histogram

def plot_histogram_to_ax(ax: plt.Axes, histogram):
    ax.bar(list(histogram.keys()), list(histogram.values()))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.set_ylabel("Number of MPR Pairs")


def plot_histogram(plot_file, histogram, width, tree_name, d, t, l, max_x=None, max_y=None, title=True):
    """
    Plots the PDV
    :param plot_file <str> - the filename to save the plot to
    :param histogram <dict int->int> - the underlying dict of values for the PDV Histogram
    :param width <float> - the width of the bars. Will be 1 unless the x-axis has been scaled
    :param tree_name <str> - the name of the tree that generated this plot. Used to
        figure out what the title of the plot should be
    :params d, t, l <float> - the DTL costs - used to generate the title
    :params max_x, max_y <float> - Limits on the axes of the plot - useful for generating multiple
        plots with the same axes
    :param title <bool> - Include a title
    """
    # Set the max limits
    if max_y is not None:
        plt.ylim(top=float(max_y))
    if max_x is not None:
        plt.xlim(right=float(max_x))
    plt.bar(list(histogram.keys()), list(histogram.values()), width)
    # Force y-axis to use scientific notation
    plt.ticklabel_format(style="sci", axis="y", scilimits=(0,0))
    # Find the exponent in order to put it in the ylabel
    # Force offset text to update using draw
    #TODO: there MUST be a better way to do this
    plt.draw()
    ax = plt.gca()
    # matplotlib sure is intuitive and easy to use!
    # Get the exponent text from the y-axis and format it into latex
    # tight_layout is a hack that makes matplotlib set yaxis offset text correctly.
    # Please refer to https://github.com/ssantichaivekin/eMPRess/pull/29
    plt.tight_layout() 
    exponent_text = ax.get_yaxis().get_offset_text().get_text()
    if exponent_text == "":
        exponent = 0
    else:
        exponent = float(exponent_text.split("e")[-1])
    latex_exponent = r"x$10^{%d}$" % exponent
    # Don't display it because we're going to use it in the y-axis label
    ax.yaxis.offsetText.set_visible(False)
    # Set the labels
    plt.xlabel("Distance", fontsize=18)
    plt.ylabel("Number of MPR Pairs {}".format(latex_exponent), fontsize=18)
    # y=1.08 is a hack to make the title display above
    if title:
        plt.title("{} with costs D:{}, T:{}, L:{}".format(tree_name, d, t, l), y=1.08, fontsize=18)
    plt.savefig(plot_file, bbox_inches='tight')
    plt.clf()

def csv_histogram(csv_file, histogram):
    """
    Write the histogram to a .csv file
    :param csv_file <str> - the path to a file to write to
    :param histogram <dict> - the underlying dict for the PDV
    """
    with open(csv_file, 'w') as csv_handle:
        writer = csv.writer(csv_handle)
        for key, value in list(histogram.items()):
            writer.writerow([key, value])

def normalize_xvals(histogram):
    """
    Normalize the x-values of the histogram to [0,1]
    :param histogram <dict>
    :return new_hist <dict> - the transformed histogram
    """
    max_xval = float(max(histogram.keys()))
    if max_xval == 0:
        return histogram
    new_hist = { k/max_xval : v for k,v in list(histogram.items()) }
    return new_hist

def normalize_yvals(histogram):
    """
    Normalize the y-values of the histogram to [0,1]
    :param histogram <dict>
    :return new_hist <dict> - the transformed histogram
    """
    total_yval = float(sum(histogram.values()))
    if total_yval == 0:
        return histogram
    new_hist = { k : v/total_yval for k,v in list(histogram.items()) }
    return new_hist

def cumulative(histogram):
    """
    Make the histogram cumulative
    :param histogram <dict>
    :return new_hist <dict> - the transformed histogram
    """
    total = 0
    new_hist = {}
    for k, v in list(histogram.items()):
        new_hist[k] = v + total
        total += v
    return new_hist

def omit_zeros(histogram):
    """
    Omit the zeros of the histogram (all are induced by comparing an MPR with itself)
    :param histogram <dict>
    :return new_hist <dict> - the transformed histogram
    """
    return { k : v for k,v in list(histogram.items()) if k != 0 }

def compute_stats(histogram):
    """
    Get various stats on the histogram
    :param histogram <dict>
    :return diameter <int> - the largest distance between two MPRs
    :return mean <float> - the average pairwise distance
    :return std <float> - the standard deviation of the distribution of distances
    """
    # Diameter of MPR-space
    # Average distance between MPRs and standard deviation
    diameter = max(histogram.keys())
    # Re-convert to a Histogram to calculate stats
    h = Histogram.Histogram(histogram)
    mean = h.mean()
    std = h.standard_deviation()
    return diameter, mean, std

