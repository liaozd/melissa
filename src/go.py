#!/usr/bin/env python
import getopt
import sys

from scanner import Scanner
from genxml import FcpXML


def Usage():
    print '''Usage:
go /path/to/movies/20160318
'''


def main(argv):
    if len(argv) == 1 or len(argv) > 2:
        Usage()
        sys.exit(2)
    try:
        path = argv[1]
        scanner = Scanner()
        scanner.scan(path)
        scanner.rebuild_tracks()
        fcpxml = FcpXML()
        fcpxml.create_xml()
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv)
