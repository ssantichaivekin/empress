'''
This script generates all possible (1) newick host tree 
(2) newick parasite tree and (3) mapping from host to 
parasite.

This script will save the outputs as a .newick files
in the specified folder (see description of at the bottom
of the page).

Author: Santi Santichaivekin
'''

import itertools
import os
import random
random.seed(1)

def generateTreeTuples(numLeaves, prefix, startNum):
    '''
    Generate all possible binary trees with some number of leaves
    in Newick format. It uses a recursive algorithm that
    works by selecting all possible size of the left subtree.
    If we know the size of the left subtree, then we also know
    the size of the right subtree. Then, we recursively generate all
    the possible left and right subtrees recursively.

    Note: We don't actually generate all possible trees in this
    format. In the code, you will see that we only generate a right-heavy
    tree, meaning that the right subtree has equal or greater number of
    nodes than the left subtree. We do this to reduce the number of trees
    that are isomorphic to one another.

    :return: An iterator to trees in python tuple format
    '''
    root = "{}{}".format(prefix, startNum)
    if numLeaves == 1 :
        yield root

    leftTreeStartNum = startNum + 1
    mid = numLeaves // 2
    for leftTreeLeaves in range(1, mid+1): # from 1 to mid inclusive
        rightTreeLeaves = numLeaves - leftTreeLeaves
        rightTreeStartNum = leftTreeStartNum + (2**leftTreeLeaves - 1) # add the left tree size
        for leftTreeTuple in generateTreeTuples(leftTreeLeaves, prefix, leftTreeStartNum) :
            for rightTreeTuple in generateTreeTuples(rightTreeLeaves, prefix, rightTreeStartNum):
                yield (root, leftTreeTuple, rightTreeTuple)

def treeTupleStrings(treeTuple):
    '''
    Convert a python representation of tree to a string in newick format.

    :return: A string represenging the tree
    '''
    if type(treeTuple) is str :
        return treeTuple
    else :
        return "({},{}){}".format(
            treeTupleStrings(treeTuple[1]), # left
            treeTupleStrings(treeTuple[2]), # right
            treeTuple[0] # root
            )

def treeTupleLeaves(treeTuple):
    '''
    Return the list of leaves of the tree.
    '''
    if type(treeTuple) is str :
        leaves = [treeTuple]
        return leaves
    else :
        leaves = []
        # ignore the root treeTuple[0] !
        leaves += treeTupleLeaves(treeTuple[1])
        leaves += treeTupleLeaves(treeTuple[2])
        return leaves

def generateAllMappings(parasiteLeaves, hostLeaves):
    '''
    Return an iterator to all possible parasite tree to
    host tree mapping. Each mapping is represented in lists of tuples. 
    Each tuple is of the form (parasiteLeaf, hostLeaf).
    The list contains |parasiteLeaf| == |hostLeaf| elements.
    '''
    for hostLeavesPermuted in itertools.permutations(hostLeaves) :
        yield list(zip(parasiteLeaves, hostLeavesPermuted))

def generateMappingsViaSample(parasiteLeaves, hostLeaves, n_sample):
    '''
    Return an iterator to some possible parasite tree to
    host tree mapping. Thue number of mappings generated is set
    by using the n_sample parameter.
    Each mapping is represented in lists of tuples. 
    Each tuple is of the form (parasiteLeaf, hostLeaf).
    The list contains |parasiteLeaf| == |hostLeaf| elements.
    '''
    for _ in range(n_sample):
        hostLeavesPermuted = random.sample(hostLeaves, len(hostLeaves))
        yield list(zip(parasiteLeaves, hostLeavesPermuted))

def mappingToString(parasiteHostMapping):
    '''
    Return a string representing the parasite tree to host tree mapping
    in newick format.
    '''
    outStr = ""
    for parasiteLeaf, hostLeaf in parasiteHostMapping :
        outStr += "{}:{}\n".format(parasiteLeaf, hostLeaf)
    return outStr

def generateNewickTests(numLeaves, destFolderName, sample=None, prob=1):
    '''
    Generate all possible trees with numLeaves number of leaves
    in newick format and save them in the designated folder.
    The names of the files are in the format 
    "test-size{numLeaves}-no{i}.newick" where i goes from 0 to
    the number of trees minus 1.

    #TODO: When we go over numLeaves == 6, there are too many possible
    trees to generate. To solve this, I decide to generate trees of
    greater size with randomness instead. However, the current way is
    not the clean way to do it. We should create a random tree generator
    function named "generateRandomNewickTests" and rename this function
    to "generateAllNewickTests" and remove the sample and prob parameter. 
    We all also need to create a new function "generateRandomTreeTuples" 
    in the process.

    :param numLeaves: The number of leaves in the generated trees
    :param destFolderName: The path to desination folder
    '''
    filenum = 0
    count = 0
    # assume that the foldername exist.
    for parasiteTree in generateTreeTuples(numLeaves, 'n', 0):
        for hostTree in generateTreeTuples(numLeaves, 'm', 0):
            parasiteLeaves = treeTupleLeaves(parasiteTree)
            hostLeaves = treeTupleLeaves(hostTree)
            count += 1
            print(count)
            if sample == None:
                mappings = generateAllMappings(parasiteLeaves, hostLeaves)
            else:
                mappings = generateMappingsViaSample(parasiteLeaves, hostLeaves, sample)
            for mappingPhi in mappings:
                if random.random() > prob:
                    continue
                # print it to a file instead of to screen
                filename = "test-size{}-no{}.newick".format(numLeaves, filenum)
                filepath = os.path.join(destFolderName, filename)
                with open(filepath, 'w') as f :
                    f.write(treeTupleStrings(hostTree) + ';\n')
                    f.write(treeTupleStrings(parasiteTree) + ';\n')
                    f.write(mappingToString(mappingPhi))
                filenum += 1
                
if __name__ == '__main__':
    '''
    Generate newick tree samples to test the histogram algorithm.
    The trees generated has 1-10 leaves.
    '''
    # Generate newick tree 
    for tree_size in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        targetFolder = './newickSample/size%d' % tree_size
        if not os.path.exists(targetFolder):
            os.makedirs(targetFolder)
            if tree_size < 7:
                generateNewickTests(tree_size, targetFolder)
            # When the tree size is 7 or greater, it is necessary for us
            # to select only a small subset of all possible newick trees
            # and mappings.
            elif tree_size == 7:
                generateNewickTests(tree_size, targetFolder, prob=0.001)
            elif tree_size == 8:
                generateNewickTests(tree_size, targetFolder, prob=0.00001)
            elif tree_size == 9:
                generateNewickTests(tree_size, targetFolder, prob=0.0000001)
            else:
                generateNewickTests(tree_size, targetFolder, prob=0.003, sample=1)