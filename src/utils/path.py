#!/usr/bin/env python
import os
import time


def get_normalized_path(path):
    path = path.split('//localhost')[-1]
    if path != '/':
        return path.rstrip('/')


def get_output_file_path(OUTPUT_FOLDER, filename='output', extension='.xml'):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    timestr = time.strftime("%Y%m%d")
    output_name = filename + '_' + timestr + extension
    output = os.path.join(OUTPUT_FOLDER, output_name)
    print 'Create file: ', output
    return output
