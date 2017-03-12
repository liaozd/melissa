#!/usr/bin/env python
import os

CLIP_FILTER = ['.mov']
DB_FILE = 'melissa.db'
OUTPUT_FOLDER = os.path.join(os.environ['HOME'], 'Desktop/melissa')
FRAMERATE = 25

VIDEO_CLIP_TEMPLATE = """
<clipitem id="[place holder]0301_280_a_d02_cam20264_01 ">
    <name>[place holder]0301_280_a_d02_cam20264_01</name>
    <duration>[place holder]293</duration>
    <rate>
        <ntsc>FALSE</ntsc>
        <timebase>25</timebase>
    </rate>
    <in>0</in>
    <out>293</out>
    <start>0</start>
    <end>293</end>
    <pixelaspectratio>Square</pixelaspectratio>
    <anamorphic>FALSE</anamorphic>
    <alphatype>none</alphatype>
    <file id="[place holder]0301_280_a_d02_cam20264_01 1">
        <name>[place holder]0301_280_a_d02_cam20264_01.mov</name>
        <pathurl>file://localhost/git-repos/melissa/input/160303/ep01/01_video/20160301/280/0301_280_a_003/0301_280_a_d02_cam20264_01.mov</pathurl>
        <rate>
            <timebase>25</timebase>
        </rate>
        <duration>293</duration>
        <timecode>
            <rate>
                <timebase>25</timebase>
            </rate>
            <string>14:19:55:00</string>
            <frame>1289875</frame>
            <displayformat>NDF</displayformat>
            <source>source</source>
        </timecode>
        <media>
            <video>
                <duration>293</duration>
                <samplecharacteristics>
                    <width>1920</width>
                    <height>1080</height>
                </samplecharacteristics>
            </video>
        </media>
    </file>
</clipitem>"""

AUDIO_NODE_INSIDE_VIDEO = """
<audio>
    <samplecharacteristics>
        <samplerate>48000</samplerate>
        <depth>16</depth>
    </samplecharacteristics>
    <channelcount>2</channelcount>
</audio>"""

AUDIO_CLIP_TEMPLATE = """
<clipitem id="[0301_280_a_d02_cam20264_01] 3">
    <name>[0301_280_a_d02_cam20264_01]</name>
    <duration>[173]</duration>
    <rate>
        <ntsc>FALSE</ntsc>
        <timebase>25</timebase>
    </rate>
    <in>0</in>
    <out>[173]</out>
    <start>[13]</start>
    <end>[186]</end>
    <file id="[0301_280_a_d02_cam20264_01] 1"/>
</clipitem>
"""

# Every lxml instance needs a root
LINK_TEMPLATE = """
<fakeroot>
    <link>
        <linkclipref>0301_280_a_d02_cam20264_01 </linkclipref>
        <mediatype>video</mediatype>
        <trackindex>1</trackindex>
        <clipindex>1</clipindex>
    </link>
    <link>
        <linkclipref>0301_280_a_d02_cam20264_01 2</linkclipref>
        <mediatype>audio</mediatype>
        <trackindex>1</trackindex>
        <clipindex>1</clipindex>
        <groupindex>1</groupindex>
    </link>
    <link>
        <linkclipref>0301_280_a_d02_cam20264_01 3</linkclipref>
        <mediatype>audio</mediatype>
        <trackindex>1</trackindex>
        <clipindex>2</clipindex>
        <groupindex>1</groupindex>
    </link>
</fakeroot>
"""


# Every lxml instance needs a root
LINK_VIDEO_TEMPLATE = """
<link>
    <linkclipref>[0301_280_a_d02_cam20264_01] </linkclipref>
    <mediatype>video</mediatype>
    <trackindex>[1]</trackindex>
    <clipindex>1</clipindex>
</link>
"""

LINK_AUDIO_TEMPLATE = """
<link>
    <linkclipref>[0301_280_a_d02_cam20264_01] 3</linkclipref>
    <mediatype>audio</mediatype>
    <trackindex>[1]</trackindex>
    <clipindex>1</clipindex>
    <groupindex>1</groupindex>
</link>
"""