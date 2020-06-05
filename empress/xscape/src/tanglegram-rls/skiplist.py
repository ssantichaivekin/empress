"""
An implementation of Skip Lists by William Pugh for tanglegram.
The data structure is simplified to perform search,
insert and rank (additional op) only.

As recommended in the paper, we only increment maxLevel by 1,
hence we always start the search from there.

Since we use sys.maxint as NIL.data, all valid data sould be < sys.maxint

Maybe the traversal operations can be implemented as a visitor pattern
since there are so many 
occurrence of:
    def function(self):
        <PreTour task>
        curr =  self.head
        for i in xrange(self.maxLevel-1, -1, -1):
            while curr.forward[i].data < maxint/data:
                curr = curr.forward[i]
                <ForEach task>
        
        curr = curr.forward[0]
        <PostTour task>

or:
    def function(self):
        curr = self.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]

Author: wcc
Ref: Wikipedia:SkipList
"""
import random
from sys import maxint

class SkipList(object):
    """
    the main class
    """
    
    class SkipNode(object):
        """
        the container class
        """
        def __init__(self, level, data, count=1):
            self.data = data
            self.count = count
            self.partialSum = 0         # total number of elements that is less than self.data
            self.forward = [None] * level           # the forward pointers 
    
        def __repr__(self):
            """
            for debugging purpose
            """
            return "[%s|%d|%s|%d]" % (self.data, self.count, len(self.forward), self.partialSum) 
    
    def __init__(self, L=None, p=0.5):
        self.p = p
        self.maxLevel = 1               # len(head.forward)
        self.head = self.SkipNode(self.maxLevel, maxint, 0)    # so we know it's the end of the line
        # self.head.count also double as total count
        self.head.forward[0] = self.head
        # wcc: for less() and greater()
        self.sumCorrect = True             # turn False whenever insert()

        if L != None:
            try:
                for x in L:
                    self.insert(x)
            #except TypeError:
            #    print "Error: provided data object is not iterable"
            finally:
                pass

    def __len__(self):
        return self.head.count

    def __repr__(self):
        return repr(self.toList())
        #return "Hello!"

    def toList(self):
        result = []
        for x in self:
            result.append(x)
        return result

    def debug(self):
        result = []
        curr = self.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]
            result.append(curr)
        return result

    def __iter__(self):
        return self.iterData(self) 

    def iterNode(self, L):
        """
        special iterator that goes through all nodes
        """
        curr = L.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]
            yield curr

    def iterData(self, L):
        """
        normal iterator that goes through all data items
        """
        curr = L.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]
            for i in xrange(curr.count):
                yield curr.data

    def search(self, data):
        """
        return the SkipNode that has data, otherwise, None
        does not seem necessary in tanglegram except for testing
        """
        curr = self.head
        # loop invariant: curr.data < data
        for i in xrange(self.maxLevel-1, -1, -1):
            while curr.forward[i].data < data:
                curr = curr.forward[i]
        # curr.data < data <= curr.forward[0].data
        curr = curr.forward[0]
        # should we return the whole node?
        return (None, curr.data)[curr.data == data]
    
    def insert(self, data, count=1):
        """
        WARNING: partialSum is no longer correct after this operation
        """
        # maybe we can skip the following assertion?
        assert data < maxint
        # always a new element
        self.sumCorrect = False
        self.head.count += count
        update = [None] * self.maxLevel       # update[0,...,self.maxLevel-1]
        curr = self.head
        for i in xrange(self.maxLevel-1, -1, -1):
            while curr.forward[i].data < data:
                curr = curr.forward[i]
            update[i] = curr
        
        curr = curr.forward[0]
        if curr.data == data:
            # the node with the data exists; just increment the counter
            curr.count += count
        else:
            # we need to insert a new node
            lvl = self.randomLevel()
            # we implement the third approach, "fix the dice"
            if lvl == self.maxLevel:
                # we raise maxLevel by 1
                self.maxLevel += 1
                self.head.forward.append(self.head)      # double as tail
                update.append(self.head)
            # the new node
            curr = self.SkipNode(lvl+1, data, count)
            for i in xrange(lvl+1):
                # i = 0..lvl
                curr.forward[i] = update[i].forward[i]
                update[i].forward[i] = curr
    
    def less(self, data):
        """
        return the count of elements that is less than data
        based on search()
        """
        # update on demand.
        # amortized cost of partialSum should be constant
        if not self.sumCorrect:
            self.partialSum()

        curr = self.head
        # loop invariant: curr.data < data
        for i in xrange(self.maxLevel-1, -1, -1):
            while curr.forward[i].data < data:
                curr = curr.forward[i]
        # curr.data < data <= curr.forward[0].data
        return curr.partialSum

    def greater(self, data):
        """
        return the count of elements that is greater then data
        based on less()
        """
        if not self.sumCorrect:
            self.partialSum()

        curr = self.head
        for i in xrange(self.maxLevel-1, -1, -1):
            while curr.forward[i].data < data:
                curr = curr.forward[i]
        # curr.data < data <= curr.forward[0].data
        return len(self) - curr.partialSum - (0, curr.forward[0].count)[data == curr.forward[0].data]

    def partialSum(self):
        """
        curr.partialSum counts total elements <= curr.data
        update the partialSume field in O(N)
        """
        sum = 0
        curr = self.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]
            sum += curr.count
            curr.partialSum = sum
        # we don't have to update self.head
        self.sumCorrect = True
    
    def extend(self, other):
        """
        extend self by all nodes in other in O(N)
        """
        assert type(other) == SkipList
        curr = other.head
        while curr.forward[0].data < maxint:
            curr = curr.forward[0]
            self.insert(curr.data, curr.count)

        self.partialSum()
        
    def randomLevel(self):
        """
        return [0, self.maxLevel]
        """
        lvl = 0
        while random.random() < self.p and lvl < self.maxLevel:
            lvl += 1
        return lvl
    
