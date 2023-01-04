# -*- coding: utf-8 -*-
"""
Question XBlock.
"""
import html
import json
import logging
from typing import List, Optional
from xml.etree.ElementTree import tostring

from lxml import etree
from webob import Response
from xblock import fields
from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope
from xblock.scorable import Score

from .utils import StudentViewBlockMixin, _

log = logging.getLogger(__name__)


class QuestionBlock(XBlock, StudentViewBlockMixin):
    """
    XBlock to store a question.

    OLX is mostly compatible with
    https://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/components/problem-components.html
    (the open edx problem block).
    Some features are unimplemented or not supported.

    See `labxchange_xblocks/tests/question_block_test.py`
    for expected OLX and resulting internal structure.
    """

    has_score = True

    display_name = fields.String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Question",
        scope=Scope.content,
    )

    data = fields.XMLString(
        help=_("XML data for the problem"),
        scope=Scope.content,
        enforce_type=True,
        default="<lx_question></lx_question>",
    )

    max_attempts = fields.Integer(
        display_name=_("Max Attempts"),
        help=_("Maximum number of attempts allowed.  0 means unlimited attempts."),
        scope=Scope.content,
        default=0,
        values={
            "min": 0,
        },
    )

    # Using "weight" to be more consistent with the olx we're supporting.
    # Currently though there are only two outcomes for the score: `weight` and 0,
    # so this field is semantically the points obtained on correctly answering question.
    weight = fields.Float(
        display_name=_("Weight"),
        help=_("Weight (multiplier) applied to the score."),
        scope=Scope.settings,
        default=1,
        values={
            "min": 0,
            "step": 0.1,
        },
    )

    # This field is serialized to olx as the body of the root `problem` node.
    # The structure depends on the value of the `type` key.
    # The `type` key must always be set.
    # If type is "stringresponse":
    #     {
    #         "type": "stringresponse",
    #         "answers": str[],
    #         "question": str,  # html formatted
    #         "comments": {
    #           [key]: str,  # key is the plain text answer
    #         },
    #     }
    # If type is "choiceresponse":
    #     {
    #         'type': 'choiceresponse',
    #         'question': '<p>Question?</p>',
    #         'choices': [{
    #              'content': 'response <b>correct</b>',
    #              'correct': True,
    #              'selected_comment': 'selected comment',
    #              'unselected_comment': 'unselected comment',
    #          }],
    #          'comments': {
    #              '1 2': 'group comment 1'
    #          }
    #     }
    # If type is "optionresponse":
    #     {
    #         'type': 'optionresponse',
    #         'display': 'dropdown' or 'radio',
    #         'question': '<p>Question?</p>',
    #         'options': [{
    #              'content': 'response <b>correct</b>',
    #              'correct': True,
    #              'comment': 'comment when selected',
    #          }],
    #     }
    question_data = fields.Dict(
        display_name=_("Question Data"),
        help=_("Data that defines this question."),
        scope=Scope.content,
        default={},
    )

    # [{ content: "plain text hint" }]
    hints = fields.List(
        display_name=_("Hints"),
        help=_("Array of toplevel hints for this question."),
        scope=Scope.content,
        default=[],
    )

    # student state
    student_attempts = fields.Integer(
        display_name=_("Student Attempts"),
        default=0,
        help=_("Number of attempts the student has made"),
        scope=Scope.user_state,
    )
    # this dict is structured differently depending on the question type
    # If type is "optionresponse": {"index": 1}, where `1` is index of option last submitted.
    #     if "index" is not present, then no option has been submited.
    # If type is "stringresponse": {"response": "student response"}
    #     if "response" is not present, then no option has been submited.
    # If type is "choiceresponse": {"selected": [0, 2, 3] }, where value is index of selected answer
    #     if "selected" is not present, then no option has been submited.
    student_answer = fields.Dict(
        display_name=_("Student Answer"),
        default={},
        help=_(
            "Latest student answers for this question.  Points are calculated from this field."
        ),
        scope=Scope.user_state,
    )

    student_view_template = "templates/question_student_view.html"

    @property
    def _question_data(self):
        """
        Calls parse_xml to parse the question data if it hasn't already been done.

        Once this property is accessed for a QuestionBlock, it's safe to simply access self.question_data,
        as that field has been populated.

        This is needed temporarily to handle switching between cached ProblemBlock fields and QuestionBlock
        fields, and can safely be removed when ProblemBlocks are no longer in use by LabXchange.
        """
        if not self.question_data:
            # If no question data has been parsed yet, then parse it.
            log.debug(
                f"QuestionBlock: re-parsing XML data for block {self.scope_ids.usage_id}"
            )
            try:
                node = etree.XML(self.data)
            except etree.XMLSyntaxError:
                log.error(
                    f"Error parsing problem types from xml for question block {self.scope_ids.usage_id}"
                )
                return None
            self._parse_xml(node)
            # Unmark the modified fields as "dirty" -- nothing has actually changed.
            self._clear_dirty_fields()
        return self.question_data

    def student_view_data(self, context=None):
        """
        Return all data required to render or edit the xblock.
        """
        return {}

    def _has_attempts(self) -> bool:
        return self.max_attempts < 1 or self.student_attempts < self.max_attempts

    def get_score(self):
        possible = self.weight if self.weight > 0 else 1
        correct = self._is_correct()
        earned = possible if correct else 0
        return Score(raw_earned=earned, raw_possible=possible)

    def _student_view_question_data(self, correct: bool) -> dict:
        """
        Return a copy of the question data,
        with all sensitive non-student facing information stripped.
        This should also include feedback comments based on the student answer.
        """
        t = self._question_data["type"]
        if t == "stringresponse":
            data = {
                "type": t,
                "question": self.question_data["question"],
                "studentAnswer": self.student_answer,
            }

            student_answer = self.student_answer.get("response", None) or None
            if student_answer:
                data["comment"] = {
                    k.lower(): v for k, v in self.question_data["comments"].items()
                }.get(student_answer.lower(), "")

            # only show answers if student has no attempts remaining
            if not self._has_attempts():
                data["answer"] = self.question_data["answers"][0]

            return data

        elif t == "choiceresponse":
            selected = self.student_answer.get("selected")
            has_answer = selected is not None

            # global comment based on correctness
            comment = ""
            if has_answer:
                group_key = "correct" if correct else "incorrect"
                comment = self.question_data["comments"].get(group_key, "")

            return {
                "type": t,
                "question": self.question_data["question"],
                "choices": [
                    {
                        "content": choice["content"],
                        "checked": index in selected if has_answer else False,
                        # only include comment if student has actually submitted an answer
                        "comment": (
                            choice["selected_comment"]
                            if index in selected
                            else choice["unselected_comment"]
                        )
                        if has_answer
                        else "",
                    }
                    for index, choice in enumerate(
                        self.question_data.get("choices", [])
                    )
                ],
                "comment": comment,
                "studentAnswer": self.student_answer,
            }

        elif t == "optionresponse":
            answer_index = self._answer_index(not_found=-1)
            options = self.question_data["options"]
            return {
                "type": t,
                "question": self.question_data["question"],
                "display": self.question_data["display"],
                "options": [
                    {
                        "content": option["content"],
                        "checked": i == answer_index,
                        "comment": option["comment"] if i == answer_index else "",
                    }
                    for i, option in enumerate(options)
                ],
                "studentAnswer": self.student_answer,
            }

    def _answer_index(self, student_answer=None, not_found=None) -> int:
        """
        Returns the integer index of the student's chosen answer.
        Returns -1 if no answer has been chosen yet, or if a previously chosen answer has been removed from the options.

        For optionresponse problems only.

        This method is used to convert xblock data stored by Open edX CAPA problems to the format used by this XBlock.

        If "student_answer" provided, then uses this provided dict instead of self.student_answer
        """
        t = self._question_data["type"]
        assert t == "optionresponse"

        if not student_answer:
            student_answer = self.student_answer

        options = self.question_data["options"]

        answer_index = student_answer.get("index")
        if answer_index is None and "response" in self.student_answer:
            # If no index was provided, but the actual response was (i.e. from Open edX),
            # locate the response among the available options.
            response = html.unescape(student_answer.pop("response").strip())
            for i, option in enumerate(options):
                if option.get("content") == response:
                    answer_index = i
                    student_answer["index"] = answer_index
                    break
        if answer_index is None:
            return not_found
        return answer_index

    def _is_correct(self) -> Optional[bool]:
        """
        Return:
        - None if the student hasn't submitted an answer
        - True if last answer submitted was correct
        - False if last answer submitted was incorrect
        """
        if not self.student_answer:
            return None

        t = self._question_data["type"]
        if t == "optionresponse":
            index = self._answer_index(not_found=-1)
            # this could happen if student submits answer, then options are removed later
            if index >= len(self.question_data["options"]):
                return False
            return self.question_data["options"][index]["correct"]
        if t == "stringresponse":
            response = self.student_answer["response"]
            return response.lower() in map(
                lambda x: x.lower(), self.question_data["answers"]
            )
        if t == "choiceresponse":
            selected = self.student_answer["selected"]
            for index, choice in enumerate(self.question_data["choices"]):
                if choice["correct"] != (index in selected):
                    return False
            return True

    def _student_view_user_state_data(self):
        correct = self._is_correct()
        question_data = self._student_view_question_data(correct=correct)
        weight = self.weight if self.weight > 0 else 1
        return {
            "maxAttempts": self.max_attempts,
            "current_score": weight if correct else 0,
            "total_possible": weight,
            "questionData": question_data,
            "hints": self.hints,
            "studentAttempts": self.student_attempts,
            "correct": correct,
        }

    @XBlock.handler
    def student_view_user_state(
        self, request, suffix=""
    ):  # pylint: disable=unused-argument
        """
        Return JSON representation of the block with enough data to render the student view
        (ie. everything except for the answers),
        and the student state.
        """
        state = self._student_view_user_state_data()
        return Response(
            json.dumps(state), content_type="application/json", charset="UTF-8"
        )

    @XBlock.json_handler
    def submit_answer(self, data, suffix=""):  # pylint: disable=unused-argument
        """
        Save and submit the student answer.
        Return information about correctness,
        and any applicable hints if enabled.
        """
        if self.max_attempts > 0 and self.student_attempts >= self.max_attempts:
            raise JsonHandlerError(400, "No more attempts remaining")

        if self._is_correct():
            raise JsonHandlerError(
                400, "You have already correctly answered this question."
            )

        self.student_answer = self._validated_student_answer_data(data)
        self.student_attempts += 1

        return self._student_view_user_state_data()

    def _validated_student_answer_data(self, data: dict) -> dict:
        """
        Take the `data` that is the submitted student answer,
        and either:

        - return a validated and cleaned copy of it
        - raise an informative JsonHandlerError
        """

        t = self._question_data["type"]
        if t == "optionresponse":
            index = self._answer_index(student_answer=data)
            n_options = len(self.question_data["options"])
            if index is None:
                raise JsonHandlerError(400, "`index` field missing")
            try:
                index = int(index)
            except ValueError:
                raise JsonHandlerError(
                    400, "`index` field must be an integer"
                ) from None
            if index < 0 or index >= n_options:
                raise JsonHandlerError(
                    400, "`index` field must be >= 0 and < number of options"
                )
            return {"index": index}

        elif t == "stringresponse":
            response = data.get("response")
            if response is None:
                raise JsonHandlerError(400, "`response` field missing")
            if not isinstance(response, str):
                raise JsonHandlerError(400, "`response` field must be string")
            return {"response": response}

        elif t == "choiceresponse":
            selected = data.get("selected")
            n_choices = len(self.question_data["choices"])
            if selected is None:
                raise JsonHandlerError(400, "`selected` field missing")
            if not isinstance(selected, list):
                raise JsonHandlerError(400, "`selected` field must be list")
            for i in selected:
                if not isinstance(i, int):
                    raise JsonHandlerError(
                        400, "`selected` field list values must be integers"
                    )
                if i < 0 or i >= n_choices:
                    raise JsonHandlerError(
                        400,
                        "`selected` field list values must be an index >= 0 and index < number of choices",
                    )
            return {"selected": selected}

        else:
            raise JsonHandlerError(500, "Question is broken: invalid question type")

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator=None) -> "QuestionBlock":
        """
        Parse olx into this block.
        """
        block = runtime.construct_xblock_from_class(cls, keys)
        block._parse_xml(node)  # pylint: disable=protected-access
        return block

    def _parse_xml(self, node):
        """
        Parse olx into this block's fields.
        """
        self.hints = []

        for child in iter_without_comments(node):
            if child.tag == "demandhint":
                self.hints.extend(parse_hints_from_node(child))
            elif child.tag == "stringresponse":
                self.question_data = parse_stringresponse_from_node(child)
            elif child.tag == "choiceresponse":
                self.question_data = parse_choiceresponse_from_node(child)
            elif child.tag in ["multiplechoiceresponse", "optionresponse"]:
                self.question_data = parse_optionresponse_from_node(child)

        self.max_attempts = int(node.attrib.get("max_attempts", 0))
        self.weight = float(node.attrib.get("weight", 1))
        self.display_name = node.attrib.get("display_name", "Question")


