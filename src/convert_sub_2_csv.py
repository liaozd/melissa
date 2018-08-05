#!/usr/bin/env python

import getopt
import os
import sys
from lxml import etree as ET
from timecode import Timecode


class Sub2CSV(object):
    def __init__(self, xml_path=None):
        self.path = xml_path
        self.scan_path()

    def scan_path(self):
        for path, subdirs, files in os.walk(self.path):
            for _file in files:
                fullpath = os.path.join(path, _file)
                filename, file_extension = os.path.splitext(fullpath)
                if file_extension.lower() == '.xml':
                    try:
                        self.export_dialogs(filename, fullpath)
                    except Exception as e:
                        print e

    def export_dialogs(self, filename, xml_file_path):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        media = root.getchildren()[0].find('media')
        video = media.find('video')
        tracks = video.findall('track')
        output_file = filename + '.csv'
        output_file_object = open(output_file, 'w')
        for track in tracks:
            clipitems = track.findall('clipitem')
            for clipitem in clipitems:
                start = clipitem.find('start').text
                start_tc = Timecode('25', frames=int(start)+1).__repr__()
                end = clipitem.find('end').text
                end_tc = Timecode('25', frames=int(end)+1).__repr__()
                dialog = clipitem.find('name').text
                output_line = u','.join([start_tc, dialog, end_tc]).encode('utf-8').strip()
                output_file_object.write(output_line)
                output_file_object.write(os.linesep)
        output_file_object.close()
        print(output_file)


def usage():
    print '''Usage:
convert_sub_2_csv /path/to/movies/20160318
'''


def main(argv):
    if len(argv) == 1 or len(argv) > 2:
        usage()
        sys.exit(2)
    try:
        xmls_path = argv[1]
        Sub2CSV(xmls_path)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)


if __name__ == '__main__':
    xml_path = '/Users/liaozhuodi/Desktop/20180801/'
    xml = Sub2CSV(xml_path)
