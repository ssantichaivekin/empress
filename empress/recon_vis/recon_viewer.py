"""
recon_viewer.py
View a single reconciliation using matplotlib
Justin Jiang, Trenton Wesley
"""
from empress.recon_vis import recon, tree, utils, plot_tools, render_settings

from typing import Union, Dict
import math
import matplotlib.pyplot as plt

FONT_SIZE_STRETCH = 3.0     # Parameter used in _calculate_font_size
SIGMOID_SCALE = 0.8         # Parameter used in _sigmoid

def render(host_dict: dict, parasite_dict: dict, recon_dict: dict, event_frequencies: Dict[tuple, float] = None, show_internal_labels: bool = False, 
           show_freq: bool = False, show_legend: bool = True, axes: Union[plt.Axes, None] = None):
    """ Renders a reconciliation using matplotlib
    :param host_dict:  Host tree represented in dictionary format
    :param parasite_dict:  Parasite tree represented in dictionary format
    :param recon_dict: Reconciliation represented in dictionary format
    :param event_frequencies: Dictionary that maps event tuples to their frequencies
    :param show_internal_labels: Boolean that determines wheter internal labels are shown or not
    :param show_freq: Boolean that determines whether event frequencies are shown or not
    :param axes: If specified, draw on the axes instead of creating a new figure
    :return Figure Object
    """
    host_tree, parasite_tree, consistency_type = utils.build_trees_with_temporal_order(host_dict, parasite_dict, recon_dict)
    recon_obj = utils.dict_to_reconciliation(recon_dict, event_frequencies)

    # Checks to see if the trees(or reconciliation) are empty
    if host_tree is None or parasite_tree is None or recon_obj is None:
        return None

    fig = plot_tools.FigureWrapper(render_settings.TREE_TITLE, axes)

    if show_legend:
        _create_legend(fig, consistency_type)

    # Calculates font sizes
    num_tip_nodes = len(host_tree.leaf_list()) + len(parasite_tree.leaf_list())
    font_size = _calculate_font_size(num_tip_nodes)

    root = parasite_tree.root_node
    host_lookup = host_tree.name_to_node_dict()
    parasite_lookup = parasite_tree.name_to_node_dict()

    # Populate Host Nodes with track count
    _populate_host_tracks(root, recon_obj, host_lookup)

    # Render Host Tree
    _render_host(fig, host_tree, show_internal_labels, font_size)

    # Sets the offsets between tracks on each host node
    _set_offsets(host_tree)

    # Determine the length of the longest string in the host tree's leaf list
    longest_host_name = max([len(leaf.name) for leaf in host_tree.leaf_list()])
    # Render Parasite Tree
    _render_parasite(fig, parasite_tree, recon_obj, host_lookup, parasite_lookup, show_internal_labels, show_freq, font_size, longest_host_name)

    return fig


def _create_legend(fig: plot_tools.FigureWrapper, consistency_type: str):
    """
    Creates a legend on the figure
    :param fig: Figure object that visualizes trees using MatplotLib
    :param consistency_type: String that gives the consistency of a tree
    """
    fig.set_legend(render_settings.LEGEND_ELEMENTS, title=consistency_type)


def _set_offsets(tree: tree.Tree):
    """
    Populates the nodes of a Tree with an offset
    :param tree: Tree Object
    """
    pos_dict = tree.pos_dict

    for node in tree.postorder_list():
        y_1 = None
        y_0 = node.layout.row
        for logical_pos in pos_dict:
            if node.is_leaf():
                if y_0 < logical_pos[0] and node.layout.col <= logical_pos[1]:
                    if y_1 is None or y_1 > logical_pos[0]:
                        y_1 = logical_pos[0]
            else:
                y_1 = max(node.left_node.layout.row, node.right_node.layout.row)
        if y_1 is None or node.layout.node_count == 0:
            node.layout.offset = render_settings.TRACK_OFFSET
        else:
            # Gives an offset based on the predicted number of horizontal tracks mapped to a host node
            # COUNT_OFFSET artificially adds extra nodes/tracks to lower the offset and pull parasite nodes closer to the host node their mapped to
            node.layout.offset = abs(y_0 - y_1) / (node.layout.node_count + render_settings.COUNT_OFFSET)


