#!/usr/bin/env python
from __future__ import division

import json
import os
import re
import sqlite3
import subprocess

REG_CAM_ID = '^\d{4}_[a-zA-Z0-9]+_\w+_\d{3}$'
CLIP_FILTER = ['.mov']


def read_meta(clips):
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
               '-show_format', '-show_streams', clips]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        data = json.loads(proc.communicate()[0])
        data_needed = {'timecode': data['streams'][0]['tags']['timecode'],
                       'duration': data['streams'][0]['duration'],
                       'codec_time_base': data['streams'][0]['codec_time_base']
                       }
        return data_needed
    except Exception:
        return None


class Scanner(object):
    def __init__(self):
        self.db = 'test.db'
        self.conn = sqlite3.connect('test.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE   TABLE IF NOT EXISTS  TRACKS'
                       '(ID      INTEGER  PRIMARY KEY AUTOINCREMENT,'
                       'CAM_ID   CHAR(100)            NOT NULL,'
                       'TC       CHAR(11)             NOT NULL,'
                       'DURATION INT                  NOT NULL,'
                       'FULLPATH CHAR(300)            NOT NULL);')
        self.conn.commit()
        print "Create Database"

    def insert_record(self, cam_id, tc, duration, fullpath):
        sql = ('INSERT INTO TRACKS (CAM_ID,TC,DURATION,FULLPATH) '
               'VALUES ("{CAM_ID}","{TC}","{DURATION}","{FULLPATH}");'.
               format(CAM_ID=cam_id,
                      TC=tc, DURATION=duration,
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
                        data = read_meta(fullpath)
                        if data:
                            frames = int(float(data['duration']) / eval(data['codec_time_base']))
                            self.insert_record(cam_id=camera_id_folder,
                                               tc=data['timecode'],
                                               duration=frames,
                                               fullpath=fullpath)
                            print 'Insert clip: {0}'.format(fullpath)
                        else:
                            print "Warning!, {0} is not recognizable.".\
                                format(fullpath)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan()
    scanner.conn.commit()
