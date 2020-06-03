'''
First written by Dennis Wang,
modified by Santi Santichaivekin (Feb 28, 19).
'''

import networkx as nx

EXAMPLE1 = {
    ('p1', 'h1'): [['C', (None, None), (None, None), 1.0], 0],
    ('p2', 'h3'): [['C', (None, None), (None, None), 1.0], 0],
    ('p3', 'h2'): [['C', (None, None), (None, None), 1.0], 0],
    ('p4', 'h4'): [['C', (None, None), (None, None), 1.0], 0],
    ('p6', 'h7'): [['S', ('p7', 'h1'), ('p8', 'h2'), 0.5], 2],
    ('p6', 'h8'): [['S', ('p7', 'h3'), ('p8', 'h4'), 0.5], 2],
    ('p7', 'h1'): [['T', ('p1', 'h1'), ('p2', 'h3'), 0.5], 1],
    ('p7', 'h3'): [['T', ('p2', 'h3'), ('p1', 'h1'), 0.5], 1],
    ('p8', 'h2'): [['T', ('p3', 'h2'), ('p4', 'h4'), 0.5], 1],
    ('p8', 'h4'): [['T', ('p4', 'h4'), ('p3', 'h2'), 0.5], 1]
}

EXAMPLE2 = {
    ('p1', 'h1'): [('C', (None, None), (None, None))],
    ('p2', 'h3'): [('C', (None, None), (None, None))],
    ('p3', 'h2'): [('C', (None, None), (None, None))],
    ('p4', 'h4'): [('C', (None, None), (None, None))],
    ('p6', 'h7'): [('S', ('p7', 'h1'), ('p8', 'h2'))],
    ('p6', 'h8'): [('S', ('p7', 'h3'), ('p8', 'h4'))],
    ('p7', 'h1'): [('T', ('p1', 'h1'), ('p2', 'h3'))],
    ('p7', 'h3'): [('T', ('p2', 'h3'), ('p1', 'h1'))],
    ('p8', 'h2'): [('T', ('p3', 'h2'), ('p4', 'h4'))],
    ('p8', 'h4'): [('T', ('p4', 'h4'), ('p3', 'h2'))]
}

def eventNodeType(eventNode):
    '''
    Returns 'S', 'T', 'D', L', or 'C'
    'S': speciation
    'D': duplication
    'T': transfer
    'L': loss
    'C': end event
    '''
    return eventNode[0]

def mappingNodeToStr(mappingNode):
    return "{}-{}".format(mappingNode[0], mappingNode[1])

def firstChild(eventNode):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # returns a mapping node
    assert(eventNode[1][0] and eventNode[1][1])
    return eventNode[1]

def secondChild(eventNode):
    # ['T', ('p3', 'h2'), ('p4', 'h4'), 0.5]
    # ['C', (None, None), (None, None), 1.0]
    # returns a mapping node
    # do not use on null entities
    assert(eventNode[2][0] and eventNode[2][1])
    return eventNode[2]

def eventNodeToStr(eventNode):
    # ('S', ('p7', 'h1'), ('p8', 'h2'), 0.5], 2)
    # ('S', ('n32', 'm143'), ('n31', 'm144'))
    if eventNodeType(eventNode) == 'S':
        return "spec | {}-{}, {}-{}".format(
            eventNode[1][0], eventNode[1][1],
            eventNode[2][0], eventNode[2][1]
        )
    elif eventNodeType(eventNode) == 'T':
        return "tran | {}-{}, {}-{}".format(
            eventNode[1][0], eventNode[1][1],
            eventNode[2][0], eventNode[2][1]
        )
    elif eventNodeType(eventNode) == 'D':
        return "dupl | {}-{}, {}-{}".format(
            eventNode[1][0], eventNode[1][1],
            eventNode[2][0], eventNode[2][1]
        )
    elif eventNodeType(eventNode) == 'L':
        return "loss | {}-{}".format(
            eventNode[1][0], eventNode[1][1],
        )
    if eventNodeType(eventNode) == 'C':
        return "END"

def edgesFromReconciliationGraph(dtlGraph):
    outputEdgesList = []
    for mappingNode, eventNodes in list(dtlGraph.items()):
        mappingNodeName = mappingNodeToStr(mappingNode)
        for eventNode in eventNodes :
            # check whether this is an event node or just
            # extra data -- SEE EXAMPLE1
            try:
                assert eventNode[0] in ['S', 'T', 'D', 'L', 'C']
            except:
                continue

            eventNodeName = eventNodeToStr(eventNode)
            # we do not have to insert the end event to
            # the visualization
            if eventNodeType(eventNode) == 'C':
                pass
            # loss has only one children
            elif eventNodeType(eventNode) == 'L':
                outputEdgesList.append((mappingNodeName, eventNodeName))

                nextMappingNodeName = mappingNodeToStr(firstChild(eventNode))
                outputEdgesList.append((eventNodeName, nextMappingNodeName))
            # other types have two children
            else:
                outputEdgesList.append((mappingNodeName, eventNodeName))
             
                nextMappingNodeName0 = mappingNodeToStr(firstChild(eventNode))
                outputEdgesList.append((eventNodeName, nextMappingNodeName0))
                nextMappingNodeName1 = mappingNodeToStr(secondChild(eventNode))
                outputEdgesList.append((eventNodeName, nextMappingNodeName1))

    return outputEdgesList

def visualizeAndSave(dtlGraph, targetFile):
    '''
    Receives that graph part of the reconciliation graph.
    Visualizes it and saves it to targetfile.

    Note: targetfile must ends with .png
    '''
    assert(targetFile.endswith(".png"))
    # creates an empty graph
    nxDtlGraph = nx.DiGraph()
    # add edges -- note that the library already perfers to place
    # topoligically lower nodes on the top
    nxDtlGraph.add_edges_from(edgesFromReconciliationGraph(dtlGraph))
    pydotDtlGraph = nx.drawing.nx_pydot.to_pydot(nxDtlGraph)
    pydotDtlGraph.write_png(targetFile)

if __name__ == '__main__' :
    visualizeAndSave(EXAMPLE1, "example1.png")
    visualizeAndSave(EXAMPLE2, "example2.png")