def _render_host(fig: plot_tools.FigureWrapper, host_tree: tree.Tree, show_internal_labels: bool, font_size: float):
    """
    Renders the host tree
    :param fig: Figure object that visualizes trees using MatplotLib
    :param host_tree: Host tree represented as a Tree object
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param font_size: Font size for the text of the tips and internal nodes of the tree
    """
    _set_host_node_layout(host_tree)
    root = host_tree.root_node
    _draw_host_handle(fig, root)
    _render_host_helper(fig, root, show_internal_labels, font_size, host_tree)


def _draw_host_handle(fig: plot_tools.FigureWrapper, root: tree.Node):
    """
    Draw edge leading to root of host tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param root: The root node of a tree object
    """
    fig.line((0, root.layout.y), (root.layout.x, root.layout.y), render_settings.HOST_EDGE_COLOR)


def _render_host_helper(fig: plot_tools.FigureWrapper, node: tree.Node, show_internal_labels: bool, font_size: float, host_tree: tree.Tree):
    """
    Helper function for rendering the host tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Host Node object that will be rendered
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param font_size: Font size for the text of the tips and internal nodes of the tree
    :param host_tree: Tree object representing a Host Tree
    """
    host_tree.pos_dict[(node.layout.row, node.layout.col)] = node

    node_pos = plot_tools.Position(node.layout.x, node.layout.y)

    if node.is_leaf():
        text_offset = (node_pos.x + render_settings.TIP_TEXT_OFFSET_X, node_pos.y)
        if node.layout.node_count == 0:
            fig.text_v2(text_offset, node.name, render_settings.HOST_NODE_COLOR, size=font_size, vertical_alignment=render_settings.TIP_ALIGNMENT)
        else:
            fig.text_v2(text_offset, node.name, render_settings.HOST_NODE_COLOR, size=font_size, vertical_alignment=render_settings.TIP_ALIGNMENT)    
    else:
        fig.dot(node_pos, col=render_settings.HOST_NODE_COLOR)  # Render host node
        if show_internal_labels:
            color = plot_tools.transparent_color(render_settings.HOST_NODE_COLOR, render_settings.INTERNAL_NODE_ALPHA)
            text_xy = (node_pos.x, node_pos.y)
            fig.text_v2(text_xy, node.name, color, size=font_size, border_col=render_settings.HOST_NODE_BORDER_COLOR)
        left_x, left_y = node.left_node.layout.x, node.left_node.layout.y
        right_x, right_y = node.right_node.layout.x, node.right_node.layout.y
        fig.line(node_pos, (node_pos.x, left_y), render_settings.HOST_EDGE_COLOR)
        fig.line(node_pos, (node_pos.x, right_y), render_settings.HOST_EDGE_COLOR)
        fig.line((node_pos.x, left_y), (left_x, left_y), render_settings.HOST_EDGE_COLOR)
        fig.line((node_pos.x, right_y), (right_x, right_y), render_settings.HOST_EDGE_COLOR)
        _render_host_helper(fig, node.left_node, show_internal_labels, font_size, host_tree)
        _render_host_helper(fig, node.right_node, show_internal_labels, font_size, host_tree)


def _render_parasite(fig: plot_tools.FigureWrapper, parasite_tree: tree.Tree, recon_obj: recon.Reconciliation,  
        host_lookup: dict, parasite_lookup: dict, show_internal_labels: bool, show_freq: bool, 
        font_size: float, longest_host_name: int):
    """
    Render the parasite tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param parasite_tree: Parasite tree represented as a Tree object
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from a parasite tree to a host tree
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    :param font_size: Font size for the text of the tips and internal nodes of the tree
    :param longest_host_name: The number of symbols in the longest host tree tip name
    """
    root = parasite_tree.root_node
    _render_parasite_helper(fig, root, recon_obj, host_lookup, parasite_lookup, show_internal_labels, show_freq, font_size, longest_host_name)


