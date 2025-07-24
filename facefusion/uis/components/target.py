from typing import Optional, Tuple


import gradio


from facefusion import state_manager, wording
from facefusion.face_store import clear_reference_faces, clear_static_faces
from facefusion.filesystem import is_image, is_video
from facefusion.uis.core import register_ui_component
from facefusion.uis.types import ComponentOptions


TARGET_PATH_INPUT: Optional[gradio.Textbox] = None
TARGET_IMAGE: Optional[gradio.Image] = None
TARGET_VIDEO: Optional[gradio.Video] = None


def render() -> None:
    global TARGET_PATH_INPUT
    global TARGET_IMAGE
    global TARGET_VIDEO

    target_path = state_manager.get_item("target_path")
    is_target_image = is_image(target_path)
    is_target_video = is_video(target_path)

    TARGET_PATH_INPUT = gradio.Textbox(
        label=wording.get("uis.target_file"),
        value=target_path or "",
        placeholder="Enter path to image or video file",
        lines=1,
    )

    target_image_options: ComponentOptions = {"show_label": False, "visible": False}
    target_video_options: ComponentOptions = {"show_label": False, "visible": False}
    if is_target_image:
        target_image_options["value"] = target_path
        target_image_options["visible"] = True
    if is_target_video:
        target_video_options["value"] = target_path
        target_video_options["visible"] = True
    TARGET_IMAGE = gradio.Image(**target_image_options)
    TARGET_VIDEO = gradio.Video(**target_video_options)
    register_ui_component("target_path_input", TARGET_PATH_INPUT)
    register_ui_component("target_image", TARGET_IMAGE)
    register_ui_component("target_video", TARGET_VIDEO)


def listen() -> None:
    TARGET_PATH_INPUT.change(
        update, inputs=TARGET_PATH_INPUT, outputs=[TARGET_IMAGE, TARGET_VIDEO]
    )


def update(path: str) -> Tuple[gradio.Image, gradio.Video]:
    clear_reference_faces()
    clear_static_faces()

    if path and is_image(path):
        state_manager.set_item("target_path", path)
        return gradio.Image(value=path, visible=True), gradio.Video(
            value=None, visible=False
        )

    if path and is_video(path):
        state_manager.set_item("target_path", path)
        return gradio.Image(value=None, visible=False), gradio.Video(
            value=path, visible=True
        )

    state_manager.clear_item("target_path")
    return gradio.Image(value=None, visible=False), gradio.Video(
        value=None, visible=False
    )
