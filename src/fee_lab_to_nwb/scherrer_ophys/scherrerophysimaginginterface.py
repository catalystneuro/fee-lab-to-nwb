from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from neuroconv.utils import calculate_regular_series_rate
from roiextractors.multiimagingextractor import MultiImagingExtractor

from ..scherrer_ophys.utils import get_timestamps_from_csv, shift_timestamps_to_start_from_zero
from .scherrerophysimagingextractor import ScherrerOphysImagingExtractor


class ScherrerOphysImagingInterface(BaseImagingExtractorInterface):
    """
    Data Interface for writing the Fee lab imaging data to NWB file using the
    MultiImagingExtractor to extract the frames from each ScherrerOphysImagingExtractor.
    """

    Extractor = MultiImagingExtractor

    def __init__(self, ophys_file_paths: list, timestamps_file_path: str, verbose: bool = True):
        # Initialize the imaging extractors for each file
        imaging_extractors = [ScherrerOphysImagingExtractor(file_path=file_path) for file_path in ophys_file_paths]
        super().__init__(imaging_extractors=imaging_extractors)
        timestamps = get_timestamps_from_csv(file_path=timestamps_file_path)
        timestamps = shift_timestamps_to_start_from_zero(timestamps=timestamps)
        if not calculate_regular_series_rate(timestamps):
            # only use timestamps if they are not regular
            self.imaging_extractor.set_times(times=timestamps)
        self.verbose = verbose