def parse_stringresponse_from_node(node: "xmlnode") -> dict:
    """
    Take an xml node, and return data for a short string response question
    """
    # the question text
    question = ""
    # list of strings which are correct answers to the question
    answers = []
    # answer-specific comments
    # { "answer": "hint text when `answer` is entered" }
    comments = {}

    main_answer = node.attrib.get("answer", "")
    if main_answer:
        answers.append(main_answer)

    # pylint: disable=too-many-nested-blocks
    for child in iter_without_comments(node):
        if child.tag == "label":
            question = html.unescape(decode_text(child, inner_html=True))
        elif child.tag == "correcthint":
            text = decode_text(child)
            if main_answer and text:
                comments[main_answer] = text
        elif child.tag == "additional_answer":
            answer = child.attrib.get("answer")
            if answer:
                answers.append(answer)
                for grandchild in iter_without_comments(child):
                    if grandchild.tag == "correcthint":
                        text = decode_text(grandchild)
                        if text:
                            comments[answer] = text
        elif child.tag == "stringequalhint":
            answer = child.attrib.get("answer")
            text = decode_text(child)
            if answer and text:
                comments[answer] = text

    return {
        "type": node.tag,
        "answers": answers,
        "question": question,
        "comments": comments,
    }


def parse_choiceresponse_from_node(node: "xmlnode") -> dict:
    """
    Take an xml node, and maybe return data for a multiple choice question,
    that has possibly more than one correct answer.
    """
    # the question text
    question = ""
    # list of choices for the question
    choices = []
    # answer-specific comments
    # { "0 2": "comment text when `answer` is entered" }
    comments = {}

    for child in iter_without_comments(node):
        if child.tag == "label":
            question = html.unescape(decode_text(child, inner_html=True))
        elif child.tag == "checkboxgroup":
            for grandchild in iter_without_comments(child):
                if grandchild.tag == "choice":
                    choices.append(parse_choice_from_node(grandchild))
                elif grandchild.tag == "compoundhint":
                    value = grandchild.attrib.get("correct", "").lower()
                    if value in ("true", "false"):
                        key = "correct" if value == "true" else "incorrect"
                        comments[key] = decode_text(grandchild)

    return {
        "type": node.tag,
        "question": question,
        "choices": choices,
        "comments": comments,
    }


