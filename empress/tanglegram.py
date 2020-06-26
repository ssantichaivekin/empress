import newickFormatReader
import tree_format_converter
import Tree
import plot_tools
import copy
import random  # You won't use this!

host_counter = 0.0
parasite_counter = 0.0
def get_host_parasite_phi(filename):
    host_dict, parasite_dict, phi = newickFormatReader.getInput(filename)
    host_tree = tree_format_converter.dict_to_tree(host_dict, Tree.TreeType.HOST)
    parasite_tree = tree_format_converter.dict_to_tree(parasite_dict, Tree.TreeType.PARASITE)
    return host_tree, parasite_tree, phi

def render(host_tree, parasite_tree, phi, graph_title, show_internal_labels, mapping_color):
    fig = plot_tools.FigureWrapper(graph_title+"\nHost Tree | Parasite Tree")
    render_helper_host(fig, host_tree.root_node, show_internal_labels, mapping_color)
    render_helper_parasite(fig, parasite_tree.root_node, show_internal_labels, mapping_color)

    host_dict = {}
    for host in host_tree.leaf_list():
        host_dict[host.name] = host

    # connect hosts leaves to parasite leaves
    for leaf in parasite_tree.leaf_list():
        parasite = leaf
        host = host_dict[phi[leaf.name]]
        if mapping_color == "Gray":
            color = plot_tools.GRAY
        else:
            color = (random.uniform(0.2,1), random.uniform(0.2,1), random.uniform(0.2,1), 1)
        fig.line((host.layout.col, host.layout.row), (parasite.layout.col, parasite.layout.row), col=color)

    fig.show()

def render_helper_host (fig, node, show_internal_labels, mapping_color):
    if node.is_leaf:
        #plot_loc = (random.uniform(0, 100), random.uniform(0, 100))  # this is goofy!
        global host_counter

        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = Tree.NodeLayout()
        leaf_layout.col = -20.0
        leaf_layout.row = copy.deepcopy(host_counter)
        host_counter += 5.0
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        fig.text(plot_loc, node.name, col=plot_tools.BLUE, h_a='left')

    else:
        # recursively call helper funciton on child nodes
        render_helper_host(fig, node.left_node, show_internal_labels, mapping_color)
        render_helper_host(fig, node.right_node, show_internal_labels, mapping_color)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = Tree.NodeLayout()
        node.layout.col = min(right_layout.col, left_layout.col) - 10.0
        y_avg = (float(right_layout.row)+float(left_layout.row))/2.0
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels == "Y":
            fig.text(current_loc, node.name, col=plot_tools.BLUE, h_a='left')

        # draw line from current node to left node
        left_loc = (left_layout.col, left_layout.row)
        fig.line(current_loc, (node.layout.col, left_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, left_layout.row), left_loc, col=plot_tools.BLACK)

        # draw line from current node to right node
        right_loc = (right_layout.col, right_layout.row)
        fig.line(current_loc, (node.layout.col, right_layout.row), col=plot_tools.BLACK)
        fig.line((node.layout.col, right_layout.row), right_loc, col=plot_tools.BLACK)


def render_helper_parasite(fig, node, show_internal_labels, mapping_color):
    if node.is_leaf:
        #plot_loc = (random.uniform(0, 100), random.uniform(0, 100))  # this is goofy!
        global parasite_counter

        # set up layout for node (will be used later for drawing lines between nodes)
        leaf_layout = Tree.NodeLayout()
        leaf_layout.col = 20.0
        leaf_layout.row = copy.deepcopy(parasite_counter)
        parasite_counter += 5.0
        node.layout = leaf_layout

        # plot node using leaf_layout
        plot_loc = (leaf_layout.col, leaf_layout.row)
        fig.text(plot_loc, node.name, col=plot_tools.BLUE, h_a='right')

    else:
        # recursively call helper funciton on child nodes
        render_helper_parasite(fig, node.left_node, show_internal_labels, mapping_color)
        render_helper_parasite(fig, node.right_node, show_internal_labels, mapping_color)

        # get layouts for child nodes to determine position of current node
        right_layout = node.right_node.layout
        left_layout = node.left_node.layout

        # create layout for current node
        node.layout = Tree.NodeLayout()
        node.layout.col = max(left_layout.col, right_layout.col) + 10.0
        y_avg = (float(right_layout.row)+float(left_layout.row))/2.0
        node.layout.row = y_avg

        # plot node using node_layout
        current_loc = (node.layout.col, node.layout.row)
        if show_internal_labels == "Y":
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
    host_tree, parasite_tree, phi = get_host_parasite_phi(file_name)
    graph_title = input("Title of graph: ")
    show_internal_labels = input("Show internal labels. Y/N?: ")
    mapping_color = input("Choose mapping color. Gray/Random?: ")
    render(host_tree, parasite_tree, phi, graph_title, show_internal_labels, mapping_color)


if __name__ == '__main__':
    main()