def _populate_host_tracks(node: tree.Node, recon_obj: recon.Reconciliation, host_lookup: dict):
    """
    :param node: Node object
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    """
    mapping_node = recon_obj.mapping_of(node.name)
    event = recon_obj.event_of(mapping_node)
    host_name = mapping_node.host
    host_node = host_lookup[host_name]

    if not(event.event_type is recon.EventType.DUPLICATION or event.event_type is recon.EventType.TRANSFER):
        host_node.update_count()
    else:
        if not(_is_sharing_track(node, host_name, recon_obj)):
            host_node.update_count()

    if not(node.is_leaf()):
        _populate_host_tracks(node.left_node, recon_obj, host_lookup)
        _populate_host_tracks(node.right_node, recon_obj, host_lookup)


def _is_sharing_track(node: tree.Node, host_name: str, recon_obj: recon.Reconciliation):
    """
    Determines if a node is sharing it's horizontal track with its children
    :param node: Node object representing a parasite event
    :param host_name: Name of host node
    :param recon_obj: Reconciliation Object
    """
    left_host_name = recon_obj.mapping_of(node.left_node.name).host
    right_host_name = recon_obj.mapping_of(node.right_node.name).host

    return host_name == left_host_name or host_name == right_host_name


def _render_parasite_helper(fig: plot_tools.FigureWrapper,  node: tree.Node, recon_obj: recon.Reconciliation, host_lookup: dict, parasite_lookup: dict, show_internal_labels: bool, show_freq: bool, font_size: float, longest_host_name : int):
    """
    Helper function for rendering the parasite tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object representing the parasite event being rendered
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    :param font_size: Font size for the text of the tips and internal nodes of the tree
    :param longest_host_name: The number of symbols in the longest host tree tip name
    """
    # mapping_node is of type MappingNode which associates
    # a parasite to a host in a reconciliation
    mapping_node = recon_obj.mapping_of(node.name)

    # A reconciliation has an event_of method which is an object of
    # type Event.
    event = recon_obj.event_of(mapping_node)

    host_name = mapping_node.host

    # host_lookup is a dictionary computed in the Tree class
    # that associates a host name (a string) with the correspond node
    # object for that host.  The node object contains layout information
    # which we need here.
    host_node = host_lookup[host_name]

    # Set parasite node layout
    host_row = host_node.layout.row
    # host_col = host_node.layout.col
    # host_x = host_node.layout.x
    host_y = host_node.layout.y
    node.set_layout(row=host_row, x=node.layout.col, y=host_y)

    # Render parasite node and recurse if not a leaf
    if node.is_leaf():
        node.layout.y += host_node.get_and_update_track(tree.Track.HORIZONTAL) * host_node.layout.offset
        _render_parasite_node(fig, node, event, font_size, longest_host_name)
        return

    # If the Node is in their own track, change their position
    if not(_is_sharing_track(node, host_name, recon_obj)):
        node.layout.y += host_node.layout.h_track * host_node.layout.offset

    left_node, right_node = _get_children(node, recon_obj, parasite_lookup)

    _render_parasite_helper(fig, left_node, recon_obj, host_lookup,
        parasite_lookup, show_internal_labels, show_freq, font_size, longest_host_name)
    _render_parasite_helper(fig, right_node, recon_obj, host_lookup,
        parasite_lookup, show_internal_labels, show_freq, font_size, longest_host_name)

    # Checking to see if left node is mapped to the same host node as parent
    if node.layout.row == left_node.layout.row:
        node.set_layout(y=left_node.layout.y)
    elif node.layout.row == right_node.layout.row:
        node.set_layout(y=right_node.layout.y)
    elif event.event_type is recon.EventType.TRANSFER:
        node.layout.y = host_node.layout.y + host_node.layout.h_track * host_node.layout.offset
    
    min_col = host_lookup[recon_obj.mapping_of(right_node.name).host].parent_node.layout.col
    #Checks to see if transfer node is inconsistent and if it can be fixed
    if event.event_type is recon.EventType.TRANSFER and min_col >= node.layout.col:
        _fix_transfer(node, left_node, right_node, host_node, host_lookup, parasite_lookup, recon_obj)

    _render_parasite_branches(fig, node, recon_obj, host_lookup, parasite_lookup)
    _render_parasite_node(fig, node, event, font_size, longest_host_name, show_internal_labels, show_freq)


