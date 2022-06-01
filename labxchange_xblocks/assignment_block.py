# -*- coding: utf-8 -*-
"""
Assignment XBlock.
"""
import json

from webob import Response
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import Scope, String

from .utils import StudentViewBlockMixin, _, xblock_specs_from_categories

try:
    from xblockutils.studio_editable import (
        StudioContainerWithNestedXBlocksMixin,
        StudioEditableXBlockMixin,
        XBlockWithPreviewMixin
    )
except ImportError:
    class StudioContainerWithNestedXBlocksMixin:
        """
        Dummy class to use when running outside of Open edX.
        """

    class StudioEditableXBlockMixin:
        """
        Dummy class to use when running outside of Open edX.
        """

    class XBlockWithPreviewMixin:
        """
        Dummy class to use when running outside of Open edX.
        """


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

    completion_mode = XBlockCompletionMode.AGGREGATOR

    has_children = True
    allowed_nested_blocks = xblock_specs_from_categories(('problem', 'drag-and-drop-v2'))

    student_view_template = 'templates/assignment_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        child_blocks_data = []
        context = context or {}

        block_type_overrides = context.get('block_type_overrides')
        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id, block_type_overrides=block_type_overrides)
            if child_block:
                weight = self._get_weighted_score_possible_for_child(child_block)
                child_block_data = {
                    'usage_id': str(child_usage_id),
                    'block_type': child_block.scope_ids.block_type,
                    'display_name': child_block.display_name,
                    'graded': weight > 0,
                    # Max attempts: 0 means unlimited, None means not applicable
                    'max_attempts': getattr(child_block, 'max_attempts', None),
                    # Weight: the (weighted) maximum possible score that students can earn on this child XBlock
                    'weight': weight,
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

        block_type_overrides = self._block_type_overrides(request)
        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id, block_type_overrides=block_type_overrides)
            if child_block:
                score = self.get_weighted_score_for_block(child_block)
                child_blocks_state[str(child_usage_id)] = {'score': score}
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
        # If this is a unit with children:
        if getattr(block, 'has_children', False):
            earned = 0
            possible = 0
            any_graded = False
            for child in block.get_children():
                data = self.get_weighted_score_for_block(child)
                if data is None:
                    continue
                any_graded = True
                earned += data['earned']
                possible += data['possible']
            if any_graded:
                return {'earned': earned, 'possible': possible}
        # If this is a scorable block like a capa problem:
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

    def _get_weighted_score_possible_for_child(self, block):
        """
        Get the [weighted] maximum possible score for an XBlock.
        """
        if getattr(block, 'has_children', False):
            return sum(self._get_weighted_score_possible_for_child(child) for child in block.get_children())
        elif not getattr(block, 'has_score', False):
            return 0
        weight_factor = getattr(block, 'weight', 1)
        if weight_factor is not None:
            return weight_factor
        # This is not a weighted problem, so we need to determine the raw score possible.
        # Determining the number of points possible in a capa problem requires initializing its
        # LoncapaSystem/LoncapaProblem, which requires a user ID. But this gets called from student_view_data, and
        # student_view data is meant to be user-agnostic and can be called without any user ID provided.
        if self.scope_ids.user_id is not None:
            # If we have a user ID, let's use it to determine the possible score accurately. Note that this works for
            # any scorable XBlock, not just capa.
            score = block.get_score()
            if score:
                return score.raw_possible
            return 1
        else:
            # If we don't have a user_id, we can't fetch the real 'raw_possible' value, so let's just assume
            # it's the default (one single question/response) in the XBlock.
            return 1
