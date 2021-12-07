# -*- coding: utf-8 -*-
"""
Audio XBlock.
"""
import json

import pysrt
import requests
import six
from openedx.core.djangoapps.content_libraries import api as library_api
from webob import Response
from xblock.core import XBlock
from xblock.fields import Dict, Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .i18n import iso_languages
from .utils import StudentViewBlockMixin, _


def srt_to_html(srt_string):
    """
    Takes an str formatted string, and returns marked up html.
    Strips all timestamps; this is to simply render it neatly.
    """
    sequences = pysrt.from_string(srt_string.decode('utf-8'))
    return "\n".join(f"<p>{x.text}</p>" for x in sequences)


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
    #   'de': 'german_translation.srt',
    #   'uk': 'ukrainian_translation.srt',
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
    css_resource_url = 'public/css/audio-xblock.css'
    js_resource_url = 'public/js/audio-xblock.js'
    js_init_function = 'LXAudioXBlock'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        options = []
        transcripts = {}
        for lang in self.transcripts.keys():
            current_asset = self.get_transcript_asset(lang)
            options.append({
                'lang': lang,
                'language': iso_languages.get(lang),
            })

            # Convert legacy srt subtitles on the fly.
            # These will be permanently saved when the client saves.
            value = self.transcripts[lang]
            if current_asset and isinstance(value, str):
                content = self.get_transcript_content(current_asset.url)
                transcripts[lang] = {
                    "type": "inlinehtml",
                    "content": srt_to_html(content),
                }
            else:
                transcripts[lang] = value

        return {
            'display_name': self.display_name,
            'embed_code': self.embed_code,
            'options': options,
            'transcripts': transcripts,
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

    @property
    def assets(self):
        """ Returns every block assets from Blockstore """
        if not hasattr(self, '_assets') or not self._assets:  # pylint: disable=access-member-before-definition
            self._assets = library_api.get_library_block_static_asset_files(  # pylint: disable=attribute-defined-outside-init,   # noqa: E501
                self.location,  # pylint: disable=no-member
            )
        return self._assets

    def get_transcript_asset(self, lang):
        """
        Returns the lang asset object (not the actual content)
        from Blockstore
        """
        transcript_name = 'transcript-{}.srt'.format(lang)
        for asset in self.assets:
            if asset.path == transcript_name:
                return asset

        return None

    def get_transcript_content(self, url):
        """ Retrieves and returns transcript content from Blockstore """
        response = requests.get(url)
        return response.content

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

    @XBlock.handler
    def sequences(self, request, dispatch):  # pylint: disable=unused-argument
        """
        Returns sequences based on lang parameter.
        This is used by the frontend audio-xblock.js to render the srt content in audio_student_view.html.
        NOTE: this will be removed once we begin rendering the block in the labxchange frontend (in LX-2243).
        """
        lang = request.GET.get('lang', None)
        if not lang:
            lang = self.user_state.get('current_language')

        lang = lang.rstrip('/')
        value = self.transcripts.get(lang)

        if isinstance(value, str):
            # value is file name
            asset = self.get_transcript_asset(lang)
            if asset:
                content = self.get_transcript_content(asset.url)
                return Response(
                    json.dumps({"content": srt_to_html(content)}),
                    headerlist=[('Content-Type', 'application/json')],
                    charset='utf8'
                )
        else:
            # `value` is of shape {"type": "inlinehtml", "content": "<p>content</p>"}
            if value["type"] == "inlinehtml":
                return Response(
                    json.dumps({"content": value["content"]}),
                    headerlist=[('Content-Type', 'application/json')],
                    charset='utf8'
                )

        return Response(status=404)

    @XBlock.handler
    def transcript(self, request, dispatch):
        """
        Returns a transcript from the Blockstore
        """
        if dispatch.startswith('download'):
            lang = request.GET.get('lang', None)
            if lang:
                lang = lang.rstrip('/')

            asset = self.get_transcript_asset(lang)
            if not asset:
                return Response(status=404)

            transcript = self.get_transcript_content(asset.url)
            headerlist = [('Content-Language', lang), ]
            headerlist.append(
                (
                    'Content-Disposition',
                    'attachment; filename="{}"'.format(asset.path.encode('utf-8') if six.PY2 else asset.path)
                )
            )

            response = Response(
                transcript,
                headerlist=headerlist,
                charset='utf8'
            )
            response.content_type = 'text/srt'
            return response
        return Response(status=400)
