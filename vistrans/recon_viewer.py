"""
recon_viewer.py
View a single reconciliation using matplotlib
"""

from recon import EventType
from tree import Track
from math import exp, ceil
import utils
import plot_tools
from render_settings import *

def render(host_dict, parasite_dict, recon_dict, show_internal_labels=False, show_freq=False):
    """ Renders a reconciliation using matplotlib
    :param host_dict:  Host tree represented in dictionary format
    :param parasite_dict:  Parasite tree represented in dictionary format
    :recon_dict: Reconciliation represented in dictionary format
    """
    host_tree, parasite_tree, recon, consistency_type = utils.convert_to_objects(host_dict, parasite_dict, recon_dict)

    fig = plot_tools.FigureWrapper(TREE_TITLE, consistency_type)

    #Calculates font sizes
    num_tips = len(host_tree.leaf_list) + len(parasite_tree.leaf_list)
    num_nodes = len(host_tree.postorder_list) + len(parasite_tree.postorder_list)
    tip_font_size, internal_font_size = calculate_font_size(num_tips, num_nodes)

    root = parasite_tree.root_node
    host_lookup = host_tree.name_to_node_dict()
    parasite_lookup = parasite_tree.name_to_node_dict()
    
    #Populate Host Nodes with track count
    populate_host_tracks(root, recon, host_lookup)
    
    #Render Host Tree
    render_host(fig, host_tree, show_internal_labels, tip_font_size, internal_font_size)
    
    #Sets the offsets between tracks on each host node
    set_offsets(host_tree)
    
    #Render Parasite Tree
    render_parasite(fig, parasite_tree, recon, host_lookup, parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size)

    #Show Visualization
    fig.show()

def set_offsets(tree):
    """
    Populates the nodes of a Tree with an offset
    :param tree: Tree Object
    """
    pos_dict = tree.pos_dict
    
    for node in tree.postorder_list:
        y_1 = None
        y_0 = node.layout.row
        for logical_pos in pos_dict:
            if node.is_leaf:
                if y_0 < logical_pos[0] and node.layout.col <= logical_pos[1]:
                    if y_1 == None or y_1 > logical_pos[0]:
                        y_1 = logical_pos[0]
            else:
                y_1 = max(node.left_node.layout.row, node.right_node.layout.row)
        if y_1 == None or node.layout.node_count == 0:
            node.layout.offset = TRACK_OFFSET
        else:
            node.layout.offset = abs(y_0 - y_1) / (node.layout.node_count + 3)

def render_host(fig, host_tree, show_internal_labels, tip_font_size, internal_font_size):
    """
    Renders the host tree
    :param host_tree: Host tree represented as a Tree object
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param tip_font_size: Font size for the text of the tips of the tree
    :param internal_font_size: Font size for text of the internal nodes of the tree
    """
    set_host_node_layout(host_tree)
    root = host_tree.root_node
    draw_host_handle(fig, root)
    render_host_helper(fig, root, show_internal_labels, tip_font_size, internal_font_size, host_tree)

def draw_host_handle(fig, root):
    """
    Draw edge leading to root of host tree.
    :param root: The root node of a tree object
    """
    fig.line((0, root.layout.y), (root.layout.x, root.layout.y), HOST_EDGE_COLOR)

