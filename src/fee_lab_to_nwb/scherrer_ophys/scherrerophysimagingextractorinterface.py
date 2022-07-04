from nwb_conversion_tools.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from nwb_conversion_tools.utils import calculate_regular_series_rate
from roiextractors.multiimagingextractor import MultiImagingExtractor

from fee_lab_to_nwb.scherrer_ophys import ScherrerOphysImagingExtractor


class ScherrerOphysImagingExtractorInterface(BaseImagingExtractorInterface):
    IX = MultiImagingExtractor

    def __init__(self, file_paths: list, timestamps: list, verbose: bool = True):
        imaging_extractors = [
            ScherrerOphysImagingExtractor(file_path=file_path)
            for file_path in file_paths
        ]
        super().__init__(imaging_extractors=imaging_extractors)
        self.imaging_extractor = self.IX(imaging_extractors=imaging_extractors)
        if not calculate_regular_series_rate(timestamps):
            # only use timestamps if they are not regular
            self.imaging_extractor.set_times(times=timestamps[:3000])
        self.verbose = verbose