def _fix_transfer(node: tree.Node, left_node, right_node: tree.Node, host_node: tree.Node, host_lookup: dict, parasite_lookup: dict, recon_obj: recon.Reconciliation, node_col: float = None, offset_number: int = 1):
    """
    Checks to see in tranfer node is inconsistent and the tries to fix node if it can be slid down the host edge
    The tries to push a given node forward if possible to correct the assumed inconsistency
    :param node: Node object representing the parasite event being rendered
    :param node: Right node of the node object
    :param left_node: Left node of the node object
    :param right_node: Right node of the node object
    :param host_node: Node object represeting a host that the parasite node is mapped to
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param node_col: Column of the node, used when function is called recursively to check the next available transfer spot
    :param offset_number: Used to push node to an available transfer spot
    """
    min_col = host_lookup[recon_obj.mapping_of(right_node.name).host].parent_node.layout.col
    max_col = host_node.layout.col
    node_col = node.layout.col
    max_col = min(host_node.layout.col, left_node.layout.col)
    if not(node_col):
        node_col = node.layout.col

    # Checks to see if transfer is inconsistent and if the inconsistency can be fixed by sliding the transfer node down the host edge
    if min_col >= node_col and min_col < max_col and not(_is_sharing_track(node, host_node.name, recon_obj)):
        node.set_layout(col=min_col+0.5, x=min_col+0.5)
    if min_col < max_col:
        new_value = min_col + render_settings.PUSHED_NODE_OFFSET * offset_number
        if _is_col_taken(new_value, host_lookup, parasite_lookup):
            _fix_transfer(node, left_node, right_node, host_node, host_lookup, parasite_lookup, recon_obj, node_col=new_value, offset_number = offset_number + 1)
        else:
            node.set_layout(col=new_value, x=new_value)


def _is_col_taken(node_col, host_lookup, parasite_lookup):
    """
    Checks to see if a node is already in a given col
    :param node_col: Column of a given node
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :return True if there is already a node at the given column and False otherwise
    """
    for key in host_lookup:
        if host_lookup[key].layout.col == node_col:
            return True
    for key in parasite_lookup:
        if parasite_lookup[key].layout.col == node_col:
            return True
    return False


def _render_parasite_node(fig: plot_tools.FigureWrapper,  node: tree.Node, event: recon.Event, font_size: float, longest_host_name : int, show_internal_labels: bool = False, show_freq: bool = False):
    """
    Renders a single parasite node
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: parasite Node that will be rendered
    :param event: Event object that gives event for the given Node
    :param font_size: Font size for text
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    :param longest_host_name: The number of symbols in the longest host tree tip name
    """

    node_pos = plot_tools.Position(node.layout.x, node.layout.y)
    render_color, render_shape = _event_color_shape(event)


    if node.is_leaf():
        fig.text_v2((node.layout.x + render_settings.TIP_TEXT_OFFSET_X, node.layout.y), "-"*(3+longest_host_name)+node.name, render_color, size=font_size, vertical_alignment=render_settings.TIP_ALIGNMENT)
        return

    fig.dot(node_pos, col=render_color, marker=render_shape)
    text = ''
    text_color = plot_tools.transparent_color(render_color, render_settings.INTERNAL_NODE_ALPHA)
    if show_internal_labels and show_freq:
        text = node.name + ', ' + _get_frequency_text(event.freq)
    elif show_internal_labels:
        text = node.name
    elif show_freq:
        if event.freq:
            text = _get_frequency_text(event.freq)
        else:
            raise RuntimeError("Could not render reconciliation: show_freq is True but event.freq is None")
    if text:
        fig.text_v2(node_pos, text, text_color, size=font_size, border_col=render_settings.PARASITE_NODE_BORDER_COLOR)


def _get_frequency_text(frequency: float):
    """
    Give the frequency as a string in percentage form
    :param frequency: The frequency of an event
    :return a string that has the frequency as a percentage
    """
    return str(round(frequency * 100))


def _calculate_font_size(num_tip_nodes: int):
    """
    Calculates the font_size
    :param num_tip_nodes: Number of tip nodes in a tree
    :return the font size for the tips and internal nodes of a tree
    """
    x = (render_settings.START_SIZE - num_tip_nodes) / render_settings.STEP_SIZE
    return FONT_SIZE_STRETCH * _sigmoid(x)  # 3.0 is a magic value that can be adjusted


