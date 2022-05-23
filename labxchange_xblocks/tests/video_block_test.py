"""
Video block tests
"""
# pylint: disable=too-many-statements
# pylint: disable=protected-access
import json

import ddt
from mock import Mock
from xblock.field_data import DictFieldData

from labxchange_xblocks.tests.utils import BlockTestCaseBase
from labxchange_xblocks.video_block import VideoBlock


@ddt.ddt
class VideoBlockTestCase(BlockTestCaseBase):
    """
    Test the video block
    """
    maxDiff = None
    block_type = "lx_video"
    block_class = VideoBlock
    data_for_user_state = (
        (
            {},
            {
                "encoded_videos": {},
                "saved_video_position": 0.0,
                "speed": None,
                "transcripts": {},
            },
        ),
        (
            {
                "youtube_id_1_0": "-SNwRT85WMo",
            },
            {
                "encoded_videos": {
                    "youtube": {"url": "https://www.youtube.com/watch?v=-SNwRT85WMo"}
                },
                "saved_video_position": 0.0,
                "speed": None,
                "transcripts": {},
            },
        ),
        (
            {
                "html5_sources": ["https://vimeo.com/456648063"],
            },
            {
                "encoded_videos": {
                    "fallback": {"url": "https://vimeo.com/456648063"}
                },
                "saved_video_position": 0.0,
                "speed": None,
                "transcripts": {},
            },
        ),
        (
            {
                "html5_sources": ["https://example.com/my-video.m3u8"],
            },
            {
                "encoded_videos": {
                    "fallback": {"url": "https://example.com/my-video.m3u8"}
                },
                "saved_video_position": 0.0,
                "speed": None,
                "transcripts": {},
            },
        ),
        (
            {
                "youtube_id_1_0": "-SNwRT85WMo",
                "transcripts": {"en": "my-file.srt"},
            },
            {
                "encoded_videos": {
                    "youtube": {"url": "https://www.youtube.com/watch?v=-SNwRT85WMo"}
                },
                "saved_video_position": 0.0,
                "speed": None,
                "transcripts": {"en": "transcript/download/lang=en"},
            },
        ),
        (
            {
                "youtube_id_1_0": "-SNwRT85WMo",
                "transcripts": {"en": "my-file.srt"},
                "speed": 1.5,
                "saved_video_position": "00:01:30",
                "transcript_language": "fr",
            },
            {
                "encoded_videos": {
                    "youtube": {"url": "https://www.youtube.com/watch?v=-SNwRT85WMo"}
                },
                "speed": 1.5,
                "saved_video_position": 90.0,
                "transcripts": {"en": "transcript/download/lang=en"},
            },
        ),
    )

    @ddt.data(*data_for_user_state)
    @ddt.unpack
    def test_student_view_user_state(self, field_data, expected_data):
        """
        Test various states.
        See `data_for_user_state` for details on what is tested.
        """
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )
        response = block.student_view_user_state(Mock())
        assert json.loads(response.body.decode("utf-8")) == expected_data

    @ddt.data(
        (
            {
                "youtube_id_1_0": "-SNwRT85WMo",
                "transcripts": {"en": "my-file.srt"},
                "speed": 1.5,
                "saved_video_position": "00:01:30",
                "transcript_language": "fr",
            },
            {
                "en": "my-file.srt"
            }
        ), (
            {
                "transcripts": {"en": "my-file.srt", "fr": ""},
            },
            {
                "en": "my-file.srt"
            }
        )
    )
    @ddt.unpack
    def test_transcripts_info(self, field_data, expected_data):
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )
        assert block.get_transcripts_info() == expected_data
