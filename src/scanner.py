#!/usr/bin/env python

import os
import re
import sqlite3

REG_CAM_ID = '^\d{4}_[a-zA-Z0-9]+_\w+_\d{3}$'
TRACK_FILES = ['mov']


class Scanner(object):
    def __init__(self):
        self.db = 'test.db'
        self.conn = sqlite3.connect('test.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE   TABLE IF NOT EXISTS  TRACKS'
                       '(ID      INTEGER  PRIMARY KEY AUTOINCREMENT,'
                       'CAM_ID   TEXT                 NOT NULL,'
                       'IP       TEXT                 NOT NULL,'
                       'OP       TEXT                 NOT NULL,'
                       'FULLPATH CHAR(150)            NOT NULL);')
        self.conn.commit()
        print "Create Database"

    def insert_record(self, cam_id, ip, op, fullpath):
        sql = ('INSERT INTO TRACKS (CAM_ID,IP,OP,FULLPATH) '
               'VALUES ("{CAM_ID}","{IP}","{OP}","{FULLPATH}");'.
               format(CAM_ID=cam_id,
                      IP=ip, OP=op,
                      FULLPATH=fullpath))
        self.c.execute(sql)

    def scan(self,
             path='/git-repos/melissa/input/160303/ep01/01_video/20160301'):
        for path, subdirs, files in os.walk(path):
            if re.search(REG_CAM_ID, os.path.basename(path)):
                camera_path = os.path.basename(path)
                self.insert_record(cam_id=camera_path,
                                   ip='12', op='23',
                                   fullpath=camera_path)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan()
    scanner.conn.commit()
