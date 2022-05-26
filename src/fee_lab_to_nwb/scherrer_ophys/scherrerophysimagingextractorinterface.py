from typing import Optional

from nwb_conversion_tools.basedatainterface import BaseDataInterface
from nwb_conversion_tools.tools.roiextractors import write_imaging
from nwb_conversion_tools.utils import OptionalFilePathType
from pynwb import NWBFile

from fee_lab_to_nwb.scherrer_ophys.scherrerophysimagingextractor import (
    ScherrerOphysImagingExtractor,
)


class ScherrerOphysImagingExtractorInterface(BaseDataInterface):
    IX = ScherrerOphysImagingExtractor

    def __init__(self, file_path: str):
        super().__init__(file_path=file_path)
        self.imaging_extractor = self.IX(file_path=file_path)
        self.verbose = True

    def run_conversion(
        self,
        nwbfile_path: OptionalFilePathType = None,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        save_path: OptionalFilePathType = None,
    ):
        write_imaging(
            imaging=self.imaging_extractor,
            nwbfile_path=nwbfile_path,
            nwbfile=nwbfile,
            metadata=metadata,
            overwrite=overwrite,
            verbose=self.verbose,
            save_path=save_path,
        )
