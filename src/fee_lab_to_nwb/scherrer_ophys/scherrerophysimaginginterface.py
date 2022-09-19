from pathlib import Path

from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from neuroconv.utils import calculate_regular_series_rate, FolderPathType
from roiextractors.multiimagingextractor import MultiImagingExtractor

from ..scherrer_ophys.utils import get_timestamps_from_csv
from .scherrerophysimagingextractor import ScherrerOphysImagingExtractor


class ScherrerOphysImagingInterface(BaseImagingExtractorInterface):
    Extractor = MultiImagingExtractor

    def __init__(
        self, folder_path: FolderPathType, timestamps_file_path: str, verbose: bool = True
    ):
        ophys_file_paths = [
            ophys_file_name
            for ophys_file_name in Path(folder_path).iterdir()
            if ophys_file_name.suffix == ".avi"
        ]
        # Initialize the imaging extractors for each file
        imaging_extractors = [
            ScherrerOphysImagingExtractor(file_path=file_path)
            for file_path in sorted(ophys_file_paths)
        ]
        super().__init__(imaging_extractors=imaging_extractors)
        timestamps = get_timestamps_from_csv(file_path=timestamps_file_path)
        if not calculate_regular_series_rate(timestamps):
            # only use timestamps if they are not regular
            self.imaging_extractor.set_times(times=timestamps)
        self.verbose = verbose
