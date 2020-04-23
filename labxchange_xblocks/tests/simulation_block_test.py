# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt

from labxchange_xblocks.simulation_block import SimulationBlock
from utils import BlockTestCaseBase


@ddt.ddt
class SimulationBlockTestCase(BlockTestCaseBase):

    block_type = 'lx_simulation'
    block_class = SimulationBlock

    data = (
        (
            {},
            {
                'display_name': 'Simulation',
                'simulation_url': '',
            },
            (
                '<div class="simulation-block-student-view">\n'
                '<iframe src="" title="Simulation">\n</iframe>\n'
                '</div>'
            ),
        ), (
            {
                'display_name': 'A galaxy - ایک کہکشاں',
                'simulation_url': 'https://cdn.org/galaxy.jpeg',
            },
            {
                'display_name': 'A galaxy - ایک کہکشاں',
                'simulation_url': 'https://cdn.org/galaxy.jpeg',
            },
            (
                '<div class="simulation-block-student-view">\n'
                '<iframe src="https://cdn.org/galaxy.jpeg" title="A galaxy - ایک کہکشاں">\n</iframe>\n'
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
