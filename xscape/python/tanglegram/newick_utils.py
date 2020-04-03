#!/usr/bin/python
"""# -*- coding: utf-8 -*-"""
"""
$Id: newick_utils.py,v 1.9 2008-11-25 09:04:12 wcchang Exp $
generate random trees using the newick module
"""
"""
class DFS_visitor(newick.tree.TreeVisitor):
    def __init__(self):
        pass
    def pre_visit_tree(self, node):
        pass
    def pre_visit_edge(self, prnt, bs, lth, chld):
        pass
    def post_visit_edge(self, prnt, bs, lth, chld):
        pass
    def post_visit_tree(self, node):
        pass
    def visit_leaf(self, lf):
        pass
"""    



import newick.tree
import random

def newick_random(L, balanced=False, shuffle=False):
    """
    randomly generate a tree based on L as leaf set
    """
    assert len(L) > 1

    nodes = [newick.tree.Leaf(str(x)) for x in L]
    # any reason we should not shuffle here?
    # let the user decide?
    if shuffle: random.shuffle(nodes)

    # recursive approach, size balanced
    def newick_rec(L, balanced=False):
        """
        return a newick tree of leaf set L, recursively
        """
        n = len(L)

        if n == 1:
            return L[0]

        if balanced:
            p = int(n/2)
        else:
            p = random.randint(1, n-1)
        
        n1, n2 = newick_rec(L[:p], balanced), newick_rec(L[p:], balanced)
        t = newick.tree.Tree()
        # edge = (child, bootstrap, length)
        t.add_edge((n1, None, None))
        t.add_edge((n2, None, None))
        return t

    #print nodes
    T = newick_rec(nodes, balanced)

    newick.tree.add_parent_links(T)
    newick.tree.add_distance_from_root(T)
    return T
                           

    # iterative approach, only depth balanced
    #while len(nodes) > 1:
    #    if not balanced:
    #        random.shuffle(nodes)
    #    # height balanced, not size balanced
    #    # fully balanced unless 2^x
    #    # it's balanced in the sense that any leaf is at most deeper than another by 1
    #    n1, n2 = nodes.pop(0), nodes.pop(0)
    #
    #    t = newick.tree.Tree()
    #    t.add_edge([n1, 0, 0])
    #    t.add_edge([n2, 0, 0])
    #    nodes.append(t)

    # a little house-keeping
    #newick.tree.add_parent_links(nodes[0])
    #newick.tree.add_distance_from_root(nodes[0])

    #return nodes[0]

def newick_multi_multi(N, M, P1, balanced=False, verbose=False):
    """
    generate a pair of trees that supports multi-multi leaf mapping
    if P1 = 0, then this is one-multi
    """
    
    # w.l.o.g., we simply assume M >= N
    if M < N: M = N
    EXTRA = int(N*P1)

    # generate the list of taxa of size N
    L = ['t%d' % x for x in xrange(N)]
    #random.shuffle(L)
    S = newick_random(L, shuffle=True, balanced=balanced)
    
    # generate the other set
    if EXTRA > 0: 
        # multi-multi, need (x, y) to define matchings
        L2 = L + ['t%d' % x for x in xrange(N, M)]
    else:
        # multi-one is sufficient, i.e, mathcing ids (x, x)
        L2 = L + [random.choice(L) for x in xrange(N, M)]
    #random.shuffle(L2)
    G = newick_random(L2, shuffle=True, balanced=balanced)
    
    if verbose:
        print N, M
        print L 
        print L2
        print S
        print G
        
    I = None    # in case I is None, the mapping is determined by id

    if EXTRA > 0:
        # generating the leaf mapping:
        # 1) random permute
        # 2) extend side N
        # 3) choose extra ones for P1 pairs
        random.shuffle(L)
        random.shuffle(L2)
        
        L1 = L + [random.choice(L) for x in xrange(N, M)]
            
        # 
        for i in xrange(EXTRA):
            L1.append(random.choice(L1[:N]))
            L2.append(random.choice(L2[:M]))

        I = zip(L1, L2)
                
        if verbose:
            print N, M, EXTRA+M
            print L1
            print L2
        

    # don't forget to establish the mapping
    newick_leaf_map(S, G, I)
        
    if verbose:
        print S
        print plot_ascii_tree(S, attr="interleaf")
        for s in S.leaves:
            print s.id, s.interleaf
        print G
        print plot_ascii_tree(G, attr="interleaf")
        for g in G.leaves:
            print g.id, g.interleaf
        if I:
            for i in I:
                print i

    return (S, G, I)

