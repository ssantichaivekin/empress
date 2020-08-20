from . import newickFormatReader
from . import tree_format_converter
from . import tree
from . import plot_tools
from mip import *

VERTICAL_OFFSET = 20
HORIZONTAL_SPACING = 10
LEAF_SPACING = 5
HOST_COUNTER = 0
PARASITE_COUNTER = 0

def get_host_parasite_phi(filename):
    """
    To be removed
    """
    host_dict, parasite_dict, phi = newickFormatReader.getInput(filename)
    return host_dict, parasite_dict, phi

def render(host_dict: dict, parasite_dict: dict, phi: dict, show_internal_labels: bool) -> None:
    """
    Render tanglegram
    :param host_dict - host tree (dictionary representation)
    :param parasite_dict - parasite tree (dictionary representation)
    :param phi - tip mapping dictionary
    :param show_internal_labes - boolean indicator of whether internal node names should
        be displayed
    """
    fig = plot_tools.FigureWrapper("Host | Parasite")
    host_tree = tree_format_converter.dict_to_tree(host_dict, tree.TreeType.HOST)
    parasite_tree = tree_format_converter.dict_to_tree(parasite_dict, tree.TreeType.PARASITE)

    """Uncomment first block for ILP, second block for polynomial uncrossings"""
    # host_swap_dict, parasite_swap_dict = get_swap_dicts(host_tree, parasite_tree, phi, 2) 
    # parasite_tree.root_node.swap_fix(parasite_swap_dict)
    # host_tree.root_node.swap_fix(host_swap_dict)
    
    # parasite_swap_dict = get_one_tree_swap_dict(host_tree, parasite_tree, phi)
    # parasite_tree.root_node.swap_fix(parasite_swap_dict)

    host_dict = {}
    for host in host_tree.leaf_list():
        host_dict[host.name] = host

    render_helper_host(fig, host_tree.root_node, show_internal_labels)
    render_helper_parasite(fig, parasite_tree.root_node, show_internal_labels)

    # connect hosts leaves to parasite leaves
    for leaf in parasite_tree.leaf_list():
        parasite = leaf
        host = host_dict[phi[leaf.name]]
        fig.line((host.layout.col, host.layout.row), (parasite.layout.col, parasite.layout.row),
                 col=plot_tools.GRAY, style='--')

    fig.show()

def get_one_tree_swap_dict(host_tree, parasite_tree, mapping):
    """
    Get the swap dictionary with the one-tree polynomial time algorithm
    :param host_tree - host tree (tree representation)
    :param parasite_tree - parasite tree (tree representation)
    :param phi - tip mapping dictionary
    :return swap dictionary
    """
    host_order_dict, parasite_order_dict = generate_orders(host_tree, parasite_tree, mapping)[2], generate_orders(host_tree, parasite_tree, mapping)[3]
    count = count_crossings(host_order_dict, parasite_order_dict, mapping)
    swap_dict = get_one_tree_swap_helper(parasite_tree.root_node, host_tree, parasite_tree, mapping, count, {})
    return swap_dict

def get_one_tree_swap_helper(node, host_tree, parasite_tree, mapping, count, swap_dict):
    if not node.is_leaf:
        node.swap()
        host_order_dict, parasite_order_dict = generate_orders(host_tree, parasite_tree, mapping)[2], generate_orders(host_tree, parasite_tree, mapping)[3]
        node.swap()
        if count_crossings(host_order_dict, parasite_order_dict, mapping) < count:
            swap_dict[node.name] = 0
        else:
            swap_dict[node.name] = 1
        swap_dict = get_one_tree_swap_helper(node.left_node, host_tree, parasite_tree, mapping, count, swap_dict)
        swap_dict = get_one_tree_swap_helper(node.right_node, host_tree, parasite_tree, mapping, count, swap_dict)
    return swap_dict

def in_left_subtree(root, target, bound_dict, order_dict):
    return order_dict[target] <= bound_dict[root][1]

