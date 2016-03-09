#!/usr/bin/env python
from __future__ import division

import json
import os
import re
import sqlite3
import subprocess

from config import DB_FILE, FRAMERATE, CLIP_FILTER

REG_CAM_ID = '^\d{4}_[a-zA-Z0-9]+_\w+_\d{3}$'


'''
COMMAND: ffmpeg change timecode
ffmpeg -i [SourcePath] -vcodec copy -acodec copy -timecode 1:23:45:01 [DestPath]
'''


def read_clip_meta(clips):
    try:
        '''
        Use command get clip meta:
        ffprobe -print_format json -show_format -show_streams [SourcePath]
        '''
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
               '-show_format', '-show_streams', clips]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        data = json.loads(proc.communicate()[0])
        data_needed = {'timecode': data['streams'][0]['tags']['timecode'],
                       'duration': data['streams'][0]['duration'],
                       'all_meta': data,
                       }
        return data_needed
    except Exception:
        return None


class Scanner(object):

    def __init__(self):
        print 'Initial clip database: {0}'.format(DB_FILE)
        self.db = DB_FILE
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.c.execute('DROP TABLE IF EXISTS TRACKS;')
        self.c.execute('CREATE   TABLE    TRACKS'
                       '(ID      INTEGER  PRIMARY KEY AUTOINCREMENT,'
                       'CAM_ID   CHAR(100)            NOT NULL,'
                       'TC       CHAR(11)             NOT NULL,'
                       'DURATION INT                  NOT NULL,'
                       'ALLMETA  TEXT                 NOT NULL,'
                       'FULLPATH CHAR(300)            NOT NULL);')
        self.conn.commit()
        print "Create Database"

    def insert_record(self, cam_id, tc, duration, allmeta, fullpath):
        sql = ('INSERT INTO TRACKS (CAM_ID,TC,DURATION,ALLMETA,FULLPATH) '
               'VALUES '
               '("{CAM_ID}","{TC}","{DURATION}","{ALLMETA}","{FULLPATH}");'.
               format(CAM_ID=cam_id,
                      TC=tc, DURATION=duration, ALLMETA=allmeta,
                      FULLPATH=fullpath))
        self.c.execute(sql)

    def scan(self,
             path='/git-repos/melissa/input/160303/ep01/01_video/20160301'):
        for path, subdirs, files in os.walk(path):
            if re.search(REG_CAM_ID, os.path.basename(path)):
                camera_id_folder = os.path.basename(path)
                for file in files:
                    extension = os.path.splitext(file)[1]
                    if not file.startswith('.') and \
                                    extension.lower() in CLIP_FILTER:
                        fullpath = os.path.join(path, file)
                        data = read_clip_meta(fullpath)
                        print data
                        if data:
                            frames = int(float(data['duration']) * FRAMERATE)
                            self.insert_record(cam_id=camera_id_folder,
                                               tc=data['timecode'],
                                               duration=frames,
                                               allmeta=data,
                                               fullpath=fullpath)
                            print 'Insert clip: {0}'.format(fullpath)
                        else:
                            print "Warning!, {0} is not recognizable.".\
                                format(fullpath)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan()
    scanner.conn.commit()
