#!/usr/bin/env python

import os
import re
import sqlite3

REG_CAM_ID = '^\d{4}_[a-zA-Z0-9]+_\w+_\d{3}$'
TRACK_FILES = ['mov']


def insert_record(db, **kargs):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = ('INSERT INTO TRACKS () VALUES (CAM_ID,IP,OP,FULLPATH)'
           'VALUE ({CAM_ID},{IP},{OP},{FULLPATH})'.format(**kargs))
    c.execute(sql)


class Scanner(object):

    def __init__(self):
        self.db = 'test.db'
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        print "Opened database successfully"
        conn.commit()

        c.execute('CREATE   TABLE IF NOT EXISTS  TRACKS'
                  '(ID      INTEGER  PRIMARY KEY AUTOINCREMENT,'
                  'CAM_ID   TEXT                 NOT NULL,'
                  'IP       INT                  NOT NULL,'
                  'OP       INT                  NOT NULL,'
                  'FULLPATH CHAR(150)            NOT NULL);')
        conn.commit()

    def scan(self, path='/git-repos/melissa/input/160303/ep01/01_video/20160301'):
        for path, subdirs, files in os.walk(path):
            if re.search(REG_CAM_ID, os.path.basename(path)):
                camera_path = os.path.basename(path)
                print camera_path
                print files
                clip = {'CAM_ID': camera_path,
                        'IP': '12',
                        'OP': '23',
                        'FULLPATH': camera_path}
                insert_record(self.db, clip)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan()
