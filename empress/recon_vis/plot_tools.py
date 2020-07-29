"""
plot_tools.py
Plotting tools using matplotlib
"""

# If matplotlib doesn't pop up a window, force it to use tkinter backend
# matplotlib.use("tkagg")
from typing import Union, NamedTuple, Tuple
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import rcParams
from matplotlib.collections import LineCollection
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib import font_manager
import matplotlib.patheffects as PathEffects

from empress.recon_vis import render_settings

LINEWIDTH = 1
TEXTWIDTH = .3
BORDER_WIDTH = 1.2

LINE_Z_ORDER = 0
DOT_Z_ORDER = 1
TEXT_Z_ORDER = 2

SIZE = 6
TRANSFERSIZE = 10

FONTSIZE = 12

DEFAULT_VERTICAL_ALIGNMENT = 'bottom'
DEFAULT_VERTICAL_ALIGNMENT_2 = 'top'
DEFAULT_HORIZONTAL_ALIGNMENT = 'right'
DEFAULT_LOCATION = 'best'
DEFAULT_LINESTYLE = '-'
DEFAULT_TRIANGLE_LINESTYLE = 'None'
DEFAULT_DOT_MARKER = 'o'
CENTER = 'center'

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

    def set_legend(self, legend_elements: list, loc: str = DEFAULT_LOCATION, fontsize: int = FONTSIZE, title: str = None):
        """
        create legend
        """
        self.axis.legend(handles=legend_elements, loc=loc, fontsize=fontsize, title=title)

    def line(self, point_1: Position, point_2: Position, col: tuple = render_settings.BLACK, linestyle: str = DEFAULT_LINESTYLE):
        """
        Draw line from point p1 to p2
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        self.axis.plot([x_1, x_2], [y_1, y_2], color=col, linewidth=LINEWIDTH, linestyle=linestyle, zorder=LINE_Z_ORDER)

    def dot(self, point: Position, marker: str = DEFAULT_DOT_MARKER, col: tuple = render_settings.BLACK):
        """
        Plot dot at point p
        """
        self.axis.plot(point.x, point.y, marker, color=col, zorder=DOT_Z_ORDER)

    def text(self, point: tuple, string: str, col: tuple = render_settings.RED, size=FONTSIZE, h_a: str = DEFAULT_HORIZONTAL_ALIGNMENT):
        x, y = point
        self.axis.text(x, y, string, color=col, fontsize = size, horizontalalignment=h_a, verticalalignment=DEFAULT_VERTICAL_ALIGNMENT_2)
    
    def text_v2(self, point: tuple, text: str, col: tuple = render_settings.BLACK, size: float = SIZE, vertical_alignment: str = DEFAULT_VERTICAL_ALIGNMENT, border_col: tuple = None):
        """
        Plot text string s at point p in monospace font
        """
        if text is not None:
            if vertical_alignment == CENTER:
                point = (point[0], point[1] - size * render_settings.CENTER_CONSTANT)

            mono_property = font_manager.FontProperties(family='monospace')
            tp = TextPath(point, text, size=size, prop=mono_property)
            path_patch = PathPatch(tp, color=col, linewidth = TEXTWIDTH, zorder=TEXT_Z_ORDER)
            if border_col:
                path_patch.set_path_effects([PathEffects.withStroke(linewidth=BORDER_WIDTH, foreground=border_col)])
            self.fig.gca().add_patch(path_patch)
    
    def triangle(self, point: Position, col: tuple = render_settings.BLACK, markersize: int = TRANSFERSIZE, rotation: float = render_settings.UP_ARROW_ROTATION):
        """
        Draws a triangle in the desired position
        """
        self.axis.plot(point.x, point.y, color=col, marker=(3, 0, rotation), markersize=TRANSFERSIZE, linestyle=DEFAULT_TRIANGLE_LINESTYLE)

    def arrow_segment(self, point_1: Position, point_2: Position, col: tuple = render_settings.BLACK):
        """
        Draws a line from point 1 to point 2 with an arrow in the middle
        """
        plt.plot((point_1.x, point_2.x), (point_1.y, point_2.y), linewidth=2, color=col)
        arrow_length_x, arrow_length_y = (point_2.x - point_1.x) / 2, (point_2.y - point_1.y) / 2
        plt.arrow(point_1.x, point_1.y, arrow_length_x, arrow_length_y, linewidth=2, 
                  head_width=0.3, head_length=0.5, facecolor=col, edgecolor=col,
                  length_includes_head=False)


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
