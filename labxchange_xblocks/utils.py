"""
Helper code.
"""
from __future__ import absolute_import, unicode_literals

import json

from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock, XBlockMixin
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import NestedXBlockSpec

loader = ResourceLoader(__name__)


def _(text):
    """
    Mark string for extraction.
    """
    return text


def xblock_specs_from_categories(categories):
    """
    Return NestedXBlockSpecs for available XBlocks from categories.
    """
    return (
        NestedXBlockSpec(class_, category=category, label=class_.display_name.default)
        for category, class_ in XBlock.load_classes() if category in categories
    )


class StudentViewBlockMixin(XBlockMixin):
    """
    Mixin for shared code for student views.
    """

    student_view_template = None
    css_resource_url = None

    def student_view_data(self, context=None):  # pylint: disable=unused-argument
        """
        Return content and settings for student view.
        """
        return {}

    @XBlock.supports("multi_device")  # Mark as mobile-friendly
    def student_view(self, context=None):
        """
        Render student view for LMS.
        """
        context = context or {}

        fragment = Fragment()
        render_context = self.student_view_data()

        if self.has_children:
            for child_block_data in render_context['child_blocks']:
                child_block_id = child_block_data['block_id']
                child_block = self.runtime.get_block(child_block_id)
                if child_block:
                    child_block_fragment = child_block.render('student_view', context)
                    child_block_content = child_block_fragment.content
                    fragment.add_fragment_resources(child_block_fragment)
                    child_block_data['content'] = child_block_content

        fragment.add_content(loader.render_template(self.student_view_template, render_context))

        if self.css_resource_url:
            fragment.add_css_url(self.runtime.local_resource_url(self, self.css_resource_url))

        return fragment

    @XBlock.handler
    def v1_student_view_data(self, request, suffix=None):  # pylint: disable=unused-argument
        """
        Return JSON representation of content and settings for student view.
        """
        return Response(
            json.dumps(self.student_view_data()),
            content_type='application/json',
            charset='UTF-8'
        )
