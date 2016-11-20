#!/usr/bin/env python

import getopt
import sys

from readxml import XmlReader
from scanner import Scanner


def usage():
    print('''Usage:
    timeline-check.py final-cut-sync.xml''')


def main(argv):
    if len(argv) == 1 or len(argv) > 2:
        usage()
        sys.exit(2)
    try:
        xml_path = argv[1]
        xml_reader = XmlReader(xml_path)
        xml_reader.get_all_clip_paths()
        common_path = xml_reader.get_common_path()
        print common_path
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv)
