from nwb_conversion_tools.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from roiextractors.multiimagingextractor import MultiImagingExtractor


class ScherrerOphysImagingExtractorInterface(BaseImagingExtractorInterface):
    IX = MultiImagingExtractor

    def __init__(self, imaging_extractors: list, timestamps: list, verbose: bool = True):
        super().__init__(imaging_extractors=imaging_extractors)
        self.imaging_extractor = self.IX(imaging_extractors=imaging_extractors)
        self.imaging_extractor.set_times(times=timestamps)
        self.verbose = verbose
