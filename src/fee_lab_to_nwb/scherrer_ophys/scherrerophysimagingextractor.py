from typing import Tuple

import numpy as np
from nwb_conversion_tools.datainterfaces.behavior.movie.movie_utils import (
    VideoCaptureContext,
    HAVE_OPENCV,
    INSTALL_MESSAGE,
)
from roiextractors import ImagingExtractor
from nwb_conversion_tools.utils import FilePathType, ArrayType
from roiextractors.extraction_tools import NumpyArray


class ScherrerOphysImagingExtractor(ImagingExtractor):
    extractor_name = "ScherrerOphysImaging"
    installed = HAVE_OPENCV
    installation_mesg = INSTALL_MESSAGE

    def __init__(self, file_path: FilePathType):
        super().__init__()
        self.file_path = file_path
        self.video_capture_context = VideoCaptureContext(str(self.file_path))
        self._num_channels = 0
        self._channel_names = ["channel_0"]

        with self.video_capture_context as vc:
            self._num_frames = vc.get_movie_frame_count()
            self._image_size = vc.get_frame_shape()
            self._sampling_frequency = vc.get_movie_fps()

    def get_frames(self, frame_idxs: ArrayType, channel: int = 0) -> NumpyArray:
        frames = []
        for frame_index in frame_idxs:
            with self.video_capture_context as vc:
                rgb_frame = vc.get_movie_frame(frame_number=frame_index)
            # Convert from RGB888 to RGB565 to get green and blue correct values
            green_color_data = (rgb_frame[..., 1] >> 2).astype(np.uint16) << 5
            blue_color_data = (rgb_frame[..., 2] >> 3).astype(np.uint16)
            # Apply custom conversion to frames : green * 8 + blue / 8
            gray_frame = (green_color_data * 8) + (blue_color_data / 8)
            # Cast frame back to uint16
            gray_frame = gray_frame.astype(np.uint16)
            # Transpose frame to maintain original orientation after conversion
            gray_frame = gray_frame.T

            frames.append(gray_frame[np.newaxis, ...])

        concatenated_frames = np.concatenate(frames, axis=0).squeeze()
        return concatenated_frames

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
