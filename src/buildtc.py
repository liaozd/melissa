#!/usr/bin/env python
import getopt
import os
import re
import subprocess
import sys

from config import CLIP_FILTER

REG_QQ_MOV = '[a-zA-Z0-9_]?\d{16}[a-zA-Z0-9_]?'


def create_sub_under(path):
    """

    :param path: create a sub folder under path
    :return full path of the sub folder created
    """

    sub_folder = os.path.basename(path) + '_TC'
    sub_folder_fullpath = os.path.join(path, sub_folder)
    if not os.path.exists(sub_folder_fullpath):
        print('Create Folder: {0}'.format(sub_folder_fullpath))
        os.mkdir(sub_folder_fullpath)
    return sub_folder_fullpath


def get_tc(filename):
    """

    :param filename: get time code from file name
    :return: timecode
    """
    m = re.search("\d{16}", filename).group()[-8:]
    re.findall('..?', m)
    timecode = ':'.join(re.findall('..?', m))
    return timecode


class QQScanner(object):
    def scan(self, path):
        for path, subdirs, files in os.walk(path):
            for file in files:
                extension = os.path.splitext(file)[1]
                base_name = os.path.splitext(file)[0]
                if not file.startswith('.') and not base_name.endswith('_with_tc') and extension.lower() in CLIP_FILTER:
                    if re.search(REG_QQ_MOV, os.path.splitext(file)[0]):
                        fullpath = os.path.join(path, file)
                        dest_path = create_sub_under(os.path.dirname(fullpath))
                        output_file_name = os.path.splitext(file)[0] + '_with_tc' + os.path.splitext(file)[1]
                        tc = get_tc(base_name)
                        cmd = ['ffmpeg', '-i', fullpath, '-vcodec', 'copy', '-acodec', 'copy', '-timecode', tc,
                               os.path.join(dest_path, output_file_name)]
                        subprocess.call(cmd)
                        print("Create new file with timecode: ", os.path.join(dest_path, output_file_name))


def usage():
    print('''Usage:
buildtc /path/to/0312_qq_da_c_02/
''')


def main(argv):
    if len(argv) == 1 or len(argv) > 2:
        usage()
        sys.exit(2)
    try:
        path = argv[1]
        scanner = QQScanner()
        scanner.scan(path)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv)
