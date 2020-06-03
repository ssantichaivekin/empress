#!/usr/bin/env python
"""
use python visual module to display a newick tree.
mainly this is a subclass of the newick.tree.TreeVisitor

visual 4-beta26 seems to cause segfault all the time upon termination.
visual 3 has no such problem.

recall: the newick.tree.TreeVisitor has the following methods:

class DFS_visitor(newick.tree.TreeVisitor):
    def __init__(self):
        pass
    def pre_visit_tree(self, node):
        pass
    def post_visit_tree(self, node):
        pass
    def pre_visit_edge(self, src, bootstrap, length, trg):
        pass
    def post_visit_edge(self, src, bootstrap, length, trg):
        pass
    def visit_leaf(self, leaf):
        pass


-- wcchang
"""

from __future__ import division # yeah! from the future!

from visual import *
import newick, LCA

class DFS_visual(newick.tree.TreeVisitor):
    """
    draw the newick tree in a 2-d plane using python-visual
    """
    def __init__(self, frame = None, style = 'cladogram'):
        self.originX = 0
        self.originY = 0
        self.stepX = 1.5
        self.stepY = 2
        self.nodeRadius = 0.2
        self.edgeRadius = 0.05
        self.nodeColor = color.red
        self.edgeColor = 0.5
        self.labelColor = color.white
        self.frame = frame
        self.style = style              
        # wcc: one of the three styles: cladogram, additive, ultrametric
        # not quite ultrametric here either
        pass

#===============================================================================
#    def clear(self):
#        """clear the visual objects in the given frame"""
#        if self.frame:
#            #self.frame.visible = False
#            for obj in self.frame.objects:
#                obj.visible = False
#                #obj.__del__()
#===============================================================================

    # before visiting a (sub)tree
    def pre_visit_tree(self, t):
        posx = self.originX + len(t.leaves) * self.stepX - self.stepX
        posy = self.originY + (len(t.leaves) * self.stepY - self.stepY) / 2
        t.pos = vector(posx, posy, 0)
        t.corners = []
        pass

    # after visiting a (sub)tree
    def post_visit_tree(self, t):
        #print t.leaves
        #print "[%d, %d]" % (t.leaves[0].pos.y, t.leaves[-1].pos.y)
        if hasattr(t, 'vnode'):
            t.vnode.pos = t.pos
            t.vnode.radius = self.nodeRadius
            t.vnode.color = self.nodeColor

            if self.style == 'ultrametric':
                t.vedgeAZ.pos = t.corners[0]
                t.vedgeAZ.axis = t.corners[-1] - t.corners[0]
                t.vedgeAZ.radius = self.edgeRadius
                t.vcornerA.pos = t.corners[0]
                t.vcornerA.radius = self.edgeRadius
                t.vcornerZ.pos = t.corners[-1]
                t.vcornerZ.radius = self.edgeRadius
            elif self.style == 'additive':
                print "not available yet"
            
        else:
            t.vnode = sphere(pos = t.pos, radius = self.nodeRadius, color = self.nodeColor, frame = self.frame)

            if self.style == 'ultrametric':
                t.vedgeAZ = cylinder(pos = t.corners[0], axis = (t.corners[-1] - t.corners[0]), \
                                     radius = self.edgeRadius, color = self.edgeColor, frame = self.frame)
                t.vcornerA = sphere(pos = t.corners[0], radius = self.edgeRadius, color = self.edgeColor, frame = self.frame)
                t.vcornerZ = sphere(pos = t.corners[-1], radius = self.edgeRadius, color = self.edgeColor, frame = self.frame)
            elif self.style == 'additive':
                print "not available yet"
        pass

    # before visiting an edge/child
    def pre_visit_edge(self, src, bootstrap, length, dst):
        pass

    # after visting an edge/child
    def post_visit_edge(self, src, bootstrap, length, dst):
        
        if self.style == 'cladogram':
            if hasattr(dst, 'vedge'):
                dst.vedge.pos = src.pos
                dst.vedge.axis = dst.pos - src.pos
                dst.vedge.radius = self.edgeRadius
            else:
                dst.vedge = cylinder(pos = src.pos, axis = (dst.pos - src.pos), \
                                     radius = self.edgeRadius, color = self.edgeColor, frame = self.frame)

        elif self.style == 'additive':
            print "not available yet"

        elif self.style == 'ultrametric':
            corner = vector(src.pos.x, dst.pos.y, 0)
            src.corners.append(corner)

            if hasattr(dst, 'vedge'):
                dst.vedge.pos = corner
                dst.vedge.axis = dst.pos - corner
                dst.vedge.radius = self.edgeRadius
            else:
                dst.vedge = cylinder(pos = corner, axis = (dst.pos - corner), \
                                     radius = self.edgeRadius, color = self.edgeColor, frame = self.frame) 
                
    # the leaf case
    def visit_leaf(self, l):
        l.pos = vector(self.originX, self.originY, 0)
        self.originY += self.stepY
        #print l.id, l.pos.x
        if hasattr(l, 'vnode'):
            l.vnode.pos = l.pos
            l.vnode.radius = self.nodeRadius
            l.vlbl.pos = l.pos
        else:
            l.vnode = sphere(pos = l.pos, radius = self.nodeRadius, color = self.nodeColor, frame = self.frame)
            l.vlbl = label(pos = l.pos, text = l.id, frame = self.frame, color = self.labelColor)
        pass

