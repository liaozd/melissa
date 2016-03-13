#!/usr/bin/env python

CLIP_FILTER = ['.mov']
DB_FILE = 'melissa.db'
FRAMERATE = 25

CLIP_SAMPLE_XML = """
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
    <masterclipid>[place holder]0301_280_a_d02_cam20264_01 1</masterclipid>
    <file id="[place holder]0301_280_a_d02_cam20264_01 2">
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
    <sourcetrack>
        <mediatype>video</mediatype>
    </sourcetrack>
    <fielddominance>none</fielddominance>
</clipitem>"""