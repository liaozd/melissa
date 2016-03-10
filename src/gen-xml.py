#!/usr/bin/env python

import sqlite3
import uuid

from lxml import etree as ET

from config import DB_FILE


class FcpXML(object):

    def __init__(self, xml_output='output.xml', xml_template='template.xml'):
        print 'Read database: {0}'.format(DB_FILE)
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.xml_output = xml_output
        self.base_tree = ET.parse(xml_template)
        self.sequence = self.base_tree.find('sequence')
        self.video_node = self.sequence.find('media').find('video')
        self.update_xml_header()

    def update_xml_header(self):
        self.sequence.find('uuid').text = str(uuid.uuid1())
        # TODO update duration from by db info

    def get_tracks(self):
        '''
        Get all tracks devided by camera ia
        :return: all_tracks in list
        '''
        sql = 'SELECT DISTINCT CAM_ID FROM tracks;'
        self.c.execute(sql)
        all_tracks = self.c.fetchall()
        return all_tracks

    def insert_track(self, cam_id):
        pass

    def insert_clip(self):
        self.video_node.append(ET.Element("child1"))

    def create_xml(self):
        tracks = self.get_tracks()
        for track in tracks:
            self.insert_track()
        print type(self.get_tracks())
        # print ET.tostring(self.base_tree, pretty_print=True)


if __name__ == '__main__':
    fcpxml = FcpXML()

    fcpxml.create_xml()
