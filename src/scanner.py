#!/usr/bin/env python
from __future__ import division

import json
import os
import re
import sqlite3
import subprocess

from config import CLIP_FILTER
from config import DB_FILE
from config import FRAMERATE
from timecode import Timecode

REG_CAM_ID = '^(\d{4}_[a-zA-Z0-9]+)(_[a-zA-Z]{1}|_[a-zA-Z]{2,})?(_\d{2})$'


'''
COMMAND: ffmpeg change timecode
ffmpeg -i [SourcePath] -vcodec copy -acodec copy -timecode 1:23:45:01 [DestPath]
'''


def read_clip_meta(clip):
    """
    Use command get clip meta:
    ffprobe -print_format json -show_format -show_streams [SourcePath]
    """
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
               '-show_format', '-show_streams', clip]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        data = json.loads(proc.communicate()[0])
        data_needed = dict()
        for stream in data['streams']:
            if stream.get('codec_type') == 'video' and \
                            stream.get('r_frame_rate') == '25/1':
                # Some of the stream doesn't has a timecode key
                tc_in = stream['tags'].get('timecode')
                if not tc_in:
                    tc_in = data['format']['tags']['timecode']
                data_needed.update({
                    'tc_in': tc_in,
                    'duration': stream['duration'],
                    'meta': data, })
            elif stream.get('codec_type') == 'audio':
                data_needed.update({'audio': stream.get('codec_time_base')})
        if not data_needed.get('audio'):
            data_needed.update({'audio': 'N/A'})
        return data_needed
    except Exception:
        print 'No data extraced from mov file.'
        return None


def get_tracks(curser):
        """
        Get all tracks defined by camera id
        :return: all_tracks in list
                [(u'0301_280_03',), (u'0301_280_03_overlap',), ]
        """
        # TODO get all tracks defined by track_idx
        sql = 'SELECT DISTINCT TRACK_ID FROM tracks ORDER BY TRACK_ID;'
        curser.execute(sql)
        all_tracks = curser.fetchall()
        return all_tracks


