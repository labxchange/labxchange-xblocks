# -*- coding: utf-8 -*-
"""
Annotated Video XBlock.
"""
import json

from django.conf import settings
from webob import Response
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import List, Scope, String

from .utils import LX_BLOCK_TYPES_OVERRIDE, StudentViewBlockMixin, _, xblock_specs_from_categories

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


class AnnotatedVideoBlock(
    XBlock,
    StudentViewBlockMixin,
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin,
):
    """
    XBlock for annotated video.
    """
    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Annotated video",
        scope=Scope.content,
    )

    video_id = String(
        display_name=_("Video ID"),
        help=_("Video child block ID"),
        scope=Scope.content,
    )

    # Data format: [
    #   {
    #     "id": "715ad1df-1be0-4fe7-b0d0-fc21e2a0d050",
    #     "title": "Title",
    #     "description": "Description",
    #     "start": "1",
    #     "end": "10",
    #     "tags": ["help", "tag"],
    #     "link": "https://opencraft.com",
    #     "image_url": "/static/image.png",
    #     "image_alt": "Image alternative text",
    #     "question": {
    #       "type": "select",
    #       "question": "The questions",
    #       "answers": [
    #         {
    #           "text": "First answer",
    #           "correct": true
    #         }, {
    #           "text": "Second answer",
    #           "correct": false
    #         }
    #       ]
    #     }
    #   }
    #
    # Question types:
    #   - select
    #   - input
    annotations = List(
        display_name=_("Annotations"),
        default=[],
        scope=Scope.content,
        help=_("The annotations of the video."),
    )

    completion_mode = XBlockCompletionMode.AGGREGATOR

    has_children = True
    allowed_nested_blocks = xblock_specs_from_categories(('lx_image', 'video'))

    editable_fields = (
        "display_name",
        "video_id",
        "annotations"
    )

    student_view_template = 'templates/annotated_video_student_view.html'

    @XBlock.handler
    def student_view_data_and_user_state(self, request, suffix=""):  # pylint: disable=unused-argument
        """
        Return content and settings for student view.
        """
        child_blocks = []
        annotations = []
        video_block = None

        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id, block_type_overrides=LX_BLOCK_TYPES_OVERRIDE)

            if child_block:
                block_type = child_block.scope_ids.block_type
                # We can assume there's going to be only one video
                # associated with the annotated video block to avoid calculating
                # the replica id when using this in pathways.
                if block_type in ["video", "lx_video"]:
                    video_block = child_block
                child_block_data = {
                    "usage_id": str(child_usage_id),
                    "block_type": block_type,
                    "display_name": child_block.display_name,
                }
                child_blocks.append(child_block_data)

        for embedded_annotation in self.annotations:
            annotation = embedded_annotation.copy()
            if embedded_annotation.get("image_url"):
                annotation["image_url"] = self.expand_static_url(
                    embedded_annotation.get("image_url"),
                )
            annotations.append(annotation)

        state = {
            "display_name": self.display_name,
            "annotations": annotations,
            "child_blocks": child_blocks,
            "video_id": self.video_id,
        }

        if video_block:
            state.update({
                "video_poster": settings.YOUTUBE['IMAGE_API'].format(
                    youtube_id=video_block.youtube_id_1_0,
                ),
                "video_youtube_id": video_block.youtube_id_1_0,
            })

        return Response(
            json.dumps(state),
            content_type='application/json',
            charset='UTF-8'
        )
