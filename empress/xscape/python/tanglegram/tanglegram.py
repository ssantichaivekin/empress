#! /usr/bin/python
"""
$Id: tanglegram.py,v 1.17 2008-11-25 09:04:12 wcchang Exp $
A tanglegram implementation.
Goals:  1) the naive O(n^2) [done - list works well]
        1.5) visualization using python-visual [works]
        2) improved O(nlg^2n) [done - skiplist]
        3) if possible, get the subset rank to work [...]

- ToDo: leaf mapping redesign to support many-many leaf mapping.
- ToDo: get the trees out of IP solutions instead of only the crossing value 

[20080523] 
        - AVL tree is available for improved runtime.
        
[20080717] 
        - ToTest: change corssing init case for one-many leaf mapping. 
        
[20081027] 
        - deepcopy: removing all deepcopy uses for performance.
        - XXX_MOD will modified the input.
        - to handle free-form leaf mapping (multi-multi),
          we extend leaf.ids to be a list of mapped ids
          otherwise, leaf.id is used for matching the target
        - WARNING: LCA mapping no longer applies when multi-multi is used.
          
[20081030]
        - implement O(kh) algorithm by adding new solver='kh'
[20081111]
        - need to isolate leaf mapping processing from tanglegram algorithms
          in order to get accurate runtime measurement
        - WARNING: don't use tree.leaves if the order is critical after layout changes.
          tree.leaves is static
[20081118]
        - use newick_leaf_map to handle the initinal mapping between two trees
"""

from avltree import *
from skiplist import *

import newick, LCA
import newick_utils

import sys, time

# for testing prupose
#INPUT_S = "input/BigNJinput.tre"       # ?? this species tree does not cover all taxa?!
                                        # it was fine. just use leaves_ids instead of leaves
#INPUT_S = "input/BigNJ.input.75620.newick"     
#INPUT_G = "input/BigNJ.gtree.few"

INPUT_S = "input/simpleS.tre"
INPUT_G = "input/simpleG.tre"


# available solvers: LIST, AVL, SL, GLPK, CPLEX, KH
# available optimization modes: NONE, MIN, MAX, MIN_MOD, MAX_MOD
#SOLVER = "LIST" 
#SOLVER = "AVL"


########################################################################
# various crossing subroutines to handle the actual crossing computation

#def crossKH(t, L0, L1):
#    """
#    to support the O(kh) algorithm
#    t is the threshold s.t. the right path are greater to
#    pre: multi label that got expanded has to be in sorted order
#    L0 used to find cross0
#    L1 used to find cross1
#    the simple one, but could be slower
#    """
#    chL = [[x for x in L0 if x <= t], [x for x in L1 if x <= t]]
#    chR = [[x for x in L0 if x >  t], [x for x in L1 if x >  t]]
#    preL, postL = 0, len(chL[0])
#
#    cross0, cross1 = 0, 0
#    for (x, y) in zip(L0, L1):
#        if x <= t:
#            # x is in chL, and x crosses process y in chR
#            # or x crosses unprocess y in chR in reversed order
#            postL-= 1
#        else:
#            # x is in chR, and x cross unprocess y in chL
#            cross0 += postL
#        # mirror case
#        if y <= t:
#            preL += 1
#        else:
#            cross1 += preL
#
#    return cross0, cross1, chL, chR

def crossKH(t, L):
    """
    L is a list of list
    """
    chL, chR = [], []
    cross0, cross1 = 0, 0
    #buckets = []

    for x in L:
        l, r = [], []
        for y in x:
            if y <= t:
                l.append(y)
            else:
                r.append(y)
        chL.append(l)
        chR.append(r)
        #chL.append([y for y in x if y <= t])
        #chR.append([y for y in x if y >  t])

        #buckets.append(len(l))
        #postL += len(l)
        #if len(l) > 0:
        #    chL.append(l)
        #if len(r) > 0:
        #    chR.append(r)

    buckets = map(len, chL)
    preL, postL = 0, sum(buckets)

    assert len(buckets) == len(L), (L, buckets)

    for x in L:
        postL -= buckets[0]
        for y in x:
            if y > t:
                cross0 += postL
                cross1 += preL
        preL += buckets[0]
        buckets.pop(0)

    return cross0, cross1, [e for e in chL if len(e) > 0], [e for e in chR if len(e) > 0]

def rankList(L, x):
    """
    Find the rank of x in L, i.e., 
    how many elements in L that's less than x
    notice: it's 0-based ranking
    """
    #return len([i for i in L if i < x])
    # wcc: can this really slow it down much?
    count = 0
    for y in L:
        if y < x: count += 1
    return count
    
