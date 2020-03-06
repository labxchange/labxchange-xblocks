# -*- coding: utf-8 -*-
"""
Case Study XBlock.
"""
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.studio_editable import (
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin
)

from .utils import StudentViewBlockMixin, _, xblock_specs_from_categories


class CaseStudyBlock(
    XBlock,
    StudentViewBlockMixin,
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin,
):
    """
    XBlock for case studies.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        default='Case Study',
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
    )

    completion_mode = XBlockCompletionMode.AGGREGATOR

    has_children = True
    allowed_nested_blocks = xblock_specs_from_categories(('html', 'video', 'document'))

    student_view_template = 'templates/case_study_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        child_blocks_data = []

        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id)
            if child_block:
                child_block_data = {
                    'usage_id': str(child_usage_id),
                    'block_type': child_block.scope_ids.block_type,
                    'display_name': child_block.display_name,
                }
                child_blocks_data.append(child_block_data)

        return {
            'display_name': self.display_name,
            'child_blocks': child_blocks_data,
        }
