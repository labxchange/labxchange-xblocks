# -*- coding: utf-8 -*-
"""
Narrative XBlock.
"""
from xblock.core import XBlock
from xblock.fields import Scope, String

from .utils import StudentViewBlockMixin, _


try:
    from xblockutils.studio_editable import StudioEditableXBlockMixin
except ImportError:
    class StudioEditableXBlockMixin:
        """
        Dummy class to use when running outside of Open edX.
        """


class NarrativeBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for narratives.
    """

    display_name = String(
        default='Narrative',
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        scope=Scope.content,
    )

    key_points = String(
        default='',
        display_name=_('Key Points'),
        help=_('The key points of this narrative.'),
        multiline_editor='html',
        resettable_editor=False,
        scope=Scope.content,
    )

    narrative = String(
        default='',
        display_name=_('Narrative'),
        help=_('The complete narrative.'),
        multiline_editor='html',
        resettable_editor=False,
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
        'key_points',
        'narrative',
    )

    student_view_template = 'templates/narrative_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'key_points': self.key_points,
            'narrative': self.narrative,
        }