def crossList(L1, L2):
    """
    Find the crossing number between L1, L2
    Notice that the order of L1, L2 matters
    """
    # then flaten/merge the list, again, binary only
    #node.ranks = [y for x in node.ranks for y in x]
    # wcc: just to make the List really bad looking
    ranks0 = [rankList(L2, x) for x in L1]
    ranks1 = [rankList(L1, x) for x in L2]
    #return sum([rankList(L2, x) for x in L1]), [y for x in [L1,L2] for y in x]
    return sum(ranks0), sum(ranks1), L1 + L2

def crossSL(S1, S2):
    """
    Find the crossing number between S1, S2, which are both SkipLists
    Node that one of the SkipList is mutated, and the other of S1, S2 matters.
    """
    # special case, need to call partialSum() to ensure less/greater
    if type(S1) != SkipList:
        S1 = SkipList(S1)
    if type(S2) != SkipList:
        S2 = SkipList(S2)

    ranks0, ranks1 = 0, 0
    # implicitly call partialSum() updates
    if len(S1) <= len(S2):
        for x in S1:
            ranks0 += S2.less(x)
            ranks1 += S2.greater(x)
            #print x, ranks0, ranks1
            
        #print S1, S2, len(S1), len(S2), ranks0, ranks1

        S2.extend(S1)   # has to call extend() due to parcial sum
        newList = S2

    else:
        for x in S2:
            ranks0 += S1.greater(x)
            ranks1 += S1.less(x)
        S1.extend(S2)
        newList = S1

    return ranks0, ranks1, newList


def crossAVL(T1, T2):
    """
    Find the crossing number between T1, T2, which are both AVLNode
    Note that one of the tree is mutated, and the order of T1, T2 matters.
    """
    # ugly! (in case the mapping is not onto)
    if T1 == [] or T2 == []:
        return 0, 0, (T1, T2)[len(T1) == 0]
    
    # AVLTree should be defuncted?
    if type(T1) != AVLNode and type(T1) != AVLTree:
        # we are just above leaf, T1 has to be [id]
        #if len(T1) != 1:
        #    print T1
        T = AVLNode(T1[0])
        for x in T1[1:]:
            T.insert(x)
        T1 = T
            
    if type(T2) != AVLNode and type(T2) != AVLTree:
        #assert len(T1) == 1
        #if len(T2) != 1:
        #    print T2
        T = AVLNode(T2[0])
        for x in T2[1:]:
            T.insert(x)
        T2 = T

    ranks0, ranks1 = 0, 0
    #ranks = []

    if len(T1) <= len(T2):
        for x in T1:
            ranks0 += T2.less(x)
            ranks1 += T2.greater(x)
            # need to -1 since rank is 1-based
            #ranks.append(T2.rank(x) - 1)
            #result += (T2.rank(x) - 1)
        for x in T1:
            T2.insert(x)
        newTree = T2

    else:
        # reversed case, T2 is smaller
        for x in T2:
            ranks0 += T1.greater(x)
            ranks1 += T1.less(x)
            # the reversed direction, we count how many elements in T1 > x
            #ranks.append(len(T1) - T1.rank(x, False))
            #result += (len(T1) - T1.rank(x, False))
        for x in T2:
            T1.insert(x)
        newTree = T1

    return ranks0, ranks1, newTree

###################################################################################
# end of crossing subroutines


class DFS_reset(newick.tree.TreeVisitor):
    """
    Restore the tree to it's original layout after tanglegram
    should be obseleted since we better only modify the tree when necessary
    """
    def __init__(self):
        pass

    def pre_visit_tree(self, node):
        if hasattr(node, "reversed") and node.reversed:
            #print "restoring..."
            node.edges.reverse()
            node.reversed = False
    def __call__(self, T):
        assert type(T) == newick.tree.Tree
        T.dfs_traverse(self)

