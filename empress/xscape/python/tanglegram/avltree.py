# -*- coding: utf-8 -*-  
# an AVL Tree implementation.
# source: http://bjourne.blogspot.com/2006/11/avl-tree-in-python.html
#
# [20080522]
#
# wcc: it supports duplicated elements!
# wcc: modified to support ranking
#      following Ch.14 in CLRS
# wcc: note that this implementation only supports insertion, no deletion
# wcc: improve the balancing complexity based on TAOCP V.3

class AVLNode(object): 
    def __init__(self, data): 
        self.data = data 
        self.balance = 0                # wcc: the balance factor, so we can insert it efficiently
        self.count = 1                  # wcc: data and count should go together
        self.size = 0                   # wcc: for rank()
        self.parent = None              # wcc: seems necessary for rank(). can we get rid of it?
        self.set_childs(None, None) 

    # wcc: make it look like a list object
    def __len__(self):
        return self.size

    # wcc: make it look like a list object
    #      notice the index is 0-based, 
    #      but rank is 1-based
    def __getitem__(self, i):
        return self.select(i + 1)

    def __repr__(self):
        return self.print_tree()
        #return repr(self.print_list())

    def set_childs(self, left, right): 
        self.left = left 
        self.right = right 
        # wcc
        if self.left:                        # wcc
            self.left.parent = self
        if self.right:
            self.right.parent = self
        self.size = self.get_size(left)+ self.get_size(right) + self.count   # wcc

#    # wcc: do not use this
#    def do_balance(self): 
#        bal = self.balance() 
#        if bal > 1: 
#            if self.left.balance() > 0: 
#                self.rotate_right() 
#            else: 
#                self.rotate_left_right() 
#        elif bal < -1: 
#            if self.right.balance() < 0: 
#                self.rotate_left() 
#            else: 
#                self.rotate_right_left() 
#
#    # wcc: do not use this
#    def balance(self): 
#        lheight = 0 
#        if self.left: 
#            lheight = self.left.height() 
#        rheight = 0 
#        if self.right: 
#            rheight = self.right.height() 
#        return lheight - rheight 
#
#    # wcc: do not use this
#    def height(self): 
#        lheight = 0 
#        if self.left: 
#            lheight = self.left.height() 
#        rheight = 0 
#        if self.right: 
#            rheight = self.right.height() 
#        return 1 + max(lheight, rheight) 

    def rotate_left(self): 
        #print "rotate left"
        self.data,  self.right.data  = self.right.data,  self.data 
        self.count, self.right.count = self.right.count, self.count

        # wcc: modified the order s.t. the size is correct
        #old_left = self.left 
        #self.set_childs(self.right, self.right.right) 
        #self.left.set_childs(old_left, self.left.left) 
        old_right_right = self.right.right
        #print self
        self.right.set_childs(self.left, self.right.left)
        #print self
        self.set_childs(self.right, old_right_right)
        #print self


    def rotate_right(self): 
        self.data,  self.left.data  = self.left.data,  self.data 
        self.count, self.left.count = self.left.count, self.count
        
        # wcc: as above
        #old_right = self.right 
        #self.set_childs(self.left.left, self.left) 
        #self.right.set_childs(self.right.right, old_right) 
        old_left_left = self.left.left
        self.left.set_childs(self.left.right, self.right)
        self.set_childs(old_left_left, self.left)
        

    def rotate_left_right(self): 
        self.left.rotate_left() 
        self.rotate_right() 

    def rotate_right_left(self): 
        self.right.rotate_right() 
        self.rotate_left() 

    # wcc: the actual balancing actions
    def do_balance(self, a):
        """
        actual balancing actions
        """
        child = self.left if a < 0 else self.right
        assert child, self.data        # wcc: we can only reach this if child exists

        # wcc: we know that self.balance == a
        if child.balance == a:
            #print "DEBUG: single rotation", self.data, child.data, a
            # wcc: the single rotation cases
            self.rotate_right() if a < 0 else self.rotate_left()
            self.balance = child.balance = 0
        else:
            #print "DEBUG: double rotations:", self.data, child.data, a
            # wcc: child.balance == -a, i.e., double rotations
            grand_child = self.left.right if a < 0 else self.right.left
            assert grand_child, (self.data, child.data, a)
            self.rotate_left_right() if a < 0 else self.rotate_right_left()
            # now we update the balance factors
            # after the double rotation, child and grand_child became children of self
            # the trick is to determine which one of them has balance = 0 or -grand_child.balance
            if grand_child.balance == a:
                child.balance, grand_child.balance = -a, 0
            elif grand_child.balance == 0:
                child.balance, grand_child.balance =  0, 0
            else:
                child.balance, grand_child.balance =  0, a
            # wcc: it's always balanced at self
            self.balance = 0                

    # wcc: adjust the balance factors after insert a new node
    def adj_balance(self, data):
        """
        updating balance factors, from bottom up, until we need rebalance the tree 
        """
        # a is the direction of previous insertion
        a = -1 if data < self.data else +1
        # data can't be node.data
        #assert data != self.data

        if self.balance == 0:
            self.balance = a
            if self.parent: self.parent.adj_balance(data)
        elif self.balance == -a:
            # wcc: we just balanced out ourself!
            self.balance = 0
        else: 
            # wcc: self.balance == a, now we are out of balance 
            #      time to do some actual balancing actions
            self.do_balance(a)
                

    def insert(self, data): 
        # wcc: we immediately add a new size count
        self.size += 1                          # wcc: not in self.__init__

        # wcc: the original recursive method
        if data == self.data:                   # wcc
            self.count += 1
        elif data < self.data: 
            if self.left: 
                self.left.insert(data) 
            else: 
                self.left = AVLNode(data) 
                self.left.parent = self         # wcc
                self.adj_balance(data)            # wcc: trace up until either root or balance != 0 
        else: 
            if self.right: 
                self.right.insert(data) 
            else: 
                self.right = AVLNode(data) 
                self.right.parent = self        # wcc
                self.adj_balance(data)            # wcc: trace up until either root or balance != 0 

        #self.do_balance()                        
        # wcc: balance is triggered by the actual insertion now

    # wcc: return the data of given rank
    def select(self, rank):

        min_rank = self.get_size(self.left) + 1
        max_rank = min_rank + self.count - 1

        if min_rank <= rank <= max_rank:
            return self.data
        elif rank < min_rank and self.left:
            return self.left.select(rank)
        elif rank > max_rank and self.right:
            return self.right.select(rank - max_rank)

        raise IndexError ("invalid rank, out of index")

    # wcc:
    def get_size(self, node):
        if node:
            return node.size
        else:
            return 0

    # wcc: return the (min/max) rank of given data
    #      note that this is 1-based rank
    def rank(self, data, minRank = True):
        """
        return the rank of data in the set, which is always >= 1 unless
        the data is not in the set, then 0 is returned ... (is this a good decision?) 
        """
        try:
            node, node_data = self.find_node(data)     # only a valid node will be returned
        except ValueError, e:
            if __debug__: print e
            return 0
            # wcc: should better return the rank data if it exists?  

        curr_rank = self.get_size(node.left)

        if minRank:
            curr_rank += 1
        else:
            curr_rank += node.count

        # wcc: can we find rank w/o parent?
        while node.parent:
            parent = node.parent
            if node == parent.right:
                curr_rank += (parent.size - node.size)
            node = parent

        return curr_rank

    # wcc: instead of using rank(), use this to count crossings
    #      return number of elements that are less than input
    def less(self, data):
        node, node_data = self.find_node(data)

        assert node

        count = self.get_size(node.left)

        if data > node_data:
            count += node.count

        while node.parent:
            parent = node.parent
            if node == parent.right:
                count += (parent.size - node.size)
            node = parent
        return count

    # wcc: count number of elements greater than data
    def greater(self, data):
        node, node_data = self.find_node(data)

        count = self.get_size(node.right)

        if data < node_data:
            count += node.count

        while node.parent:
            parent = node.parent
            if node == parent.left:
                count += (parent.size - node.size)
            node = parent
        return count

    # wcc: find the node of given data
    #      we need to find the lowest occurence in case of duplicated items
    def find_node(self, data):
        if data == self.data:
            return (self, data)
        elif data < self.data and self.left:
            return self.left.find_node(data)
        elif data > self.data and self.right:
            return self.right.find_node(data)
        #elif (not self.left) and (not self.right):
        else:
            return (self, self.data)
        
        #raise ValueError ("given data is not found")
        

    # wcc: to be used by __repr__?
    def print_tree(self, indent = 2): 
        strT = str(self.data) + " [*" + str(self.count) + "|" + str(self.size) + "|" + str(self.balance) + "]"  # wcc
        if self.left: 
            strT += "\n" + " " * indent + "L: " + self.left.print_tree(indent + 2) 
        if self.right: 
            strT += "\n" + " " * indent + "R: " + self.right.print_tree(indent + 2) 
        return strT

    # wcc: for debugging
    def to_list(self):
        l = []
        if self.left:
            l += self.left.to_list()
        l += [self.data] * self.count
        if self.right:
            l += self.right.to_list()
        return l

    # wcc: iterator support
    def __iter__(self):
        return self.inorder(self)

    # wcc: reversed iterator
    def reverse(self):
        """return the reversed iterator"""
        return self.inorder(self, reverse=True)
    
    # wcc: iterator object, using yield
    def inorder(self, t, reverse = False):
        if t:
            for x in self.inorder(t.right if reverse else t.left, reverse):
                yield x
            for x in xrange(t.count):
                yield t.data
            for x in self.inorder(t.left if reverse else t.right, reverse):
                yield x