def newick_leaf_map(S, T, I=None):
    """
    establish the mapping of leaf nodes between S and T (both way).
    if I is None, then matching 'id' of nodes are linked.
    otherwise, I = [(x1, y1), (x2, y2)...],
    where xi are ids in S and yi are ids in T,
    is used to link them.
    Note that if S or T are str, then it is parsed into newick.tree.Tree.
    """
    if type(S) == str:
        S = newick.tree.parse_tree(S)
    if type(T) == str:
        T = newick.tree.parse_tree(T)
        
    assert type(S) == type(T) == newick.tree.Tree, (type(S), type(T))

    def ID2Nodes(tree):
        """
        return a dict that maps node.id to node
        since we need node.id, it only applys to the leaf nodes for now
        """
        ID2NDs = {}
        nodes = tree.leaves
        for n in nodes:
            # normally, single id maps to a single node
            # but in case of generalized version, we might consider repeated ids
            ID2NDs.setdefault(n.id, [])
            ID2NDs[n.id].append(n)
        return ID2NDs

    [setattr(n, "interleaf", []) for n in S.leaves]
    [setattr(n, "interleaf", []) for n in T.leaves]

    id2nodesS = ID2Nodes(S)
    id2nodesT = ID2Nodes(T)

    if type(I) == list and len(I) > 0:
        # now we apply the inter-leaf edges, in case of multi-multi
        for (x, y) in I:
            [t.interleaf.extend(id2nodesS[x]) for t in id2nodesT[y]]
            [s.interleaf.extend(id2nodesT[y]) for s in id2nodesS[x]]
    else:
        # map the leafs based on their id
        # use dict.get since the id might not exist in the other tree
        [t.interleaf.extend(id2nodesS.get(t.id, [])) for t in T.leaves]
        [s.interleaf.extend(id2nodesT.get(s.id, [])) for s in S.leaves]

    return S, T

class DFS_nodes(newick.tree.TreeVisitor):
    """
    traverse the tree and return internal nodes and leaves in lists
    """
    def __init__(self):
        self.nodes = []
        self.leaves = []

    def pre_visit_tree(self, t):
        self.nodes.append(t)

    #def visit_leaf(self, l):
    #    #print l.leaves_ids
    #    #yield l.leaves_ids
    #    #self.leaves.append(l)
    #    pass

    def __call__(self, T):
        self.__init__()
        T.dfs_traverse(self)
        #return (self.nodes, self.leaves)
        return self.nodes



def random_internal_switch(T):
    """
    randomly swapping the children of internal nodes 
    """
    assert type(T) == newick.tree.Tree, (T, type(T))
    nodes = DFS_nodes()(T)
    
    for n in nodes:
        if random.random() > 0.5: n.edges.reverse() 


def internal_permute(T):
    """
    a simple generator that permutes all possible layouts of the input tree
    currently, no new tree is generated. hence be careful on shared tree

    using gray code to simply the permutations such that only one
    node changes at a time.
    """
    assert type(T) == newick.tree.Tree, (T, type(T))

    nodes = DFS_nodes()(T)
    
    n = len(nodes)

    for i in gray_bit_gen(n):
        nodes[i].edges.reverse()
        yield (T, nodes[i])

def gray_bit_gen(N):
    """
    generates the bits that changes in gray code of N-bits (0 ~ 2**N - 1)
    Gray(i) = i ^ (i/2)
    """
    import math
    def gray(i):
        """
        return the i-th Gray code
        ref: numerical recipe
        """
        return i^(i>>1)
    
    limit = 2**N
    for x in xrange(limit):
        b = gray(x)^gray((x+1) % limit)
        yield int(math.log(b)/math.log(2))

def bin_bit_gen(N):
    """
    generates bits in N that's a 1
    """
    import math
    if N <= 0:
        #yield 0
        return
    n = int(math.floor(math.log(N)/math.log(2))) + 1
    #print n, N
    for i in xrange(n):
        if (1 << i) & N > 0:
            yield i