def parse_choice_from_node(node: "xmlnode") -> dict:
    """
    Parse a choice for a multiple choice, multiple select question.

    Returns:
      {
          correct: boolean,
          content: string,
          selected_comment: string,
          unselected_comment: string,
      }
    """
    selected_comment = ""
    # unselected_comment = ""
    for child in iter_without_comments(node):
        if child.tag == "choicehint":
            if child.attrib.get("selected", "false") == "true":
                selected_comment = decode_text(child)
            else:
                unselected_comment = decode_text(child)

    choice = {
        "content": html.unescape(decode_text(node)),
        "correct": node.attrib.get("correct", "false") == "true",
        "selected_comment": selected_comment,
        # Disable unselected comment
        # https://app.asana.com/0/1202822149778018/1203232161649928/f
        "unselected_comment": "",
    }

    return choice


def parse_option_from_node(node: "xmlnode") -> dict:
    """
    Parse a choice or option for a single select choice question.

    Returns:
      {
          correct: boolean,
          content: string,
          comment: string,
      }
    """
    option = {
        "content": html.unescape(decode_text(node)),
        "correct": node.attrib.get("correct", "false") == "true",
        "comment": "",
    }

    for child in iter_without_comments(node):
        if child.tag in ["choicehint", "optionhint"]:
            option["comment"] = decode_text(child)

    return option


