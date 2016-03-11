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
        """
        Get all tracks define by camera id
        :return: all_tracks in list
        """
        sql = 'SELECT DISTINCT CAM_ID FROM tracks;'
        self.c.execute(sql)
        all_tracks = self.c.fetchall()
        return all_tracks

    def insert_track(self, cam_id):
        """
        <track>
            <clipitem id="0301_280_a_d02_cam20264_01 "></clipitem>
            <clipitem id="0301_280_a03_cam20264_01 "></clipitem>
            ... ...
            <clipitem id="0301_280_a02_cam20264_02 "></clipitem>
            <enabled>TRUE</enabled>
            <locked>FALSE</locked>
        </track>
        """
        track = ET.SubElement(self.video_node, 'track')
        # self.video_node.append(ET.Element("child2"))
        # self.video_node.append(ET.Element('track'))
        clips = self.c.execute('SELECT cam_id, tc, duration, fullpath '
                               'FROM tracks WHERE cam_id=?;', cam_id)
        ET.SubElement(track, 'clipitem')
        for clip in clips:
            print clip

    def insert_clipitem(self):
        # root = ET.fromstring("<fruits><fruit>banana</fruit><fruit>apple</fruit></fruits>""")
        clip_sample_xml = """
<clipitem id="0301_280_a_d02_cam20264_01 ">
    <name>0301_280_a_d02_cam20264_01</name>
    <duration>293</duration>
    <rate>
        <ntsc>FALSE</ntsc>
        <timebase>25</timebase>
    </rate>
    <in>0</in>
    <out>293</out>
    <start>0</start>
    <end>293</end>
    <pixelaspectratio>Square</pixelaspectratio>
    <anamorphic>FALSE</anamorphic>
    <alphatype>none</alphatype>
    <masterclipid>0301_280_a_d02_cam20264_01 1</masterclipid>
    <file id="0301_280_a_d02_cam20264_01 2">
        <name>0301_280_a_d02_cam20264_01.mov</name>
        <pathurl>file://localhost/git-repos/melissa/input/160303/ep01/01_video/20160301/280/0301_280_a_003/0301_280_a_d02_cam20264_01.mov</pathurl>
        <rate>
            <timebase>25</timebase>
        </rate>
        <duration>293</duration>
        <timecode>
            <rate>
                <timebase>25</timebase>
            </rate>
            <string>14:19:55:00</string>
            <frame>1289875</frame>
            <displayformat>NDF</displayformat>
            <source>source</source>
        </timecode>
        <media>
            <video>
                <duration>293</duration>
                <samplecharacteristics>
                    <width>1920</width>
                    <height>1080</height>
                </samplecharacteristics>
            </video>
        </media>
    </file>
    <sourcetrack>
        <mediatype>video</mediatype>
    </sourcetrack>
    <fielddominance>none</fielddominance>
</clipitem>"""
        self.video_node.append(ET.Element("child1"))

    def create_xml(self):
        tracks = self.get_tracks()
        for track in tracks:
            self.insert_track(track)
        print ET.tostring(self.base_tree, pretty_print=True)


if __name__ == '__main__':
    fcpxml = FcpXML()
    fcpxml.create_xml()