def simple_gen(N=10):
    for x in xrange(N):
        yield random.random()

def one_internal_switch(T):
    """
    a generator that returns all trees by switching exactly 1 internal node
    after each yield, the nodes are switched back.
    """
    assert type(T) == newick.tree.Tree

    nodes = DFS_nodes()(T)

    for n in nodes:
        n.edges.reverse()
        yield (T, n)
        # switch them back
        n.edges.reverse()

def quick_leaves(T):
    return str(T).replace('(','').replace(')','').replace("'",'').replace(" ",'').split(',')


def plot_ascii_tree(T, indent = 4, attr = "id", verbose = False):
    """
    print the tree in leveled format (in ascii) for comparison
    and make it looks pretty by using extended ascii codes 
    (in unicode, ref: 
    http://ascii-table.com/ascii-extended-pc-list.php
    http://www.reportlab.com/i18n/python_unicode_tutorial.html)
    """
    class DFS_ascii_tree(newick.tree.TreeVisitor):
        def __init__(self, indent = 4):
            self.indent = indent
            self.attr = "id"
            self.indent_str = ""
            self.output_str = ""

        def pre_visit_tree(self, node):
            self.output_str += "%s|%s\n" % \
            (str(node.leaves_ids), str(getattr(node, self.attr) if hasattr(node, self.attr) else "N/A"))

        def pre_visit_edge(self, src, bootstrap, length, dst):
            # length = 0 is not allowed
            if verbose:
                print src, bootstrap, length, dst
            extraIndent = self.indent * (int(length) if length else 1)
            isLast = (dst is src.edges[-1][0])
            #self.output_str += self.indent_str + (u"\u2514" if isLast else u"\u251c") + u"\u2500" * (extraIndent - 1)
            #self.indent_str += (" " if isLast else u"\u2502") + " " * (extraIndent - 1)
            # well, in case uft-8 is not supported...
            self.output_str += self.indent_str + ('`' if isLast else '+') + '-' * (extraIndent -1 )
            self.indent_str += (' ' if isLast else '|') + ' ' * (extraIndent - 1)

        def post_visit_edge(self, src, bootstrap, length, dst):
            extraIndent = self.indent * (int(length) if length else 1)
            self.indent_str = self.indent_str[:-extraIndent]
        
        def visit_leaf(self, leaf):
            self.output_str += "%s|%s\n" % \
            (str(leaf.leaves_ids), str(getattr(leaf, self.attr) if hasattr(leaf, self.attr) else "N/A"))

        def __call__(self, T, indent = 4, attr = "id", verbose = False):
            self.__init__(indent)
            self.verbose = verbose
            self.attr = attr if attr != None else "id"
            T.dfs_traverse(self)
            return self.output_str
        
    assert type(T) == newick.tree.Tree or newick.tree.Leaf, type(T)
    return DFS_ascii_tree()(T, indent = indent, attr = attr, verbose = verbose)
    