def _sigmoid(x: float):
    """
    sigmoid Function
    :param x: A number to be plugged into the function
    :return a sigmoid value based on the input value, x
    """
    return (1 / (1 + math.e**(-SIGMOID_SCALE*x)))  # 0.8 is a magic value that can be adjusted


def _render_parasite_branches(fig: plot_tools.FigureWrapper,  node: tree.Node, recon_obj: recon.Reconciliation, host_lookup: dict, parasite_lookup: dict):
    """
    Very basic branch drawing
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object representing the parasite event being rendered
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    """
    node_pos = plot_tools.Position(node.layout.x, node.layout.y)

    left_node, right_node = _get_children(node, recon_obj, parasite_lookup)

    right_pos = plot_tools.Position(right_node.layout.x, right_node.layout.y)

    mapping_node = recon_obj.mapping_of(node.name)
    event = recon_obj.event_of(mapping_node)

    if event.event_type is recon.EventType.COSPECIATION:
        _render_cospeciation_branch(node, host_lookup, parasite_lookup, recon_obj, fig)
    elif event.event_type is recon.EventType.DUPLICATION:
        _connect_children(node, host_lookup, parasite_lookup, recon_obj, fig)
    elif event.event_type is recon.EventType.TRANSFER:
        _render_transfer_branch(node_pos, right_pos, fig, node, host_lookup, recon_obj, right_node)
        _connect_child_to_parent(node, left_node, host_lookup, recon_obj, fig)
    else:
        raise ValueError('%s is not an known event type' % event.event_type)
    # Losses are implicitly implied and are not mapped to any specific node


def _connect_children(node: tree.Node, host_lookup: dict, parasite_lookup: dict, recon_obj: recon.Reconciliation, fig: plot_tools.FigureWrapper):
    """
    Connects the children of a node
    :param node: Node object representing a parasite event
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    left_node, right_node = _get_children(node, recon_obj, parasite_lookup)
    _connect_child_to_parent(node, left_node, host_lookup, recon_obj, fig)
    _connect_child_to_parent(node, right_node, host_lookup, recon_obj, fig)


def _render_loss_branch(node_pos: plot_tools.Position, next_pos: plot_tools.Position, fig: plot_tools.FigureWrapper):
    """
    Renders a loss branch given a two positions
    :param node_pos: x and y position of a node
    :param next_pos: x and y position of another node
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    # Create vertical line to next node
    mid_pos = plot_tools.Position(node_pos.x, next_pos.y)
    fig.line(node_pos, mid_pos, render_settings.LOSS_EDGE_COLOR, linestyle='--')
    fig.line(mid_pos, next_pos, render_settings.PARASITE_EDGE_COLOR)


