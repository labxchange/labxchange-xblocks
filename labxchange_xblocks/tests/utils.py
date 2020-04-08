# -*- coding: utf-8 -*-
import json
import re
from unittest import TestCase
from xml.dom import minidom

import mock
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from xblock.runtime import Runtime


class BlockTestCaseBase(TestCase):

    block_type = None
    block_class = None

    def setUp(self):
        super(BlockTestCaseBase, self).setUp()
        self.keys = ScopeIds('a_user', self.block_type, 'def_id', 'usage_id')
        self.runtime_mock = mock.Mock(spec=Runtime)
        self.runtime_mock.construct_xblock_from_class = mock.Mock(side_effect=self._construct_xblock_mock)
        self.runtime_mock.local_resource_url = lambda self, u: u
        self.runtime_mock.get_policy = mock.Mock(return_value={})

    def _construct_xblock_mock(self, cls, keys, field_data):
        """
        Builds target xblock instance
        """
        return cls(self.runtime_mock, scope_ids=keys, field_data=field_data)

    def assertXmlEqual(self, xml_str_a, xml_str_b):
        """
        Assert that the given XML strings are equal,
        ignoring attribute order and some whitespace variations.
        """
        def clean(xml_str):
            # Collapse repeated whitespace:
            xml_str = re.sub(r'(\s)\s+', r'\1', xml_str)
            xml_bytes = xml_str.encode('utf8')
            return minidom.parseString(xml_bytes).toprettyxml()
        self.assertEqual(clean(xml_str_a), clean(xml_str_b))

    def _test_student_view_data(self, field_data, expected_data):
        block = self._construct_xblock_mock(self.block_class, self.keys, field_data=DictFieldData(field_data))

        data = block.student_view_data(None)
        self.assertDictEqual(data, expected_data)

        handler_response = block.v1_student_view_data(mock.Mock())
        self.assertDictEqual(data, json.loads(handler_response.body.decode("utf-8")))

    def _test_student_view(self, field_data, expected_html):
        block = self._construct_xblock_mock(self.block_class, self.keys, field_data=DictFieldData(field_data))

        fragment = block.student_view(None)
        self.assertXmlEqual(fragment.content, expected_html)