def render_host_helper(fig, node, show_internal_labels, tip_font_size, internal_font_size, host_tree):
    """
    Helper function for rendering the host tree.
    :param node: node object
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param tip_font_size: Font size for the text of the tips of the tree
    :param internal_font_size: Font size for text of the internal nodes of the tree
    :param host_tree: Tree object representing a Host Tree
    """
    host_tree.pos_dict[(node.layout.row, node.layout.col)] = node
    node_x, node_y = node.layout.x, node.layout.y
    node_xy = (node_x, node_y)
    if node.is_leaf:
        text_offset = (node_x + TIP_TEXT_OFFSET[0], node_y + TIP_TEXT_OFFSET[1])
        fig.dot(node_xy, col = HOST_NODE_COLOR)
        if node.layout.node_count == 0:
            fig.text(text_offset, node.name, HOST_NODE_COLOR, size = tip_font_size, vertical_alignment=TIP_ALIGNMENT)
        else:
            fig.text(text_offset, node.name, HOST_NODE_COLOR, size = tip_font_size/node.layout.node_count, vertical_alignment=TIP_ALIGNMENT)    
    else:
        fig.dot(node_xy, col = HOST_NODE_COLOR)  # Render host node
        if show_internal_labels:
            color = HOST_NODE_COLOR[0:3] + (INTERNAL_NODE_ALPHA,)
            text_xy = (node_x + INTERNAL_TEXT_OFFSET[0], node_y + INTERNAL_TEXT_OFFSET[1])
            fig.text(text_xy, node.name, color, size = internal_font_size, border_col=HOST_NODE_BORDER_COLOR)
        left_x, left_y = node.left_node.layout.x, node.left_node.layout.y
        right_x, right_y = node.right_node.layout.x, node.right_node.layout.y
        fig.line(node_xy, (node_x, left_y), HOST_EDGE_COLOR)
        fig.line(node_xy, (node_x, right_y), HOST_EDGE_COLOR)
        fig.line((node_x, left_y), (left_x, left_y), HOST_EDGE_COLOR)
        fig.line((node_x, right_y), (right_x, right_y), HOST_EDGE_COLOR)
        render_host_helper(fig, node.left_node, show_internal_labels, tip_font_size, internal_font_size, host_tree)
        render_host_helper(fig, node.right_node, show_internal_labels, tip_font_size, internal_font_size, host_tree)

def render_parasite(fig, parasite_tree, recon, host_lookup, parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size):
    """
    Render the parasite tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param parasite_tree: Parasite tree represented as a Tree object
    :param recon: Reconciliation object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    :param tip_font_size: Font size for the text of the tips of the tree
    :param internal_font_size: Font size for text of the internal nodes of the tree
    """
    root = parasite_tree.root_node
    render_parasite_helper(fig, root, recon, host_lookup, parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size)

def populate_host_tracks(node, recon, host_lookup):
    """
    :param node: Node object
    :param recon: Reconciliation object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    """
    mapping_node = recon.mapping_of(node.name)
    event = recon.event_of(mapping_node)
    host_name = mapping_node.host
    host_node = host_lookup[host_name]

    if not(event.event_type is EventType.DUPLICATION or event.event_type is EventType.TRANSFER):
        host_node.update_count()
    else:
        if not(is_sharing_track(node, host_name, recon)):
            host_node.update_count()
        
    if not(node.is_leaf):
        populate_host_tracks(node.left_node, recon, host_lookup)
        populate_host_tracks(node.right_node, recon, host_lookup)


def is_sharing_track(node, host_name, recon):
    """
    Determines if a node is on its own track
    :param node: Node object
    :param host_name: Name of host node
    :param recon: Reconciliation Object
    """
    left_host_name = recon.mapping_of(node.left_node.name).host
    right_host_name = recon.mapping_of(node.right_node.name).host

    return host_name == left_host_name or host_name == right_host_name

def render_parasite_helper(fig, node, recon, host_lookup, parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size):
    """
    Helper function for rendering the parasite tree.
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object
    :param recon: Reconciliation object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    :param tip_font_size: Font size for the text of the tips of the tree
    :param internal_font_size: Font size for text of the internal nodes of the tree
    """
    # mapping_node is of type MappingNode which associates
    # a parasite to a host in a reconciliation
    mapping_node = recon.mapping_of(node.name)

    # A reconciliation has an event_of method which is an object of
    # type Event.
    event = recon.event_of(mapping_node)

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
    if node.is_leaf:
        node.layout.y += host_node.iter_track(Track.HORIZONTAL) * host_node.layout.offset
        render_parasite_node(fig, node, event, (tip_font_size/host_node.layout.node_count))
        return

    #If the Node is in their own track, change their position
    if not(is_sharing_track(node, host_name, recon)):
        node.layout.y += host_node.layout.h_track * host_node.layout.offset

    left_node, right_node = get_children(node, recon, parasite_lookup)

    render_parasite_helper(fig, left_node, recon, host_lookup, \
        parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size)
    render_parasite_helper(fig, right_node, recon, host_lookup, \
        parasite_lookup, show_internal_labels, show_freq, tip_font_size, internal_font_size)
    
    #Checking to see if left node is mapped to the same host node as parent
    if node.layout.row == left_node.layout.row:
        node.set_layout(y=left_node.layout.y)
    elif event.event_type is EventType.TRANSFER:
        node.layout.y = host_node.layout.y + host_node.layout.h_track * host_node.layout.offset

    render_parasite_branches(fig, node, recon, host_lookup, parasite_lookup)
    render_parasite_node(fig, node, event, tip_font_size, show_internal_labels, show_freq)