def tanglegram1T(Tsrc, Ttrg, optimize="NONE", solver="LIST", verbose=False):
    """
    If optimize is XXX_MOD, then Ttrg is modified during the process.

    establish the leaf ranking in Tg according to Ts
    returns a linear ordering of leaves in the tree as a dictionary
    {id:[ranks]}, where ranks start from 1 (necessary?)

    NOTICE: this is not leaf mapping, but only ranks

    [20080716]
            - extended to handle alternating heuristic
    [20081027]
            - to handle freeform mapping, i.e., multi-multi
            - assume leafs are properly mapped through ids
              id = ['self id', 'projected id', ...]
    """

    class DFS_tanglegram(newick.tree.TreeVisitor):
        """
        Finding the crossing value in DFS and minimize it.
        """
        solvers = {"LIST":crossList, "AVL":crossAVL, "SL":crossSL, "KH":crossKH}

        def __init__(self, leafRank=None, verbose=False, optimize="MIN", solver="LIST"):

            #assert leafRank
            self.total_cross = 0
            self.leafRank = leafRank        # where leafRank is a dictionary
            self.verbose = verbose
            self.optimize = optimize
            # optimize = "NONE":    just count the crossing
            # optimize = "MIN":     minimize crossing, don't swap
            # optimize = "MIN_MOD": minimize crossing, swap
            # optimize = "MAX":     maximize crossing, don't swap
            # optimize = "MAX_MOD": maximize crossing, swap

            # why is it necessary to cast type(self) here? is it a design flaw of python?
            self.solver = type(self).solvers[solver]
    
        def __call__(self, T):
            assert type(T) == newick.tree.Tree, type(T)
            self.reset()
            T.dfs_traverse(self)
            return self.total_cross
    
        def reset(self, leafRank=None, verbose=None, optimize=None, solver=None):
            # caution: None is Flase
            self.total_cross = 0
            if leafRank != None: self.leafRank = leafRank
            if verbose != None:  self.verbose = verbose
            # since None == False, we force the default as False
            if optimize != None: self.optimize = optimize
            if solver != None:   self.solver = type(self).solvers[solver]
    
        def pre_visit_tree(self, node):
            # simply using a list as the query structure
            node.reversed = False
            if self.solver in [crossList, crossAVL, crossSL]:
                node.ranks = []
            elif self.solver in [crossKH]:
                # we already have ranks to process
                # assume binary tree
                node.cross0, node.cross1, node.edges[0][0].ranks, node.edges[1][0].ranks = \
                             self.solver(node.kh, node.ranks)
                if self.verbose:
                    print "(%d:%d) %d |" % (node.cross0, node.cross1, node.kh), node.ranks
    
        def post_visit_tree(self, node):
    
            #print node.ranks,
            # need to return both crossing values for optimization
            # due to multi-labels
    
            # binary only
            # the following crossing values are wrong!!! (due to multi labels)
            #node.max_cross = reduce(lambda x, y: len(x) * len(y), node.ranks)
    
            # find out the cross value, binary only
            if self.verbose:
                print node.ranks
    
            # calling specific solver to find the crossing values
            if self.solver in [crossList, crossAVL, crossSL]:
                node.cross0, node.cross1, node.ranks = self.solver(*node.ranks)
    
            #assert hasattr(node, "cross0"), \
            #       (self.solver, node, node.cross0, node.ranks)
            #assert hasattr(node, "cross1"), \
            #       (self.solver, node, node.cross1, node.ranks)
    
            # determine whether should we exchange the children
            if self.optimize == "NONE":
                # just count cross
                node.cross = node.cross0
    
            elif self.optimize == "MIN":
                # minimize, don't swap
                node.cross = min(node.cross0, node.cross1)
    
            elif self.optimize == "MAX":
                # maximize, don't sawp
                node.cross = max(node.cross0, node.cross1)
                
            elif self.optimize == "MIN_MOD":
                node.cross = min(node.cross0, node.cross1)
                if node.cross0 > node.cross1:
                    # wcc: TODO: for binary trees only..., and not a good practice
                    node.edges.reverse()
                    node.reversed = True
    
            elif self.optimize == "MAX_MOD":
                node.cross = max(node.cross0, node.cross1)
                if node.cross0 < node.cross1:
                    node.edges.reverse()
                    node.reversed = True
            # wcc: tanglegram should not change the layout. let drawing do that.
            else:
                ValueError, "invalid optimization mode"
    
    
            if self.verbose:
                print "%d (%d, %d)" % (node.cross, node.cross0, node.cross1), node.ranks
    
            self.total_cross += node.cross
            pass
    
        def post_visit_edge(self, src, bootstrap, length, dst):
            if self.solver in [crossList, crossAVL, crossSL]:
                src.ranks.append(dst.ranks)         # n-ary safe
            pass
    
        #def visit_leaf(self, leaf):
        #    if self.solver == "LIST":
        #        #leaf.ranks = [self.leafRank[x] for x in leaf.leaves_ids]
        #        # translating taxon to ranking
        #        leaf.ranks = [self.leafRank[leaf.leaves_ids[0]]]
        #    elif self.solver == "AVL":
	    #        leaf.ranks = AVLNode(self.leafRank[leaf.leaves_ids[0]])

    ##class DFS_leafRanks(newick.tree.TreeVisitor):
    ##    """
    ##    returns a linear ordering of leaves in the tree as a dictionary
    ##    {id:[ranks]}, where ranks start from 1 (necessary?)
    ##
    ##    NOTICE: use [ranks] to support one-many mapping
    ##    NOTICE: this is a two-pass visitor
    ##
    ##    ToDo: verify that ranks start from 0 won't cause a problem (LIST, SL, AVLTREE)
    ##
    ##    [20081027] 
    ##            - extend getRanks to handle multi-multi free form mapping
    ##            the idea based on the leaf ids from the other tree being projected to this tree.
    ##    """
    ##    def __init__(self):
    ##        self.rtnLeafRank = {}       # use to determine the ranks of leaves, 1st pass
    ##        self.gvnLeafRank = None     # use to set the ranks of leaves, 2nd pass
    ##        self.rank = 0
    ##
    ##    def visit_leaf(self, leaf):
    ##        self.rank += 1
    ##        # wcc: leaf.ids are added to accomedate multi-multi labeling
    ##        # they are part of the trees during input parsing or generating process
    ##        if self.gvnLeafRank == None:
    ##            # we are in the first pass, simply map the current 'id' to its rank
    ##            self.rtnLeafRank.setdefault(leaf.id, [])
    ##            # we are sure that the ranks are in increasing order for the particular id
    ##            self.rtnLeafRank[leaf.id].append(self.rank)
    ##            leaf.rank = self.rank
    ##        else:
    ##            # 2nd pass, we are setting the ranks
    ##            ids = leaf.ids if hasattr(leaf, "ids") else leaf.leaves_ids
    ##            leaf.ranks = []
    ##            #[leaf.ranks.extend(self.gvnLeafRank[id]) for id in ids if self.gvnLeafRank.has_key(id)]
    ##            [leaf.ranks.append(n.rank) for n in leaf.interleaf]
    ##            self.rtnLeafRank.append(leaf.ranks)
    ##            #leaf.ranks.sort()
    ##            # wcc: should we keep the sorting here? no we don't..
    ##    def post_visit_edge(self, node, bs, lth, ch):
    ##        # wcc: pick the rank of left child as the threshold for NH algorithm
    ##        # only works for binary trees
    ##        if ch == node.edges[0][0]:
    ##            # we had finished processing the first child
    ##            node.kh = self.rank
    ##
    ##    def __call__(self, T, leafRank=None):
    ##        assert type(T) == newick.tree.Tree
    ##        self.__init__()             # technically, only need to set self.rank = 0
    ##        self.gvnLeafRank = leafRank
    ##        self.rtnLeafRank = [] if self.gvnLeafRank else {}
    ##        T.dfs_traverse(self)
    ##        return self.rtnLeafRank

    class DFS_LeafRanksPass1(newick.tree.TreeVisitor):
        """
        [20081118]
                - revised version to simplify the process
                - assign a linear ranks to leafs in DFS
        """
        def __init__(self):
            self.rank = 0

        def visit_leaf(self, leaf):
            self.rank += 1
            leaf.rank = self.rank
            #if verbose: print leaf, leaf.rank

        def post_visit_edge(self, node, bs, lth, ch):
            # wcc: only works for binary trees
            # for KH only.
            # since we don't know if we will be running KH algorithm any time soon
            if ch == node.edges[0][0]:
                node.kh = self.rank

        def __call__(self, T):
            assert type(T) == newick.tree.Tree, (type(T), newick.tree.Tree)
            self.__init__()
            T.dfs_traverse(self)
            
    class DFS_LeafRanksPass2(newick.tree.TreeVisitor):
        """
        [20081118]
                - 2nd pass of leaf ranks assignment
        """
        def __init__(self):
            # the sequential ranks collected from leaves
            self.leafRanks = []
            
        def visit_leaf(self, leaf):
            assert hasattr(leaf, "interleaf"), leaf
            leaf.ranks = []
            [leaf.ranks.append(n.rank) for n in leaf.interleaf]
            self.leafRanks.append(leaf.ranks)
            #if verbose: print leaf, leaf.interleaf, leaf.ranks

        def __call__(self, T):
            assert type(T) == newick.tree.Tree, type(T)
            self.__init__()
            T.dfs_traverse(self)
            return self.leafRanks

    if verbose: 
        print "Source:", Tsrc
        print "Target:", Ttrg
    
    # need to rebuild every time
    #dfsLeafRanks = DFS_leafRanks()

    if solver == "KH":
        DFS_LeafRanksPass1()(Ttrg)
        Ttrg.ranks = DFS_LeafRanksPass2()(Tsrc)
        # wcc: testing single pass version
        # don't use tree.leaves if the order matters!
        # this is wrong:
        #Ttrg.ranks = [x.ranks for x in Tsrc.leaves]
        
        if verbose: print Ttrg.ranks
    else:
        DFS_LeafRanksPass1()(Tsrc)
        DFS_LeafRanksPass2()(Ttrg)
        #ranks = dfsLeafRanks(Tsrc)
        #dummy = dfsLeafRanks(Ttrg, ranks)


    dfsTanglegram = DFS_tanglegram(optimize=optimize, solver=solver, verbose=verbose)

    if verbose: print "opt: %s, solver: %s" % (dfsTanglegram.optimize, dfsTanglegram.solver)

    crossing = dfsTanglegram(Ttrg)

    # optimize "NONE":    plain crossing
    # optimize "MIN":     optimized crossing, Tg is unchanged
    # optimize "MIN_MOD": optimized crossing, Tg is changed

    #dfsReset = DFS_reset()
    #dfsReset(Tg)
    #dfsReset(Tg)
    return (crossing, Tsrc, Ttrg, None)