class Scanner(object):

    def __init__(self):
        print 'Initial clip database: {0}'.format(DB_FILE)
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.build_db()
        self.all_clip_paths = []

    def build_db(self):
        self.c.execute('DROP TABLE IF EXISTS TRACKS;')
        """
        CAM_ID: Camera name
        TRACK_ID: ID for each tracks, to distinguish them from each other
        TRACK_IDX: Track index for genxml to guild tracks sequentially.
        TC_IN: in point, get from the metadata
        TC_OUT: out point, calculated
        DURATION: duration in the metadata
        FIR_F: first frame calculated by timecode, map to fcp xml <start>
        LAST_F: last frame calculated by `first frame` + `duration`, map to
                fcp xml <end>
        META: all metadata
        FULLPATH: file full path on disk
        AUDIO: save the audio codec time base if file have a audio
        """
        self.c.execute('CREATE TABLE TRACKS'
                       '(ID       INTEGER  PRIMARY KEY AUTOINCREMENT,'
                       'CAM_ID    CHAR(100)            NOT NULL,'
                       'TRACK_ID  CHAR(100),'
                       'TRACK_IDX INT,'
                       'TC_IN     CHAR(11)             NOT NULL,'
                       'TC_OUT    CHAR(11)             NOT NULL,'
                       'FIR_F     INT                  NOT NULL,'
                       'LAST_F    INT                  NOT NULL,'
                       'DURATION  INT                  NOT NULL,'
                       'META      TEXT                 NOT NULL,'
                       'FULLPATH  CHAR(300)            NOT NULL,'
                       'AUDIO     CHAR(18));')
        self.conn.commit()

    # TODO use dict pass parameters
    def insert_record(self, cam_id, tc_in, duration, meta, fullpath, audio):
        """When initiate, track_id = cam_id, then use rebuild_track() put
        overlap clip into the second track
        """
        fir_f = Timecode(FRAMERATE, tc_in).frames
        last_f = fir_f + duration
        tc_out = Timecode(FRAMERATE, frames=last_f-1)
        track_id = cam_id
        sql = ('INSERT INTO TRACKS (CAM_ID,TRACK_ID,TC_IN,TC_OUT,FIR_F,LAST_F,'
               'DURATION,META,FULLPATH, AUDIO) '
               'VALUES ("{CAM_ID}","{TRACK_ID}","{TC_IN}","{TC_OUT}",'
               '"{FIR_F}","{LAST_F}","{DURATION}","{META}","{FULLPATH}",'
               '"{AUDIO}");'.
               format(CAM_ID=cam_id, TRACK_ID=track_id, TC_IN=tc_in,
                      TC_OUT=tc_out, FIR_F=fir_f, LAST_F=last_f,
                      DURATION=duration, META=meta, FULLPATH=fullpath,
                      AUDIO=audio))
        self.c.execute(sql)

    def rebuild_tracks(self):
        tracks = get_tracks(self.c)
        for track in tracks:
            self.c.execute(
                'SELECT id, fir_f, last_f, track_id, fullpath '
                'FROM tracks WHERE track_id=? ORDER BY fir_f;',
                track)
            all_clips = self.c.fetchall()
            overlay_clips = []
            # data: (id, fir_f, last_f, track_id)
            for idx, clip in enumerate(all_clips):
                if idx is not 0:
                    # Compare current clip in-point with the out-point of last
                    # clip.
                    last_clip = all_clips[idx-1]
                    if clip[1] <= last_clip[2]:
                        fullpath = clip[-1]
                        print "Timecode duplicated:", fullpath
                        overlay_clips.append(clip)
            # Update track_id in database
            for clip in overlay_clips:
                track_id = clip[3]
                new_track = track_id + '_overlap'
                id = clip[0]
                sql = ('UPDATE TRACKS SET track_id = "{new_track}" '
                       'WHERE ID = "{id}";'.format(new_track=new_track, id=id))
                self.c.execute(sql)
        # After update the overlap tracks, get all tracks again to update track
        # index - the TRACK_IDX column in the database
        tracks = get_tracks(self.c)
        for index, track in enumerate(tracks):
            sql = ('UPDATE TRACKS SET track_idx = {track_idx} WHERE '
                   'track_id = "{track_id}";'.format(track_idx=index+1,
                                                     track_id=track[0]))
            self.c.execute(sql)
        self.conn.commit()

    def scan(self, path):
        for path, subdirs, files in os.walk(path):
            m = re.match(REG_CAM_ID, os.path.basename(path))
            if m:
                if m.group(2) is None or len(m.group(2)) == 2:
                    camera_id = m.group(1) + m.group(3)
                elif m.group(2) > 2:
                    camera_id = m.group(1) + m.group(2) + m.group(3)
                for file in files:
                    extension = os.path.splitext(file)[1]
                    if not file.startswith('.') and \
                                    extension.lower() in CLIP_FILTER:
                        fullpath = os.path.join(path, file)
                        data = read_clip_meta(fullpath)
                        if data:
                            frames = int(float(data['duration']) * FRAMERATE)
                            self.insert_record(cam_id=camera_id,
                                               tc_in=data['tc_in'],
                                               duration=frames,
                                               meta=data,
                                               fullpath=fullpath,
                                               audio=data['audio'])
                            print('Insert clip: {0}'.format(fullpath))
                        else:
                            print("Warning!, {0} is not recognizable.".
                                  format(fullpath))

    def scan_all_clips(self, path):
        """Scan all clip file the `path`"""
        all_clip_paths = []
        for path, subdirs, files in os.walk(path):
            for file in files:
                extension = os.path.splitext(file)[1]
                if not file.startswith('.') and \
                        extension.lower() in CLIP_FILTER:
                    fullpath = os.path.join(path, file)
                    all_clip_paths.append(fullpath)
        self.all_clip_paths = all_clip_paths

if __name__ == '__main__':
    path = '/2T/Downloads/my-projects/1102_280_d_05/'
    scanner = Scanner()
    scanner.scan(path)
    scanner.rebuild_tracks()
    scanner.scan_all_clips(path)
    print scanner.all_clip_paths