def create_bounds(inner_node_list, num_dict):
    """
    Creates dictionary of the leftmost and rightmost leaves for each inner node in a tree
    :param inner_node_list - list of inner nodes in tree
    :param num_dict - dictionary with key of a leaf and value of the position of its mapping in the original order 
    :param phi - tip mapping dictionary
    :return bound_dict - dictionary of the left/rightmost leaves for inner nodes of tree
    """
    bound_dict = {}
    for node in inner_node_list:
        left = node.left_node
        leaf_1 = left
        leaf_2 = left
        while not leaf_1.is_leaf:
            leaf_1 = leaf_1.left_node
        while not leaf_2.is_leaf:
            leaf_2 = leaf_2.right_node
        right = node.right_node
        leaf_3 = right
        leaf_4 = right
        while not leaf_3.is_leaf:
            leaf_3 = leaf_3.left_node
        while not leaf_4.is_leaf:
            leaf_4 = leaf_4.right_node
        bound_dict[node] = [num_dict[leaf_1], num_dict[leaf_2], num_dict[leaf_3], num_dict[leaf_4]]
    return bound_dict

def get_swap_dicts(host_tree, parasite_tree, phi, num_trees):
    """
    Gets the swap dictionaries for both trees with the ILP optimization
    :param host_tree - host tree (tree representation)
    :param parasite_tree - parasite tree (tree representation)
    :param phi - tip mapping dictionary
    :param num_trees - int 1 or 2 to do 1 or 2 tree optimization
    :return host_swap_dict, parasite_swap_dict - the dictionaries for which inner nodes to switch
    """
    host_num_dict, parasite_num_dict, host_order_dict, parasite_order_dict, inner_node_list_2, inner_node_list = generate_orders(host_tree, parasite_tree, phi)

    y, y2 = create_model(host_tree, parasite_tree, phi, host_num_dict, parasite_num_dict, host_order_dict, parasite_order_dict, inner_node_list_2, inner_node_list, num_trees)

    parasite_swap_dict = {}
    for i in range(len(inner_node_list)):
        parasite_swap_dict[inner_node_list[i].name] = int(y[i].x)

    host_swap_dict = {}
    for i in range(len(inner_node_list_2)):
        host_swap_dict[inner_node_list_2[i].name] = int(y2[i].x)

    return host_swap_dict, parasite_swap_dict