def tanglegram2TE(tSrc, tTrg, optimize="NONE", solver="LIST", verbose=False):
    """
    naive 2T exact solution. trying to iterate through all possible tSrc sibling switching
    """
    assert solver in ("LIST", "AVL", "SL")
    
    cStar = (0 if optimize[:3] == "MAX" else sys.maxint)

    nCommit = {}
    nElapse = []

    if verbose: print optimize
    
    # NOTE: after full iteration, Tsrc is back to its original
    for (T, n) in newick_utils.internal_permute(tSrc):
        # keep a track of uncommitted nodes
        nElapse.append(n)
        (c1, tSrc, tTrg, dummy) = tanglegram1T(tSrc, tTrg, optimize=optimize, solver=solver, verbose=verbose)
        if (optimize[:3] == "MIN" and cStar > c1) or (optimize[:3] == "MAX" and cStar < c1):
            # once a better solution is found, fill up the gap from last check point to current
            cStar = c1
            
            if optimize[-3:] == "MOD":
                # need to update nCommit with nElapse
                for n in nElapse:
                     nCommit.setdefault(n, False)      # since we immediately flip the bit, the default is False
                     nCommit[n] = not nCommit[n]
                nElapse = []    # don't forget to reset

    if optimize[-3:] == "MOD":
        # update the solution to be the optimal one with the nodes that's been flipped
        for (n, b) in nCommit.iteritems():
            if b: n.edges.reverse()
        # since tTrg might be changed while not reaching optimal
        (cStar, tSrc, tTrg, dummy) = tanglegram1T(tSrc, tTrg, optimize=optimize, solver=solver, verbose=verbose)
    
    return (cStar, tSrc, tTrg, None)

