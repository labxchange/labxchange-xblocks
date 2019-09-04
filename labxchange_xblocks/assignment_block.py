# -*- coding: utf-8 -*-
"""
Assignment XBlock.
"""

from __future__ import absolute_import, division, unicode_literals

import json

from six import text_type
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.studio_editable import (
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin
)

from .utils import StudentViewBlockMixin, _, xblock_specs_from_categories


class AssignmentBlock(
    XBlock,
    StudentViewBlockMixin,
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin,
):
    """
    XBlock for assignments.
    """

    display_name = String(
        default='Assignment',
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
    )

    has_children = True
    allowed_nested_blocks = xblock_specs_from_categories(('problem', 'drag-and-drop-v2'))

    student_view_template = 'templates/assignment_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        child_blocks_data = []
        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id)
            if child_block:
                child_block_data = {
                    'usage_id': text_type(child_usage_id),
                    'block_type': child_block.scope_ids.block_type,
                    'display_name': child_block.display_name,
                    'graded': child_block.graded,
                }
                child_blocks_data.append(child_block_data)

        return {
            'display_name': self.display_name,
            'child_blocks': child_blocks_data,
        }

    @XBlock.handler
    def student_view_user_state(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        Return JSON representation of student state.
        """
        child_blocks_state = {}
        total_earned = 0
        total_possible = 0

        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id)
            if child_block:
                score = self.get_weighted_score_for_block(child_block)
                child_blocks_state[text_type(child_usage_id)] = {'score': score}
                if score:
                    total_earned += score['earned']
                    total_possible += score['possible']

        state = {
            'score': {
                'earned': total_earned,
                'possible': total_possible,
            },
            'child_blocks': child_blocks_state,
        }

        return Response(
            json.dumps(state),
            content_type='application/json',
            charset='UTF-8'
        )

    def get_weighted_score_for_block(self, block):
        """
        Return the weighted (earned, possible) score for the block.

        If weight is None or raw_possible is 0, returns the original values.
        """
        if getattr(block, 'has_score', False) is True:
            score = block.get_score()
            if score is not None:
                cannot_compute_with_weight = block.weight is None or score.raw_possible == 0
                if cannot_compute_with_weight:
                    return {
                        'earned': score.raw_earned,
                        'possible': score.raw_possible,
                    }
                else:
                    return {
                        'earned': float(score.raw_earned) * block.weight / score.raw_possible,
                        'possible': float(block.weight),
                    }
        return None
