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

def test0(N = 100):
    import random, time
    L = [random.randint(1, N) for x in xrange(N)]
    R = [sum([y < x for y in L]) + 1 for x in L]

    t1 = time.time()
    T = AVLNode(L[0])
    for x in L[1:]:
        T.insert(x)
    t_insert = time.time() - t1
    
    t1 = time.time()
    for i in xrange(N):
        assert R[i] == T.rank(L[i])
    t_rank = (time.time() - t1) / N
    
    print "done: insertion: %f, avg-rank: %f" % (t_insert, t_rank)

def test1(N = 10):
    import time
    # only single rotation is tested
    L = range(N)

    t1 = time.time()
    tree = AVLNode(L[0]) 
    for x in L[1:]:
        tree.insert(x)
    print time.time() - t1
        
    #print tree.print_tree()
    assert tree.to_list() == L
    assert check_parent_child(tree)

def test_double():
    T = AVLNode(1)
    T.insert(10)
    T.insert(9)
    T.insert(3)
    T.insert(2)
    print T

def test_special():
    """
    a special case of double rotation on the same node, i.e., 43, that fails the 2nd time
    """
    #L = [21, 16, 49, 43, 48, 0, 11, 26, 15, 6, 7, 40, 12, 44, 33, 31, 28, 36, 30, 38, 13, 9, 17, 19, 18, 27, 23, 14, 8, 20, 3, 25, 46, 29, 24, 35, 32, 45, 41, 22, 47, 42, 1, 2, 10, 39, 5, 4, 34, 37]
    #L = [21, 16, 49, 43, 48, 0, 11, 26, 15, 6, 7, 40, 12, 44, 33, 31, 28, 36, 30, 38, 13, 9, 17, 19, 18, 27, 23, 14, 8, 20, 3, 25, 46, 29, 24, 35, 32, 45, 41]
    L = [15, 76, 12, 30, 11, 43, 86, 55, 78, 19, 42, 84, 94, 91, 8, 3, 16, 26, 93, 18, 89, 20, 27, 2, 17, 79, 50, 45, 51, 83, 0, 56, 53, 44, 32, 22, 97, 47, 67, 96, 98, 68, 7, 41, 40, 70, 38, 52, 82, 66, 88, 81, 80, 65, 69, 29, 13, 39, 85, 77, 24, 99, 72, 1, 46, 31, 21, 87, 9, 28, 35, 36, 4, 61, 71, 5, 57, 62, 54, 60, 73, 34, 75, 37, 74, 59, 63, 95, 10, 49, 90, 33, 25, 92, 48, 58, 14, 23, 6, 64]

    T = AVLNode(L[0])
    for x in L[1:]:
        if x in [55, 53]:
            print "before inserting:", x
            print T
        try:
            T.insert(x)
            check_balance(T)
        except AssertionError, e:
            print "assertion error after inserting:", x
            print e
            print T
            break

    #print T

def check_balance(T):
    if not T:
        return 0
    else:
        lheight = check_balance(T.left)
        rheight = check_balance(T.right)
        assert T.balance == (rheight - lheight), "balance error: %d %d %d" % (T.data, lheight, rheight)
        return 1 + max(lheight, rheight)

def test2(N = 10):
    import time, random
    #  test double rotations, but how?
    L = range(N)
    random.shuffle(L)
    
    t1 = time.time()
    T = AVLNode(L[0])
    for x in L[1:]:
        #print T
        try:
            T.insert(x)
            check_balance(T)
        except AssertionError, e:
            print x, e
            print T
            print L
            break;
    print time.time() - t1

    L.sort()
    assert check_parent_child(T)
    #    print "ERROR:", e 
    assert T.to_list() == L

def check_parent_child(T):
    if T.left:
        return (T.left.parent == T) and check_parent_child(T.left)
            #raise Exception, (T.data, T.left.data)
        #return check_parent_child(T.left)
    if T.right:
        return (T.right.parent == T) and check_parent_child(T.right)
            #raise Exception, (T.data, T.right.data)
        #return check_parent_child(T.right)
    return True
    

