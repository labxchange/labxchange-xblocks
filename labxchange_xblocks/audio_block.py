# -*- coding: utf-8 -*-
"""
Audio XBlock.
"""
import json

from webob import Response
from xblock.core import XBlock
from xblock.fields import Dict, Scope, String

from .i18n import iso_languages
from .utils import StudentViewBlockMixin, _

try:
    from openedx.core.djangoapps.content_libraries import api as library_api
    USE_LIBRARY_API = True
except ModuleNotFoundError:
    USE_LIBRARY_API = False

try:
    from xblockutils.studio_editable import StudioEditableXBlockMixin
except ImportError:
    class StudioEditableXBlockMixin:
        """
        Dummy class to use when running outside of Open edX.
        """

@XBlock.wants('blockstore')
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

    # Data format: {
    #   'au': {
    #     'type': 'inlinehtml',
    #     'content': '<p>Welcome to the show</p> ...',
    # }
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
        'transcripts',
    )

    student_view_template = 'templates/audio_student_view.html'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        options = []
        for lang in self.transcripts.keys():
            options.append({
                'lang': lang,
                'language': iso_languages.get(lang),
            })

        return {
            'display_name': self.display_name,
            'embed_code': self.embed_code,
            'options': options,
            'transcripts': self.transcripts,
            'user_state': self.user_state,
        }

    @property
    def user_state(self):
        languages = self.transcripts.keys()
        current_language = None
        if languages:
            current_language = list(languages)[0]
        return {
            'current_language': current_language,
        }

    @XBlock.handler
    def student_view_user_state(
        self, request, suffix=""
    ):  # pylint: disable=unused-argument
        """
        Return JSON representation of the block with enough data to render the student view.
        Also, we can use this endpoint to render the view somewhere else
        """
        state = self.student_view_data()
        return Response(
            json.dumps(state), content_type="application/json", charset="UTF-8"
        )
