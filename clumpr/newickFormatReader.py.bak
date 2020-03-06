# newickFormatReader.py
# Ran Libeskind-Hadas, October 2013
# Newick file reader and parser

# Uses BioPython's Phylo package to read and parse a newick tree with internal
# node names specified.  Specifically, the input is of the form
# (LeftTree, RightTree) RootName
# LeftTree and RightTree are themselves newick trees and RootName is the
# name given to the root node.

# All node names (internal and tips) must be non-numeric!

# Returns a dictionary representation of the tree where
# keys are strings that are the names of edges and values are 4-tuples
# of strings of the form:
# (topVertex, bottomVertex, leftEdgeName, rightEdgeName)

# python libraries
from cStringIO import StringIO

# BioPython libraries
from Bio import Phylo

def getInput(fileName):
    """ Takes a fileName as input and returns the hostTree, parasiteTree, and tip mapping phi. """

    fileHandle = open(fileName, 'r')
    hostTree, parasiteTree, phi = newickFormatReader(fileHandle)
    fileHandle.close()
    return hostTree, parasiteTree, phi

def newickFormatReader(fileHandle):
    """ Queries the user for a newick host tree, newick parasite tree, and
        a tip association file.  Reads those files, parses them, and returns
        the three items.  The file of associations contains entries of the form
        parasiteTip:hostTip, one entry per line.
        The trees are returned in the dictionary format
        used by xscape and the tip associations are returned as a dictionary
        with parasite names as keys and host tips as values. """

    if isinstance(fileHandle, basestring):
        fileHandle = open(fileHandle, 'r')
        autoclose = True
    else:
        autoclose = False

    # Read contents, split the host tree, parasite tree, and tip associations
    contents = fileHandle.read()
    hostString, parasiteString, phiString = contents.split(";")
    hostString = hostString.strip()
    parasiteString = parasiteString.strip()
    phiList = phiString.split()

    # Parse the input and build dictionary representations
    hostDict = parseNewick(hostString, "host")
    parasiteDict = parseNewick(parasiteString, "parasite")
    phiDict = parsePhi(phiList)

    if autoclose:
        fileHandle.close()

    return hostDict, parasiteDict, phiDict

def parseNewick(newickString, treeType):
    """ Queries the user for a newick file name and returns the contents
        of that file in the dictionary representation used by the xscape
        tools. """
    tree = Phylo.read(StringIO(newickString), "newick")
    distanceDict = tree.depths(unit_branch_lengths=True)
    D = {}
    for clade in distanceDict:
        name = clade.name
        dist = distanceDict[clade]
        D[name] = dist
    dfsList = [(node.name, int(D[node.name])) for node in tree.find_clades()]
    treeDict = {}
    buildTreeDictionary(buildTree(dfsList), "Top", treeDict, treeType)
    return treeDict

def buildTree(dfsList):
    """ Takes as input a list of tuples of the form (nodeName, distanceFromRoot)
        and returns a tuple representation of the tree of the form
        (Root, Left, Right) where Left and Right are themselves of this form
        or None. This is an intermediate tree representation that can then
        be used to build the dictionary representation of trees used in
        the xscape tools."""
    if len(dfsList) == 1:
        return (dfsList[0][0], None, None)
    else:
        rootName = dfsList[0][0]
        dist = dfsList[0][1]
        splitPoint = 0
        for x in range(len(dfsList)-1, 0, -1):
            if dfsList[x][1] == dist+1:
                splitPoint = x
                break
        leftList = dfsList[1:splitPoint]
        rightList = dfsList[splitPoint:]
        leftTree = buildTree(leftList)
        rightTree = buildTree(rightList)
        return (rootName, leftTree, rightTree)

def buildTreeDictionary(tupleTree, parentVertex, D, treeType):
    """ Takes as input a tuple representation of a tree (constructed by
        the buildTree function, for example) and returns the dictionary
        representation of the tree used by the xscape tools. """
    root = tupleTree[0]
    leftTree = tupleTree[1]
    rightTree = tupleTree[2]
    if treeType == "parasite" and parentVertex == "Top":
        edgeName = "pTop"
    elif treeType == "host" and parentVertex == "Top":
        edgeName = "hTop"
    else:
        edgeName = (parentVertex, root)

    if leftTree == None:  # and thus rightTree == None and this is a leaf
        D[edgeName] = edgeName + (None, None)
    else:
        leftEdgeName = (root, leftTree[0])
        rightEdgeName = (root, rightTree[0])
        if edgeName == "pTop":
            D[edgeName] = ("Top", root, leftEdgeName, rightEdgeName)
        elif edgeName == "hTop":
            D[edgeName] = ("Top", root, leftEdgeName, rightEdgeName)
        else:
            D[edgeName] = edgeName + (leftEdgeName, rightEdgeName)
        buildTreeDictionary(leftTree, root, D, treeType)
        buildTreeDictionary(rightTree, root, D, treeType)

def parsePhi(pairs):
    """ Queries the user for a file name containing tip associations of
        the form parasiteTip:hostTip, one entry per line.  Returns a
        tip association dictionary. """

    phiDict = {}
    for pair in pairs:
        parasite, colon, host = pair.partition(":")
        key = parasite.strip()
        value = host.strip()
        phiDict[key] = value
    return phiDict