def tanglegram2TIP(tSrc, tTrg, optimize = "NONE", solver = "GLPK", verbose = False):
    """
    solving the exact solution using glpk or cplex
    by converting the problem into an integer programming instance.
    only minization is possible for now.

    1) build LCA for both trees
    2) build link crossing constraints/variables
    3) call glpk solver
    4) return the results

    """
    ## don't need to do a thing here if no optimization is used
    #if optimize == "NONE":
    #    return tanglegram1T(tSrc, tTrg, optimize = optimize, solver = solver, verbose = verbose)

    # just a formality
    solvers = {"GLPK": crossGLPK, "CPLEX": crossCPLEX}
    assert type(tSrc) == type(tTrg) == newick.tree.Tree, (type(tSrc), type(tTrg))
    assert solver in solvers.keys()

    class DFS_LCA(newick.tree.TreeVisitor):
        """
        visit the tree, label nid (DFS order), and compute LCA
        as well as using nid, a DFS preorder id, as the leafToRank 
        (taken from getRanks/setRanks in build_leaf_ranks)
        """
        def __init__(self):
            self.pa = {}        # the child-parent relation
            self.count = 0
            self.nodes = []
            self.getLeafRanks = {}      # to store leaf ranks of current tree
            self.setLeafRanks = None    # to set leaf ranks w.r.t. to the other tree

        def pre_visit_tree(self, node):
            node.nid = self.count
            self.count += 1
            self.nodes.append(node)

        def visit_leaf(self, leaf):
            # need to process the leaf node like a tree node
            # this is missing from the original tree_visitor
            self.pre_visit_tree(leaf)
            # taken from build_leaf_rank().DFS_getRanks(), but different in handling the 2nd pass
            # always collect current rank
            self.getLeafRanks.setdefault(leaf.id, [])
            self.getLeafRanks[leaf.id].append(leaf.nid)

            if self.setLeafRanks != None:
                # 2nd pass
                ids = leaf.ids if hasattr(leaf, "ids") else leaf.leaves_ids
                # modified to handle multi-multi case
                # still keep the leafRanks for target tree, since we need all leaf nid(s)
                # check if we should assign ranks attributes
                leaf.ranks = []
                [leaf.ranks.extend(self.setLeafRanks[id]) for id in ids if self.setLeafRanks.has_key(id)]
            
        def post_visit_edge(self, src, bt, ln, dst):
            self.pa[dst.nid] = src.nid

        # mixing getRanks and setRanks into one visitor obj, use leafRanks to set them apart
        def __call__(self, T, leafRanks = None):
            self.__init__()
            # to indicate whether we are in the 2nd pass
            self.setLeafRanks = leafRanks
            T.dfs_traverse(self)
            lca = LCA.LCA(self.pa)
            return (lca, self.nodes, self.getLeafRanks)

    dfsLCA = DFS_LCA()
    lcaS, nodesS, lfRanksS = dfsLCA(tSrc)
    lcaT, nodesT, lfRanksT = dfsLCA(tTrg, lfRanksS)

    # mid step verification, just to make sure things are on track
    if verbose:
        print "-- In tanglegram.tanglegram2TEG()"
        #print lcaS, nodesS
        #print lcaT, nodesT
        N = len(nodesS)
        print "tSrc w/ nid:"
        print newick_utils.plot_ascii_tree(tSrc, attr="nid")
        print "tTrg w/ ranks:"
        print newick_utils.plot_ascii_tree(tTrg, attr="ranks")
        print lfRanksS #
        print lfRanksT # not {} anymore; we use this for retrieving leafs
        #print lfRanksT.values()
        #for i in xrange(N):
        #    for j in xrange(i+1, N):
        #        print "%d, %d => %d" % (i, j, lcaS(i,j))
        print "tSrc w/ ids:"
        print newick_utils.plot_ascii_tree(tSrc, attr="ids")
        print "tTrg w/ ids:"
        print newick_utils.plot_ascii_tree(tTrg, attr="ids")

    # we should have everything to convert the instance to IP now
    leafT = []
    for R in lfRanksT.values(): leafT.extend(R)

    # iterate through all pairs of links
    iNodeX, iNodeU = {}, {}
    # X: crossed; U: non-crossed
    # can we do better w/o these nested for-loops?
    for i in leafT:
        for j in leafT:
            # only work on (idx(i) > idx(j))
            if i == j: break;
            for x in nodesT[i].ranks:
                for y in nodesT[j].ranks:
                    #(x, i) vs (y, j)
                    # only verify < 0 or > 0; ignore = 0 as the two links never cross
                    if verbose: print "(%d, %d)-(%d, %d)" % (x, i, y, j)
                    cCurr = (x-y) * (i-j)
                    if cCurr < 0:
                        iNodeToAdd = iNodeX 
                    elif cCurr > 0:
                        iNodeToAdd = iNodeU
                    else:
                        #  cCurr == 0, no difference in either case
                        continue
                    edgePair = (lcaS(x,y), lcaT(i,j))
                    iNodeToAdd.setdefault(edgePair, 0)
                    iNodeToAdd[edgePair] += 1

    # again, testing only
    if verbose: print "crossing:", sum(iNodeX.values())

    # to be self-sufficient
    if optimize == "NONE":
        return (sum(iNodeX.values()), tSrc, tTrg, None)
    else:
        (optCross, switchS, switchT) = solvers[solver](iNodeX, iNodeU, optimize = optimize, verbose = verbose)
                            

    # TODO: take care of MOD cases
    if optimize[-3:] == "MOD":
        pass

    return (optCross, None, None, None)

