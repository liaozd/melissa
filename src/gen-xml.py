#!/usr/bin/env python

import sqlite3

from lxml import etree as ET

from config import DB_FILE


class FcpXML(object):

    def __init__(self, xml_output='output.xml'):
        print 'Read database: {0}'.format(DB_FILE)
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.xml_output = xml_output

    def create_xml_header(self):
        pass

    def insert_clip(self):
        pass

    def write_to_xml(self):
        root = ET.Element('s')

if __name__ == '__main__':
    fcpxml = FcpXML()
    fcpxml.write_to_xml()
