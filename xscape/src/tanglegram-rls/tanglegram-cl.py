#! /usr/bin/env python
"""
$Id$

A short program to handle command line tanglegram crossing calculaiton.

Contact:
Wen-Chieh Chang
wcchang@iastate.edu
"""
from __future__ import with_statement   # in case python2.5

import tanglegram
import newick
import newick_utils

import sys



def main():

    from optparse import OptionParser

    #if len(sys.argv) == 1:
    #    print "Usage: %s [options] <host.tre> <parasite.tre>" % sys.argv[0]
    #    sys.exit()

    #else:
    
    parser = OptionParser(usage="%prog [options] <t1.tre> <t2.tre>")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose mode")

    parser.add_option("--ah", action="store_true", dest="ah",
                      help="execute AH heuristic")

    parser.add_option("--lh", action="store_true", dest="lh",
                      help="execute LH heuristic")

    parser.add_option("--lah", action="store_true", dest="lah",
                      help="execute LAH heuristic")


    (options, args) = parser.parse_args()

    if options.verbose:
        print options, args

    if len(args) < 2:
        parser.print_help()
        parser.exit()

    tHost, tPara = None, None

    with open(args[0], 'r') as fHost:
        tHost = newick.tree.parse_tree(fHost.readline())

    with open(args[1], 'r') as fPara:
        tPara = newick.tree.parse_tree(fPara.readline())


    if options.verbose:
        print tHost
        print tPara

    newick_utils.newick_leaf_map(tHost, tPara)

    if options.lh:
        result = tanglegram.tanglegram2TH (tHost, tPara, optimize="MIN_MOD", solver="LIST", verbose=options.verbose)
        print "Local Heuristic crossing: %d" % result[0]
        print "Iterations: %d" % result[3]
        print "Arranged host: %s" % result[1]
        print "Arranged parasite: %s" % result[2]

    if options.ah:
        result = tanglegram.tanglegram2TA(tHost, tPara, optimize="MIN_MOD", solver="LIST", verbose=options.verbose)
        print "Alternating Heuristic crossing: %d" % result[0]
        print "Iterations: %d" % result[3]
        print "Arranged host: %s" % result[1]
        print "Arranged parasite: %s" % result[2]

    if options.lah:
        result = tanglegram.tanglegram2TAH(tHost, tPara, optimize="MIN_MOD", solver="LIST", verbose=options.verbose)
        print "Local Alternating Heuristic crossing: %d" % result[0]
        print "Iterations: %d" % result[3]
        print "Arranged host: %s" % result[1]
        print "Arranged parasite: %s" % result[2]



if __name__ == '__main__':
    main()
