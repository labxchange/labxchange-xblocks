# -*- coding: utf-8 -*-
"""
Audio block tests
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt
from xblock.field_data import DictFieldData

from labxchange_xblocks.audio_block import AudioBlock
from labxchange_xblocks.tests.utils import BlockTestCaseBase

# pylint: disable=line-too-long
# pylint: disable=trailing-whitespace


@ddt.ddt
class AudioBlockTestCase(BlockTestCaseBase):
    """
    Audio block test case
    """
    block_type = 'lx_audio'
    block_class = AudioBlock
    maxDiff = None
    data = (
        (
            {},
            {
                'display_name': 'Audio',
                'embed_code': '',
                'options': [],
                'transcripts': {},
                'user_state': {'current_language': None},
            },
            (
                """<div class="audio-block-student-view unfolded">
    <div class="audio-block-embed-code-student-view">
        
    </div>
    
</div>
"""  # noqa
            ),
        ), (
            {
                'display_name': 'A very cool track',
                'embed_code': '<iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/794640376&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe>',  # noqa: E501
                'transcripts': {},
                'user_state': {'current_language': None},
            },
            {
                'display_name': 'A very cool track',
                'embed_code': '<iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/794640376&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe>',  # noqa: E501
                'options': [],
                'transcripts': {},
                'user_state': {'current_language': None},
            },
            (
                """<div class="audio-block-student-view unfolded">
    <div class="audio-block-embed-code-student-view">
        <iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/794640376&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe>
    </div>
    
</div>
"""  # noqa
            ),
        )
    )

    @ddt.data(*data)
    @ddt.unpack
    def test_student_view_data(self, field_data, expected_data, _expected_html):
        self._test_student_view_data(field_data, expected_data)

    def test_inline_transcripts(self):
        """
        Tests that inline transcripts are processed as expected.
        """
        field_data = {
            'display_name': 'A very cool track',
            'embed_code': '<iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/794640376&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe>',  # noqa: E501
            'transcripts': {
                'en': {
                    'type': 'inlinehtml',
                    'content': '<p>Welcome to the show</p>',
                },
            },
            'user_state': {'current_language': None},
        }

        expected_data = {
            'display_name': 'A very cool track',
            'embed_code': '<iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/794640376&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe>',  # noqa: E501
            'options': [
                {'lang': 'en', 'language': {'name': 'English', 'native_name': 'English'}},
            ],
            'transcripts': {
                'en': {
                    'type': 'inlinehtml',
                    'content': '<p>Welcome to the show</p>',
                },
            },
            'user_state': {'current_language': 'en'},
        }

        block = self._construct_xblock_mock(self.block_class, self.keys, field_data=DictFieldData(field_data))
        data = block.student_view_data(None)
        assert data == expected_data


class MockAsset:
    def __init__(self, url):
        self.url = url
