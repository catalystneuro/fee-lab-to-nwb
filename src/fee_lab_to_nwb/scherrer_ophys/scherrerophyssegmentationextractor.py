import numpy as np
from neuroconv.utils import FilePathType
from roiextractors.extractors.schnitzerextractor import NewExtractSegmentationExtractor


class ScherrerOphysSegmentationExtractor(NewExtractSegmentationExtractor):
    extractor_name = "ScherrerOphysSegmentationExtractor"

    def __init__(
        self,
        file_path: FilePathType,
        sampling_frequency: float,
        output_struct_name: str = "output",
    ):
        super().__init__(
            file_path=file_path, sampling_frequency=sampling_frequency, output_struct_name=output_struct_name
        )

    def get_roi_image_masks(self, roi_ids=None) -> np.ndarray:
        """Returns the image masks extracted from segmentation algorithm.

        Parameters
        ----------
        roi_ids: array_like
            A list or 1D array of ids of the ROIs. Length is the number of ROIs
            requested.

        Returns
        -------
        image_masks: numpy.ndarray
            3-D array(val 0 or 1): image_height X image_width X length(roi_ids)
        """
        if roi_ids is None:
            return self._image_masks[:]

        all_ids = self.get_roi_ids()
        roi_idx_ = [all_ids.index(i) for i in roi_ids]
        return np.stack([self._image_masks[:, :, k] for k in roi_idx_], 2)
