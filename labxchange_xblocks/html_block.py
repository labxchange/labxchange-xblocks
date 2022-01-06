"""
HTML XBlock.
"""
from lxml import etree
from xblock.core import XBlock
from xblock.fields import Scope, String

from .utils import StudentViewBlockMixin, _


class HtmlBlock(XBlock, StudentViewBlockMixin):
    """
    XBlock for html asset.
    """

    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Html",
        scope=Scope.content,
    )
    data = String(
        help=_("Html contents to display for this module"),
        default="",
        scope=Scope.content,
    )

    student_view_template = "templates/html_student_view.html"

    @classmethod
    def parse_xml(
        cls, node, runtime, keys, id_generator=None
    ):  # pylint: disable=unused-argument
        """Retrieve blockstore olx"""
        block = runtime.construct_xblock_from_class(cls, keys)
        parts = [node.text]
        for c in node.getchildren():
            parts.append(etree.tostring(c, with_tail=True, encoding="unicode"))

        block.data = "".join([part for part in parts if part])
        # Attributes become fields.
        for name, value in node.items():
            cls._set_field_if_present(block, name, value, {})
        return block

    def student_view_data(self, context=None):
        """Return all data required to render or edit the xblock"""
        return {"html": self.data}
