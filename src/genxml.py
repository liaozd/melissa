#!/usr/bin/env python

import os
import sqlite3
import uuid
from config import AUDIO_CLIP_TEMPLATE
from config import AUDIO_NODE_INSIDE_VIDEO
from config import DB_FILE
from config import FRAMERATE
from config import LINK_TEMPLATE
from config import OUTPUT_FOLDER
from config import VIDEO_CLIP_TEMPLATE

from lxml import etree as ET
from timecode import Timecode

from scanner import get_tracks
from utils.path import get_output_file_path

parser = ET.XMLParser(remove_blank_text=True)
xml_template = os.path.join(os.path.dirname(__file__), 'template.xml')


def get_columns(curser, table='tracks'):
    """ Returns columns of the table in list
    """
    curser.execute('PRAGMA TABLE_INFO({})'.format(table))
    info = curser.fetchall()
    columns = []
    for col in info:
        columns.append(col[1])
    return columns


def get_clips(curser, track_id):
    curser.execute(
        'SELECT id, track_id, tc_in, duration, fir_f, last_f, fullpath,'
        'track_idx, audio FROM tracks WHERE track_id=? ORDER BY fir_f;',
        track_id)
    clips = curser.fetchall()
    # TODO use dict to store sql data
    return clips


def insert_links(clip_idx, name, track_idx):
    root = ET.fromstring(LINK_TEMPLATE, parser)
    # Video link
    root[0].find('linkclipref').text = name + ' '
    root[0].find('trackindex').text = str(track_idx)
    root[0].find('clipindex').text = str(clip_idx)

    # Two audio links
    root[1].find('linkclipref').text = name + ' 2'
    root[1].find('trackindex').text = str(track_idx*2-1)
    root[1].find('clipindex').text = str(clip_idx)

    root[2].find('linkclipref').text = name + ' 3'
    root[2].find('trackindex').text = str(track_idx*2)
    root[2].find('clipindex').text = str(clip_idx)
    return root.getchildren()


