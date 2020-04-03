# ReconGraphFileInterchange.py
# Written July 19 2017 by Eli Zupke
# A small program for saving and loading DTL reconciliation graphs to tab delineated SIF files.
# This file is not very robust, and does not sanitize inputs. It will break if node names contain spaces or dashes.
#
# This file would be much more useful if we could save attributes (Like whether any particular node is part of a median)
# to a SIF file, but this would actually require a file format change, as SIF does not seem to support that kind of
# thing. If expanded in this way, then you would have a powerful debugging and art-generation tool on your hands.

# These two variables are the strings we use to delimit the two node types. Safer characters would be '(', ')', and
# ',', as they are used in the newick files and are probably safe.
mapping_deliminator = "-"
event_deliminator = " "


def event_node_to_string(event):
    """
    Take a python event node ('T','c1','c2') and turn it into a string 'T c1 c2'.
    :param event:   The event node we are converting
    :return:        The SIF representation of the event
    """
    return event[0] + event_deliminator + mapping_node_to_string(event[1]) + event_deliminator + \
        mapping_node_to_string(event[2])


def mapping_node_to_string(mapping):
    """
    Takes a python mapping node ('u', 'U') and turns it into a string 'u-U'
    :param mapping:     The mapping node we are converting
    :return:            The SIF representation of the mapping node.
    """
    if mapping == (None, None):
        return ""  # We encode none mapping nodes as empty strings for some reason
    else:
        return mapping[0] + mapping_deliminator + mapping[1]


def write_mapping_to_event(mapping, event, output):
    """
    Takes a python mapping node ('u', 'U') and a python event node ('T','c1','c2'), and writes the SIF representation
    of the relationship between them, 'u-U____me____T c1 c2' (where 4 underscores represent one tab), or in the case
    of contemporaneous events, 'u-U____me____C u-U'
    :param mapping:     The python mapping node that has the event node
    :param event:       The event node we are converting
    :param output:      The file we have opened and are writing to
    """
    if event[0] == 'C':
        output.write(mapping_node_to_string(mapping) + "\tme\t" + "C " + mapping_node_to_string(mapping))
    else:
        output.write(mapping_node_to_string(mapping) + "\tme\t" + event_node_to_string(event))
    output.write("\n")


def write_event_to_mapping(event, output):
    """
    Takes a python event node ('T','c1','c2') and writes the SIF representation of the relationship between it and its
    mapping node children.
    :param event:
    :param output:
    """
    if event[1] != (None, None):
        output.write(event_node_to_string(event) + "\tem\t" + mapping_node_to_string(event[1]))
        output.write("\n")
    if event[2] != (None, None):
        output.write(event_node_to_string(event) + "\tem\t" + mapping_node_to_string(event[2]))
        output.write("\n")


def read_mapping(mapping):
    """
    Turns a string inside the sif file into the mapping node that it represents
    :param mapping:     The string representation of the mapping node (of format 'u-U')
    :return:            The python representation of the mapping node (of format ('u', 'U')
    """
    if len(mapping) == 0:  # We encode none mapping nodes as empty strings for some reason
        return None, None
    (u, U) = mapping.split(mapping_deliminator)
    return u, U


def save_recon_graph(recon_graph, file_path):

    """
    Turns a DTL reconciliation graph into a sif file that can be visualized by programs like Cytoscape, or re-imported
    :param recon_graph: The reconciliation graph we are exporting
    :param file_path:    The location we are saving this sif file.
    """
    assert event_deliminator != mapping_deliminator, "Mapping and event nodes must use different deliminators!"
    with open(file_path, "w") as output:
        for mapping_node in recon_graph:
            for event_node in recon_graph[mapping_node]:
                write_mapping_to_event(mapping_node, event_node, output)
                write_event_to_mapping(event_node, output)


def load_recon_graph(file_path):

    """
    Turns an sif file created by this program into a DTL reconciliation graph that this program can read. Note that this
    function makes drastic assumptions about the file it is fed; namely, that the event nodes names contain the names
    of their mapping node children.
    :param file_path:    The location of the graph we are trying to load.
    :return:             A dtl reconciliation graph, represented as a dictionary (see other files for a reference)
    """
    dtl_recon_graph = {}
    assert event_deliminator != mapping_deliminator, "Mapping and event nodes must use different deliminators!"
    with open(file_path, "r") as input_file:
        for row in input_file:
            source, rel_type, destination = row.split("\t")
            destination = destination.replace("\n", "")
            if rel_type == "em":
                # A more robust reader would probably use these edges, but we can infer them from the 'me' edges.
                continue
            elif rel_type == "me":
                # This means that source is a mapping node and destination is an event node
                last_seen_node = read_mapping(source)
                if last_seen_node not in dtl_recon_graph:
                    dtl_recon_graph[last_seen_node] = []
                if destination[0] == "C":
                    # If the event node is a contemporaneous event, then we will need to do this from scratch
                    t = "C"
                    c1 = (None, None)
                    c2 = (None, None)
                else:
                    # Otherwise, we can read in the event node.
                    (t, c1, c2) = destination.split(event_deliminator)
                    c1 = read_mapping(c1)
                    c2 = read_mapping(c2)
                dtl_recon_graph[last_seen_node] += [(t, c1, c2)]
            else:
                raise IOError("Unknown relationship type {0}".format(rel_type))
    return dtl_recon_graph
