'''
A Python module for parsing Newick files.

Copyright (C) 2003-2008, Thomas Mailund <mailund@birc.au.dk>
'''

from lexer  import LexerError
from parser import *
from tree   import parse_tree

if __name__ == '__main__':
    import tokens
    from lexer  import *

    print "Testing lexer...",
    lexer = Lexer("()'foo' bar :0.00,;")
    lexer.read_token(tokens.LParen)
    lexer.read_token(tokens.RParen)
    id = lexer.read_token(tokens.ID)
    if id.get_name() != 'foo':
        raise "Unexpected name!"
    id = lexer.read_token(tokens.ID)
    if id.get_name() != 'bar':
        raise "Unexpected name!"
    lexer.read_token(tokens.Colon)
    n = lexer.read_token(tokens.Number)
    if n.get_number() != 0.00:
        raise "Unexpected number!"
    lexer.read_token(tokens.Comma)
    lexer.read_token(tokens.SemiColon)
    print "Done"

    print "Testing parse...",
    import parser
    import tree
    lexer = Lexer("(('foo' : 0.1, 'bar' : 1.0) : 2, baz)")
    handler = tree._TreeBuilder()
    p = parser._Parser(lexer,handler)
    p.parse()
    t = handler.get_result()

    if len(t.get_edges()) != 2:
        raise "Unexpected number of edges"
    [(t1,b1,l1), (t2,b2,l2)] = t.get_edges()
    if len(t1.get_edges()) != 2:
        raise "Unexpected number of edges"
    if l1 != 2.0:
        raise "Unexpected edge length"

    if t2.__class__ != tree.Leaf:
        raise "Leaf expected"
    if l2 != None:
        raise "Unexpected edge length"


    t = tree.parse_tree("(('foo' : 0.1, 'bar' : 1.0) : 2, baz)")

    if len(t.get_edges()) != 2:
        raise "Unexpected number of edges"
    [(t1,b1,l1), (t2,b2,l2)] = t.get_edges()
    if len(t1.get_edges()) != 2:
        raise "Unexpected number of edges"
    if l1 != 2.0:
        raise "Unexpected edge length"

    if t2.__class__ != tree.Leaf:
        raise "Leaf expected"
    if l2 != None:
        raise "Unexpected edge length"



    class BranchLengthSum(AbstractHandler):
        def __init__(self):
            self.sum = 0.0

        def new_edge(self,bootstrap,length):
            if length:
                self.sum += length

        def get_sum(self):
            return self.sum

    lexer = Lexer("(('foo' : 0.1, 'bar' : 1.0) : 2, baz)")
    handler = BranchLengthSum()
    p = parser._Parser(lexer,handler)
    p.parse()
    sum = handler.get_sum()

    if sum != 3.1:
        raise "Unexpected sum"

    from tree import parse_tree
    tree = parse_tree("(B,(A,C,E),D);")
    #print tree
    tree = parse_tree("(,(,,),);")
    #print tree
    tree = parse_tree("(_,(_,_,_),_);")
    #print tree

    tree = parse_tree("""
(
  ('Chimp':0.052625,
   'Human':0.042375):0.007875,
  'Gorilla':0.060125,
  ('Gibbon':0.124833,
   'Orangutan':0.0971667):0.038875
);
    """)

    tree = parse_tree("""
(
  ('Chimp':0.052625,
   'Human':0.042375) 0.71 : 0.007875,
  'Gorilla':0.060125,
  ('Gibbon':0.124833,
   'Orangutan':0.0971667) 1.00 :0.038875
);
    """)

    print "Done"

    print "Testing tree... ",
    t = parse_tree('((A,B),C);')
    assert t.leaves_ids == ['A','B','C']
    assert t.leaves     != ['A','B','C']

    from tree import add_parent_links
    add_parent_links(t)
    assert [str(l.parent) for l in t.leaves] == \
           ["('A', 'B')", "('A', 'B')", "(('A', 'B'), 'C')"]

    from tree import add_distance_from_root
    add_distance_from_root(t)
    assert [l.distance_from_root for l in t.leaves] == [0,0,0]

    t = parse_tree('((A:2,B:3):1,C:6);')
    add_distance_from_root(t)
    assert [l.distance_from_root for l in t.leaves] == [3,4,6]

    print "Done"

    
