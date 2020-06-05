# ReconRender.py
# This code draws a representation of a given host tree, parasite tree, and reconfiguration
# using tkinter

import tkinter as tk
from ReconBuilder import build_trees_with_temporal_order
import Constants as cons

def render_tree(host_tree, parasite_tree, reconciliation):
    """
    Renders Host tree and Parasite tree using tkinter
    :param host_tree:  host tree dictionary
    :param parasite_tree:  parasite tree dictionary
    :param reconciliation:  reconciliation dictionary
    :return: None
    """
   
    #Create our tree objects
    host_tree_object, parasite_tree_object = build_trees_with_temporal_order(host_tree, parasite_tree, reconciliation)
    

    #Set the values for the logical rows of our tree object
    compute_node_logical_rows(host_tree_object, parasite_tree_object, reconciliation)


def compute_node_logical_rows(host_tree_object, parasite_tree_object, reconciliation):
    '''
    Sets the logicalRow values of each Node in the host and parasite tree.
    Assumes that each Node has its logical column set already and this function
    uses those values and the reconfiguration to set logicalRow and logicalCol
    :param host_tree_object:  A Tree object representing the host tree
    :param parasite_tree_object:  A Tree object representing the parasite tree
    :param reconciliation:  reconciliation dictionary
    :return None
    '''

    compute_host_logical_rows(host_tree_object)
    compute_parasite_logical_rows(parasite_tree_object, reconciliation)




def compute_host_logical_rows(host_tree_object):
    '''
    Sets the logicalRow values of each Node in the host tree.
    Assumes that each host Node has its column set already and this function
    uses those values and structure of the tree to set the logicalRow
    :param host_tree_object:  A Tree object representing the host tree
    :return None
    '''

    row_counter = 0
    for node in host_tree_object:
        if node.is_leaf:
            node.layout.row = row_counter
            row_counter += 1
        else:
            node.layout.row = (node.left_node.layout.row + node.right_node.layout.row) / 2


def compute_parasite_logical_rows(parasite_tree_object, reconciliation):
    '''
    Sets the logicalRow values of each Node in the parasite tree.
    Assumes that each host Node has its column set already and this function
    uses those values and structure of the tree to set the logicalRow
    :param parasite_tree_object:  A Tree object representing the parasite tree
    :return None
    '''

    # TODO Get this to work with new Recon class




def compute_host_node_actual_positions(host_tree_object, canvas):
    """
    Sets the xcoord and ycoord for rendering the Node host tree
    :param host_tree:  A Tree object representing the host tree
    :parem x_min: Integer; minimum x-coordinate for tree rendering
    :param x_max: Integer; maximum y-coordinate for tree rendering
    :param y_min: Integer; minimum y-coordinate for tree rendering
    :param y_max: Integer; maximum y-coordinate for tree rendering
    :return: None
    """


def render_host_tree(host_tree_root, canvas):
    '''
    Draws the given host tree using tkinter
    :param host_tree_object: A Tree object representing the host tree
    :param canvas: Drawing canvas from tkinter
    :return None
    '''
