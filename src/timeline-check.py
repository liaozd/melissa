#!/usr/bin/env python

import csv
import getopt
import sqlite3
import sys

from config import DB_FILE
from config import OUTPUT_FOLDER
from readxml import XmlReader
from scanner import Scanner
from utils.path import get_normalized_path
from utils.path import get_output_file_path


def usage():
    print('''Usage:
    timeline-check.py final-cut-sync.xml''')


def get_clip_in_db_fullpaths(curser):
    """Collect all clip paths in db"""
    curser.execute('SELECT DISTINCT fullpath FROM tracks;')
    clips = curser.fetchall()
    return [clip[0] for clip in clips]


class TimelineChecker(object):
    def __init__(self):
        print('Read database: {0}'.format(DB_FILE))
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.clip_db_fullpaths = get_clip_in_db_fullpaths(self.c)

    def check_missing_clips(self, clips_in_path, clips_in_xml):
        """Compare clips_in_xml with clip_fullpaths in db, and generate a
        csv report."""
        if len(clips_in_xml) < len(self.clip_db_fullpaths):
            print("Warning: missing clips in time line.")
        output = get_output_file_path(OUTPUT_FOLDER,
                                      filename='timeline_check_report',
                                      extension='.csv')
        with open(output, 'wb') as csvfile:
            fieldnames = ['Tree', 'go.py XML', 'XML']
            report_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            report_writer.writeheader()
            for clip in clips_in_path:
                row_to_insert = {'Tree': clip, }
                if clip not in self.clip_db_fullpaths:
                    row_to_insert.update({'go.py XML': 'Missing'})
                if clip not in clips_in_xml:
                    row_to_insert.update({'XML': 'Missing'})
                report_writer.writerow(row_to_insert)


def main(argv):
    if len(argv) == 1 or len(argv) > 2:
        usage()
        sys.exit(2)
    try:
        xml_path = argv[1]
        xml = XmlReader(xml_path)
        path_to_scan = get_normalized_path(xml.common_path)
        scanner = Scanner()
        scanner.scan(path_to_scan)
        scanner.rebuild_tracks()
        scanner.scan_all_clips(path_to_scan)
        for path in xml.clips_in_xml:
            print(path)
        checker = TimelineChecker()
        checker.check_missing_clips(
            scanner.all_clip_paths,
            xml.clips_in_xml)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv)
