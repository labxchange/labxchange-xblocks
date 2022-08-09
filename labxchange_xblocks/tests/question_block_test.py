# -*- coding: utf-8 -*-
"""
Question block tests
"""
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# open edx runtime uses defusedxml.lxml.RestrictedElement in some form,
# but this seems to work fine for now for tests
import json
import xml.etree.ElementTree as ET

import ddt
from mock import Mock
from xblock.field_data import DictFieldData

from labxchange_xblocks.question_block import (
    QuestionBlock,
    parse_choiceresponse_from_node,
    parse_hints_from_node,
    parse_optionresponse_from_node,
    parse_stringresponse_from_node
)
from labxchange_xblocks.tests.utils import BlockTestCaseBase


@ddt.ddt
class QuestionBlockTestCase(BlockTestCaseBase):
    """
    Test the question block (tests that require block runtime mocking)
    """

    maxDiff = None

    block_type = "lx_question"
    block_class = QuestionBlock

    data_for_user_state = (
        (  # defaults for string response (no attempts yet)
            {
                "question_data": {
                    "type": "stringresponse",
                    "answers": ["correct"],
                    "question": "The answer is correct.",
                    "comments": {},
                },
            },
            {
                "maxAttempts": 0,
                "current_score": 0,
                "total_possible": 1,
                "questionData": {
                    "type": "stringresponse",
                    "question": "The answer is correct.",
                    "studentAnswer": {},
                },
                "hints": [],
                "studentAttempts": 0,
                "correct": None,
            },
        ),
        (  # correct string response
            {
                "question_data": {
                    "type": "stringresponse",
                    "answers": ["correct"],
                    "question": "The answer is correct.",
                    "comments": {},
                },
                "student_answer": {
                    "response": "correct",
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 1,
                "total_possible": 1,
                "questionData": {
                    "type": "stringresponse",
                    "question": "The answer is correct.",
                    "studentAnswer": {"response": "correct"},
                    "comment": "",
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": True,
            },
        ),
        (  # incorrect string response with no more attempts
            # (should display the answer)
            {
                "question_data": {
                    "type": "stringresponse",
                    "answers": ["correct"],
                    "question": "The answer is correct.",
                    "comments": {},
                },
                "student_answer": {
                    "response": "incorrect",
                },
                "student_attempts": 2,
                "max_attempts": 2,
            },
            {
                "maxAttempts": 2,
                "current_score": 0,
                "total_possible": 1,
                "questionData": {
                    "type": "stringresponse",
                    "question": "The answer is correct.",
                    "studentAnswer": {"response": "incorrect"},
                    "comment": "",
                    "answer": "correct",
                },
                "hints": [],
                "studentAttempts": 2,
                "correct": False,
            },
        ),
        (  # correct option response
            {
                "question_data": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "correct": False,
                            "comment": "comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "correct": True,
                            "comment": "comment two",
                        },
                    ],
                },
                "student_answer": {
                    "index": 1,
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 1,
                "total_possible": 1,
                "questionData": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "checked": False,
                            "comment": "",
                        },
                        {
                            "content": "two",
                            "checked": True,
                            "comment": "comment two",
                        },
                    ],
                    "studentAnswer": {"index": 1},
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": True,
            },
        ),
        (  # correct multiple choice response
            {
                "question_data": {
                    "type": "choiceresponse",
                    "question": "The answer is two and three.",
                    "choices": [
                        {
                            "content": "on\u00e9",
                            "correct": False,
                            "selected_comment": "comment on\u00e9",
                            "unselected_comment": "un comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "correct": True,
                            "selected_comment": "comment two",
                            "unselected_comment": "un comment two",
                        },
                        {
                            "content": "three",
                            "correct": True,
                            "selected_comment": "comment three",
                            "unselected_comment": "un comment three",
                        },
                    ],
                    "comments": {
                        "1 2": "yay!",
                        "0 2": "nope",
                    },
                },
                "student_answer": {
                    "selected": [2, 1],
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 1,
                "total_possible": 1,
                "questionData": {
                    "type": "choiceresponse",
                    "question": "The answer is two and three.",
                    "choices": [
                        {
                            "content": "on\u00e9",
                            "checked": False,
                            "comment": "un comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "checked": True,
                            "comment": "comment two",
                        },
                        {
                            "content": "three",
                            "checked": True,
                            "comment": "comment three",
                        },
                    ],
                    "comment": "yay!",
                    "studentAnswer": {"selected": [2, 1]},
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": True,
            },
        ),
        (  # correct option response, parsed from Open edX response
            {
                "question_data": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "correct": False,
                            "comment": "comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "correct": True,
                            "comment": "comment two",
                        },
                    ],
                },
                "student_answer": {
                    "response": "two",
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 1,
                "total_possible": 1,
                "questionData": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "checked": False,
                            "comment": "",
                        },
                        {
                            "content": "two",
                            "checked": True,
                            "comment": "comment two",
                        },
                    ],
                    "studentAnswer": {"index": 1},
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": True,
            },
        ),
        (  # incorrect option response, parsed from Open edX response
            {
                "question_data": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "correct": False,
                            "comment": "comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "correct": True,
                            "comment": "comment two",
                        },
                    ],
                },
                "student_answer": {
                    "response": "on\u00e9",
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 0,
                "total_possible": 1,
                "questionData": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "checked": True,
                            "comment": "comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "checked": False,
                            "comment": "",
                        },
                    ],
                    "studentAnswer": {"index": 0},
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": False,
            },
        ),
        (  # invalid option response, parsed from Open edX response
            {
                "question_data": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "correct": False,
                            "comment": "comment on\u00e9",
                        },
                        {
                            "content": "two",
                            "correct": True,
                            "comment": "comment two",
                        },
                    ],
                },
                "student_answer": {
                    "response": "three",
                },
                "student_attempts": 1,
            },
            {
                "maxAttempts": 0,
                "current_score": 0,
                "total_possible": 1,
                "questionData": {
                    "type": "optionresponse",
                    "display": "radio",
                    "question": "The answer is two.",
                    "options": [
                        {
                            "content": "on\u00e9",
                            "checked": False,
                            "comment": "",
                        },
                        {
                            "content": "two",
                            "checked": False,
                            "comment": "",
                        },
                    ],
                    "studentAnswer": {},
                },
                "hints": [],
                "studentAttempts": 1,
                "correct": None,
            },
        ),
    )

    @ddt.data(*data_for_user_state)
    @ddt.unpack
    def test_student_view_user_state(self, field_data, expected_data):
        """
        Test various states.
        See `data_for_user_state` for details on what is tested.
        """
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )
        response = block.student_view_user_state(Mock())
        assert json.loads(response.body.decode("utf-8")) == expected_data

    def test_student_view_data(self):
        """
        Student view data isn't used, so it shouldn't return anything.
        """
        field_data = {
            "display_name": "test",
            "max_attempts": 5,
        }
        expected_data = {}
        self._test_student_view_data(field_data, expected_data)

    def test_parse_from_xml(self):
        """
        Test transforming xml into a block
        """
        node = ET.fromstring(
            """
            <lx_question max_attempts="5" weight="2" display_name="Q1">
              <stringresponse answer="correct on\u00e9">
                <label>&lt;p&gt;lorem &lt;strong&gt;ipsum&lt;/strong&gt;&lt;/p&gt;</label>
                <correcthint>this is the better correct</correcthint>
                <additional_answer answer="correct two">
                    <correcthint>also correct!</correcthint>
                </additional_answer>
                <stringequalhint answer="wrong"/>
                <stringequalhint answer="also wrong!">:P</stringequalhint>
                <textline size="20"/>
              </stringresponse>
              <demandhint>
                <hint>global hint 1</hint>
                <hint>global hint 2</hint>
              </demandhint>
          </lx_question>
        """
        )
        block = QuestionBlock.parse_xml(node, self.runtime_mock, self.keys)
        expected_question_data = {
            "type": "stringresponse",
            "question": "<p>lorem <strong>ipsum</strong></p>",
            "answers": ["correct on\u00e9", "correct two"],
            "comments": {
                "correct on\u00e9": "this is the better correct",
                "also wrong!": ":P",
                "correct two": "also correct!",
            },
        }
        assert block.question_data == expected_question_data
        assert block.max_attempts == 5
        assert block.weight == 2
        assert block.display_name == "Q1"
        assert block.hints == [
            {"content": "global hint 1"},
            {"content": "global hint 2"},
        ]

    def test_lazy_parse_from_xml(self):
        """
        Test the lazy xml parsing that occurs when a QuestionBlock is loaded from a cached ProblemBlock's field data.
        """
        field_data = {
            'data': """
                <problem max_attempts="5" weight="2" display_name="Q1">
                  <stringresponse answer="correct on\u00e9">
                    <label>&lt;p&gt;lorem &lt;strong&gt;ipsum&lt;/strong&gt;&lt;/p&gt;</label>
                    <correcthint>this is the better correct</correcthint>
                    <additional_answer answer="correct two">
                        <correcthint>also correct!</correcthint>
                    </additional_answer>
                    <stringequalhint answer="wrong"/>
                    <stringequalhint answer="also wrong!">:P</stringequalhint>
                    <textline size="20"/>
                  </stringresponse>
                  <demandhint>
                    <hint>global hint 1</hint>
                    <hint>global hint 2</hint>
                  </demandhint>
              </problem>
            """
        }
        expected_data = {
            "maxAttempts": 5,
            "current_score": 0,
            "total_possible": 2.0,
            "questionData": {
                "type": "stringresponse",
                "question": "<p>lorem <strong>ipsum</strong></p>",
                "studentAnswer": {},
            },
            "hints": [
                {"content": "global hint 1"},
                {"content": "global hint 2"},
            ],
            "studentAttempts": 0,
            "correct": None,
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )
        # Note that the question_data hasn't been loaded yet
        assert block.question_data == {}
        response = block.student_view_user_state(Mock())
        assert json.loads(response.body.decode("utf-8")) == expected_data
        # ..but it has now
        assert block.question_data['type'] == "stringresponse"
        assert block.display_name == 'Q1'
        assert block.weight == 2
        assert block.max_attempts == 5

    def test_submit_answer_choiceresponse(self):
        """
        Test the submitting answer process
        """
        field_data = {
            "question_data": {
                "type": "choiceresponse",
                "question": "The answer is two and three.",
                "choices": [
                    {
                        "content": "one",
                        "correct": False,
                        "selected_comment": "comment one",
                        "unselected_comment": "un comment one",
                    },
                    {
                        "content": "two",
                        "correct": True,
                        "selected_comment": "comment two",
                        "unselected_comment": "un comment two",
                    },
                    {
                        "content": "three",
                        "correct": True,
                        "selected_comment": "comment three",
                        "unselected_comment": "un comment three",
                    },
                ],
                "comments": {
                    "1 2": "yay!",
                    "0 2": "nope",
                },
            },
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        response = block.submit_answer(request_wrap({"invalid": "key"}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is None
        assert data["questionData"]["studentAnswer"] == {}

        response = block.submit_answer(request_wrap({"selected": "invalid value"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"selected": ["invalid"]}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"selected": [-1, 1]}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is None
        assert data["questionData"]["studentAnswer"] == {}

        response = block.submit_answer(request_wrap({"selected": [0, 1]}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"selected": [0, 1]}
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"selected": [0, 1, 5]}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"selected": [0, 1]}
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"selected": [1, 2]}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"selected": [1, 2]}
        assert block.get_score().raw_earned == 1

        # once a correct answer is submitted, no more answers are accepted
        response = block.submit_answer(request_wrap({"selected": [0, 1]}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"selected": [1, 2]}
        assert block.get_score().raw_earned == 1

    def test_submit_answer_stringresponse(self):
        """
        Test the submitting answer process
        """
        field_data = {
            "question_data": {
                "type": "stringresponse",
                "question": "The answer is two or maybe three.",
                "answers": ["two", "three"],
                "comments": {
                    "three": "yep this is ok too",
                    "one": "no",
                },
            },
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        response = block.submit_answer(request_wrap({"selected": "invalid key"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"response": 3}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"response": ["invalid"]}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is None
        assert data["questionData"]["studentAnswer"] == {}

        response = block.submit_answer(request_wrap({"response": "one"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"response": "one"}
        assert data["questionData"]["comment"] == "no"
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"response": "four"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"response": "four"}
        assert data["questionData"]["comment"] == ""
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"response": "three"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"response": "three"}
        assert data["questionData"]["comment"] == "yep this is ok too"
        assert block.get_score().raw_earned == 1

        response = block.submit_answer(request_wrap({"response": "two"}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"response": "three"}
        assert data["questionData"]["comment"] == "yep this is ok too"
        assert block.get_score().raw_earned == 1

    def test_submit_answer_optionresponse(self):
        """
        Test the submitting answer process
        """
        field_data = {
            "question_data": {
                "type": "optionresponse",
                "display": "radio",
                "question": "The answer is two.",
                "options": [
                    {
                        "content": "one",
                        "correct": False,
                        "comment": "comment one",
                    },
                    {
                        "content": "three",
                        "correct": False,
                        "comment": "comment three",
                    },
                    {
                        "content": "two",
                        "correct": True,
                        "comment": "comment two",
                    },
                ],
            },
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        response = block.submit_answer(request_wrap({"selected": "invalid key"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"index": "invalid value type"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"index": "10"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"index": 3}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"index": "-7"}))
        assert response.status_code == 400
        response = block.submit_answer(request_wrap({"index": -1}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is None
        assert data["questionData"]["studentAnswer"] == {}

        response = block.submit_answer(request_wrap({"index": "0"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"index": 0}
        assert data["questionData"]["options"][0]["comment"] == "comment one"
        assert data["questionData"]["options"][1]["comment"] == ""
        assert data["questionData"]["options"][2]["comment"] == ""
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"index": 1}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"index": 1}
        assert data["questionData"]["options"][0]["comment"] == ""
        assert data["questionData"]["options"][1]["comment"] == "comment three"
        assert data["questionData"]["options"][2]["comment"] == ""
        assert block.get_score().raw_earned == 0

        response = block.submit_answer(request_wrap({"index": 2}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"index": 2}
        assert data["questionData"]["options"][0]["comment"] == ""
        assert data["questionData"]["options"][1]["comment"] == ""
        assert data["questionData"]["options"][2]["comment"] == "comment two"
        assert block.get_score().raw_earned == 1

        response = block.submit_answer(request_wrap({"index": 1}))
        assert response.status_code == 400

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"index": 2}
        assert data["questionData"]["options"][0]["comment"] == ""
        assert data["questionData"]["options"][1]["comment"] == ""
        assert data["questionData"]["options"][2]["comment"] == "comment two"
        assert block.get_score().raw_earned == 1

        # test edge case where student answers, then list of options shortened
        block.question_data = {
            "type": "optionresponse",
            "display": "radio",
            "question": "The answer is two.",
            "options": [
                {
                    "content": "one",
                    "correct": False,
                    "comment": "comment one",
                },
                {
                    "content": "three",
                    "correct": True,
                    "comment": "comment three",
                },
            ],
        }

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["questionData"]["studentAnswer"] == {"index": 2}

        response = block.submit_answer(request_wrap({"index": 1}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is True
        assert data["questionData"]["studentAnswer"] == {"index": 1}

        response = block.submit_answer(request_wrap({"index": 0}))
        assert response.status_code == 400

    def test_submit_answer_optionresponse_max_attempts(self):
        """
        Test the submitting answer process
        """
        field_data = {
            "question_data": {
                "type": "optionresponse",
                "display": "radio",
                "question": "The answer is two.",
                "options": [
                    {
                        "content": "one",
                        "correct": False,
                        "comment": "comment one",
                    },
                    {
                        "content": "three",
                        "correct": False,
                        "comment": "comment three",
                    },
                    {
                        "content": "two",
                        "correct": True,
                        "comment": "comment two",
                    },
                ],
            },
            "max_attempts": 2,
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        response = block.submit_answer(request_wrap({"index": "0"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["maxAttempts"] == 2
        assert data["studentAttempts"] == 1

        response = block.submit_answer(request_wrap({"index": "1"}))
        assert response.status_code == 200

        data = block._student_view_user_state_data()
        assert data["correct"] is False
        assert data["maxAttempts"] == 2
        assert data["studentAttempts"] == 2

        response = block.submit_answer(request_wrap({"index": "1"}))
        assert response.status_code == 400
        assert "attempts remaining" in response.json["error"]

    def test_submit_answer_broken(self):
        """
        Test the submitting answer process
        """
        field_data = {
            "question_data": {
                "type": "invalidtype",
            },
        }
        block = self._construct_xblock_mock(
            self.block_class, self.keys, field_data=DictFieldData(field_data)
        )

        response = block.submit_answer(request_wrap({"index": 1}))
        assert response.status_code == 500
        assert "invalid question type" in response.json["error"]


def request_wrap(data: dict):
    """
    Wrapper for sending data to a json handler
    """
    request = Mock()
    request.method = "POST"
    request.body = json.dumps(data).encode("utf-8")
    return request


def test_parse_hints():
    node = ET.fromstring(
        """
      <demandhint>
        <hint>global hint 1</hint>
        <hint>global hint 2</hint>
      </demandhint>
    """
    )
    expected = [
        {"content": "global hint 1"},
        {"content": "global hint 2"},
    ]
    assert parse_hints_from_node(node) == expected


def test_parse_optionresponse():
    node = ET.fromstring(
        """
      <optionresponse>
        <label>&lt;p&gt;lorem ipsum&lt;/p&gt;</label>
        <optioninput>
          <option correct="true">correct
            <optionhint>hint 1</optionhint>
          </option>
          <option correct="false">incorrect
            <optionhint>hint 2</optionhint>
          </option>
          <option>also incorrect</option>
        </optioninput>
      </optionresponse>
    """
    )
    expected = {
        "type": "optionresponse",
        "display": "dropdown",
        "question": "<p>lorem ipsum</p>",
        "options": [
            {
                "content": "correct",
                "comment": "hint 1",
                "correct": True,
            },
            {
                "content": "incorrect",
                "comment": "hint 2",
                "correct": False,
            },
            {
                "content": "also incorrect",
                "comment": "",
                "correct": False,
            },
        ],
    }
    assert parse_optionresponse_from_node(node) == expected


def test_parse_multiplechoiceresponse():
    node = ET.fromstring(
        """
      <multiplechoiceresponse>
        <label>&lt;p&gt;lorem ipsum&lt;/p&gt;</label>
        <choicegroup>
          <choice correct="true">correct
            <choicehint>hint 1 </choicehint>
          </choice>
          <choice correct="false"> incorrect
            <choicehint>hint 2</choicehint>
          </choice>
          <choice>also incorrect</choice>
        </choicegroup>
      </multiplechoiceresponse>
    """
    )
    expected = {
        "type": "optionresponse",
        "display": "radio",
        "question": "<p>lorem ipsum</p>",
        "options": [
            {
                "content": "correct",
                "comment": "hint 1",
                "correct": True,
            },
            {
                "content": "incorrect",
                "comment": "hint 2",
                "correct": False,
            },
            {
                "content": "also incorrect",
                "comment": "",
                "correct": False,
            },
        ],
    }
    assert parse_optionresponse_from_node(node) == expected


def test_parse_choiceresponse():
    node = ET.fromstring(
        """
      <choiceresponse>
        <label>&lt;p&gt;lorem&lt;/p&gt; </label>
        <checkboxgroup>
          <choice correct="true">one </choice>
          <choice correct="false">&lt;p&gt;two&lt;/p&gt;
            <choicehint selected="true">wrong! </choicehint>
            <choicehint selected="false">right!</choicehint>
          </choice>
          <choice correct="true">three</choice>
          <compoundhint value="B  A "> group comment</compoundhint>
        </checkboxgroup>
      </choiceresponse>
    """
    )
    expected = {
        "type": "choiceresponse",
        "question": "<p>lorem</p>",
        "choices": [
            {
                "content": "one",
                "selected_comment": "",
                "unselected_comment": "",
                "correct": True,
            },
            {
                "content": "<p>two</p>",
                "selected_comment": "wrong!",
                "unselected_comment": "right!",
                "correct": False,
            },
            {
                "content": "three",
                "selected_comment": "",
                "unselected_comment": "",
                "correct": True,
            },
        ],
        "comments": {
            "0 1": "group comment",
        },
    }
    assert parse_choiceresponse_from_node(node) == expected


def test_parse_stringresponse():
    node = ET.fromstring(
        """
      <stringresponse type="ci" answer="correct one">
        <label>&lt;p&gt;lorem &lt;strong&gt;ipsum&lt;/strong&gt;&lt;/p&gt;</label>
        <correcthint>this is the better correct</correcthint>
        <additional_answer answer="correct two">
            <correcthint>also correct!</correcthint>
        </additional_answer>
        <stringequalhint answer="wrong"/>
        <stringequalhint answer="also wrong!">:P</stringequalhint>
        <textline size="20"/>
      </stringresponse>
    """
    )
    expected = {
        "type": "stringresponse",
        "question": "<p>lorem <strong>ipsum</strong></p>",
        "answers": ["correct one", "correct two"],
        "comments": {
            "correct one": "this is the better correct",
            "also wrong!": ":P",
            "correct two": "also correct!",
        },
    }
    assert parse_stringresponse_from_node(node) == expected
