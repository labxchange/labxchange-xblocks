# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt
from six import text_type

from labxchange_xblocks.narrative_block import NarrativeBlock
from utils import BlockTestCaseBase


@ddt.ddt
class NarrativeBlockTestCase(BlockTestCaseBase):

    block_type = 'lx_narrative'
    block_class = NarrativeBlock

    data = (
        (
            {},
            {
                'display_name': text_type('Narrative'),
                'key_points': '',
                'narrative': '',
            },
            (
                '<div class="narrative-block-student-view">\n'
                '</div>\n'
            ),
        ), (
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '',
                'narrative': '',
            },
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '',
                'narrative': '',
            },
            (
                '<div class="narrative-block-student-view">\n'
                '</div>\n'
            ),
        ), (
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '<ul><li>Point one.</li></ul>',
                'narrative': '<p>This is a narrative about stars.</p>',
            },
            {
                'display_name': text_type('Stars - ستارے'),
                'key_points': '<ul><li>Point one.</li></ul>',
                'narrative': '<p>This is a narrative about stars.</p>',
            },
            (
                '<div class="narrative-block-student-view">\n'
                '<div class="narrative-block-key-points">\n'
                '<div class="narrative-block-key-points-heading">\n'
                'Key Points\n'
                '</div>\n'
                '<div class="narrative-block-key-points-details">\n'
                '<ul><li>Point one.</li></ul>\n'
                '</div>\n'
                '</div>\n'
                '<div class="narrative-block-narrative">\n'
                '<p>This is a narrative about stars.</p>\n'
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
        self._test_public_view(field_data, expected_html)