def test3():
    T = AVLNode(3)
    T.insert(2)
    T.insert(4)
    T.insert(3)
    T.insert(5)
    T.insert(8)
    T.insert(1)
    T.insert(1)
    T.insert(5)
    T.insert(3)

    print "T[3]:", T[3]
    print "size", len(T)

    print T
    print T.to_list()
    print "rank of 3:", T.rank(3), T.rank(3, False)
    print "rank of 5:", T.rank(5), T.rank(5, False)
    print "rank of 100:", T.rank(100)

    print "testing AVLTree wrapper ..."
    t2 = AVLTree()
    print t2.to_list()
    print len(t2)
    print t2[3]
    print t2.rank(3)
    
    t2.insert([1,2,3,4,5])
    t2.insert(2)
    print t2.to_list()
    print len(t2)
    print t2[3]
    print t2.rank(3)
    
    print "continue ..."
    t3 = AVLTree([3,2,1,5,3])
    print t3.to_list()
    print len(t3)
    print t3[3]
    print t3.rank(3)

    print "comparing results from AVLNode and AVLTree"
    t4 = AVLTree(T.to_list())
    print t4.to_list()
    print T.to_list()
    print t4
    print "rank of 3:", T.rank(3), t4.rank(3), T.rank(3, False), t4.rank(3, False)
    print "rank of 5:", T.rank(5), t4.rank(5), T.rank(5, False), t4.rank(5, False)

def test4(N = 10):

    import random
    L = [random.randint(1, N) for x in range(N)]

    T = AVLTree()
    print L
    for i in xrange(N):
        x = L[i]
        less = len([y for y in L[:i] if y < x])
        greater = len([y for y in L[:i] if y > x])
        if less != T.less(x) or greater != T.greater(x):
            print (x, less, T.less(x), greater, T.greater(x))
        T.insert(x)


def test5(N = 10):
    import time, random

    L = [random.randint(1, N) for x in xrange(5*N)]

    T = AVLNode(L[0])
    for x in L[1:]:
        T.insert(x)

    for x in L:
        assert T.less(x)    == len(filter(lambda y: y < x, L))
        assert T.greater(x) == len(filter(lambda y: y > x, L))

    t1 = time.time()
    for x in L:
        T.less(x)
    t2 = time.time()
    for x in L:
        len(filter(lambda y: y < x, L))
    t3 = time.time()
    print "N: %d, list: %f, AVLTree: %f" % (N, t3-t2, t2-t1)

# N:  100, list:  0.036377, AVLTree: 0.006275
# N:  200, list:  0.144284, AVLTree: 0.014375
# N:  400, list:  0.585451, AVLTree: 0.033542
# N: 1000, list:  3.677870, AVLTree: 0.101296
# N: 2000, list: 14.920394, AVLTree: 0.229239
# N: 4000, list: 60.240717, AVLTree: 0.497330
# 

if __name__ == "__main__":
    #print "t1, N=10\t",; test1(10) 
    #test1(15)
    #print "t1, N=100\t",; test1(100)
    #test1(200)
    #print "t1, N=1000\t",; test1(1000)
    #test1(10000)
    #test1(20000)
    #test1(100000)
    #test1(1000000)  # hmmm...
    #print "t2, N=10\t",;   test2(10)
    #print "t2, N=50\t",;   test2(50)
    #print "t2, N=100\t",;  test2(100)
    #print "t2, N=500\t",;  test2(500)
    #print "t2, N=1000\t",; test2(1000)

    #test_double()
    #test_special()    
    
    #test0(100)
    #test0(1000)
    #test0(10000)

    #test3()
    #test4(10)
    #test4(100)
    #test4(1000)
    #test4(10000)

    test5(100)
    test5(200)
    test5(400)
    test5(1000)
    test5(2000)
    test5(4000)

    print "done"
