from clumpr import DTLReconGraph
import unittest

class EdgeTreeTraversalTestCase(unittest.TestCase):
    """
    Creates an edge tree:
         [Top]
           |
          'A'
          / \
       'B'  'C'
       / \
    'D'  'E'

    Preorder:  Top-A A-B B-D B-E A-C
    Postorder: B-D B-E A-B A-C Top-A
    """
    def setUp(self):
        self.tree = {
            ('Top', 'A'): ('Top', 'A', ('A', 'B'), ('A', 'C')),
            ('A', 'B'): ('A', 'B', ('B', 'D'), ('B', 'E')),
            ('A', 'C'): ('A', 'C', None, None),
            ('B', 'D'): ('B', 'D', None, None),
            ('B', 'E'): ('B', 'E', None, None)
        }

    def test_preorder(self):
        result = list(DTLReconGraph.preorder(self.tree, ('Top', 'A')))
        expected = [('Top', 'A'), ('A', 'B'), ('B', 'D'), ('B', 'E'), ('A', 'C')]
        self.assertEqual(result, expected)

    def test_postorder(self):
        result = list (DTLReconGraph.postorder(self.tree, ('Top', 'A')))
        expected = [('B', 'D'), ('B', 'E'), ('A', 'B'), ('A', 'C'), ('Top', 'A')]
        self.assertEqual(result, expected)

