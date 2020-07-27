# render_settings.py
from collections import namedtuple
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection

VERTICAL_OFFSET = 0.3       # Offset for drawing parasite nodes above host nodes
COSPECIATION_OFFSET = .3    # Offest for drawing parasite nodes closer to host 
                            # nodes for speciation events
NODE_OFFSET = 0.3
TRACK_OFFSET = 0.3
TIP_TEXT_OFFSET_X = .3


# Colors
# Define new colors as 4-tuples of the form (r, g, b, 1) where
# r, g, b are values between 0 and 1 indicating the amount of red, green, and blue.
RED = (1, 0, 0, 1)


MAROON = (0.5, 0, 0, 1)
GREEN = (0, 0.5, 0, 1)

PURPLE = (0.5, 0, 0.5, 1)
BLACK = (0, 0, 0, 1)
GRAY = (0.5, 0.5, 0.5, 1)
WHITE = (1, 1, 1, 1)
PURPLE = (.843, .00, 1.0, 1)

BLUE = (.09, .216, .584, 1)
ROYAL_BLUE = (.3, .4, .9, 1)
CYAN = (.3, .9, .75, 1)
RED_BLUSH = (.882, .255, .412, 1)
PRETTY_YELLOW = (.882, .725, .255, 1)
ORANGE_ORANGE = (1.00, .502, 0, 1)

LEAF_NODE_COLOR = BLUE
COSPECIATION_NODE_COLOR = ORANGE_ORANGE
DUPLICATION_NODE_COLOR = PURPLE
TRANSFER_NODE_COLOR = RED_BLUSH
HOST_NODE_COLOR = BLACK
HOST_EDGE_COLOR = BLACK
PARASITE_EDGE_COLOR = ROYAL_BLUE
LOSS_EDGE_COLOR = GRAY

TRANSFER_TRANSPARENCY = 0.25

LEAF_NODE_SHAPE = "o"
COSPECIATION_NODE_SHAPE = "o"
DUPLICATION_NODE_SHAPE = "D"
TRANSFER_NODE_SHAPE = "s"

TIP_ALIGNMENT = 'center'

CENTER_CONSTANT = 3 / 8

NODESIZE = 8
START_SIZE = -60
STEP_SIZE = 50
MIN_FONT_SIZE = 0
MAX_FONT_SIZE = .3
COUNT_OFFSET = 3
PUSHED_NODE_OFFSET = 0.5

INTERNAL_NODE_ALPHA = 0.7

HOST_NODE_BORDER_COLOR = WHITE
PARASITE_NODE_BORDER_COLOR = BLACK

TREE_TITLE = ""

LEGEND_ELEMENTS = [
       Line2D([0], [0], marker= COSPECIATION_NODE_SHAPE, color='w', label='Cospeciation',
              markerfacecolor=COSPECIATION_NODE_COLOR, markersize=NODESIZE),
       Line2D([0], [0], marker=DUPLICATION_NODE_SHAPE, color='w', label='Duplication',
              markerfacecolor=DUPLICATION_NODE_COLOR, markersize=NODESIZE),
       Line2D([0], [0], marker=TRANSFER_NODE_SHAPE, color='w', label='Transfer',
              markerfacecolor=TRANSFER_NODE_COLOR, markersize=NODESIZE),
       LineCollection([[(0, 0)]], linestyles=['dashed'],
              colors=[LOSS_EDGE_COLOR], label='Loss')
]

UP_ARROW_ROTATION = 0
DOWN_ARROW_ROTATION = 180
