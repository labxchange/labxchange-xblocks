# -*- coding: utf-8 -*-
"""
Video XBlock.
"""
import datetime
import json
import logging
import os

from webob import Response
from webob.multidict import MultiDict
from xblock import fields
from xblock.core import XBlock
from xblock.fields import Scope

from .exceptions import NotFoundError
from .fields import RelativeTime
from .utils import StudentViewBlockMixin, _

try:
    from openedx.core.djangolib import blockstore_cache
    from openedx.core.lib import blockstore_api
    USE_BLOCKSTORE_CACHE = True
except ModuleNotFoundError:
    # We'll try to use the blockstore service instead.
    USE_BLOCKSTORE_CACHE = False

log = logging.getLogger(__name__)


class Transcript:
    """Container for transcript methods"""

    SRT = "srt"
    SJSON = "sjson"
    TXT = "txt"
    mime_types = {
        SRT: "application/x-subrip; charset=utf-8",
        SJSON: "application/json",
        TXT: "text/plain; charset=utf-8",
    }


@XBlock.wants('blockstore')
class VideoBlock(XBlock, StudentViewBlockMixin):
    """
    XBlock to store a video.
    """

    display_name = fields.String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Video",
        scope=Scope.content,
    )

    # This field is the YouTube video ID
    youtube_id_1_0 = fields.String(
        display_name=_("YouTube ID"),
        help=_("The YouTube ID for this video."),
        default="",
        scope=Scope.content,
    )

    # This field is all other video sources
    # ["https://example.com/video.m3u8", "https://vimeo.com/1234567890"]
    html5_sources = fields.List(
        help=_(
            "The URL or URLs where you've posted non-YouTube versions of the video."
        ),
        display_name=_("Video File URLs"),
        scope=Scope.content,
    )

    # This field contains the different transcripts:
    # {
    #   "en": "my-file.srt",
    #   "fr": "my-fr-file.srt",
    # }
    transcripts = fields.Dict(
        help=_("Transcripts for this video."),
        display_name=_("Transcript Languages"),
        scope=Scope.content,
        default={},
    )

    # This field contains the student favorite transcript language
    transcript_language = fields.String(
        help=_("Preferred language for transcript."),
        display_name=_("Preferred language for transcript"),
        scope=Scope.user_state,
        default="en",
    )

    # This field contains the student transcript display toggle value
    show_captions = fields.Boolean(
        display_name=_(
            "Specify whether the transcripts appear with the video by default."
        ),
        help=_("The transcripts for this video."),
        default="",
        scope=Scope.content,
    )

    # This field contains the student current video position
    saved_video_position = RelativeTime(
        help=_("Current position in the video."),
        scope=Scope.user_state,
        default=datetime.timedelta(seconds=0),
    )

    # This field contains the student current video playback speed
    speed = fields.Float(
        help=_("The last speed that the user specified for the video."),
        scope=Scope.user_state,
    )

    student_view_template = "templates/video_student_view.html"

    def student_view_data(self, context=None):
        """Return all data required to render or edit the xblock"""
        return self._get_student_view_user_state()

    def _get_youtube_url(self, video_id):
        return f"https://www.youtube.com/watch?v={video_id}"

    def _get_student_view_user_state(self):
        """Return student view user state"""
        state = {
            "saved_video_position": self.saved_video_position.total_seconds(),
            "speed": self.speed,
        }

        transcripts = self.transcripts.copy()
        for language_code in self.transcripts.keys():
            transcripts[language_code] = self.runtime.handler_url(
                self, "transcript/download", query=f"lang={language_code}"
            )
        state["transcripts"] = transcripts

        encoded_videos = {}
        if self.youtube_id_1_0:
            encoded_videos.update(
                {"youtube": {"url": self._get_youtube_url(self.youtube_id_1_0)}}
            )
        elif self.html5_sources:
            encoded_videos.update({"fallback": {"url": self.html5_sources[0]}})
        state["encoded_videos"] = encoded_videos
        return state

    @XBlock.handler
    def student_view_user_state(
        self, request, suffix=""
    ):  # pylint: disable=unused-argument
        """Return student view user state"""
        state = self._get_student_view_user_state()
        return Response(
            json.dumps(state), content_type="application/json", charset="UTF-8"
        )

    @XBlock.handler
    def xmodule_handler(self, request, suffix=None):
        """Catchall handler for the xmodule path"""

        data = MultiDict(request.POST or request.data)
        response_data = {"success": False}
        conversions = {
            "saved_video_position": RelativeTime.isotime_to_timedelta,
            "speed": lambda s: json.loads(str(s)),
            "transcript_language": lambda s: s,
        }

        if suffix == "save_user_state":
            for key in data:
                if key in conversions:
                    value = conversions[key](data[key])

                setattr(self, key, value)

            response_data = {"success": True}
        return Response(
            json.dumps(response_data), content_type="application/json", charset="UTF-8"
        )

    def get_transcripts_info(self):
        """Return all transcripts info"""
        transcripts = self.transcripts if self.transcripts else {}
        transcripts_info = {}
        for language_code, transcript_file in transcripts.items():
            if transcript_file:
                transcripts_info[language_code] = transcript_file
        return transcripts_info

    def get_transcript_from_blockstore(self, language, output_format, transcripts):
        """Return trancsript from blockstore"""
        language = language or "en"

        if output_format not in (Transcript.SRT, Transcript.SJSON, Transcript.TXT):
            raise NotFoundError(f"Invalid transcript format `{output_format}`")
        if language not in transcripts:
            raise NotFoundError(
                f"Video {self.scope_ids.usage_id} does not have a transcript "
                f"file defined for the '{language}' language in its OLX."
            )
        filename = transcripts[language]
        if not filename.endswith(".srt"):
            raise NotFoundError(
                "Video XBlocks in Blockstore only support .srt transcript files."
            )

        if USE_BLOCKSTORE_CACHE:
            bundle_uuid = self.scope_ids.def_id.bundle_uuid
            path = self.scope_ids.def_id.olx_path.rpartition("/")[0] + "/static/" + filename
            bundle_version = self.scope_ids.def_id.bundle_version
            draft_name = self.scope_ids.def_id.draft_name
            try:
                content_binary = blockstore_cache.get_bundle_file_data_with_cache(
                    bundle_uuid, path, bundle_version, draft_name
                )

            except blockstore_api.BundleFileNotFound as err:
                raise NotFoundError(
                    f"Transcript file '{path}' missing for video XBlock {self.scope_ids.usage_id}"
                ) from err
        else:
            blockstore_service = self.runtime.service(self, 'blockstore')
            if blockstore_service:
                try:
                    content_binary = blockstore_service.get_library_block_asset_file_content(
                        self.scope_ids.usage_id, filename,
                    )
                except Exception as err:  # pylint: disable=broad-except
                    raise NotFoundError(
                        f"Transcript file '{filename}' missing for video XBlock {self.scope_ids.usage_id}"
                    ) from err
            else:
                raise NotFoundError(
                    "Unable to load transcript file '{filename}' for video XBlock {self.scope_ids.usage_id}: "
                    "blockstore service not available"
                )
        # Now convert the transcript data to the requested format:
        filename_no_extension = os.path.splitext(filename)[0]
        output_filename = f"{filename_no_extension}.{output_format}"
        # TODO: Do we only have srt subtitles?
        # output_transcript = Transcript.convert(
        #     content_binary.decode("utf-8"),
        #     input_format=Transcript.SRT,
        #     output_format=output_format,
        # )
        output_transcript = content_binary.decode("utf-8")
        if not output_transcript.strip():
            raise NotFoundError("The transcript is empty.")
        return output_transcript, output_filename, Transcript.mime_types[output_format]

    def handle_transcript_translation(self, request, transcripts, language):
        """Handler for the transcript/translation endpoint"""
        if not language:
            log.info("Invalid /translation request: no language.")
            return Response(status=400)

        if language not in ["en"] + transcripts.keys():
            log.info(
                f"Video: transcript not available for given language (language: {language})."
            )
            return Response(status=404)

        try:
            content, _, mimetype = self.get_transcript_from_blockstore(
                language=self.transcript_language,
                output_format=Transcript.SJSON,
                transcripts=transcripts,
            )

            response = Response(
                content,
                headerlist=[
                    ("Content-Language", language),
                ],
                charset="utf8",
            )
            response.content_type = mimetype
        except Exception:  # pylint: disable=broad-except
            edx_video_id = self.edx_video_id and self.edx_video_id.strip()
            log.warning(
                f"[transcript/translation] {self.location}: ",
                f"Transcript not found for {edx_video_id} (language: {self.transcript_language})",
            )
            response = self.get_static_transcript(request, transcripts)
        return response

    def handle_transcript_download(self, transcripts, lang):
        """Handler for the transcript/download endpoint"""
        try:
            content, filename, mimetype = self.get_transcript_from_blockstore(
                language=lang,
                output_format=Transcript.SRT,
                transcripts=transcripts,
            )
        except NotFoundError:
            return Response(status=404)

        headerlist = [
            ("Content-Language", self.transcript_language),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ]

        response = Response(content, headerlist=headerlist, charset="utf8")
        response.content_type = mimetype
        return response

    @XBlock.handler
    def transcript(self, request, dispatch):  # pylint: disable=unused-argument
        """Handler for transcripts"""
        transcripts = self.get_transcripts_info()
        if dispatch.startswith("translation"):
            path = request.path_info
            language = path.replace("translation", "").strip("/")
            return self.handle_transcript_translation(request, transcripts, language)
        elif dispatch.startswith("download"):
            params = {}
            if hasattr(request, 'params'):
                params = request.params
            elif hasattr(request, 'query_params'):
                params = request.query_params
            lang = params.get("lang", None)
            return self.handle_transcript_download(transcripts, lang)
        else:
            log.debug("Path not supported.")
            response = Response(status=404)
        return response

    @classmethod
    def parse_xml(
        cls, node, runtime, keys, id_generator=None
    ):  # pylint: disable=unused-argument
        """
        Parse block XML.

        This is short circuiting some methods in the original `parse_xml`
        method and skipping adding the child nodes to the class.

        Everything we need is already included in the block properties,
        so we don't need to look at the children nor pass them through
        the runtime.
        """
        block = runtime.construct_xblock_from_class(cls, keys)

        for name, value in node.items():
            cls._set_field_if_present(block, name, value, {})

        return block