class DFS_tanglegram_visual(newick.tree.TreeVisitor):
    """
    draw the connections, i.e., tanglegram of the trees
    always from G to S
    only use this after LCA-mapping and initial drawing are done
    """
    def __init__(self, frame = None, lca = true):
        self.tangleRadiusL = 0.1
        self.tangleRadiusN = 0.05
        self.tangleColorL = color.green
        self.tangleColorN = color.orange
        self.tangleSegs = 50
        self.frame = frame
        self.lca = lca
    
    def clear(self):
        """clear the visual objects in the given frame"""
        if self.frame:
            #self.frame.visible = False
            for obj in self.frame.objects:
                obj.visible = False


    def rainbow(self, _p1, _p2, n):
        """
        return the list of points from p1 to p2 in n segments that forms a half circle
        """
        p1 = vector(_p1)
        p2 = vector(_p2)
        pts = []
        c = (p1+p2)/2
        raxis = ((p1 - c).cross(vector(0, 0, 1))).norm()
        for th in arange(0, pi, pi/n):
            pts.append((p1 - c).rotate(axis = raxis, angle = th) + c)
        pts.append(p2)
        return pts

    
    def post_visit_tree(self, t):    
        if not self.lca: return
        s1 = t.pos
        s2 = t.M.pos
        dts = self.rainbow(s1, s2, self.tangleSegs)
        t.vM = curve(pos = dts, color = self.tangleColorN, radius = self.tangleRadiusN, frame = self.frame)
    
    def visit_leaf(self, l):
        #l.vM = cylinder(pos = l.pos, axis = (l.M.pos - l.pos), \
        #         radius = self.tangleRadiusL, color = self.tangleColorL, frame = self.frame)
        l.vM = curve(pos = [l.pos, l.M.pos], radius = self.tangleRadiusL, color = self.tangleColorL, \
                     frame = self.frame)



def build_LCA(G, S, verbose = False):
    """
    build the LCA mapping from given G to given S:
    1. preprocess S
    2. construct leaf-mapping
    3. DFS through G, map G to S
    """
    class DFS_species_preLCA(newick.tree.TreeVisitor):
        """
        preprocess S for LCA:
        1. build the child-parent dictionary for LCA
        2. build the leaf-node dictionary
        """
        def __init__(self):
            self.Pa = {}         # child-parent relation, Pa()
            self.Le = {}         # 'id'-leaf relation, Le('id')
            self.nodes = []

        def pre_visit_edge(self, src, bootstrap, length, dst):
            self.Pa.setdefault(dst, src)

        def post_visit_tree(self, t):
            self.nodes.append(t)

        def visit_leaf(self, s):
            id = s.leaves_ids[0]
            if self.Le.has_key(id):
                raise "ERROR: Species tree has duplicated taxon: %s" % id
            self.Le.setdefault(s.leaves_ids[0], s)
            self.nodes.append(s)

    class DFS_gene_LCA(newick.tree.TreeVisitor):
        """
        recursively build up the LCA mapping
        """
        def __init__(self, Ls, LCAs):
            self.Ls = Ls        # leaves of S, Ls['id'] = leave
            self.LCAs = LCAs    # LCA of S
            self.nodes = []
            
        def pre_visit_tree(self, t):
            t.M = None

        def post_visit_tree(self, t):
            self.nodes.append(t)
        
        def post_visit_edge(self, src, bo, le, trg):
            if not trg.M:
                raise "ERROR: Gene tree failed LCA mapping at: %s" % trg.leaves
            src.M = self.LCAs(src.M, trg.M)

        def visit_leaf(self, g):
            if hasattr(g, "interleaf"):
                g.M = self.LCAs(*g.interleaf)
            else:
                id = g.leaves_ids[0]
                if not self.Ls.has_key(id):
                    raise "ERROR: Gene tree has orphan taxon: %s" % id
                g.M = self.Ls[id]
            self.nodes.append(g)
    
    # step 1: preprocess S
    dfsS = DFS_species_preLCA()
    S.dfs_traverse(dfsS)

    lcaS = LCA.LCA(dfsS.Pa)
    
    # test:
    #print dfsS.Pa
    #print dfsS.Le
    #print dfsS.Le['a'], dfsS.Le['b']
    #print lcaS(dfsS.Le['a'], dfsS.Le['b'])
    # step 2: build the leaf-mapping
    # step 3: build the LCA-mapping
    dfsG = DFS_gene_LCA(dfsS.Le, lcaS)
    G.dfs_traverse(dfsG)

    # test:
    # a little short-cut for testing purpose
    if verbose:
        S.nodes = dfsS.nodes
        G.nodes = dfsG.nodes


