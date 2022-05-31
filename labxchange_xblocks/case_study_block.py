# -*- coding: utf-8 -*-
"""
Case Study XBlock.
"""
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import List, Scope, String

from .utils import StudentViewBlockMixin, _

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


class CaseStudyBlock(
    XBlock,
    StudentViewBlockMixin,
    StudioContainerWithNestedXBlocksMixin,
    StudioEditableXBlockMixin,
    XBlockWithPreviewMixin,
):
    """
    XBlock for case studies and teaching guides.
    """

    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Case Study",
        scope=Scope.content,
    )

    # TODO: can we enforce stronger validation here, such as nested types, data shape?
    sections = List(
        help=_("""List of sections for this component.
For example: [
    {
        "title": "Section 1",
        "children": [
            { "inlinehtml": "<span>hello</span>" },
            { "usage_id": "lb:LabXchange:770d8e06:video:1-1" },
        ],
    }
]
"""),
        scope=Scope.content,
        display_name=_("Sections"),
        enforce_type=True,
    )

    attachments = List(
        help=_("List of ids of child xblocks to be shown as attachments, but not inline."),
        scope=Scope.content,
        display_name=_("Attachments"),
        enforce_type=True,
    )

    editable_fields = (
        "display_name",
        "sections",
        "attachments",
    )

    completion_mode = XBlockCompletionMode.AGGREGATOR
    has_children = True
    student_view_template = "templates/case_study_student_view.html"

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        valid_child_block_ids = set()
        child_blocks = []
        context = context or {}

        block_type_overrides = context.get('block_type_overrides')
        for child_usage_id in self.children:  # pylint: disable=no-member
            child_block = self.runtime.get_block(child_usage_id, block_type_overrides=block_type_overrides)
            if child_block:
                valid_child_block_ids.add(str(child_usage_id))
                child_block_data = {
                    "usage_id": str(child_usage_id),
                    "block_type": child_block.scope_ids.block_type,
                    "display_name": child_block.display_name,
                }
                child_blocks.append(child_block_data)

        sections = []
        for section in self.sections:
            children = []
            for child in section.get("children"):
                # Here we only add valid entries to the sections returned.
                # This ensures that clients always get type-safe response.
                if "inlinehtml" in child and isinstance(child["inlinehtml"], str):
                    children.append({
                        "inlinehtml": child["inlinehtml"]
                    })
                elif child.get("usage_id"):
                    # if we're embedding, it needs to be a valid xblock
                    if child.get("embed", True) and not child["usage_id"] in valid_child_block_ids:
                        continue

                    children.append({
                        "usage_id": child["usage_id"],
                        "embed": child.get("embed", True),
                    })

            sections.append({
                "title": section.get("title", ""),
                "children": children,
            })

        attachments = []
        for xblock_id in self.attachments:
            if isinstance(xblock_id, str):
                attachments.append(xblock_id)

        return {
            "display_name": self.display_name,
            "sections": sections,
            "child_blocks": child_blocks,
            "attachments": attachments,
        }
