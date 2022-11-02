from typing import Tuple, Optional

import numpy as np
from neuroconv.datainterfaces.behavior.video.video_utils import VideoCaptureContext
from roiextractors import ImagingExtractor
from neuroconv.utils import FilePathType, ArrayType
from roiextractors.extraction_tools import NumpyArray


def convert_rgb_frame_to_grayscale(rgb_frame: np.ndarray) -> np.ndarray:
    """
    Convert an RGB frame to grayscale using the custom conversion of color channels
    specified by the Fee lab: green * 8 + blue / 8. The data type of the resulting
    grayscale frame is uint16.
    """
    # Cast values from uint8 to uint16
    green_color_data = rgb_frame[..., 1].astype(np.uint16)
    blue_color_data = rgb_frame[..., 2].astype(np.uint16)
    # Apply custom conversion to frames : green * 8 + blue / 8
    gray_frame = (green_color_data * 8) + (blue_color_data / 8)
    gray_frame = gray_frame.astype(np.uint16)

    return gray_frame


class ScherrerOphysImagingExtractor(ImagingExtractor):
    """Custom extractor for reading a single AVI file from the Fee lab imaging data."""

    extractor_name = "ScherrerOphysImaging"

    def __init__(self, file_path: FilePathType):
        super().__init__()
        self.file_path = file_path
        self.video_capture_context = VideoCaptureContext(str(self.file_path))
        self._num_channels = 0
        self._channel_names = ["channel_0"]

        with VideoCaptureContext(str(self.file_path)) as vc:
            self._num_frames = vc.get_video_frame_count()
            self._image_size = vc.get_frame_shape()[:-1]
            self._sampling_frequency = vc.get_video_fps()

    def get_frames(self, frame_idxs: ArrayType, channel: int = 0) -> NumpyArray:
        frames = []
        for frame_index in frame_idxs:
            with VideoCaptureContext(str(self.file_path)) as vc:
                rgb_frame = vc.get_video_frame(frame_number=frame_index)

            gray_frame = convert_rgb_frame_to_grayscale(rgb_frame)
            frames.append(gray_frame[np.newaxis, ...])

        concatenated_frames = np.concatenate(frames, axis=0)
        return concatenated_frames

    def get_video(
        self,
        start_frame: Optional[int] = None,
        end_frame: Optional[int] = None,
        channel: Optional[int] = 0,
    ) -> np.ndarray:
        start_frame = start_frame if start_frame is not None else 0
        end_frame = end_frame if end_frame is not None else self.get_num_frames()

        # Set video current frame to start_frame
        self.video_capture_context.current_frame = start_frame

        video_shape = (end_frame - start_frame,) + self._image_size

        video = np.empty(shape=video_shape, dtype=np.uint16)
        for frame_number, rgb_frame in enumerate(self.video_capture_context):
            video[frame_number, ...] = convert_rgb_frame_to_grayscale(rgb_frame)
            if self.video_capture_context.current_frame == end_frame:
                return video

        return video

    def get_image_size(self) -> Tuple:
        return self._image_size

    def get_num_frames(self) -> int:
        return self._num_frames

    def get_sampling_frequency(self) -> float:
        return self._sampling_frequency

    def get_channel_names(self) -> list:
        return self._channel_names

    def get_num_channels(self) -> int:
        return self._num_channels
