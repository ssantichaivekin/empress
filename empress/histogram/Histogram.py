'''
Histogram class for Histogram Algorithm
Extension of the diameter algorithm.
Author: Santi Santichaivekin (working under Ran Libeskind-Hadas)
'''

class Histogram:
    def __init__(self, init):
        '''
        Initialize the Histoogram to either be {} or {0:1}. {0:1} corresponds to (1a) in the paper,
        and {} corresponds to (1b) in the paper.
        '''
        assert(init == None or init == 0 or type(init) == dict)
        if init == 0:
            self.histogram_dict = {0:1}
        elif type(init) == dict:
            self.histogram_dict = init
        else:
            self.histogram_dict = {}
    
    def shift(self, value):
        '''
        Shift the histogram by some value.
        This corresponds to +1 and +2 constants in the paper.
        {0:1, 3:2} << 2   => {2:1, 5:2}
        '''
        new_dict = {}
        old_dict = self.histogram_dict
        for old_key in old_dict :
            new_dict[old_key + value] = old_dict[old_key]
        return Histogram(new_dict)

    def combine(self, other):
        '''
        Add the two histogram together, the way you would expect it to work.
        This corresponds to the max operation in the paper.
        {0:1, 3:2} + {0:3, 5:1}  => {0:4, 3:2, 5:1}
        '''
        new_hist = Histogram.sum([self, other])
        return new_hist
    
    def subtract(self, other):
        '''
        Subtract the count of self from another.
        '''
        new_hist = self.histogram_dict.copy()
        other_hist = other.histogram_dict
        for key in other_hist:
            new_hist[key] -= other_hist[key]
            assert new_hist[key] >= 0, (self, other, key)
        return Histogram(new_hist)

    def xscale(self, factor):
        '''
        Scale the distances by the given factor
        '''
        new_hist = { k*factor : v for k,v in list(self.histogram_dict.items()) }
        return Histogram(new_hist)

    def mean(self):
        '''
        The mean distance
        '''
        n = 0
        total = 0
        for k,v in list(self.histogram_dict.items()):
            n += v
            total += k * v
        return total / float(n)

    def total(self):
        '''
        The total amount of distance
        '''
        total = 0
        for k,v in list(self.histogram_dict.items()):
            total += k * v
        return total

    def standard_deviation(self):
        '''
        The standard deviation of the distances
        '''
        mean = self.mean()
        s=0
        n = 0
        for k,v in list(self.histogram_dict.items()):
            n += v
            s += v * ((k-mean)**2)
        return ((s / float(n)) ** 0.5)

    @staticmethod
    def sum(hist_list):
        new_dict = {}
        for hist in hist_list :
            for key in hist.histogram_dict :
                if key not in new_dict :
                    new_dict[key] = 0
                new_dict[key] += hist.histogram_dict[key]
        return Histogram(new_dict)
    
    def product_combine(self, other, n_choices):
        '''
        Generally, combine would work like this:
        {0:1} * {3:1}  => {3:1}
        {0:1, 2:1} * {3:1}  => {3:1. 5:1}
        {0:1, 2:1} * {3:1, 5:2}  => {3:1, 5:3, 7:2}
        However, if the original histograms are from
        the same mapping node, we multiply the number of
        histograms by 2 if the indeces are not 0.

        '''
        #TODO: maybe rename to convolution, rewrite the test, rewrite the docstring
        new_dict = {}

        old_dict_A = self.histogram_dict
        old_keys_A = list(old_dict_A.keys())
        old_dict_B = other.histogram_dict
        old_keys_B = list(old_dict_B.keys())

        for old_key_A in old_keys_A :
            for old_key_B in old_keys_B :
                new_key = old_key_A + old_key_B
                if new_key not in new_dict:
                    new_dict[new_key] = 0
                # Determine how many choices
                local_choices = n_choices
                if old_key_A == 0:
                    local_choices -= 1
                if old_key_B == 0:
                    local_choices -= 1
                if local_choices < 0:
                    local_choices = 0
                n_pairs = old_dict_A[old_key_A] * old_dict_B[old_key_B]
                new_dict[new_key] += n_pairs * (2**local_choices)

        return Histogram(new_dict)

    def double_nonzero_entry(self):
        '''
        Return a new histogram with its nonzero entry
        doubled.
        '''
        new_dict = self.histogram_dict.copy()
        for key in new_dict:
            if key != 0:
                new_dict[key] *= 2
        return Histogram(new_dict)
    
    def __eq__(self, other):
        return self.histogram_dict == other.histogram_dict
    
    def __ne__(self, other):
        return not self == other
    
    def __lshift__(self, value):
        return self.shift(value)
    
    def __add__(self, other):
        return self.combine(other)
    
    def __sub__(self, other):
        return self.subtract(other)
    
    def __mul__(self, other):
        raise DeprecationWarning("Use self.product_combine(other, isSameMappingNode) instead")

    def __repr__(self):
        return str(self.histogram_dict)

