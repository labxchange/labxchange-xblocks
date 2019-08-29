# -*- coding: utf-8 -*-
"""
Document XBlock.
"""

from __future__ import absolute_import, unicode_literals

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import StudentViewBlockMixin, _


class DocumentBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for documents.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The name of the document.'),
        default='Document',
        scope=Scope.content,
    )

    document_type = String(
        display_name=_('Document Type'),
        help=_('The type of the document.'),
        default='application/pdf',
        values=[
            {'display_name': _('PDF'), 'value': 'application/pdf'},
        ],
        scope=Scope.content,
    )

    document_url = String(
        display_name=_('Document URL'),
        help=_('The url of the document file.'),
        default='',
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
        'document_type',
        'document_url',
    )

    student_view_template = 'templates/document_student_view.html'
    css_resource_url = 'public/css/document-xblock.css'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'document_type': self.document_type,
            'document_url': self.document_url,
        }
