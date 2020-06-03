'''
A Python module for parsing Newick files.

Copyright (C) 2003-2008, Thomas Mailund <mailund@birc.au.dk>

This module contains the functionality for grammatical analysis.

[20081024]
        - wcc: modified to handle cases like (xxx):0.00 by
          adding bootstrap and length attribs to the root node directly

'''

import tokens

class ParserError:
    '''Exception thrown if the parser encounters an error.'''
    def __init__(self,err):
        self.err = err

    def __repr__(self):
        return "ParserError: "+self.err


class AbstractHandler:
    '''Interface (and NO-OP implementations) of event handlers for
    parsing trees.  A handler can be used for extracting information
    from a tree without explicitly representing the tree in a
    datastructure.'''
   
    def new_tree_begin(self):
        '''Callback called when the parsing begins.'''
        pass
    def new_tree_end(self, name = None):
        # wcc: add internal label
        '''Callback called when the tree is completely parsed.'''
        pass

    def new_edge(self, bootstrap, length):
        '''Callback called when a new edge is parsed.  Bootstrap value
        and length is given if these are parsed, otherwise these are
        None.'''
        pass
    def new_leaf(self, name):
        '''Callback called when a leaf is passed.  A name is always
        provided, although it can be the empty string if an identifier
        was not explicitly given in the input.'''
        pass

class _Parser:
    '''State of the parser during parsing.  Should not be used
    directly by users of this package.'''

    def __init__(self, lexer, handler):
        self.lexer = lexer
        self.handler = handler

    def parse(self):
        result = None
        if self.lexer.peek_token(tokens.LParen):
            result = self.parse_node()
        else:
            result = self.parse_leaf()

        # wcc: normally a tree should ends here
        # but we left the last edge from the root unhandled...
        # wcc: ? what if there is a comment right at this point?
        if self.lexer.peek_token(tokens.Colon):
            self.parse_edge()

        remaining = self.lexer.remaining()
        if remaining != '' and not self.lexer.peek_token(tokens.SemiColon):
            raise ParserError("Unexpected token following tree: " +
                              self.lexer.remaining())
        return result

    def parse_node(self):
        ''' Parse node on the form ( <edge list> ) '''
        self.lexer.read_token(tokens.LParen)
        self.handler.new_tree_begin()
        self.parse_edge_list()
        self.lexer.read_token(tokens.RParen)
        # wcc: to add internal labeling
        if self.lexer.peek_token(tokens.ID):
            id = self.lexer.read_token(tokens.ID).get_name()
        else:
            id = ''
        self.handler.new_tree_end(id)

    def parse_leaf(self):
        ''' Parse a node on the form "id" '''
        if self.lexer.peek_token(tokens.Comma) or \
               self.lexer.peek_token(tokens.RParen):
            # blank name
            self.handler.new_leaf("")
            return

        # special case for when the id is just a number
        if self.lexer.peek_token(tokens.Number):
            id = str(int(self.lexer.read_token(tokens.Number).get_number()))
            self.handler.new_leaf(id)
            return
            
        id = self.lexer.read_token(tokens.ID).get_name()
        if id == '_':
            # blank name
            self.handler.new_leaf('')
        else:
            self.handler.new_leaf(id)

        
    def parse_edge_list(self):
        ''' parse a comma-separated list of edges. '''
        while 1:
            self.parse_edge()

            if self.lexer.peek_token(tokens.Comma):
                self.lexer.read_token(tokens.Comma)
            # wcc: ?
            # tokens.ID includes everything but numbers
            # how about )?
            elif self.lexer.peek_token(tokens.ID):
                continue
            else:
                break
               

    def parse_edge(self):
        ''' Parse a single edge, either
        leaf [bootstrap] [: branch-length] or
        tree [bootstrap] [: branch-length]. '''
        if self.lexer.peek_token(tokens.LParen):
            self.parse_node()
        elif self.lexer.peek_token(tokens.ID):
            # wcc: only parse_leaf if it's an ID
            self.parse_leaf()

        if self.lexer.peek_token(tokens.Number):
            bootstrap = self.lexer.read_token(tokens.Number).get_number()
        else:
            bootstrap = None

        if self.lexer.peek_token(tokens.Colon):
            self.lexer.read_token(tokens.Colon)
            length = self.lexer.read_token(tokens.Number).get_number()
        else:
            length = None

        self.handler.new_edge(bootstrap,length)


def parse(input, event_handler):
    '''Parse input and invoke callbacks in event_handler.  If
    event_handler implements a get_result() method, parse will return
    the result of calling this after complete parsing, otherwise None
    is returned.'''
    import lexer
    l = lexer.Lexer(input)
    _Parser(l,event_handler).parse()
    if hasattr(event_handler,"get_result"):
        return event_handler.get_result()
    

    
