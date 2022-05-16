# -*- coding: utf-8 -*-
"""
Image XBlock.
"""
from xblock.core import XBlock
from xblock.fields import Scope, String

from .utils import StudentViewBlockMixin, _

try:
    from xblockutils.studio_editable import StudioEditableXBlockMixin
except ImportError:
    class StudioEditableXBlockMixin:
        """
        Dummy class to use when running outside of Open edX.
        """


class ImageBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for images.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        default='Image',
        scope=Scope.content,
    )

    alt_text = String(
        display_name=_('Alt Text'),
        help=_('The alt text for screen readers.'),
        default='',
        scope=Scope.content,
    )

    image_url = String(
        display_name=_('Image URL'),
        help=_('The url for the image.'),
        default='',
        scope=Scope.content,
    )

    caption = String(
        display_name=_('Image Caption'),
        help=_('The legend/caption displayed under the image. Optional.'),
        default='',
        scope=Scope.content,
    )

    citation = String(
        display_name=_('Image Citation'),
        help=_('Citation/credit explaining where the image is from. Optional.'),
        default='',
        scope=Scope.content,
    )

    extended_desc = String(
        display_name=_('Extended Description'),
        help=_('Extended description for the image. Optional.'),
        default='',
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
        'alt_text',
        'image_url',
        'caption',
        'citation',
        'extended_desc',
    )

    student_view_template = 'templates/image_student_view.html'
    css_resource_url = 'public/css/image-xblock.css'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'alt_text': self.alt_text,
            'image_url': self.expand_static_url(self.image_url),
            'caption': self.caption,
            'citation': self.citation,
            'extended_desc': self.extended_desc,
        }