def crossCPLEX(X, U, optimize = "MIN", verbose = False):
    """
    CAUTION: 
    1) the QP objective function in CPLEX does not take constant term (an offset)
    2) the form [x*y + ... ] / 2 is mandatory for quadratic terms?!
    3) QP obj func can't have repeated terms. need to pre-process and merge them as coefficients  

    using CPLEX to solve the exact two tree corssing min in QP (quadratic objective)
    1) generate a LP file (cplex format) with offset objective
    2) ... (not sure if there will be a second step for now)  
    """
    assert optimize[:3] in ("MIN", "MAX"), optimize
    
    if verbose:
        print "Crossing:", len(X), X
        print "Non-Crossing:", len(U), U
        
    from tempfile import NamedTemporaryFile
    import string               # string.join
    from os import system       # the ugly...
    from os.path import basename

    # vars for the formulation
    varX = set()
    varY = set()
    objs = []
    offset = sum(X.values())
    
    # crossing terms: -x -y + [ 4 x * y ] / 2; offset ++
    for ((x, y), w) in X.iteritems():
        objs.append("- %d x%d - %d y%d + [ %d x%d * y%d ] / 2" % (w, x, w, y, 4*w, x, y))
        varX.add("x%d" % x)
        varY.add("y%d" % y)
        
    # non-crossing terms: x + y - [ 4 x * y ] / 2
    for ((x, y), w) in U.iteritems():
        objs.append("+ %d x%d + %d y%d - [ %d x%d * y%d ] / 2" % (w, x, w, y, 4*w, x, y))
        varX.add("x%d" % x)
        varY.add("y%d" % y)

    # 'r+' for both reading and writing
    # FIXME: NamedTemporaryFile.name not usable in Windows
    lpFile = NamedTemporaryFile(mode = 'r+', suffix = ".lp")

    lpFile.write("\* Problem: tanglegrams *\ \n") 
    lpFile.write("\* offset the objective by: %d *\ \n" % offset)
    lpFile.write("\* objective *\ \n")
    lpFile.write("%s\n" % ("Minimize" if optimize[:3] == "MIN" else "Maximize"))
    lpFile.write(" Crossing:\n %s\n\n" % string.join(objs, " \n "))
    lpFile.write("\* vars - hey, Mom, no constraints! *\ \nBinary")
    lpFile.write("\n %s\n" % string.join(varX, "\n "))
    lpFile.write(" %s\n" % string.join(varY, "\n "))
    lpFile.write("\nEnd\n")
    
    lpFile.seek(0) # necessary for even only reading the file
    if verbose: 
        print "name:", lpFile.name
        print lpFile.read()
    # the file should be self-destructive upon close
    #print lpFile.read()

    # the ugly 
    runFile = NamedTemporaryFile(mode = 'r+', suffix = ".runme")
    #runFile.write("help\n")
    runFile.write("read /home/wcchang/prog/cplex/%s\n" % basename(lpFile.name))
    runFile.write("display problem all\n")
    runFile.write("optimize\n")
    runFile.write("write /home/wcchang/prog/cplex/%s.sol sol\n" % basename(lpFile.name))
    runFile.write("quit\n")
    runFile.seek(0)
    
    system("scp %s pluto:~/prog/cplex/%s" % (lpFile.name, basename(lpFile.name)))
    #system("scp %s pluto:~/prog/cplex/%s" % (runFile.name, basename(runFile.name)))
    system("ssh pluto cplex101 < %s" % runFile.name)
    system("scp pluto:~/prog/cplex/%s.sol /tmp" % basename(lpFile.name))
    
    import xml.dom.minidom as minidom
    sol = minidom.parse("/tmp/%s.sol" % basename(lpFile.name))
    u0 = sol.getElementsByTagName("header")[0].getAttribute("objectiveValue")
    c0 = round(float(u0))
    crossing = offset + int(c0)
    if verbose: print "offset", offset, u0, c0, int(c0)
    
    runFile.close()
    lpFile.close()

    return (crossing, None, None)


