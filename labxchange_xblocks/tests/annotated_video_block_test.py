from xblock.completable import XBlockCompletionMode
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from xblock.test.test_parsing import XmlTest

from xmodule.video_module import VideoBlock
from xmodule.tests.test_import import DummySystem

from labxchange_xblocks.annotated_video_block import AnnotatedVideoBlock
from utils import BlockTestCaseBase


class AnnotatedVideoBlockTestCase(XmlTest, BlockTestCaseBase):

    block_type = "lx_annotated_video"
    block_class = AnnotatedVideoBlock

    def test_is_aggregator(self):
        self.assertEqual(
            XBlockCompletionMode.get_mode(AnnotatedVideoBlock),
            XBlockCompletionMode.AGGREGATOR,
        )

    def test_student_video_data(self):
        module_system = DummySystem(load_error_modules=True)

        video_field_data = {
            "display_name": "Video",
            "youtube": "1.0:p2Q6BrNhdh8,0.75:izygArpw-Qo,1.25:1EeWXzPdhSA,1.5:rABDYkeK0x8",
            "show_captions": False,
        }
        video_block_keys = ScopeIds("a_user", "video", "def_id_video", "usage_id_video")
        video_block = VideoBlock(
            module_system,
            scope_ids=video_block_keys,
            field_data=DictFieldData(video_field_data),
        )

        field_data = {
            "display_name": "Annotated video",
            "video_id": video_block.scope_ids.usage_id,
            "annotations": [
                {
                    "id": "715ad1df-1be0-4fe7-b0d0-fc21e2a0d050",
                    "title": "Title",
                    "description": "Description",
                    "image_url": "/static/image.png",
                    "start": 10,
                }
            ],
        }
        block = self._construct_xblock_mock(
            self.block_class,
            self.keys,
            field_data=DictFieldData(field_data),
        )
        block.children.append(video_block.scope_ids.block_type)

        def get_block(usage_id):
            if usage_id == "video":
                return video_block

        self.runtime_mock.get_block.side_effect = get_block

        response = block.student_view_user_state(request=None)
        data = response.json

        self.assertDictEqual(
            data,
            {
                "child_blocks": [
                    {
                        "block_type": "video",
                        "display_name": "Video",
                        "usage_id": "video",
                    },
                ],
                "display_name": "Annotated video",
                "video_id": video_block.scope_ids.usage_id,
                "annotations": [
                    {
                        "description": "Description",
                        "id": "715ad1df-1be0-4fe7-b0d0-fc21e2a0d050",
                        "start": 10,
                        "title": "Title",
                        "image_url": "/static/image.png",
                    }
                ],
            },
        )