def parse_optionresponse_from_node(node: "xmlnode") -> dict:
    """
    Take an xml node, and maybe return data for a multiple choice question,
    that has exactly one correct answer, and students can only select a single answer.

    Parses both "multiplechoiceresponse" and "optionresponse" variants.
    The only difference is:
    - "multiplechoiceresponse": displays as radio buttons
    - "optionresponse": displays as an option dropdown menu
    """
    # the question text
    question = ""
    # list of options for the question
    options = []

    if node.tag == "multiplechoiceresponse":
        display = "radio"
    elif node.tag == "optionresponse":
        display = "dropdown"

    for child in iter_without_comments(node):
        if child.tag == "label":
            question = html.unescape(decode_text(child, inner_html=True))
        elif child.tag in ("optioninput", "choicegroup"):
            for grandchild in iter_without_comments(child):
                if grandchild.tag in ("choice", "option"):
                    options.append(parse_option_from_node(grandchild))

    return {
        "type": "optionresponse",
        "question": question,
        "options": options,
        "display": display,
    }


def parse_hints_from_node(node: "xmlnode") -> List[dict]:
    """
    Takes an xml node and returns an array of hints

    Input:

        <demandhint>
          <hint>this is another hint</hint>
        </demandhint>

    Output:

        [{ "content": "this is another hint" }]
    """
    return [
        {"content": decode_text(child)}
        for child in iter_without_comments(node)
        if child.tag == "hint"
    ]


def iter_without_comments(node):
    for child in node:
        if child.tag is not etree.Comment:
            yield child


def decode_text(node, inner_html=False):
    """
    Returns the stripped inner text/html of the given node, or empty string, if none.

    If `inner_html` requested, then the returned text will include the child tags and text too.
    """
    if inner_html:
        text = node.text or ""
        for child in node:
            text = text + tostring(child, encoding="unicode")
            text = text + (child.tail or "")
    else:
        text = node.text or ""
    return text.strip()
