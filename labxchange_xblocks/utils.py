"""
Helper code.
"""
import json

import pkg_resources
from django.template import Context, Template
from django.template.defaulttags import register
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock, XBlockMixin

module_name = __name__

try:
    from static_replace import replace_static_urls
    replace_urls_available = True
except ImportError:
    replace_urls_available = False


# Used to override block types when getting block data of children
LX_BLOCK_TYPES_OVERRIDE = {
    'problem': 'lx_question',
    'video': 'lx_video',
    'html': 'lx_html',
}


@register.filter
def get_xblock_content(child_blocks, usage_id):
    """
    Helper function to get the content of an xblock from the standard `child_blocks` list,
    given an xblock `usage_id`.
    """
    for block in child_blocks:
        if block.get("usage_id") == usage_id:
            return block.get("content")

    return None


def _(text):
    """
    Mark string for extraction.
    """
    return text


def xblock_specs_from_categories(categories):
    """
    Return XBlock classes for available XBlocks from categories.
    """
    return (
        class_ for category, class_ in XBlock.load_classes() if category in categories
    )


class StudentViewBlockMixin(XBlockMixin):
    """
    Mixin for shared code for student views.
    """

    student_view_template = None
    css_resource_url = None
    js_resource_url = None
    js_init_function = None

    @property
    def user_state(self):
        return {}

    def student_view_data(self, context=None):  # pylint: disable=unused-argument
        """
        Return content and settings for student view.
        """
        return {}

    def _block_type_overrides(self, request):
        """
        Returns LX_BLOCK_TYPES_OVERRIDE if lx_block_types=1 is part of the request.
        """
        # Deal with the many types of request objects that might come through here
        if hasattr(request, 'url'):  # WebOb
            url = request.url
        elif hasattr(request, 'get_full_path'):  # HttpRequest
            url = request.get_full_path()
        else:
            url = ''

        block_type_overrides = None
        if 'lx_block_types=1' in url:
            block_type_overrides = LX_BLOCK_TYPES_OVERRIDE
        return block_type_overrides

    @XBlock.supports("multi_device")  # Mark as mobile-friendly
    def student_view(self, context=None):
        """
        Render student view for LMS.
        """
        return self._lms_view(context, 'student_view')

    @XBlock.supports("multi_device")  # Mark as mobile-friendly
    def public_view(self, context=None):
        """
        Render public view for LMS.
        """
        return self._lms_view(context, 'public_view')

    def add_children_to_fragment(self, fragment, child_view, initial_context, render_context):
        """
        Add content for LMS view
        """
        if self.has_children:
            child_blocks_data = []
            for child_usage_id in self.children:
                child_block = self.runtime.get_block(child_usage_id)
                if child_block:
                    child_block_fragment = child_block.render(child_view, initial_context)
                    child_block_content = child_block_fragment.content
                    fragment.add_fragment_resources(child_block_fragment)
                    child_blocks_data.append({
                        'usage_id': str(child_usage_id),
                        'content': child_block_content,
                        'display_name': child_block.display_name,
                    })
            render_context['child_blocks'] = child_blocks_data
        fragment.add_content(self._render_django_template(self.student_view_template, render_context))

    def add_js_resource(self, fragment):
        if self.js_resource_url and self.js_init_function:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, self.js_resource_url))
            fragment.initialize_js(
                self.js_init_function, {'user_state': self.user_state}
            )

    def add_css_resource(self, fragment):
        if self.css_resource_url:
            fragment.add_css_url(self.runtime.local_resource_url(self, self.css_resource_url))

    def _render_django_template(self, template_path, context=None, i18n_service=None):
        """
        Evaluate a django template by resource path, applying the provided context.
        """
        template_str = self._load_unicode_template(template_path)
        template = Template(template_str)
        return template.render(Context(context or {}))

    def _load_unicode_template(self, resource_path):
        """
        Gets the content of a resource as UTF8
        """
        resource_content = pkg_resources.resource_string(module_name, resource_path)
        return resource_content.decode('utf-8')

    def _lms_view(self, context, child_view):
        """
        Render the view for LMS.
        """
        context = context or {}

        fragment = Fragment()

        self.add_children_to_fragment(
            fragment,
            child_view,
            context,
            self.student_view_data(),
        )

        self.add_css_resource(fragment)
        self.add_js_resource(fragment)
        return fragment

    @XBlock.handler
    def v1_student_view_data(self, request, suffix=None):  # pylint: disable=unused-argument
        """
        Return JSON representation of content and settings for student view.
        """
        context = {
            'block_type_overrides': self._block_type_overrides(request),
        }
        return Response(
            json.dumps(self.student_view_data(context=context)),
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
        html_str = '"{}"'.format(url)  # The static replacers look for quoted URLs like this
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
            if replace_urls_available:
                url = replace_static_urls(html_str, None, course_id=self.runtime.course_id)[1:-1]

        return url
