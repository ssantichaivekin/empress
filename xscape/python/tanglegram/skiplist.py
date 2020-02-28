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
    
