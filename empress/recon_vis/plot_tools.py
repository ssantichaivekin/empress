"""
plot_tools.py
Plotting tools using matplotlib
Modified June 26, 2020
"""

# If matplotlib doesn't pop up a window, force it to use tkinter backend
# matplotlib.use("tkagg")
from typing import Union

from matplotlib import pyplot as plt

# Colors
# Define new colors as 4-tuples of the form (r, g, b, 1) where
# r, g, b are values between 0 and 1 indicating the amount of red, green, and blue.
RED = (1, 0, 0, 1)
MAROON = (0.5, 0, 0, 1)
GREEN = (0, 0.5, 0, 1)
BLUE = (0, 0, 1, 1)
PURPLE = (0.5, 0, 0.5, 1)
BLACK = (0, 0, 0, 1)
GRAY = (0.5, 0.5, 0.5, 1)
LINEWIDTH = 2
FONTSIZE = 12

class FigureWrapper:
    """ Class definining plotting methods """
    def __init__(self, title, axes: Union[plt.Axes, None] = None):
        """
        If axes is specified, draw on axes instead.
        """
        if axes is None:
            self.fig = plt.figure()
            self.axis = self.fig.subplots(1, 1) # creates a figure with one Axes (plot)
        else:
            self.fig = axes.get_figure()
            self.axis = axes
        self.axis.autoscale()
        self.axis.margins(0.1)
        self.axis.axis("off")
        self.axis.set_title(title)

    def line(self, point_1, point_2, col=BLACK, style = '-'):
        """
        Draw line from point p1 to p2
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        self.axis.plot([x_1, x_2], [y_1, y_2], color=col, linewidth=LINEWIDTH, linestyle = style)
    
    def dot(self, point, col=BLACK):
        """
        Plot dot at point p
        """
        x, y = point
        self.axis.plot(x, y, 'o', color=col)
    
    def text(self, point, string, col=RED, h_a='right'):
        x, y = point
        self.axis.text(x, y, string, color=col, fontsize=FONTSIZE, horizontalalignment=h_a, verticalalignment='top')

    def show(self):
        """ 
        Display figure
        """
        plt.figure(self.fig.number)
        plt.show()

    def save(self, filename):
        """
        Save figure to file
        """
        self.fig.savefig(filename)