def _render_cospeciation_branch(node: tree.Node, host_lookup: dict, parasite_lookup: dict, recon_obj: recon.Reconciliation, fig: plot_tools.FigureWrapper):
    """
    Renders the cospeciation branch.
    :param node: Node object representing the parasite event being rendered
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    left_node, right_node = _get_children(node, recon_obj, parasite_lookup)

    node_pos = plot_tools.Position(node.layout.x, node.layout.y)
    left_pos = plot_tools.Position(left_node.layout.x, left_node.layout.y)
    right_pos = plot_tools.Position(right_node.layout.x, right_node.layout.y)

    mapping_node = recon_obj.mapping_of(node.name)
    host_node = host_lookup[mapping_node.host]

    # Update h_track
    host_node.get_and_update_track(tree.Track.HORIZONTAL)

    left_mapping_node = recon_obj.mapping_of(left_node.name)
    left_host_node = host_lookup[left_mapping_node.host]

    right_mapping_node = recon_obj.mapping_of(right_node.name)
    right_host_node = host_lookup[right_mapping_node.host]
    # Draw left node
    offset = host_node.layout.offset
    if host_node.left_node.name == left_host_node.name:
        _render_curved_line_to(node_pos, left_pos, fig)
        if host_node.layout.lower_v_track < (host_node.layout.x - node_pos.x) / offset:
            host_node.layout.lower_v_track += (host_node.layout.x - node_pos.x) / offset + offset
    else:
        stop_row = host_node.left_node.layout.row
        _connect_child_to_parent(node, left_node, host_lookup, recon_obj, fig, stop_row=stop_row)

    # Draw Right node
    if host_node.right_node.name == right_host_node.name:
        _render_curved_line_to(node_pos, right_pos, fig)
        if host_node.layout.upper_v_track < (host_node.layout.x - node_pos.x) / offset:
            host_node.layout.upper_v_track += (host_node.layout.x - node_pos.x) / offset + offset
    else:
        stop_row = host_node.right_node.layout.row
        _connect_child_to_parent(node, right_node, host_lookup, recon_obj, fig, stop_row=stop_row)


def _get_children(node: tree.Node, recon_obj: recon.Reconciliation, parasite_lookup: dict):
    """
    Gets the children of a node in the order they appear in the mapping node.
    :param node: Node object representing a parasite event
    :param recon_obj: Reconciliation Object
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :return A tuple consisting of the left node and right node
    """
    mapping_node = recon_obj.mapping_of(node.name)
    event = recon_obj.event_of(mapping_node)
    left_mapping_node = event.left
    right_mapping_node = event.right
    left_node_name = left_mapping_node.parasite
    right_node_name = right_mapping_node.parasite

    left_node = parasite_lookup[left_node_name]
    right_node = parasite_lookup[right_node_name]

    return left_node, right_node


def _render_curved_line_to(node_pos: plot_tools.Position, other_pos: plot_tools.Position, fig: plot_tools.FigureWrapper):
    """
    Renders a curved line from one point to another
    :param node_pos: x and y position of a node
    :param other_pos: x and y position of another node
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    mid_pos = plot_tools.Position(node_pos.x, other_pos.y)
    fig.line(node_pos, mid_pos, render_settings.PARASITE_EDGE_COLOR)
    fig.line(mid_pos, other_pos, render_settings.PARASITE_EDGE_COLOR)


def _render_transfer_branch(node_pos: plot_tools.Position, right_pos: plot_tools.Position, fig: plot_tools.FigureWrapper,  node: tree.Node, host_lookup: dict, recon_obj: recon.Reconciliation, right_node: tree.Node):
    """
    Renders a transfer branch
    :param node_xy: x and y position of a node
    :param right_pos: x and y position of the right child of a node
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object representing the parasite event being rendered
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param right_node: The right node object of node
    """

    child_mapping_node = recon_obj.mapping_of(right_node.name)
    child_host_node = host_lookup[child_mapping_node.host]

    # Check temporal consistency of transfer event
    if child_host_node.parent_node.layout.col < node.layout.col:
        # Draw right node, which is transfered
        mid_pos = plot_tools.Position(node_pos.x, right_pos.y)  # xy coords of midpoint
        y_midpoint = abs(mid_pos.y + node_pos.y) / 2  # value of midpoint between mid_xy and parent node

        # Determine if transfer is upwards or downwards, and draw triangle accordingly
        is_upwards = True if y_midpoint < mid_pos.y else False
        arrow_pos = plot_tools.Position(node_pos.x, y_midpoint)
        if is_upwards:
            fig.triangle(arrow_pos, render_settings.PARASITE_EDGE_COLOR)
        else:
            fig.triangle(arrow_pos, render_settings.PARASITE_EDGE_COLOR, rotation=render_settings.DOWN_ARROW_ROTATION)

        # Draw branch to midpoint, then draw branch to child
        fig.line(node_pos, mid_pos, render_settings.PARASITE_EDGE_COLOR)
        fig.line(mid_pos, right_pos, render_settings.PARASITE_EDGE_COLOR)
    else:
        transfer_edge_color = plot_tools.transparent_color(render_settings.PARASITE_EDGE_COLOR, render_settings.TRANSFER_TRANSPARENCY)
        fig.arrow_segment(node_pos, right_pos, transfer_edge_color)
        fig.line(node_pos, right_pos, transfer_edge_color)