# a simple test
if __name__ == '__main__':
    treeS = "(('a', ('b', 'c')), ('d', 'e'));"
    treeG = "(((('a', ('b', 'c')), (('a', 'b'), 'c')), 'e'), 'd', 'e');"
    newickS = newick.tree.parse_tree(treeS)
    newickG = newick.tree.parse_tree(treeG)

    print newickS
    print newickG

    build_LCA(newickG, newickS, verbose=True)
    
    for n in newickG.nodes:
        print "LCA mapping:", n, "->", n.M

    # wcc: testing nested module reference
    from .. import newick_utils
    newick_utils.random_internal_switch(newickS)

    #print "no visual for you!"
    sys.exit(0)

    # basic setup
    scene.toolbar = True

    # the basic axes
    xaxis = arrow(pos = (0.05, 0, 0), axis = (1, 0, 0), color = color.red)
    yaxis = arrow(pos = (0, 0.05, 0), axis = (0, 1, 0), color = color.green)
    zaxis = arrow(pos = (0, 0, 0.05), axis = (0, 0, 1), color = color.blue)

    dfsS = DFS_visual(style = 'ultrametric')
    dfsS.originY = (dfsS.stepY - dfsS.stepY * len(newickS.leaves)) / 2
    dfsS.originX = -2
    dfsS.stepX = -1                         # flip the direction, S is on the left-hand-side

    newickS.dfs_traverse(dfsS)

    # render the same tree again, but mirrored
    dfsG = DFS_visual()
    dfsG.originY = (dfsS.stepY - dfsG.stepY * len(newickG.leaves)) / 2
    dfsG.originX = 2
    dfsG.stepX = 1                             # changing the direction
    newickG.dfs_traverse(dfsG)

    dfsT = DFS_tanglegram_visual()

    # colors
    dfsT.tangleColorL = color.red
    dfsG.nodeColor  = color.green
    dfsS.nodeColor  = color.green
    dfsG.labelColor = color.black
    dfsS.labelColor = color.black
    dfsT.tangleColorL = color.red    
    
    newickG.dfs_traverse(dfsT)

    # rotate everything by -90 degrees z
    # label objects can't rotate!
    #for obj in scene.objects:
    #    obj.rotate(angle = -pi/2, axis = (0, 0, 1), origin = (0, 0, 0))

    # or we rotate the camera
    #scene.forward.rotate(axis=(0,0,1), angle=-pi/2)
    print "forward:", scene.forward
    print "up:", scene.up
    scene.up = (0, 0, 1)
    scene.forward = (0,1,-1)
    print "up:", scene.up
    print "version:", version

    labels = []

    for obj in scene.objects:
        if obj.__class__ == label:
            labels.append(obj)
    # label's text are screwed..?!
    # l.text does not return all symbols?!

    while True:
        rate(50)
        if scene.kb.keys:
            s = scene.kb.getkey()
            print "[%s] is pressed." % s

            if s == 'a' or s == 'A':
                print "realign the camera axis"
                scene.up = (0, 0, 1)
                scene.forward = (0,1,-1)
                
            if s == 'l' or s == 'L':
                print "toggle labels"
                # invisible objects are subject to be GC'ed.
                # and they will be removed from scene.objects
                for l in labels: l.visible = not l.visible

            if s == ',' or s == '<':
                # rotate the camera -z
                print "rotating CW in z"
                scene.forward = scene.forward.rotate(axis = (0, 0, -1), angle = pi/8)
            
            if s == '.' or s == '>':
                # rotate the camear +z
                print "rotating CCW in z"
                scene.forward = scene.forward.rotate(axis = (0, 0, 1), angle = pi/8)

            if s == 'q' or s == 'Q':
                print "status:"
                print "scene.up:", repr(scene.up)
                print "scene.forward:", repr(scene.forward)
                print "scene.center:", repr(scene.center)

            if s == 'up':
                scene.center[1] += 0.1
            if s == 'down':
                scene.center[1] -= 0.1
            if s == 'left':
                scene.center[0] -= 0.1
            if s == 'right':
                scene.center[0] += 0.1
            if s in ['up', 'down', 'left', 'right']:
                xaxis.pos = yaxis.pos = zaxis.pos = scene.center

#            if s == 'x' or s == 'X':
#                # how to quit vpython?
#                # not quite work in visual-beta4
#                scene.visible = False
#                print "bye"
#                sys.exit(0)
        

    print "done."