def crossGLPK(X, U, optimize = "MIN", verbose = False):
    """
    based on the given conditions, 
    1) generate a MathProg file
    2) solve it
    3) parse result
    """
    assert optimize[:3] in ("MIN", "MAX"), optimize

    if verbose: 
        print "Crossing:", sum(X.values()), X
        print "Non-Crossing:", sum(U.values()), U

    from tempfile import NamedTemporaryFile
    import glpk # based on python-glpk example.py
    import string

    # vars are unique, but the objective function is not
    varS = {}
    varT = {}
    varX = {}
    varU = {}
    stX = {}
    stU = {}
    objs = []
    # s: node in src
    # t: node in trg
    # x: crossing variable s*t
    # u: non-crossing variable s*t 
    for ((s, t), w) in X.iteritems():
        objs.append("(1 - s_%d - t_%d + 2 * x_%d_%d) * %d" % (s, t, s, t, w))
        varS["var s_%d binary >= 0;" % s] = ''
        varT["var t_%d binary >= 0;" % t] = ''
        varX["var x_%d_%d binary >= 0;" % (s, t)] = ''
        if optimize[:3] == "MIN":
            stX["s.t. c_x_%d_%d: x_%d_%d >=  s_%d + t_%d  - 1;" % (s, t, s, t, s, t)] = ''
        elif optimize[:3] == "MAX":
            stX["s.t. c_x_%d_%d: x_%d_%d <= (s_%d + t_%d) / 2;" % (s, t, s, t, s, t)] = ''
        
    for ((s, t), w) in U.iteritems():
        objs.append("(    s_%d + t_%d - 2 * u_%d_%d) * %d" % (s, t, s, t, w))
        varS["var s_%d binary >= 0;" % s] = ''
        varT["var t_%d binary >= 0;" % t] = ''
        varU["var u_%d_%d binary >= 0;" % (s, t)] = ''
        if optimize[:3] == "MIN":
            stU["s.t. c_u_%d_%d: u_%d_%d <= (s_%d + t_%d) / 2;" % (s, t, s, t, s, t)] = ''
        elif optimize[:3] == "MAX":
            stU["s.t. c_u_%d_%d: u_%d_%d >=  s_%d + t_%d  - 1;" % (s, t, s, t, s, t)] = ''

    #print "objs:\n\t", string.join(objs, " +\n\t")
    #print "vars:", string.join(varS.keys()+varT.keys()+varX.keys()+varU.keys(), ", ")
    #rint "s.t.:\n", string.join(stX.keys()+stU.keys(), "\n")
    
    # 'r+' for both reading and writing
    # FIXME: NamedTemporaryFile.name not usable in Windows
    modFile = NamedTemporaryFile(mode = 'r+', suffix = ".mod")

    modFile.write("/* vars */\n%s\n\n" % string.join(varS.keys()+varT.keys()+varX.keys()+varU.keys(), "\n"))
    modFile.write("/* objective */\n")
    modFile.write("%s optCross:\n\t%s;\n\n" % ("minimize" if optimize[:3] == "MIN" else "maximize", string.join(objs, " +\n\t")))
    modFile.write("/* subject to */\n%s\n\n" % string.join(stX.keys()+stU.keys(), "\n"))

    modFile.write("end;\n")
    
    modFile.seek(0) # necessary for even only reading the file
    if verbose: 
        print "name:", modFile.name
        print modFile.read()
    # the file should be self-destructive upon close
    glpkSol = glpk.lpx(modFile.name)
    modFile.close()

    glpkSol.solve()
    if verbose: print glpkSol.sol
    
    # TODO: if optimize[-3:] == "MOD": ...

    return int(glpkSol.sol['optCross']), None, None
     