def create_model(host_tree, parasite_tree, phi, host_num_dict, parasite_num_dict, host_order_dict, parasite_order_dict, inner_node_list_2, inner_node_list, num_trees):
    """
    Creates and optimizes the ILP model
    :param host_tree - host tree (tree representation)
    :param parasite_tree - parasite tree (tree representation)
    :param phi - tip mapping dictionary
    :param host_num_dict - dictionary with key of leaf names and values of their original positions
    :param parasite_num_dict - dictionary with key of leaf names and values of matching host original positions
    :param host_order_dict - dictionary with key of leaf names and values of their positions 
    :param parasite_order_dict - dictionary with key of leaf names and values of their original positions
    :param inner_node_list_2 - postorder list of host inner nodes
    :param inner_node_list - postorder list of parasite inner nodes
    :param num_trees - int number of trees to optimize for (1 or 2)
    :return y, y1 - arrays with each entry 1 or 0 corresponding to parasite and host trees respectively to mark the
    associated node in the inner node lists for swapping children or not
    """
    m = Model()
    x = [[m.add_var(var_type=BINARY) for i in range(len(parasite_tree.leaf_list()) - j - 1, 0, -1)] 
                                     for j in range(len(parasite_tree.leaf_list()))]
    y = [m.add_var(var_type=BINARY) for i in range(len(parasite_tree.postorder_list()) - len(parasite_tree.leaf_list()))]
    
    for i in range(len(inner_node_list)):
        left_leaves = get_left_leaves(inner_node_list[i])
        right_leaves = get_right_leaves(inner_node_list[i])

        for j in range(len(left_leaves)):
            for k in range(len(right_leaves)):
                if parasite_num_dict[left_leaves[j].name] > parasite_num_dict[right_leaves[k].name]:
                    m += 1 - x[parasite_order_dict[left_leaves[j].name]][parasite_order_dict[right_leaves[k].name] - parasite_order_dict[left_leaves[j].name] - 1] == y[i] 
                else:
                    m += y[i] == x[parasite_order_dict[left_leaves[j].name]][parasite_order_dict[right_leaves[k].name] - parasite_order_dict[left_leaves[j].name] - 1]  

    x2 = [[m.add_var(var_type=BINARY) for i in range(len(host_tree.leaf_list()) - j - 1, 0, -1)] 
                                      for j in range(len(host_tree.leaf_list()))]
    y2 = [m.add_var(var_type=BINARY) for i in range(len(host_tree.postorder_list()) - len(host_tree.leaf_list()))]

    for i in range(len(inner_node_list_2)):
        left_leaves = get_left_leaves(inner_node_list_2[i])
        right_leaves = get_right_leaves(inner_node_list_2[i])

        for j in range(len(left_leaves)):
            for k in range(len(right_leaves)):
                if host_num_dict[left_leaves[j].name] > host_num_dict[right_leaves[k].name]:
                    m += 1 - x2[host_order_dict[left_leaves[j].name]][host_order_dict[right_leaves[k].name] - host_order_dict[left_leaves[j].name] - 1] == y2[i] 
                else:
                    m += y2[i] == x2[host_order_dict[left_leaves[j].name]][host_order_dict[right_leaves[k].name] - host_order_dict[left_leaves[j].name] - 1]
    
    z = [[m.add_var(var_type=BINARY) for i in range(len(parasite_tree.leaf_list()) - j - 1, 0, -1)] for j in range(len(parasite_tree.leaf_list()))]
    for i in range(len(x)):
        for j in range(len(x[i])):
            par1 = parasite_tree.leaf_list()[i]
            par2 = parasite_tree.leaf_list()[i + j + 1]
            host1 = phi[par1.name]
            host2 = phi[par2.name]
            pos1 = host_order_dict[host1]
            pos2 = host_order_dict[host2] - pos1 - 1
            if pos2 < 0:
                pos1 = host_order_dict[host2]
                pos2 = host_order_dict[host1] - pos1 - 1
            if pos2 >= 0:
                m += x[i][j] + x2[pos1][pos2] >= z[i][j]
                m += x[i][j] - x2[pos1][pos2] <= z[i][j]
                m += x2[pos1][pos2] - x[i][j] <= z[i][j]
                m += 2 - x[i][j] - x2[pos1][pos2] >= z[i][j]

    if num_trees == 1:
        m.objective = maximize(xsum(x[i][j] for i in range(len(x)) for j in range(len(x[i]))))
    else:
        m.objective = minimize(xsum(z[i][j] for i in range(len(z)) for j in range(len(z[i]))))
    m.verbose = 0
    m.optimize()
    return y, y2

def get_left_leaves(node):
    return get_leaves_helper(node.left_node)

def get_right_leaves(node):
    return get_leaves_helper(node.right_node)
    
def get_leaves_helper(node):
    if node.is_leaf: return [node]
    else:
        list1 = get_leaves_helper(node.left_node)
        list2 = get_leaves_helper(node.right_node)
        list1.extend(list2)
        return list1

def generate_orders(host_tree, parasite_tree, mapping):
    """
    Creates dictionaries for tree properties
    :param host_tree - host tree (tree representation)
    :param parasite_tree - parasite tree (tree representation)
    :param mapping - tip mapping dictionary
    :return host_num_dict, parasite_num_dict - dictionaries with keys of leaf names and values of their position of the associated host
    :return host_order_dict, parasite_order_dict - dictionaries with keys as leaf names and values of their own positions
    :return inner_node_list_2, inner_node_list - postorder list of inner nodes for host and parasite trees respectively
    """
    host_leaves = host_tree.leaf_list()
    parasite_leaves = parasite_tree.leaf_list()

    host_num_dict = {}
    inner_node_list_2 = []
    host_order_dict = {}
    leaf_count = 0
    for i in range(len(host_tree.postorder_list())):
        if host_tree.postorder_list()[i].is_leaf:
            host_order_dict[host_tree.postorder_list()[i].name] = leaf_count
            print(host_order_dict)
            host_num_dict[host_leaves[leaf_count].name] = leaf_count
            print(host_num_dict)
            leaf_count += 1
        else:
            inner_node_list_2.append(host_tree.postorder_list()[i])

    parasite_num_dict = {}
    inner_node_list = []
    parasite_order_dict = {}
    leaf_count = 0
    for i in range(len(parasite_tree.postorder_list())):
        if parasite_tree.postorder_list()[i].is_leaf:
            parasite_order_dict[parasite_tree.postorder_list()[i].name] = leaf_count
            parasite_num_dict[parasite_leaves[leaf_count].name] = host_num_dict[mapping[parasite_leaves[leaf_count].name]]
            leaf_count += 1
        else:
            inner_node_list.append(parasite_tree.postorder_list()[i])

    return host_num_dict, parasite_num_dict, host_order_dict, parasite_order_dict, inner_node_list_2, inner_node_list
    

