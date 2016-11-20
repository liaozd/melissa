#!/usr/bin/env python

from src.scanner import Scanner

scanner = Scanner()

if __name__ == '__main__':
    path = '/Users/liaozhuodi/Downloads/single_sound_track_problem_201611'
    scanner = Scanner()
    scanner.scan(path)

