from enum import Enum

# You should assume that you'll get the following from eMPRess:
# 1. Host tree:  A Tree object with all of its attributes already populated
# 2. Parasite tree:  A Tree object with all of its attributres already populated
# HOWEVER, the Node objects in these trees will NOT have their logicalRow/logicalCol
# nor their xcoord/ycoord computed yet.

# Type of a tree:  either a host tree or a parasite tree
class TreeType(Enum):
    HOST = 1
    PARASITE = 2

# Type of an event
class EventType(Enum):
    COSPECIATION = 0
    DUPLICATION = 1
    TRANSFER = 2
    LOSS = 3
    TIPTIP = 4  # Tip to Tip association; aka contemporaneous leaf association

# The Node class defines a node of a tree
class Node:
    def __init__(self, name=None):
        self.name = name        # String; name of this host or parasite
        self.root = False       # Boolean:  True iff this is the root
        self.is_leaf = False       # Boolean: True iff this is a leaf
        self.parent = None      # Node: parent of this Node
        self.leftChild = None   # Node: first child of this Node
        self.rightChild = None  # Node: second child of this Node
        self.order = None       # Int: order of this node; root will be at 0, 
                                #   all leaves share largest value
        self.logicalRow = None  # Float: logical position of this Node in rendering
        self.logicalCol = None  # Float: logical position of thss Node in rendering
                                #   Most likely, logicalCol = order, so this field is redundant 
        self.xcoord = None      # Int:  x-coordinate for rendering
        self.ycoord = None      # Int:  y-coordinate for rendering

# The Tree type defines a tree
class Tree:
    def __init__(self, rootNode=None, allNodes=None, treeType=None):
        self.rootNode = rootNode    # Node:  Root Node of the Tree
        self.allNodes = allNodes    # List of Nodes:  All Nodes in the tree


        self.leaves = []            # List of Nodes:  List of leaves in tree from left (top) to right (bottom)
        self.updateLeaves()

        self.nameToNode = dict()    # Dictionary of Node name (string) to Node
        self.setNameToNode()

        self.type = treeType            # TreeType (TreeType.HOST or TreeType.PARASITE)

    def setNameToNode(self):
        if self.allNodes:
            for node in self.allNodes:
                self.nameToNode[node.name] = node


    def updateLeaves(self):
        """ Sets self.leaves to the list of all leaf Nodes. """
        self.leaves = self.updateLeaves_helper(self.rootNode)

    def updateLeaves_helper(self, node):
        if node.is_leaf:
            return [node]
        
        else:
            leftSubtreeLeaves = self.updateLeaves_helper(node.leftChild)
            rightSubtreeLeaves = self.updateLeaves_helper(node.rightChild)
            leftSubtreeLeaves.extend(rightSubtreeLeaves)
            return leftSubtreeLeaves


# An Event keeps the name of the parasite (a string; this is redundant 
# since it's just the key), the name of the host to which that parasite is mapped in the
# reconciliation (a string), the type of that event (an EventType), and the frequency of this 
# Event in MPR space.
class Event:
    def __init__(self, parasite=None, host=None, etype=None, freq=0):
        self.parsiteName = parasite # String:  Name of parasite (same as key value in ReconMap)
        self.hostName = host        # String:  Name of host
        self.eventType = etype      # EventType
        self.frequency = freq       # Float:  Frequency (support value) for this event

# The ReconMap is a representation of a DTL reconciliation.
# The primary component is a self.recon which is a dictionary which maps parasite names (strings)
# to Events.  
class ReconMap:
    def __init__(self):
        self.recon = dict()       # Dictionary:  Keys are parasite names (strings) and values 
                                  # are Events

    def addEvent(self, event):
        '''Adds event to the recon dictionary'''
        #Set Dictionary Key and Value
        self.recon[event.parsiteName] = event
    
    def getMap(self):
        '''returns the reconMap'''
        return self.recon
    
    def getEvent(self, node_name):
        '''returns the event associated with node'''
        return self.recon[node_name]

