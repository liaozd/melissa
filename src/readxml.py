from lxml import etree as ET

from scanner import Scanner
from utils.path import get_normalized_path


class XmlReader(object):
    def __init__(self, xml_path=None):
        self.path = xml_path
        self.clips_in_xml = self.get_all_clip_paths()
        self.common_path = self.get_common_path()

    def get_all_clip_paths(self):
        clips_in_xml = []
        tree = ET.parse(self.path)
        root = tree.getroot()
        media = root.getchildren()[0].find('media')
        video = media.find('video')
        tracks = video.findall('track')
        for track in tracks:
            clipitems = track.findall('clipitem')
            for clipitem in clipitems:
                clip_path = clipitem.find('file').find('pathurl').text
                clip_path = clip_path.split(':')[-1]
                clip_path = get_normalized_path(clip_path)
                clips_in_xml.append(clip_path)
        return clips_in_xml

    def get_common_path(self):
        common = []
        common_size = -1
        for p in self.clips_in_xml:
            s = p.split('/')
            s.pop()
            if common_size == -1:
                common_size = len(s)
                common = s
                continue
            while common_size > 0 and s[0:common_size] != common:
                common_size -= 1
                common.pop()
        return '/'.join(common) + '/'


if __name__ == '__main__':
    xml_path = \
        '/home/neo/MEGA/my-projects/melissa/20161120/1119_am_sync_cy.xml'
    xml = XmlReader(xml_path)
    print xml.clips_in_xml
    path_to_scan = get_normalized_path(xml.common_path)
    scanner = Scanner()
    scanner.scan(path_to_scan)
