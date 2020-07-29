"""
tanglegram.py
Visualizes tanglegrams using matplotlib
Berto Garcia, Sonia Sehra
"""

from matplotlib import pyplot as plt
from empress.recon_vis import utils, plot_tools, tree, render_settings


VERTICAL_OFFSET = 20
HORIZONTAL_SPACING = 10
LEAF_SPACING = 5
EXTRA_SPACING_FOR_LABEL = 50
FONTSIZE = 9

# global variables
_g_host_counter = 0
_g_parasite_counter = 0

def render(host_dict: dict, parasite_dict: dict, tip_mapping: dict, show_internal_labels: bool, ax: plt.Axes = None) \
        -> plot_tools.FigureWrapper:
    """
    Render tanglegram
    :param host_dict - host tree (dictionary representation)
    :param parasite_dict - parasite tree (dictionary representation)
    :param tip_mapping - tip mapping dictionary
    :param show_internal_labels - boolean indicator of whether internal node names should
        be displayed
    :param ax - draw on Axes instead if available
    :return FigureWrapper object 
    """
    global _g_host_counter
    global _g_parasite_counter
    _g_host_counter = 0
    _g_parasite_counter = 0

    fig = plot_tools.FigureWrapper("Host | Parasite", axes=ax)
    host_tree = utils.dict_to_tree(host_dict, tree.TreeType.HOST)
    parasite_tree = utils.dict_to_tree(parasite_dict, tree.TreeType.PARASITE)
    _render_helper_host(fig, host_tree.root_node, show_internal_labels)
    _render_helper_parasite(fig, parasite_tree.root_node, show_internal_labels)

    host_dict = {}
    for host in host_tree.leaf_list():
        host_dict[host.name] = host

    # connect hosts leaves to parasite leaves
    for leaf in parasite_tree.leaf_list():
        parasite = leaf
        host = host_dict[tip_mapping[leaf.name]]
        fig.line((host.layout.col, host.layout.row), (parasite.layout.col, parasite.layout.row),
                 col=render_settings.GRAY, linestyle='--')
    return fig

def _render_helper_host(fig, node, show_internal_labels):
    """
    Render helper for host tree
    """
    global _g_host_counter
    if node.is_leaf():

        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = tree.NodeLayout()
        leaf_layout.col = -VERTICAL_OFFSET
        leaf_layout.row = _g_host_counter

        _g_host_counter += LEAF_SPACING
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        textbox = fig.text(plot_loc, node.name, size=FONTSIZE, col=render_settings.BLUE, h_a='right')

    else:
        # recursively call helper function on child nodes
        _render_helper_host(fig, node.left_node, show_internal_labels)
        _render_helper_host(fig, node.right_node, show_internal_labels)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = tree.NodeLayout()
        node.layout.col = min(right_layout.col, left_layout.col) - HORIZONTAL_SPACING
        # If this node has a leaf child, extend the length of the branch to allow extra spacing to render label
        if node.right_node.is_leaf() or node.left_node.is_leaf():
            node.layout.col -= EXTRA_SPACING_FOR_LABEL
        y_avg = (right_layout.row + left_layout.row) / 2
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels:
            fig.text(current_loc, node.name, size=FONTSIZE, col=render_settings.BLUE, h_a='left')

        # draw line from current node to left node
        left_loc = (left_layout.col, left_layout.row)
        fig.line(current_loc, (node.layout.col, left_layout.row), col=render_settings.BLACK)
        fig.line((node.layout.col, left_layout.row), left_loc, col=render_settings.BLACK)

        # draw line from current node to right node
        right_loc = (right_layout.col, right_layout.row)
        fig.line(current_loc, (node.layout.col, right_layout.row), col=render_settings.BLACK)
        fig.line((node.layout.col, right_layout.row), right_loc, col=render_settings.BLACK)


def _render_helper_parasite(fig, node, show_internal_labels):
    """
    Render helper for parasite tree
    """
    global _g_parasite_counter
    if node.is_leaf():
        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = tree.NodeLayout()
        leaf_layout.col = VERTICAL_OFFSET
        leaf_layout.row = _g_parasite_counter

        _g_parasite_counter += LEAF_SPACING
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        fig.text(plot_loc, node.name, size=FONTSIZE, col=render_settings.BLUE, h_a='left')

    else:
        # recursively call helper funciton on child nodes
        _render_helper_parasite(fig, node.left_node, show_internal_labels)
        _render_helper_parasite(fig, node.right_node, show_internal_labels)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = tree.NodeLayout()
        node.layout.col = max(left_layout.col, right_layout.col) + HORIZONTAL_SPACING
        # If this node has a leaf child, extend the length of the branch to allow extra spacing to render label
        if node.right_node.is_leaf() or node.left_node.is_leaf():
            node.layout.col += EXTRA_SPACING_FOR_LABEL
        y_avg = (right_layout.row + left_layout.row) / 2
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels:
            fig.text(current_loc, node.name, size=FONTSIZE, col=render_settings.BLUE, h_a='right')

        # draw line from current node to left node
        left_loc = (left_layout.col, left_layout.row)
        fig.line(current_loc, (node.layout.col, left_layout.row), col=render_settings.BLACK)
        fig.line((node.layout.col, left_layout.row), left_loc, col=render_settings.BLACK)

        # draw line from current node to right node
        right_loc = (right_layout.col, right_layout.row)
        fig.line(current_loc, (node.layout.col, right_layout.row), col=render_settings.BLACK)
        fig.line((node.layout.col, right_layout.row), right_loc, col=render_settings.BLACK)