def render_parasite_node(fig, node, event, font_size, show_internal_labels=False, show_freq=False):
    """
    Renders a single parasite node
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object
    :param event: Event object
    :param font_size: Font size for text
    :param show_internal_labels: Boolean that determines whether or not the internal labels are shown
    :param show_freq: Boolean that determines wheter or not the frequencies are shown
    """
    node_xy = (node.layout.x, node.layout.y)
    render_color, render_shape = event_color_shape(event)
    
    fig.dot(node_xy, col = render_color, marker = render_shape)
    if node.is_leaf:
        fig.text((node.layout.x + TIP_TEXT_OFFSET[0], node.layout.y + TIP_TEXT_OFFSET[1]), node.name, render_color, size = font_size, vertical_alignment=TIP_ALIGNMENT)
    elif show_internal_labels:
        render_color = render_color[0:3] + (INTERNAL_NODE_ALPHA,)
        text_xy = (node_xy[0] + INTERNAL_TEXT_OFFSET[0], node_xy[1] + INTERNAL_TEXT_OFFSET[1])
        fig.text(text_xy, node.name, render_color, size = font_size, border_col=PARASITE_NODE_BORDER_COLOR)
    if show_freq:
        fig.text(node_xy, event.freq, render_color, size = font_size, border_col=PARASITE_NODE_BORDER_COLOR)

def calculate_font_size(num_tips, num_nodes):
    """
    Calculates the font_size
    :param num_tips: Number of tips in a tree
    :param num_nodes: Number of nodes in a tree
    :return a tuple containing the font sizes for the tips and internal nodes of a tree
    """
    tip_font_size = cap_font_size(num_tips/num_nodes)
    internal_font_size = cap_font_size((num_nodes - num_tips) /num_nodes)

    return tip_font_size, internal_font_size

def cap_font_size(font_size):
    """
    Calculates a font size that does not exceed a max or min
    :param font_size: an integer that represents the font size of text
    :return a new font size
    """

    if font_size < MIN_FONT_SIZE:
        return MIN_FONT_SIZE
    elif font_size > MAX_FONT_SIZE:
        return MAX_FONT_SIZE
    else:
        return font_size


def render_parasite_branches(fig, node, recon, host_lookup, parasite_lookup):
    """
    Very basic branch drawing
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object
    :param recon: Reconciliation object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    """
    node_xy = (node.layout.x, node.layout.y)

    left_node, right_node = get_children(node, recon, parasite_lookup)

    right_xy = (right_node.layout.x, right_node.layout.y)

    mapping_node = recon.mapping_of(node.name)
    event = recon.event_of(mapping_node)

    if event.event_type is EventType.COSPECIATION:
        render_cospeciation_branch(node, host_lookup, parasite_lookup, recon, fig)
    elif event.event_type is EventType.DUPLICATION:
        connect_children(node, host_lookup, parasite_lookup, recon, fig)
    elif event.event_type is EventType.TRANSFER:
        render_transfer_branch(node_xy, right_xy, fig, node, host_lookup, recon, right_node)
        connect_child_to_parent(node, left_node, host_lookup, recon, fig)
    else:
        raise ValueError('%s is not an known event type' % event.event_type)
    # Losses are implicitly implied and are not mapped to any specific node


def connect_children(node, host_lookup, parasite_lookup, recon, fig):
    """
    Connects the children of a node
    :param node: Node object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon: Reconciliation object
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    left_node, right_node = get_children(node, recon, parasite_lookup)
    connect_child_to_parent(node, left_node, host_lookup, recon, fig)
    connect_child_to_parent(node, right_node, host_lookup, recon, fig)

def render_loss_branch(node_xy, next_xy, fig):
    """
    Renders a loss branch given a two positions
    :param node_xy: x and y position of a node
    :param next_xy: x and y position of another node
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    #Create vertical line to next node
    mid_xy = (node_xy[0],next_xy[1])
    fig.line(node_xy, mid_xy, LOSS_EDGE_COLOR, linestyle='--')
    fig.line(mid_xy, next_xy, PARASITE_EDGE_COLOR)

