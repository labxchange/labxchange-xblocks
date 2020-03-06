"""
Helper code.
"""
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
            child_blocks_data = []
            for child_usage_id in self.children:
                child_block = self.runtime.get_block(child_usage_id)
                if child_block:
                    child_block_fragment = child_block.render('student_view', context)
                    child_block_content = child_block_fragment.content
                    fragment.add_fragment_resources(child_block_fragment)
                    child_blocks_data.append({
                        'content': child_block_content,
                        'display_name': child_block.display_name,
                    })
            render_context['child_blocks'] = child_blocks_data

        fragment.add_content(loader.render_template(self.student_view_template, render_context))

        if self.css_resource_url:
            fragment.add_css_url(self.runtime.local_resource_url(self, self.css_resource_url))

        return fragment

    public_view = student_view

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

    def expand_static_url(self, url):
        """
        Expand a static URL ("Studio URL").

        This is required to make URLs like '/static/image.png' work (note: that is the
        only portable URL format for static files that works across export/import and reruns).
        This method is unfortunately a bit hackish since XBlock does not provide a low-level API
        for this.

        Input: a string like "/static/image.png"
        Output: an absolute URL as a string, e.g. "https://cdn.none/course/234/image.png"
        """
        html_str = u'"{}"'.format(url)  # The static replacers look for quoted URLs like this
        if hasattr(self.runtime, 'transform_static_paths_to_urls'):
            # This runtime supports the newest API for replacing static URLs,
            # where the static assets are specific to each XBlock:
            url = self.runtime.transform_static_paths_to_urls(self, html_str)[1:-1]
        elif hasattr(self.runtime, 'replace_urls'):
            # This is the LMS modulestore runtime, which has this API:
            url = self.runtime.replace_urls(html_str)[1:-1]
        elif hasattr(self.runtime, 'course_id'):
            # edX Studio uses a different runtime for 'studio_view' than 'student_view',
            # and the 'studio_view' runtime doesn't provide the replace_urls API.
            try:
                from static_replace import replace_static_urls
                url = replace_static_urls(html_str, None, course_id=self.runtime.course_id)[1:-1]
            except ImportError:
                pass
        return url
