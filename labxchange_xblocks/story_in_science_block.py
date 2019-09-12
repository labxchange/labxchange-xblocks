# -*- coding: utf-8 -*-
"""
Story In Science XBlock.
"""

from __future__ import absolute_import, unicode_literals

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import StudentViewBlockMixin, _


class StoryInScienceBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for https://storiesinscience.org/.
    """

    display_name = String(
        default='Story in Science',
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        scope=Scope.content,
    )

    key_points = String(
        default='',
        display_name=_('Key Points'),
        help=_('The key points of this story.'),
        multiline_editor='html',
        resettable_editor=False,
        scope=Scope.content,
    )

    story = String(
        default='',
        display_name=_('Story'),
        help=_('The complete story.'),
        multiline_editor='html',
        resettable_editor=False,
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
        'key_points',
        'story',
    )

    student_view_template = 'templates/story_in_science_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'key_points': self.key_points,
            'story': self.story,
        }