def render_cospeciation_branch(node, host_lookup, parasite_lookup, recon, fig):
    """
    Renders the cospeciation branch.
    :param node: Node object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :param recon: Reconciliation object
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    left_node, right_node = get_children(node, recon, parasite_lookup)

    node_xy = (node.layout.x, node.layout.y)
    left_xy = (left_node.layout.x, left_node.layout.y)
    right_xy = (right_node.layout.x, right_node.layout.y)

    mapping_node = recon.mapping_of(node.name)
    host_node = host_lookup[mapping_node.host]

    #Update h_track
    host_node.iter_track(Track.HORIZONTAL)

    left_mapping_node = recon.mapping_of(left_node.name)
    left_host_node = host_lookup[left_mapping_node.host]

    right_mapping_node = recon.mapping_of(right_node.name)
    right_host_node = host_lookup[right_mapping_node.host]
    #Draw left node
    offset = host_node.layout.offset
    if host_node.left_node.name == left_host_node.name:
        render_curved_line_to(node_xy, left_xy, fig)
        host_node.layout.lower_v_track += (host_node.layout.x - node_xy[0]) / offset
    else:
        stop_row = host_node.left_node.layout.row
        connect_child_to_parent(node, left_node, host_lookup, recon, fig, stop_row=stop_row)

    #Draw Right node
    if host_node.right_node.name == right_host_node.name:
        render_curved_line_to(node_xy, right_xy, fig)
        host_node.layout.upper_v_track += (host_node.layout.x - node_xy[0]) / offset
    else:
        stop_row = host_node.right_node.layout.row
        connect_child_to_parent(node, right_node, host_lookup, recon, fig, stop_row=stop_row)


def get_children(node, recon, parasite_lookup):
    """
    Gets the children of a node in the order they appear in the mapping node.
    :param node: Node object
    :param recon: Reconciliation Object
    :param parasite_lookup: Dictionary with parasite node names as the key and parasite node objects as the values
    :return A tuple consisting of the left node and right node
    """
    mapping_node = recon.mapping_of(node.name)
    event = recon.event_of(mapping_node)
    left_mapping_node = event.left
    right_mapping_node = event.right
    left_node_name = left_mapping_node.parasite
    right_node_name = right_mapping_node.parasite

    left_node = parasite_lookup[left_node_name]
    right_node = parasite_lookup[right_node_name]

    return left_node, right_node

def render_curved_line_to(node_xy, other_xy, fig):
    """
    Renders a curved line from one point to another
    :param node_xy: x and y position of a node
    :param other_xy: x and y position of another node
    :param fig: Figure object that visualizes trees using MatplotLib
    """
    mid_xy = (node_xy[0], other_xy[1])
    fig.line(node_xy, mid_xy, PARASITE_EDGE_COLOR)
    fig.line(mid_xy, other_xy, PARASITE_EDGE_COLOR)

def render_transfer_branch(node_xy, right_xy, fig, node, host_lookup, recon, right_node):
    """
    Renders a transfer branch
    :param node_xy: x and y position of a node
    :param right_xy: x and y position of the right child of a node
    :param fig: Figure object that visualizes trees using MatplotLib
    :param node: Node object
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon: Reconciliation object
    :param right_node: The right node object of node
    """
    mapping_node = recon.mapping_of(node.name)
    host_node = host_lookup[mapping_node.host]

    child_mapping_node = recon.mapping_of(right_node.name)
    child_host_node = host_lookup[child_mapping_node.host]

    #check temporal consistency of transfer event
    if child_host_node.parent_node.layout.col < node.layout.col:
        #Draw right node, which is transfered
        mid_xy = (node_xy[0], right_xy[1])          #xy coords of midpoint
        y_midpoint = abs(mid_xy[1]+ node_xy[1])/2   #value of midpoint between mid_xy and parent node

        #determine if transfer is upwards or downwards, and draw triangle accordingly
        is_upwards = True if y_midpoint < mid_xy[1] else False
        if is_upwards:
            fig.up_triangle((node_xy[0], y_midpoint), PARASITE_EDGE_COLOR)
        else:
            fig.down_triangle((node_xy[0], y_midpoint), PARASITE_EDGE_COLOR)

        #draw branch to midpoint, then draw branch to child
        fig.line(node_xy, mid_xy, PARASITE_EDGE_COLOR)
        fig.line(mid_xy, right_xy, PARASITE_EDGE_COLOR)
    else:
        transfer_edge_color = (PARASITE_EDGE_COLOR[0] , PARASITE_EDGE_COLOR[1] , PARASITE_EDGE_COLOR[2], TRANSFER_TRANSPARENCY)
        fig.line(node_xy, right_xy, transfer_edge_color)

def connect_child_to_parent(node, child_node, host_lookup, recon, fig, stop_row=None):
    """
    Connects a child node to its parent node
    :param node: Node object
    :param child_node: The child node object of a given node
    :param host_lookup: Dictionary with host node names as the key and host node objects as the values
    :param recon: Reconciliation object
    :param fig: Figure object that visualizes trees using MatplotLib
    :param stop_row: row number to stop line drawing on
    """
    mapping_node = recon.mapping_of(child_node.name)
    host_node = host_lookup[mapping_node.host]
    
    if stop_row == None:
        stop_row = node.layout.row
    
    current_xy = (child_node.layout.x, child_node.layout.y)

    while host_node.layout.row != stop_row and host_node.parent_node:
        parent_node = host_node.parent_node
        if parent_node.layout.row < host_node.layout.row:
            v_track = parent_node.iter_track(Track.UPPER_VERTICAL)
        else:
            v_track = parent_node.iter_track(Track.LOWER_VERTICAL)
            while v_track < parent_node.layout.upper_v_track:
                v_track = parent_node.iter_track(Track.LOWER_VERTICAL)
        h_track = parent_node.iter_track(Track.HORIZONTAL)
        offset = parent_node.layout.offset

        sub_parent_xy = (parent_node.layout.x - (offset * v_track), \
            parent_node.layout.y + (offset * h_track))

        render_loss_branch(sub_parent_xy, current_xy, fig)

        host_node = parent_node
        current_xy = sub_parent_xy
    
    node_xy = (node.layout.x, node.layout.y)
    mid_xy = (node_xy[0], current_xy[1])

    fig.line(node_xy, mid_xy, PARASITE_EDGE_COLOR)
    fig.line(mid_xy, current_xy, PARASITE_EDGE_COLOR)

def event_color_shape(event):
    """
    Gives the color and shape for drawing event, depending on event type
    :param event: Event object
    :return A tuple with the color and shape of an event
    """
    if event.event_type is EventType.TIPTIP:
        return LEAF_NODE_COLOR, LEAF_NODE_SHAPE
    if event.event_type is EventType.COSPECIATION:
        return COSPECIATION_NODE_COLOR, COSPECIATION_NODE_SHAPE
    if event.event_type is EventType.DUPLICATION:
        return DUPLICATION_NODE_COLOR, DUPLICATION_NODE_SHAPE
    if event.event_type is EventType.TRANSFER:
        return TRANSFER_NODE_COLOR, TRANSFER_NODE_SHAPE
    return plot_tools.BLACK

def set_host_node_layout(host_tree):
    """
    Sets the logicalRow and logicalCol values of each Node in host_tree.
    Assumes that each host Node has its order set already and this function
    uses those values and structure of the tree to set the logicalRow and logicalCol
    :param host_tree:  A Tree object representing the host tree
    :return None
    """
    #sets logical row values for leaves in the order they appear in the list of host tree leaves
    logical_row_counter = 0
    for leaf in host_tree.leaf_list:
        leaf.layout.row = logical_row_counter
        leaf.layout.x = leaf.layout.col           # This can be scaled if desired
        leaf.layout.y = leaf.layout.row           # This can be scaled if desired
        logical_row_counter += 1
    #helper function to assign row values, postorder traversal
    set_internal_host_nodes(host_tree.root_node)

def set_internal_host_nodes(node):
    """
    Helper function for set_host_node_layout
    :param node: Node object
    """
    if node.is_leaf:
        return
    set_internal_host_nodes(node.left_node)
    set_internal_host_nodes(node.right_node)
    node.layout.row = (node.left_node.layout.row + node.right_node.layout.row)/2
    node.layout.x = node.layout.col         # This can be scaled if desired
    node.layout.y = node.layout.row         # This can be scaled if desired
