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
            # When providing no field data (all default)
            {},
            # Then we expect this student_view_data output:
            {
                'display_name': 'Image',
                'alt_text': '',
                'image_url': '',
                'caption': '',
                'citation': '',
            },
            # And this HTML:
            (
                '<div class="image-block-student-view">\n'
                '<img alt="" class="image-block-image" src=""/>\n'
                '</div>'
            )
        ), (
            # When providing this field data:
            {
                'display_name': 'The moon - چاند',
                'alt_text': 'Map of the moon - چاند کا نقشہ',
                'image_url': 'https://cdn.org/moon.jpeg',
                'caption': 'Fig. 1: Map of the moon - چاند کا نقشہ',
                'citation': 'Courtesy NASA Lunar Reconnaissance Orbiter science team',
            },
            # Then we expect this student_view_data output:
            {
                'display_name': 'The moon - چاند',
                'alt_text': 'Map of the moon - چاند کا نقشہ',
                'image_url': 'https://cdn.org/moon.jpeg',
                'caption': 'Fig. 1: Map of the moon - چاند کا نقشہ',
                'citation': 'Courtesy NASA Lunar Reconnaissance Orbiter science team',
            },
            # And this HTML:
            (
                '<div class="image-block-student-view">\n'
                '<img alt="Map of the moon - چاند کا نقشہ" class="image-block-image"\n'
                ' src="https://cdn.org/moon.jpeg"/>\n'
                '<p class="caption">\n'
                '<span class="caption">Fig. 1: Map of the moon - چاند کا نقشہ</span>\n'
                '<span class="citation">Courtesy NASA Lunar Reconnaissance Orbiter science team</span>\n'
                '</p>\n'
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
