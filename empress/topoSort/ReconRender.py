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
    """
   
    #Sets up canvas
    window = tk.Tk()
    window.title(cons.WINDOW_NAME)

    frame = tk.Frame(window)
    frame.pack()

    canvas = tk.Canvas(frame, width = cons.WINDOW_WIDTH, height = cons.WINDOW_HEIGHT)
    canvas.pack()

    #Create our tree objects
    host_tree_object, parasite_tree_object = build_trees_with_temporal_order(host_tree, parasite_tree, reconciliation)
    
    #Set the values for the logical rows of our tree objects
    compute_node_logical_rows(host_tree_object, parasite_tree_object, reconciliation)


    #Render Host Tree
    render_host_tree(host_tree_root, canvas)

    #Displays canvas
    canvas.pack()
    window.mainloop()



def compute_node_logical_rows(host_tree_object, parasite_tree_object, reconciliation):
    """
    Sets the row values of each Node in the host and parasite tree.
    Assumes that each Node has its logical column set already and this function
    uses those values and the reconfiguration to set row and logicalCol
    :param host_tree_object:  A Tree object representing the host tree
    :param parasite_tree_object:  A Tree object representing the parasite tree
    :param reconciliation:  reconciliation dictionary
    """

    compute_host_logical_rows(host_tree_object)
    compute_parasite_logical_rows(parasite_tree_object, reconciliation)




def compute_host_logical_rows(host_tree_object):
    """
    Sets the row values of each Node in the host tree.
    Assumes that each host Node has its column set already and this function
    uses those values and structure of the tree to set the row
    :param host_tree_object:  A Tree object representing the host tree
    """

    row_counter = 0
    for node in host_tree_object:
        if node.is_leaf:
            node.layout.row = row_counter
            row_counter += 1

    #helper function to assign row values, postorder traversal
    compute_host_logical_rows_helper(host_tree_object.rootNode)

    
def compute_host_logical_rows_helper(node):
    """takes a Node, and calculates logical row values"""

    #if both children of node have a logical row value, we can calculate the logical row value of node
    if node.right_node.layout.row is not None and node.left_node.layout.row is not None:
        node.layout.row = ((node.right_node.layout.row+node.left_node.layout.row)/2)
        return

    #recursively calculate logical row values of the right subtree 
    if node.right_node.layout.row == None:
        compute_host_logical_rows_helper(node.right_node)
    #recursively calculate logical row values of the left subtree
    if node.left_node.layout.row == None:
        compute_host_logical_rows_helper(node.left_node)
    
    #finally, calculate logical row value of node using just-calculated children values
    node.layout.row = ((node.right_node.layout.row+node.left_node.layout.row)/2)



    
def compute_parasite_logical_rows(parasite_tree_object, reconciliation):
    """
    Sets the row values of each Node in the parasite tree.
    Assumes that each host Node has its column set already and this function
    uses those values and structure of the tree to set the row
    :param parasite_tree_object:  A Tree object representing the parasite tree
    """
    # TODO Get this to work with new Recon class


def compute_host_node_actual_positions(host_tree_object, canvas):
    """
    Sets the xcoord and ycoord for rendering the Node host tree
    :param host_tree_object:  A Tree object representing the host tree
    :param canvas: Drawing Canvas from tkinter
    """
    #Gives us the boundaries of the drawing space on canvas along with units
    x_min, y_min, x_max, y_max, x_unit, y_unit = set_parameters(canvas)

    #Gives us the unit space between logical positions
    x_unit, y_unit = set_units()

def set_boundaries(canvas):
    pass

def set_parameters(canvas):
    #x_min, y_min, x_max, y_max = set_boundaries(canvas)

def render_host_tree(host_tree_root, canvas):
    """
    Draws the given host tree using tkinter
    :param host_tree_object: A Tree object representing the host tree
    :param canvas: Drawing canvas from tkinter
    """

    #Populates each node with x and y values for their actual positions
    compute_host_node_actual_positions(host_tree_object, canvas)


    