def _connect_child_to_parent(node: tree.Node, child_node: tree.Node, host_lookup: dict, recon_obj: recon.Reconciliation, fig: plot_tools.FigureWrapper,  stop_row: float = None):
    """
    Connects a child node to its parent node
    :param node: Node object representing a parasite event
    :param child_node: The child node object of a given node
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon_obj: Reconciliation object that represents an edge-to-edge mapping from  a parasite tree to a host tree
    :param fig: Figure object that visualizes trees using MatplotLib
    :param stop_row: row number to stop line drawing on
    """
    mapping_node = recon_obj.mapping_of(child_node.name)
    host_node = host_lookup[mapping_node.host]
    
    if stop_row == None:
        stop_row = node.layout.row
    
    current_pos = plot_tools.Position(child_node.layout.x, child_node.layout.y)

    while host_node.layout.row != stop_row and host_node.parent_node:
        parent_node = host_node.parent_node
        if parent_node.layout.row < host_node.layout.row:
            v_track = parent_node.get_and_update_track(tree.Track.UPPER_VERTICAL)
        else:
            v_track = parent_node.get_and_update_track(tree.Track.LOWER_VERTICAL)
            while v_track < parent_node.layout.upper_v_track:
                v_track = parent_node.get_and_update_track(tree.Track.LOWER_VERTICAL)
        h_track = parent_node.get_and_update_track(tree.Track.HORIZONTAL)
        offset = parent_node.layout.offset

        sub_parent_pos = plot_tools.Position(parent_node.layout.x - (offset * v_track), \
            parent_node.layout.y + (offset * h_track))

        _render_loss_branch(sub_parent_pos, current_pos, fig)

        host_node = parent_node
        current_pos = sub_parent_pos
    
    node_pos = plot_tools.Position(node.layout.x, node.layout.y)
    mid_pos = plot_tools.Position(node_pos.x, current_pos.y)

    fig.line(node_pos, mid_pos, render_settings.PARASITE_EDGE_COLOR)
    fig.line(mid_pos, current_pos, render_settings.PARASITE_EDGE_COLOR)


def _event_color_shape(event: recon.Event):
    """
    Gives the color and shape for drawing event, depending on event type
    :param event: Event object
    :return A tuple with the color and shape of an event
    """
    if event.event_type is recon.EventType.TIPTIP:
        return render_settings.LEAF_NODE_COLOR, render_settings.LEAF_NODE_SHAPE
    if event.event_type is recon.EventType.COSPECIATION:
        return render_settings.COSPECIATION_NODE_COLOR, render_settings.COSPECIATION_NODE_SHAPE
    if event.event_type is recon.EventType.DUPLICATION:
        return render_settings.DUPLICATION_NODE_COLOR, render_settings.DUPLICATION_NODE_SHAPE
    if event.event_type is recon.EventType.TRANSFER:
        return render_settings.TRANSFER_NODE_COLOR, render_settings.TRANSFER_NODE_SHAPE
    return None, None 


def _set_host_node_layout(host_tree: tree.Tree):
    """
    Sets the logicalRow and logicalCol values of each Node in host_tree.
    Assumes that each host Node has its order set already and this function
    uses those values and structure of the tree to set the logicalRow and logicalCol
    :param host_tree:  A Tree object representing the host tree
    :return None
    """
    # Sets logical row values for leaves in the order they appear in the list of host tree leaves
    logical_row_counter = 0
    for leaf in host_tree.leaf_list():
        leaf.layout.row = logical_row_counter
        leaf.layout.x = leaf.layout.col  # This can be scaled if desired
        leaf.layout.y = leaf.layout.row  # This can be scaled if desired
        logical_row_counter += 1
    # Helper function to assign row values, postorder traversal
    _set_internal_host_nodes(host_tree.root_node)


def _set_internal_host_nodes(node: tree.Node):
    """
    Helper function for set_host_node_layout
    :param node: Host Node object that will be rendered
    """
    if node.is_leaf():
        return
    _set_internal_host_nodes(node.left_node)
    _set_internal_host_nodes(node.right_node)
    node.layout.row = (node.left_node.layout.row + node.right_node.layout.row) / 2
    node.layout.x = node.layout.col  # This can be scaled if desired
    node.layout.y = node.layout.row  # This can be scaled if desired
