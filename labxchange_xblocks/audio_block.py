# -*- coding: utf-8 -*-
"""
Audio XBlock.
"""
from xblock.core import XBlock
from xblock.fields import Dict, Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import StudentViewBlockMixin, _


class AudioBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for audio embedding.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The name of the audio file.'),
        default='Audio',
        scope=Scope.content,
    )

    embed_code = String(
        display_name=_('Embed code'),
        default='',
        help=_('The embed code of the audio file.'),
        multiline_editor='html',
        resettable_editor=False,
        scope=Scope.content,
    )

    # Data format: {'de': 'german_translation', 'uk': 'ukrainian_translation'}
    transcripts = Dict(
        help=_('Add transcripts in different languages.'
               ' Click below to specify a language and upload an .srt transcript file for that language.'),
        display_name=_('Transcript Languages'),
        scope=Scope.settings,
        default={}
    )

    editable_fields = (
        'display_name',
        'embed_code',
    )

    student_view_template = 'templates/audio_student_view.html'
    css_resource_url = 'public/css/audio-xblock.css'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'embed_code': self.embed_code,
        }
