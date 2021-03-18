# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt

from labxchange_xblocks.document_block import DocumentBlock
from utils import BlockTestCaseBase


@ddt.ddt
class DocumentBlockTestCase(BlockTestCaseBase):

    block_type = 'lx_document'
    block_class = DocumentBlock

    data = (
        (
            {},
            {
                'display_name': 'Document',
                'document_type': 'application/pdf',
                'document_name': '',
                'document_url': '',
            },
# E   - 	<object data="" type="application/pdf" aria-label="Document">
# E   + 	<object aria-label="Document" data="" type="application/pdf">

            (
                '<div class="document-block-student-view">\n'
                '<object data="" type="application/pdf" aria-label="Document">\n'
                '<p>It appears you don\'t have an appropriate viewer plugin installed.'
                ' Click <a href="">here</a> to view the file.</p>\n'
                '</object>\n'
                '</div>'
            ),
        ), (
            {
                'display_name': 'Stars - ستارے',
                'document_type': 'text/html',
                'document_name': 'Stars - ستارے',
                'document_url': 'https://cdn.org/stars.jpeg',
            },
            {
                'display_name': 'Stars - ستارے',
                'document_type': 'text/html',
                'document_name': 'Stars - ستارے',
                'document_url': 'https://cdn.org/stars.jpeg',
            },
            (
                '<div class="document-block-student-view">\n'
                '<object data="https://cdn.org/stars.jpeg" type="text/html" aria-label="Stars - ستارے">\n'
                '<p>It appears you don\'t have an appropriate viewer plugin installed.'
                ' Click <a href="https://cdn.org/stars.jpeg">here</a> to view the file.</p>\n'
                '</object>\n'
                '</div>'
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