def test0(N=100):
    """
    currectness test
    """
    L = range(N)
    SL = SkipList()
    for x in L:
        SL.insert(x)

    for x in SL:
        print x,
    print

    print len(SL), type(SL), SL
    
    for x in L:
        n = SL.search(x)
        assert n == x

    SL.partialSum()
    print SL.debug()

    L2 = [random.randint(1, N) for x in xrange(N)]
    for x in L2:
        SL.insert(x)
    SL.partialSum()
        
    L.extend(L2)
    random.shuffle(L)
    print L
    print SL
    print SL.debug()
    for x in L:
        try:
            r1, r2 = SL.less(x), len(filter(lambda y: y < x, L))
            assert r1 == r2, (x, r1, r2)
        except AssertionError, e:
            print e
    print SL.less(-1), "this should be 0"

    SL2 = SkipList()
    for x in L2:
        SL2.insert(x)

    L.extend(L2)
    SL.extend(SL2)

    random.shuffle(L)
    for x in L:
        assert SL.less(x) == len(filter(lambda y: y < x, L))

def test2(N=100):
    import time, math
    L = [random.randint(1, N) for x in xrange(5*N)]
    # as suggested in the paper
    SL = SkipList()
    for x in L:
        SL.insert(x)
    SL.partialSum()
    for x in L:
        assert SL.less(x)    == len(filter(lambda y: y < x, L))
        assert SL.greater(x) == len(filter(lambda y: y > x, L))

    t1 = time.time()
    for x in L:
        SL.less(x)
    t2 = time.time()
    for x in L:
        len(filter(lambda y: y < x, L))
    t3 = time.time()
    print "N: %d, list: %f, skiplist: %f" % (N, t3-t2, t2-t1)

# p = 0.5
# N:  100, list:  0.036555, skiplist: 0.002525
# N:  200, list:  0.147045, skiplist: 0.005290
# N:  400, list:  0.615354, skiplist: 0.012343
# N: 1000, list:  3.693021, skiplist: 0.035578
# N: 2000, list: 14.870933, skiplist: 0.078236
# N: 4000, list: 60.831508, skiplist: 0.176233
# done
# p = 1/e
# N:  100, list:  0.038342, skiplist: 0.002757
# N:  200, list:  0.154792, skiplist: 0.006322
# N:  400, list:  0.639001, skiplist: 0.013429
# N: 1000, list:  3.821474, skiplist: 0.037355
# N: 2000, list: 15.256670, skiplist: 0.079662
# N: 4000, list: 61.261215, skiplist: 0.177003
# done
# p = 0.25
# N:  100, list:  0.037075, skiplist: 0.002483
# N:  200, list:  0.149477, skiplist: 0.004987
# N:  400, list:  0.594183, skiplist: 0.014572
# N: 1000, list:  3.669433, skiplist: 0.038465
# N: 2000, list: 15.262056, skiplist: 0.092933
# N: 4000, list: 60.601718, skiplist: 0.186927
# done
# 
# N:  100, list:  0.036630, skiplist: 0.002566
# N:  200, list:  0.147535, skiplist: 0.006152
# N:  400, list:  0.594926, skiplist: 0.011786
# N: 1000, list:  3.764942, skiplist: 0.037076
# N: 2000, list: 15.398588, skiplist: 0.079735
# N: 4000, list: 62.344449, skiplist: 0.180703
    
if __name__ == "__main__":
    #test0(5)
    test2(100)
    test2(200)
    test2(400)
    #test2(1000)
    #test2(2000)
    #test2(4000)
    
    print "done"