def tanglegram2TH(tSrc, tTrg, optimize = "NONE", solver = "LIST", verbose = False):
    """
    It only makes sense if tSrc is modified, i.e., optimize=XXX_MOD. 
    Otherwise, it always stops after 2 iterations. 
    
    [20081026]
        - wcc: deepcopy is too expensive... need to avoid using it unless necessary
    """

    cBest = (0 if optimize[:3] == "MAX" else sys.maxint)
    cCurr = (0 if optimize[:3] == "MAX" else sys.maxint)
    nBest = None

    if verbose: print optimize
    
    iIter = 0
    while True:
        iIter += 1
        # find the best solution in this iteration
        for (T, n) in newick_utils.one_internal_switch(tSrc):
            (c1, tSrc, tTrg, dummy) = tanglegram1T(T, tTrg, optimize = optimize, solver = solver, verbose = verbose)
            if (optimize[:3] == "MIN" and cCurr > c1) or (optimize[:3] == "MAX" and cCurr < c1):
                cCurr = c1
                nBest = n
                if verbose: print cCurr, nBest, tTrg

        # see if we have a better solution than the last iteration
        if (optimize[:3] == "MIN" and cBest > cCurr) or (optimize[:3] == "MAX" and cBest < cCurr):
            cBest = cCurr
            if optimize[-3:] == "MOD": nBest.edges.reverse()
            if verbose: print cBest

        else:
            # don't forget to stop the iteration
            break

    if verbose: print "iterations:", iIter
    return (cBest, tSrc, tTrg, iIter)

def tanglegram2TA(tSrc, tTrg, optimize = "NONE", solver = "LIST", verbose = False):
    """ 
    alternating heuristic:
        repeat until no improvement
            1T(src, trg)
            1T(trg, src)

    [20081027] since no changes are made to the inputs in case of "MIN", "MAX" and "NONE", 
            it will not loop more than once in these 3 cases. 
    """

    cCurr = (0 if optimize[:3] == "MAX" else sys.maxint)
    tSrcA = tSrc
    tTrgA = tTrg

    if verbose: print optimize

    iIter = 0
    while True:
        iIter += 1
        (c1, tSrcA, tTrgA, dummy) = tanglegram1T(tSrcA, tTrgA, optimize = optimize, solver = solver, verbose = verbose)
        (c2, tTrgA, tSrcA, dummy) = tanglegram1T(tTrgA, tSrcA, optimize = optimize, solver = solver, verbose = verbose)

        if (optimize[:3] == "MIN" and cCurr > c1) or (optimize[:3] == "MAX" and cCurr < c1):
            cCurr = c1

        else:
            # don't forget to stop the iteration when nothing to improve
            break

    return (cCurr, tSrcA, tTrgA, iIter)

def tanglegram2TAH(tSrc, tTrg, optimize = "None", solver = "LIST", verbose = False):
    """
    alternating local search heuristic
    """
    cCurr = (0 if optimize[:3] == "MAX" else sys.maxint)
    tSrcA = tSrc
    tTrgA = tTrg

    if verbose: print optimize

    iIter = 0
    while True:
        iIter += 1
        (c1, tSrcA, tTrgA, dummy) = tanglegram2TH(tSrcA, tTrgA, optimize = optimize, solver = solver, verbose = verbose)
        (c2, tTrgA, tSrcA, dummy) = tanglegram2TH(tTrgA, tSrcA, optimize = optimize, solver = solver, verbose = verbose)

        if (optimize[:3] == "MIN" and cCurr > c1) or (optimize[:3] == "MAX" and cCurr < c1):
            cCurr = c1

        else:
            # don't forget to stop the iteration
            break

    return (cCurr, tSrcA, tTrgA, iIter)
