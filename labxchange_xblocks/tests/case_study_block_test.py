# -*- coding: utf-8 -*-
"""
Case study block tests
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import ddt
from xblock.completable import XBlockCompletionMode
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from xblock.test.test_parsing import XmlTest

from labxchange_xblocks.case_study_block import CaseStudyBlock
from labxchange_xblocks.document_block import DocumentBlock
from labxchange_xblocks.image_block import ImageBlock
from labxchange_xblocks.tests.utils import BlockTestCaseBase


@ddt.ddt
class CaseStudyBlockTestCase(XmlTest, BlockTestCaseBase):
    """
    Case study block test case
    """
    block_type = "lx_case_study"
    block_class = CaseStudyBlock
    maxDiff = None

    def test_is_aggregator(self):
        self.assertEqual(
            XBlockCompletionMode.get_mode(CaseStudyBlock),
            XBlockCompletionMode.AGGREGATOR,
        )

    def test_student_view_data_with_defaults(self):

        field_data = {"display_name": "Case Study 1"}
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        document_block_keys = ScopeIds(
            "a_user", "lx_document", "def_id_document", "usage_id_document"
        )
        document_block = DocumentBlock(
            self.runtime_mock,
            scope_ids=document_block_keys,
            field_data=DictFieldData({"display_name": "CS Document", }),
        )
        block.children.append(document_block.scope_ids.block_type)

        image_block_keys = ScopeIds(
            "a_user", "lx_image", "def_id_image", "usage_id_image"
        )
        image_block = self._construct_xblock_mock(
            ImageBlock,
            image_block_keys,
            field_data=DictFieldData({"display_name": "CS Image", }),
        )
        block.children.append(image_block.scope_ids.block_type)

        def get_block(usage_id, block_type_overrides):
            if usage_id == "lx_document":
                return document_block
            if usage_id == "lx_image":
                return image_block

        self.runtime_mock.get_block.side_effect = get_block

        data = block.student_view_data(context=None)

        self.assertDictEqual(
            data,
            {
                "child_blocks": [
                    {
                        "block_type": "lx_document",
                        "display_name": "CS Document",
                        "usage_id": "lx_document",
                    },
                    {
                        "block_type": "lx_image",
                        "display_name": "CS Image",
                        "usage_id": "lx_image",
                    },
                ],
                "display_name": "Case Study 1",
                "sections": [],
                "attachments": [],
            },
        )

    @ddt.data(
        (
            [
                {
                    "title": "Section One",
                    "children": [
                        {"inlinehtml": "<span>hello</span>"},
                        {"usage_id": "lx_image", "embed": True},
                        {
                            "inlinehtml": ["ignore", "this"]
                        },  # invalid type here will be dropped from output
                        {"usage_id": "lx_image", "embed": True},  # dups are ok here
                    ],
                },
                {
                    "title": "Section Two",
                    "children": [
                        {"inlinehtml": ""},
                        {
                            "usage_id": "NOTFOUNDINVALID"
                        },  # invalid usage_ids should be silently ignored
                    ],
                },
            ],
            [],
            [
                {
                    "title": "Section One",
                    "children": [
                        {"inlinehtml": "<span>hello</span>"},
                        {"usage_id": "lx_image", "embed": True},
                        {"usage_id": "lx_image", "embed": True},  # dups are ok here
                    ],
                },
                {"title": "Section Two", "children": [{"inlinehtml": ""}, ], },
            ],
            [],
        ),
        (
            [
                {
                    "title": "Section One",
                    "children": [
                        {"inlinehtml": "<span>hello</span>"},
                        {"usage_id": "lx_image", "embed": True},
                    ],
                },
                {
                    "title": "Section Two",
                    "children": [{"inlinehtml": "<p>One</p><p>Two</p>"}, ],
                },
            ],
            [],
            [
                {
                    "title": "Section One",
                    "children": [
                        {"inlinehtml": "<span>hello</span>"},
                        {"usage_id": "lx_image", "embed": True},
                    ],
                },
                {
                    "title": "Section Two",
                    "children": [{"inlinehtml": "<p>One</p><p>Two</p>"}, ],
                },
            ],
            [],
        ),
        ([], ["lx_image"], [], ["lx_image"],),
        ([], ["lx_document", "lx_image"], [], ["lx_document", "lx_image"],),
        # invalid/notfound attachments are kept because they may be non-xblock attachments
        # (eg. a labxchange native asset)
        (
            [],
            ["lx_document", "does_not_exist", "lx_image"],
            [],
            ["lx_document", "does_not_exist", "lx_image"],
        ),
        (
            [],
            ["lx_document", {"key": "invalid type"}, "lx_image"],
            [],
            ["lx_document", "lx_image"],
        ),
        (
            [],
            # duplicates are ok in attachments
            ["lx_document", "lx_document", "lx_image"],
            [],
            ["lx_document", "lx_document", "lx_image"],
        ),
    )
    @ddt.unpack
    def test_student_view_data(
        self, sections, attachments, expected_sections, expected_attachments
    ):

        field_data = {"display_name": "Case Study 3"}
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        document_block_keys = ScopeIds(
            "a_user", "lx_document", "def_id_document", "usage_id_document"
        )
        document_block = DocumentBlock(
            self.runtime_mock,
            scope_ids=document_block_keys,
            field_data=DictFieldData({"display_name": "CS Document", }),
        )
        block.children.append(document_block.scope_ids.block_type)

        image_block_keys = ScopeIds(
            "a_user", "lx_image", "def_id_image", "usage_id_image"
        )
        image_block = self._construct_xblock_mock(
            ImageBlock,
            image_block_keys,
            field_data=DictFieldData({"display_name": "CS Image", }),
        )
        block.children.append(image_block.scope_ids.block_type)

        block.sections = sections
        block.attachments = attachments

        def get_block(usage_id, block_type_overrides):
            if usage_id == "lx_document":
                return document_block
            if usage_id == "lx_image":
                return image_block

        self.runtime_mock.get_block.side_effect = get_block

        data = block.student_view_data(context=None)

        self.assertDictEqual(
            data,
            {
                "child_blocks": [
                    {
                        "block_type": "lx_document",
                        "display_name": "CS Document",
                        "usage_id": "lx_document",
                    },
                    {
                        "block_type": "lx_image",
                        "display_name": "CS Image",
                        "usage_id": "lx_image",
                    },
                ],
                "display_name": "Case Study 3",
                "sections": expected_sections,
                "attachments": expected_attachments,
            },
        )

    def test_student_view_data_invalid_attachment(self):

        field_data = {"display_name": "Case Study 4"}
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        document_block_keys = ScopeIds(
            "a_user", "lx_document", "def_id_document", "usage_id_document"
        )
        document_block = DocumentBlock(
            self.runtime_mock,
            scope_ids=document_block_keys,
            field_data=DictFieldData({"display_name": "CS Document", }),
        )
        block.children.append(document_block.scope_ids.block_type)

        image_block_keys = ScopeIds(
            "a_user", "lx_image", "def_id_image", "usage_id_image"
        )
        image_block = self._construct_xblock_mock(
            ImageBlock,
            image_block_keys,
            field_data=DictFieldData({"display_name": "CS Image", }),
        )
        block.children.append(image_block.scope_ids.block_type)

        with self.assertRaises(TypeError):
            block.sections = {"key": "invalid"}
        with self.assertRaises(TypeError):
            block.sections = "foo"
        block.sections = []

        with self.assertRaises(TypeError):
            block.attachments = {"key": "invalid"}
        with self.assertRaises(TypeError):
            block.attachments = "foo"
        block.attachments = ["lx_image"]

        def get_block(usage_id, block_type_overrides):
            if usage_id == "lx_document":
                return document_block
            if usage_id == "lx_image":
                return image_block

        self.runtime_mock.get_block.side_effect = get_block

        data = block.student_view_data(context=None)

        self.assertDictEqual(
            data,
            {
                "child_blocks": [
                    {
                        "block_type": "lx_document",
                        "display_name": "CS Document",
                        "usage_id": "lx_document",
                    },
                    {
                        "block_type": "lx_image",
                        "display_name": "CS Image",
                        "usage_id": "lx_image",
                    },
                ],
                "display_name": "Case Study 4",
                "sections": [],
                "attachments": ["lx_image"],
            },
        )
