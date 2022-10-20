from neuroconv.datainterfaces import ExtractSegmentationInterface
from neuroconv.utils import calculate_regular_series_rate, FilePathType
from roiextractors import ExtractSegmentationExtractor

from fee_lab_to_nwb.scherrer_ophys.utils import (
    get_timestamps_from_csv,
    shift_timestamps_to_start_from_zero,
)


class ScherrerOphysSegmentationInterface(ExtractSegmentationInterface):
    """Data interface for ExtractSegmentationExtractor."""

    Extractor = ExtractSegmentationExtractor

    def __init__(
        self,
        file_path: FilePathType,
        timestamps_file_path: FilePathType,
        output_struct_name: str = "exOut",
    ):

        super().__init__(
            file_path=file_path,
            sampling_frequency=30.0,
            output_struct_name=output_struct_name,
        )

        timestamps = get_timestamps_from_csv(file_path=timestamps_file_path)
        timestamps = shift_timestamps_to_start_from_zero(timestamps=timestamps)
        if not calculate_regular_series_rate(timestamps):
            # only use timestamps if they are not regular
            self.segmentation_extractor.set_times(times=timestamps)