def listToTree(L):
    if len(L):
        T = AVLNode(L[0])
        for x in L[1:]:
            T.insert(x)
        return T
    else:
        return None


# wcc: better put a AVLTree wrapper around?
class AVLTree(object):
    """
    use AVLNode as the base to simplify the interface
    this might not be necessary
    """
    def __init__(self, data = None):

        self.root = None    # the default is always None

        if data:
            self.insert(data)

    def __len__(self):
        return len(self.root) if self.root else 0

    def __getitem__(self, i):
        return self.root[i] if self.root else None

    def __repr__(self):
        return repr(self.root)

    def _insert_single(self, data):
        assert type(data) not in [tuple, list, AVLNode, AVLTree]
        # the actual insertion happens here
        if self.root:
            self.root.insert(data)
        else:
            self.root = AVLNode(data)
            
    def _insert_seq(self, seq):
        if len(seq):
            self.insert(seq[0])
            for x in seq[1:]:
                self.insert(x)

    def _insert_avlnode(self, node):
        pass
        
    def insert(self, data):
        assert type(data) != type(None)
        if type(data) in [list, tuple]:
            self._insert_seq(data)
        elif type(data) == AVLNode:
            self._insert_avlnode(data)
        else:
            # simple treat it as a single item
            self._insert_single(data)
            
    def rank(self, data, minRank = True):
        # rank is always 1-based. hence rank 0 means not found
        return self.root.rank(data, minRank) if self.root else 0
    
    def to_list(self):
        return self.root.to_list() if self.root else None
    
    def __iter__(self):
        return self.root.__iter__() if self.root else None

    def reverse(self):
        return self.root.reverse() if self.root else None

    def less(self, data):
        return self.root.less(data) if self.root else 0

    def greater(self, data):
        return self.root.greater(data) if self.root else 0
