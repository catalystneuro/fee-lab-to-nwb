from typing import Optional

from nwb_conversion_tools.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from nwb_conversion_tools.tools.roiextractors import write_imaging
from nwb_conversion_tools.utils import OptionalFilePathType
from pynwb import NWBFile

from fee_lab_to_nwb.scherrer_ophys.scherrerophysimagingextractor import (
    ScherrerOphysImagingExtractor,
)


class ScherrerOphysImagingExtractorInterface(BaseImagingExtractorInterface):
    IX = ScherrerOphysImagingExtractor

    def __init__(self, file_path: str):
        super().__init__(file_path=file_path)
        self.imaging_extractor = self.IX(file_path=file_path)
        self.verbose = True

    def get_metadata(self):
        metadata = super().get_metadata()

        # Add missing properties for Ophys metadata
        ophys_metadata = metadata["Ophys"]
        device_name = ophys_metadata["Device"][0]["name"]
        imaging_plane = ophys_metadata["ImagingPlane"][0]["name"]
        if "device" not in ophys_metadata["ImagingPlane"][0].keys():
            ophys_metadata["ImagingPlane"][0]["device"] = device_name
        if "imaging_plane" not in ophys_metadata["TwoPhotonSeries"][0].keys():
            ophys_metadata["TwoPhotonSeries"][0]["imaging_plane"] = imaging_plane

        return metadata

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
