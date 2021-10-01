# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt
from utils import BlockTestCaseBase

from labxchange_xblocks.image_block import ImageBlock


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
                '<figure class="image-block-student-view">\n'
                '<img class="image-block-image" src="" alt=""/>\n'
                '</figure>'
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
                '<figure class="image-block-student-view">\n'
                '<img class="image-block-image" src="https://cdn.org/moon.jpeg"\n'
                ' alt="Map of the moon - چاند کا نقشہ"/>\n'
                '<figcaption>\n'
                '<span class="caption">Fig. 1: Map of the moon - چاند کا نقشہ</span>\n'
                '<cite>Courtesy NASA Lunar Reconnaissance Orbiter science team</cite>\n'
                '</figcaption>\n'
                '</figure>'
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
        self._test_public_view(field_data, expected_html)
