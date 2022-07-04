from nwb_conversion_tools.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from nwb_conversion_tools.utils import calculate_regular_series_rate
from roiextractors.multiimagingextractor import MultiImagingExtractor

from fee_lab_to_nwb.scherrer_ophys.scherrerophysimagingextractor import (
    ScherrerOphysImagingExtractor,
)
from fee_lab_to_nwb.scherrer_ophys.utils import get_timestamps_from_csv


class ScherrerOphysImagingExtractorInterface(BaseImagingExtractorInterface):
    IX = MultiImagingExtractor

    def __init__(
        self, ophys_file_paths: list, timestamps_file_path: str, verbose: bool = True
    ):
        imaging_extractors = [
            ScherrerOphysImagingExtractor(file_path=file_path)
            for file_path in ophys_file_paths
        ]
        super().__init__(imaging_extractors=imaging_extractors)
        timestamps = get_timestamps_from_csv(file_path=timestamps_file_path)
        if not calculate_regular_series_rate(timestamps):
            # only use timestamps if they are not regular
            self.imaging_extractor.set_times(times=timestamps)
        self.verbose = verbose