def count_crossings(host_order_dict, parasite_order_dict, mapping):
    """
    Counts crossings in a tanglegram
    :param host_order_dict - dictionary with keys as leaf names and values of their positions
    :param parasite_order_dict - dictionary with keys as leaf names and values of their positions
    :param mapping - tip mapping dictionary
    :return count - int number of crossings
    """
    checked = []
    count = 0    
    for parasite in parasite_order_dict:
        for leaf in checked:
            if host_order_dict[mapping[leaf]] > host_order_dict[mapping[parasite]]:
                count += 1
        checked.append(parasite)
    return count

def render_helper_host(fig, node, show_internal_labels):
    """
    Render helper for host tree
    """
    if node.is_leaf:
        global HOST_COUNTER

        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = tree.NodeLayout()
        leaf_layout.col = -VERTICAL_OFFSET
        leaf_layout.row = HOST_COUNTER

        HOST_COUNTER += LEAF_SPACING
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        fig.text(plot_loc, node.name, col=plot_tools.BLUE, h_a='left')

    else:
        # recursively call helper funciton on child nodes
        render_helper_host(fig, node.left_node, show_internal_labels)
        render_helper_host(fig, node.right_node, show_internal_labels)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = tree.NodeLayout()
        node.layout.col = min(right_layout.col, left_layout.col) - HORIZONTAL_SPACING
        y_avg = (float(right_layout.row)+float(left_layout.row))/2.0
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels:
            fig.text(current_loc, node.name, col=plot_tools.BLUE, h_a='left')

        # draw line from current node to left node
        left_loc = (left_layout.col, left_layout.row)
        fig.line(current_loc, (node.layout.col, left_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, left_layout.row), left_loc, col=plot_tools.BLACK)

        # draw line from current node to right node
        right_loc = (right_layout.col, right_layout.row)
        fig.line(current_loc, (node.layout.col, right_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, right_layout.row), right_loc, col=plot_tools.BLACK)


def render_helper_parasite(fig, node, show_internal_labels):
    """
    Render helper for parasite tree
    """

    global PARASITE_COUNTER
    if node.is_leaf:
        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = tree.NodeLayout()
        leaf_layout.col = VERTICAL_OFFSET
        leaf_layout.row = PARASITE_COUNTER

        PARASITE_COUNTER += LEAF_SPACING
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        fig.text(plot_loc, node.name, col=plot_tools.BLUE, h_a='right')

    else:
        # recursively call helper funciton on child nodes
        render_helper_parasite(fig, node.left_node, show_internal_labels)
        render_helper_parasite(fig, node.right_node, show_internal_labels)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = tree.NodeLayout()
        node.layout.col = max(left_layout.col, right_layout.col) + HORIZONTAL_SPACING
        y_avg = (float(right_layout.row)+float(left_layout.row))/2.0
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels:
            fig.text(current_loc, node.name, col=plot_tools.BLUE, h_a='right')

        # draw line from current node to left node
        left_loc = (left_layout.col, left_layout.row)
        fig.line(current_loc, (node.layout.col, left_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, left_layout.row), left_loc, col=plot_tools.BLACK)

        # draw line from current node to right node
        right_loc = (right_layout.col, right_layout.row)
        fig.line(current_loc, (node.layout.col, right_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, right_layout.row), right_loc, col=plot_tools.BLACK)

def main():
    file_name = input("Filename: ")
    host_dict, parasite_dict, phi = get_host_parasite_phi(file_name)
    render(host_dict, parasite_dict, phi, show_internal_labels=True)


if __name__ == '__main__':
    main()
