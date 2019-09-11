# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt
from six import text_type

from labxchange_xblocks.story_in_science_block import StoryInScienceBlock
from utils import BlockTestCaseBase


@ddt.ddt
class StoryInScienceBlockTestCase(BlockTestCaseBase):

    block_type = 'lx_story_in_science'
    block_class = StoryInScienceBlock

    data = (
        (
            {},
            {
                'display_name': text_type('Story in Science'),
                'key_points': '',
                'story': '',
            },
            (
                '<div class="story-in-science-block-student-view">\n'
                '<div class="story-in-science-block-key-points">\n'
                '<div class="story-in-science-block-key-points-heading">\n'
                'Key Points\n'
                '</div>\n'
                '<div class="story-in-science-block-key-points-details">\n'
                '</div>\n'
                '</div>\n'
                '<div class="story-in-science-block-story">\n'
                '</div>\n'
                '</div>\n'
            ),
        ), (
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '<ul><li>Point one.</li></ul>',
                'story': '<p>This is a story about stars.</p>',
            },
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '<ul><li>Point one.</li></ul>',
                'story': '<p>This is a story about stars.</p>',
            },
            (
                '<div class="story-in-science-block-student-view">\n'
                '<div class="story-in-science-block-key-points">\n'
                '<div class="story-in-science-block-key-points-heading">\n'
                'Key Points\n'
                '</div>\n'
                '<div class="story-in-science-block-key-points-details">\n'
                '<ul><li>Point one.</li></ul>\n'
                '</div>\n'
                '</div>\n'
                '<div class="story-in-science-block-story">\n'
                '<p>This is a story about stars.</p>\n'
                '</div>\n'
                '</div>\n'
            ),
        )
    )

    @ddt.data(*data)
    @ddt.unpack
    def test_student_view_data(self, field_data, expected_data, _expected_html):
        self._test_student_view_data(field_data, expected_data)

    @ddt.data(*data)
    @ddt.unpack
    def test_student_view(self, field_data, _expected_data, expected_html):
        self._test_student_view(field_data, expected_html)
