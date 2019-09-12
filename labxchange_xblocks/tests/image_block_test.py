# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt

from labxchange_xblocks.image_block import ImageBlock
from utils import BlockTestCaseBase


@ddt.ddt
class ImageBlockTestCase(BlockTestCaseBase):

    block_type = 'lx_image'
    block_class = ImageBlock

    data = (
        (
            {},
            {
                'display_name': 'Image',
                'alt_text': '',
                'image_url': '',
            },
            (
                '<div class="image-block-student-view">\n'
                '<img alt="" class="image-block-image" src=""/>\n'
                '</div>'
            )
        ), (
            {
                'display_name': u'The moon - چاند',
                'alt_text': u'Map of the moon - چاند کا نقشہ',
                'image_url': 'https://cdn.org/moon.jpeg',
            },
            {
                'display_name': u'The moon - چاند',
                'alt_text': u'Map of the moon - چاند کا نقشہ',
                'image_url': 'https://cdn.org/moon.jpeg',
            },
            (
                '<div class="image-block-student-view">\n'
                '<img alt="Map of the moon - چاند کا نقشہ" class="image-block-image"\n'
                ' src="https://cdn.org/moon.jpeg"/>\n'
                '</div>'
            )
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