def dup_loss_sim(T, la, mu, verbose = False):
    """
    a simplified probabilistic model based on
    Arvestad et al which uses birth-death processes
    to simulate duplication and loss events.
    la(mbda): birth/dup rate  
    mu: death/loss rate
    
    NOTICE: only single layer of dup/loss so far
    """
    from copy import copy   # only use the shallow copy
    
    class DFS_dup_loss(newick.tree.TreeVisitor):

        def __init__(self, verbose = False):
            self.verbose = verbose
            
        def pre_visit_tree(self, node):
            pops = []
            
            for n in self.stackNodes[-1]:
                c = newick.tree.Tree()
                c.id = node.id
                if verbose: c._leaves_cache = node._leaves_cache
                pops.append(c)

            # channels before dup/loss
            self.stackNodes.append(copy(pops))

            # dup/loss operations
            for n in reversed(pops):
                r = random.random()

                if r < self.la: # dup
                    if self.verbose: print "dup(n):", n.leaves
                    n1 = newick.tree.Tree()
                    n2 = newick.tree.Tree()
                    n1.id = n2.id = n.id
                    n.edges.append((n1, None, 1.0))
                    n.edges.append((n2, None, 1.0))
                    pops.remove(n)
                    pops += [n1, n2]

                elif r > self.mu: # loss
                    if self.verbose: print "loss(n):", n.leaves
                    pops.remove(n)
                    
                else: continue

            self.stackNodes.append(pops)
            #if self.verbose: print "pre visiting tree:", self.stackNodes

        def pre_visit_edge(self, src, b, l, dst):
            pass


        def visit_leaf(self, leaf):
            pops = []

            # need leaf level duplication too...
            # only handle the first round so far
            for n in self.stackNodes[-1]:
                r = random.random()
                
                if r < self.la: # dup
                    if self.verbose: print "dup(l):", leaf.leaves
                    n0 = newick.tree.Tree()
                    n1 = newick.tree.Leaf(leaf.id)
                    n2 = newick.tree.Leaf(leaf.id)
                    n0.edges.append((n1, None, 1.0))
                    n0.edges.append((n2, None, 1.0))
                elif r > self.mu: # loss
                    if self.verbose: print "loss(l):", leaf.leaves
                    continue
                else:
                    n0 = newick.tree.Leaf(leaf.id)

                pops.append(n0)
                    
            self.stackNodes.append(pops)
            

        def post_visit_edge(self, src, b, l, dst):
            chs = self.stackNodes.pop()
            for (p, c) in zip(self.stackNodes[-1], chs):
                p.edges.append((c, b, l))
            #if self.verbose: print "post visit edge"
            
        def post_visit_tree(self, node):
            # pop off the population in the tree, 
            # to restore it back before dup/loss
            self.stackNodes.pop()
            #if self.verbose: print "post visiting tree:", self.stackNodes

        def __call__(self, la, mu, T):
            self.la = la        # random < self.la: dup
            self.mu = 1.0 - mu  # random > self.mu: loss
            #self.cycles = 2     # how many dup/loss iterations per length?
            self.dummy = newick.tree.Tree()
            self.stackNodes = [[self.dummy]]
            T.dfs_traverse(self)
            # don't forget to skip the dummy
            return remove_single_child(self.stackNodes[-1][0], self.verbose)
    
    # background checking, and adding parent links
    assert type(T) == newick.tree.Tree
    if not hasattr(T, "parent"):
        # the trouble is that add_parent_links does not add .parent to the root node
        newick.tree.add_parent_links(T) 
        T.parent = None

    return DFS_dup_loss(verbose)(la, mu, T)


def remove_single_child(T, verbose = False):
    """
    remove internal nodes that has one or zero child.
    the edge length is combined when the node is removed.
    a new root node is returned in case of the old root got removed.
    but keep the parent's bootstrap value...
    """    
    class DFS_child_checker(newick.tree.TreeVisitor):

        def post_visit_edge(self, src, b, l, dst):
            # don't use edges.remove while iterating through edges
            if type(dst) == newick.tree.Tree:
                if len(dst.edges) == 1:
                    if self.verbose: print "found single child:", dst.leaves
                    (ch, ch_b, ch_l) = dst.edges[0]
                    # how to update b and l?
                    length = (l if l else 0.0) + (ch_l if ch_l else 0.0)
                    src.edges[src.edges.index((dst, b, l))] = (ch, b, length if length else None)
                elif len(dst.edges) == 0:
                    if self.verbose: print "found zero child:", dst.leaves
                    src.edges[src.edges.index((dst, b, l))] = None

        def post_visit_tree(self, node):
            # now we do the cleaning up; notice the reversed()
            for e in reversed(node.edges):
                if e == None:
                    node.edges.remove(e)                   
  
        def __init__(self, verbose):
            self.verbose = verbose

        def __call__(self, T):
            T.dfs_traverse(self)
            # take care of the special root case
            if len(T.edges) == 1:
                if self.verbose: print "root single child"
                T = T.edges[0][0]
                T.parent = None
            # what if len(T.deges) == 0??
            elif len(T.edges) == 0:
                if self.verbose: print "root empty child"
                T = newick.tree.Leaf('EMPTY_TREE') 
            return T
            
    # the usual background checking
    assert type(T) == newick.tree.Tree
    if not hasattr(T, "parent"):
        newick.tree.add_parent_links(T)
        T.parent = None

    return DFS_child_checker(verbose)(T)
    
