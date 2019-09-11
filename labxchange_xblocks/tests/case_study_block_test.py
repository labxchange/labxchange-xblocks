# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from xblock.completable import XBlockCompletionMode
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from xblock.test.test_parsing import XmlTest

from labxchange_xblocks.case_study_block import CaseStudyBlock
from labxchange_xblocks.document_block import DocumentBlock
from labxchange_xblocks.image_block import ImageBlock
from utils import BlockTestCaseBase


class CaseStudyBlockTestCase(XmlTest, BlockTestCaseBase):

    block_type = 'lx_case_study'
    block_class = CaseStudyBlock

    def test_is_aggregator(self):
        self.assertEqual(XBlockCompletionMode.get_mode(CaseStudyBlock), XBlockCompletionMode.AGGREGATOR)

    def test_student_view_data(self):

        field_data = {
            'display_name': 'Case Study 1'
        }
        block = self._construct_xblock_mock(self.block_class, self.keys, field_data=DictFieldData(field_data))

        document_block_keys = ScopeIds('a_user', 'lx_document', 'def_id_document', 'usage_id_document')
        document_block = DocumentBlock(self.runtime_mock, scope_ids=document_block_keys, field_data=DictFieldData({
            'display_name': 'CS Document',
        }))
        block.children.append(document_block.scope_ids.block_type)

        image_block_keys = ScopeIds('a_user', 'lx_image', 'def_id_image', 'usage_id_image')
        image_block = self._construct_xblock_mock(ImageBlock, image_block_keys, field_data=DictFieldData({
            'display_name': 'CS Image',
        }))
        block.children.append(image_block.scope_ids.block_type)

        def get_block(usage_id):
            if usage_id == 'lx_document':
                return document_block
            if usage_id == 'lx_image':
                return image_block

        self.runtime_mock.get_block.side_effect = get_block

        data = block.student_view_data(None)

        self.assertDictEqual(data, {
            u'child_blocks': [
                {
                    'block_type': 'lx_document',
                    'display_name': 'CS Document',
                    'usage_id': 'lx_document',
                }, {
                    'block_type': 'lx_image',
                    'display_name': 'CS Image',
                    'usage_id': 'lx_image',
                }
            ],
            u'display_name': u'Case Study 1'
        })
