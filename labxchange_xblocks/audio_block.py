# -*- coding: utf-8 -*-
"""
Audio XBlock.
"""
import six
import requests
from webob import Response
import pysrt

from xblock.core import XBlock
from xblock.fields import Dict, Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from openedx.core.djangoapps.content_libraries import api as library_api

from .utils import StudentViewBlockMixin, _
from .i18n import iso_languages


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
        sequences = []
        for lang in self.transcripts.keys():
            current_asset = self.get_transcript_asset(lang)
            options.append({
                'lang': lang,
                'language': iso_languages.get(lang),
                'url': current_asset.url if current_asset else ''
            })
            if current_asset:
                transcript = self.get_transcript_content(current_asset.url)
                sequences = self.get_sequences(transcript)
        return {
            'display_name': self.display_name,
            'embed_code': self.embed_code,
            'options': options,
            'transcripts': self.transcripts,
            'sequences': sequences,
            'user_state': self.user_state,
        }
    
    @property
    def user_state(self):
        languages = self.transcripts.keys()
        current_language = None
        if languages:
            current_language = list(languages)[0]
        return {'current_language': current_language}

    @property
    def assets(self):
        """ Returns every block assets from Blockstore """
        if not hasattr(self, '_assets') or not self._assets:
            self._assets = library_api.get_library_block_static_asset_files(
                self.location,
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

    def get_sequences(self, content):
        """ Returns sequences based on asset content """
        sequences = pysrt.from_string(content.decode('utf-8'))
        return [
            {
                'text': sequence.text,
                'start': {
                    'hours': str(sequence.start.hours).zfill(2),
                    'minutes': str(sequence.start.minutes).zfill(2),
                    'seconds': str(sequence.start.seconds).zfill(2),
                    'milliseconds': sequence.start.milliseconds,
                },
                'end': {
                    'hours': str(sequence.end.hours).zfill(2),
                    'minutes': str(sequence.end.minutes).zfill(2),
                    'seconds': str(sequence.end.seconds).zfill(2),
                    'milliseconds': sequence.end.milliseconds,

                },
            } for sequence in sequences]
    
    def get_transcript_content(self, url):
        """ Retrieves and returns transcript content from Blockstore """
        response = requests.get(url)
        return response.content

    @XBlock.json_handler
    def sequences(self, data, suffix=''):
        """ Returns sequences based on lang parameter """
        lang = data.get('lang')
        if not lang:
            lang = self.user_state.get('current_language')

        lang = lang.rstrip('/')
        asset = self.get_transcript_asset(lang)
        content = self.get_transcript_content(asset.url)
        return self.get_sequences(content)

    @XBlock.handler
    def transcript(self, request, dispatch):
        if dispatch.startswith('download'):
            lang = request.GET.get('lang', None)
            if lang:
                lang = lang.rstrip('/')

            asset = self.get_transcript_asset(lang)
            
            if not asset:
                return Response(status=404)

            headerlist = [
                ('Content-Language', lang),
            ]

            transcript = self.get_transcript(asset.url)

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