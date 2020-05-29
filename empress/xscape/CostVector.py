# CostVector.py
# Ran Libeskind-Hadas, October 2013

# CostVector class

# Cost vectors are in CDSL format: 
# c(ospeciation), d(uplication), s(witch), l(oss)

# python libraries
from string import *

class CostVector:
    def __init__(self, c, d, s, l, count):
        self.c = c
        self.d = d
        self.s = s
        self.l = l
        self.count = count

    def __add__(self, other):
        ''' add another CostVector '''
        return CostVector(self.c + other.c, self.d + other.d, \
                          self.s + other.s, self.l + other.l, \
                          self.count * other.count)

    def __mul__(self, CVlist):
        output = []
        for vector in CVlist:
            output.append(self+vector)
        return output

    def __repr__(self):
        return "<" + str(self.c) + ", " + str(self.d) + ", " + str(self.s) + \
               ", " + str(self.l) + "> Count = " + str(self.count)

    def __str__(self):
        return "<" + str(self.c) + ", " + str(self.d) + ", " + str(self.s) + \
               ", " + str(self.l) + "> Count = " + str(self.count)

    def __eq__(self, other):
        return self.d == other.d and self.s == other.s and self.l == other.l
    
    def __lt__(self, other):
        return (self.d <= other.d) and \
               (self.s <= other.s) and (self.l <= other.l) and \
               ((self.d < other.d) or (self.s < other.s) or (self.l < other.l))
     
    def __lte__(self, other):
        return self.__lt__(other) or self.__eq__(other)
                              
    def lex(self, other):
        if self.__eq__(other): return 0
        if self.d < other.d: return -1
        elif self.d == other.d and self.s < other.s: return -1
        elif self.d == other.d and self.s == other.s and self.l < other.l: return -1
        else: return 1

    def toTupleCDSLCount(self):
        return (self.c, self.d, self.s, self.l, self.count)
        
    def toTupleCDSL(self):
        return (self.c, self.d, self.s, self.l)

