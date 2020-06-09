import unittest

from empress.clumpr.Histogram import Histogram


class HistogramTestCase(unittest.TestCase):
    def setUp(self):
        return
    
    def test_shift1(self):
        hist = Histogram(None)
        new_hist = hist << 1

        self.assertEqual(new_hist.histogram_dict, {})

    def test_shift2(self):
        hist = Histogram(0)
        new_hist = hist << 3

        self.assertEqual(hist.histogram_dict, {0:1})
        self.assertEqual(new_hist.histogram_dict, {3:1})

    def test_shift3(self):
        hist = Histogram({0:1, 3:5})
        new_hist = hist << 1

        self.assertEqual(hist.histogram_dict, {0:1, 3:5})
        self.assertEqual(new_hist.histogram_dict, {1:1, 4:5})

    def test_combine1(self):
        histA = Histogram(0)
        histB = Histogram(None)
        new_hist = histA + histB

        self.assertEqual(histA.histogram_dict, {0:1})
        self.assertEqual(histB.histogram_dict, {})
        self.assertEqual(new_hist.histogram_dict, {0:1})

    def test_combine2(self):
        histA = Histogram({0:1, 2:1, 3:2})
        histB = Histogram({2:1, 3:1, 10:1})
        new_hist = histA + histB

        self.assertEqual(histA.histogram_dict, {0:1, 2:1, 3:2})
        self.assertEqual(histB.histogram_dict, {2:1, 3:1, 10:1})
        self.assertEqual(new_hist.histogram_dict, {0:1, 2:2, 3:3, 10:1})

    def test_product1(self):
        # TODO: update test to reflect new product function
        histA = Histogram(0)
        histB = Histogram(None)
        n_choices = 0
        new_hist = histA.product_combine(histB, n_choices)

        self.assertEqual(histA.histogram_dict, {0:1})
        self.assertEqual(histB.histogram_dict, {})
        self.assertEqual(new_hist.histogram_dict, {})

    def test_product2(self):
        # TODO: update test to reflect new product function
        histA = Histogram({0:1, 2:1, 3:2})
        histB = Histogram({2:1, 3:1, 5:1})
        n_choices = 0
        new_hist = histA.product_combine(histB, n_choices)

        self.assertEqual(histA.histogram_dict, {0:1, 2:1, 3:2})
        self.assertEqual(histB.histogram_dict, {2:1, 3:1, 5:1})
        self.assertEqual(new_hist.histogram_dict, {2:1, 3:1, 4:1, 5:4, 6:2, 7:1, 8:2})
