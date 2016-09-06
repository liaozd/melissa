#!/usr/bin/env python


import os
import sqlite3
import uuid

import time
from timecode import Timecode

from lxml import etree as ET

from config import DB_FILE, FRAMERATE, CLIP_SAMPLE_XML
from scanner import get_tracks

parser = ET.XMLParser(remove_blank_text=True)
xml_template = os.path.join(os.path.dirname(__file__), 'template.xml')


def dict_factory(cursor, row):
    dict = {}
    for idx, col in enumerate(cursor.description):
        dict[col[0]] = row[idx]
    return dict


def get_columns(curser, table='tracks'):
    """ Returns columns of the table in list
    """
    curser.execute('PRAGMA TABLE_INFO({})'.format(table))
    info = curser.fetchall()
    columns = []
    for col in info:
        columns.append(col[1])
    return columns


class FcpXML(object):
    def __init__(self, xml_output='output.xml', xml_template=xml_template):
        print 'Read database: {0}'.format(DB_FILE)
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.xml_output = xml_output
        # The `parser` will allow the parser to drop blank text nodes when
        # constructing the tree. If you now call a serialization function to
        # pretty print this tree, lxml can add fresh whitespace to the XML
        # tree to indent it.
        self.base_tree = ET.parse(xml_template, parser)
        self.sequence = self.base_tree.find('sequence')
        self.video_node = self.sequence.find('media').find('video')
        self.timeline_first = self.c.execute(
            'SELECT fir_f FROM tracks ORDER BY fir_f LIMIT 1;').fetchone()[0]
        self.timeline_last = self.c.execute(
            'SELECT last_f FROM tracks ORDER BY last_f DESC LIMIT 1;').\
            fetchone()[0]
        self.columns = get_columns(self.c)
        self.update_xml_header()

    def update_xml_header(self):
        duration = self.timeline_last - self.timeline_first
        string, frame = self.c.execute(
            'SELECT tc_in, fir_f FROM tracks ORDER BY fir_f LIMIT 1;').\
            fetchone()
        self.sequence.find('uuid').text = str(uuid.uuid1())
        self.sequence.find('duration').text = str(duration)
        timecode_node = self.sequence.find('timecode')
        timecode_node.find('string').text = string
        timecode_node.find('frame').text = str(frame-1)
        # TODO update duration from by db info

    def insert_track(self, track_id):
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

        self.c.execute(
            'SELECT id, track_id, tc_in, duration, fir_f, last_f, fullpath '
            'FROM tracks WHERE track_id=? ORDER BY fir_f;',
            track_id)
        clips = self.c.fetchall()
        # TODO use dict to store sql data

        for clip in clips:
            data = dict()
            data['id'] = clip[0]
            data['track_id'] = clip[1]
            data['tc_in'] = clip[2]
            data['duration'] = clip[3]
            data['fir_f'] = clip[4]
            data['last_f'] = clip[5]
            data['path'] = clip[6]
            self.insert_clipitem(track, data)

        node_enabled = ET.Element('enabled')
        node_enabled.text = 'TRUE'
        node_locked = ET.Element('locked')
        node_locked.text = 'FALSE'
        track.append(node_enabled)
        track.append(node_locked)

    def insert_clipitem(self, track, data):
        id = data['id']
        filename = os.path.basename(data['path'])
        name = os.path.splitext(filename)[0]
        duration = data['duration']
        start = data['fir_f'] - self.timeline_first
        end = data['last_f'] - self.timeline_first
        masterclipid = name + ' ' + str(id)
        # fixme(maybe problem here)
        pathurl = 'file://localhost' + data['path']

        clipitem = ET.fromstring(CLIP_SAMPLE_XML, parser)
        clipitem.attrib['id'] = name + ' '
        clipitem.find('name').text = name
        clipitem.find('duration').text = str(duration)
        clipitem.find('out').text = str(duration)
        clipitem.find('start').text = str(start)
        clipitem.find('end').text = str(end)
        clipitem.find('masterclipid').text = masterclipid

        clipitem_file = clipitem.find('file')
        clipitem_file.attrib['id'] = name + ' 2'
        clipitem_file.find('name').text = filename
        clipitem_file.find('pathurl').text = pathurl
        clipitem_file.find('duration').text = str(duration)

        file_timcode = clipitem_file.find('timecode')
        file_timcode.find('string').text = data['tc_in']
        frame = Timecode(FRAMERATE, data['tc_in']).frames - 1
        file_timcode.find('frame').text = str(frame)

        file_media = clipitem_file.find('media')
        media_video = file_media.find('video')
        media_video.find('duration').text = str(duration)
        track.append(clipitem)

    def create_xml(self):
        tracks = get_tracks(self.c)
        for track in tracks:
            self.insert_track(track)
        output_folder = os.path.join(os.environ['HOME'], 'Desktop/melissa')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        timestr = time.strftime("%Y%m%d")
        output_name = 'output_' + timestr + '.xml'
        output = os.path.join(output_folder, output_name)
        self.base_tree.write(output, pretty_print=True, xml_declaration=True,
                             encoding='UTF-8')
        print 'Create XML: ', output


if __name__ == '__main__':
    fcpxml = FcpXML()
    fcpxml.create_xml()
