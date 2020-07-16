"""
plot_tools.py
Plotting tools using matplotlib
"""

# If matplotlib doesn't pop up a window, force it to use tkinter backend
# matplotlib.use("tkagg")
from typing import Union, NamedTuple, Tuple
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
import matplotlib.patheffects as PathEffects


from empress.recon_vis.render_settings import *

LINEWIDTH = 2
TEXTWIDTH = .3
BORDER_WIDTH = 1.2

LINE_Z_ORDER = 0
DOT_Z_ORDER = 1
TEXT_Z_ORDER = 2

SIZE = 6
TRANSFERSIZE = 10

NODEFONTSIZE = 0.12
FONTSIZE = 12

DEFAULT_ALIGNMENT = 'bottom'


def transparent_color(col: Tuple[int, int, int, float], alpha: float):
    return col[0:3] + (alpha,)

class Position(NamedTuple):
    x: int
    y: int

class FigureWrapper:
    """ Class definining plotting methods """
    def __init__(self, title: str, axes: Union[plt.Axes, None] = None):
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

    def set_legend(self, legend_elements: list, loc: str = 'best', fontsize: int = FONTSIZE, title: str = None):
        """
        create legend
        """

        self.axis.legend(handles=legend_elements, loc=loc, fontsize=fontsize, title=title)
        
    def line(self, point_1: Position, point_2: Position, col: tuple = BLACK, linestyle: str = '-'):
        """
        Draw line from point p1 to p2
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        self.axis.plot([x_1, x_2], [y_1, y_2], color=col, linewidth=LINEWIDTH, linestyle=linestyle, zorder=LINE_Z_ORDER)

    def dot(self, point: Position, marker: str = 'o', col: tuple = BLACK):
        """
        Plot dot at point p
        """
        self.axis.plot(point.x, point.y, marker, color=col, zorder=DOT_Z_ORDER)
    
    def text(self, point: tuple, string: str, col: tuple = RED, h_a: str = 'right'):
        x, y = point
        self.axis.text(x, y, string, color=col, fontsize=FONTSIZE, horizontalalignment=h_a, verticalalignment='top')

    def text_v2(self, point: tuple, text: str, col: tuple = BLACK, size: float = SIZE, vertical_alignment: str = DEFAULT_ALIGNMENT, border_col: tuple = None):
        """
        Plot text at s at point p
        """
        if text is not None:
            if vertical_alignment == 'center':
                point = (point[0], point[1] - size * CENTER_CONSTANT)

            tp = TextPath(point, text, size=size)
            path_patch = PathPatch(tp, color=col, linewidth = TEXTWIDTH, zorder=TEXT_Z_ORDER)
            if border_col:
                path_patch.set_path_effects([PathEffects.withStroke(linewidth=BORDER_WIDTH, foreground=border_col)])
            self.fig.gca().add_patch(path_patch)
    
    def half_arrow(self, point_1: Position, point_2: Position, col: tuple = BLACK):
        """
        Draw arrow from point p1 to p2
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        self.axis.arrow(x_1, y_1, 0, abs(y_2-y_1)/2, head_width=0.15, head_length=0.15, color=col, linewidth=LINEWIDTH/2, shape='full', length_includes_head=True, zorder=LINE_Z_ORDER)

    def up_triangle(self, point: Position, col: tuple = BLACK, markersize: int = TRANSFERSIZE):
        """
        Draw an upwards triangle on point
        """
        x, y = point
        self.axis.plot(x, y, '^', color=col, zorder=LINE_Z_ORDER, markersize=TRANSFERSIZE)

    def down_triangle(self, point: Position, col: tuple = BLACK, markersize: int = TRANSFERSIZE):
        """
        Draw an downwards triangle on point
        """
        x, y = point
        self.axis.plot(x, y, 'v', color=col, zorder=LINE_Z_ORDER, markersize=TRANSFERSIZE)
        
    def show(self):
        """ 
        Display figure
        """
        plt.figure(self.fig.number)
        plt.show()

    def save(self, filename: str):
        """
        Save figure to file
        """
        self.fig.savefig(filename)