def get_clip_data(clip):
    data = dict()
    data['id'] = clip[0]
    data['track_id'] = clip[1]
    data['tc_in'] = clip[2]
    data['duration'] = clip[3]
    data['fir_f'] = clip[4]
    data['last_f'] = clip[5]
    data['fullpath'] = clip[6]
    data['track_idx'] = clip[7]
    data['audio'] = clip[8]
    return data


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
        self.audio_node = self.sequence.find('media').find('audio')
        self.timeline_first = self.c.execute('SELECT fir_f FROM tracks ORDER BY fir_f LIMIT 1;').fetchone()[0]
        self.timeline_last = self.c.execute('SELECT last_f FROM tracks ORDER BY last_f DESC LIMIT 1;').fetchone()[0]
        self.columns = get_columns(self.c)
        self.update_xml_header()

    def update_xml_header(self):
        duration = self.timeline_last - self.timeline_first
        string, frame = self.c.execute('SELECT tc_in, fir_f FROM tracks ORDER BY fir_f LIMIT 1;').fetchone()
        self.sequence.find('uuid').text = str(uuid.uuid1())
        self.sequence.find('duration').text = str(duration)
        timecode_node = self.sequence.find('timecode')
        timecode_node.find('string').text = string
        timecode_node.find('frame').text = str(frame-1)
        # TODO update duration from by db info

    def insert_video_track(self, track_id, track_idx):
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

        # TODO use dict to store sql data
        clips = get_clips(self.c, track_id)

        for clip_idx, clip in enumerate(clips):
            data = get_clip_data(clip)
            self.insert_video_clip(track, data, clip_idx+1, track_idx)

        node_enabled = ET.Element('enabled')
        node_enabled.text = 'TRUE'
        node_locked = ET.Element('locked')
        node_locked.text = 'FALSE'
        track.append(node_enabled)
        track.append(node_locked)

    def insert_video_clip(self, track, data, clip_idx, track_idx):
        # Cook all the data for inserting
        # id = data['id']
        filename = os.path.basename(data['fullpath'])
        name = os.path.splitext(filename)[0]
        duration = data['duration']
        start = data['fir_f'] - self.timeline_first
        end = data['last_f'] - self.timeline_first
        pathurl = 'file://localhost' + data['fullpath']
        track_idx = data['track_idx']

        clipitem = ET.fromstring(VIDEO_CLIP_TEMPLATE, parser)
        clipitem.attrib['id'] = name + ' '
        clipitem.find('name').text = name
        clipitem.find('duration').text = str(duration)
        clipitem.find('out').text = str(duration)
        clipitem.find('start').text = str(start)
        clipitem.find('end').text = str(end)

        # <file id=""> node
        clipitem_file = clipitem.find('file')
        clipitem_file.attrib['id'] = name + ' 1'
        clipitem_file.find('name').text = filename
        clipitem_file.find('pathurl').text = pathurl
        clipitem_file.find('duration').text = str(duration)

        # <file.timecode> node
        file_timcode = clipitem_file.find('timecode')
        file_timcode.find('string').text = data['tc_in']
        frame = Timecode(FRAMERATE, data['tc_in']).frames - 1
        file_timcode.find('frame').text = str(frame)

        # <file.meida> node
        file_media = clipitem_file.find('media')
        media_video = file_media.find('video')
        media_video.find('duration').text = str(duration)

        # insert <audio> node if mov clip has sound
        if data['audio'] != 'N/A':
            audio_node = ET.fromstring(AUDIO_NODE_INSIDE_VIDEO, parser)
            file_media.append(audio_node)
            # insert 3 link nodes
            links = insert_links(clip_idx, name, track_idx)
            for link in links:
                clipitem.append(link)

        track.append(clipitem)

    def insert_audio_track(self, track_id, offset):
        track = ET.SubElement(self.audio_node, 'track')

        # TODO use dict to store sql data
        clips = get_clips(self.c, track_id)

        for clip_idx, clip in enumerate(clips):
            data = get_clip_data(clip)
            if data['audio'] != u'N/A':
                self.insert_audio_clip(track, data, offset, clip_idx+1)

        node_enabled = ET.Element('enabled')
        node_enabled.text = 'TRUE'
        node_locked = ET.Element('locked')
        node_locked.text = 'FALSE'
        track.append(node_enabled)
        track.append(node_locked)

    def insert_audio_clip(self, track, data, offset, clip_idx):
        """Cook all the data for inserting"""
        filename = os.path.basename(data['fullpath'])
        name = os.path.splitext(filename)[0]
        duration = data['duration']
        start = data['fir_f'] - self.timeline_first
        end = data['last_f'] - self.timeline_first
        track_idx = data['track_idx']

        clipitem = ET.fromstring(AUDIO_CLIP_TEMPLATE, parser)
        clipitem.attrib['id'] = name + ' ' + str(offset+2)
        clipitem.find('name').text = name
        clipitem.find('duration').text = str(duration)
        clipitem.find('out').text = str(duration)
        clipitem.find('start').text = str(start)
        clipitem.find('end').text = str(end)
        clipitem_file = clipitem.find('file')
        clipitem_file.attrib['id'] = name + ' 1'
        # The `trackindex` inside `sourcetrack` determines the which sound track in file to be put on the timeline
        clipitem_sourcetrack = clipitem.find('sourcetrack')
        clipitem_sourcetrack.find('trackindex').text = str(offset+1)
        links = insert_links(clip_idx, name, track_idx)
        for link in links:
            clipitem.append(link)
        track.append(clipitem)

    def create_xml(self):
        """Create Final XML"""
        tracks = get_tracks(self.c)
        for track_idx, track_id in enumerate(tracks):
            self.insert_video_track(track_id, track_idx+1)
            # Sound tracks are always paired
            self.insert_audio_track(track_id, 0)
            self.insert_audio_track(track_id, 1)
        output = get_output_file_path(OUTPUT_FOLDER, filename='output', extension='.xml')
        self.base_tree.write(output, pretty_print=True, xml_declaration=True, encoding='UTF-8')


if __name__ == '__main__':
    fcpxml = FcpXML()
    fcpxml.create_xml()
