from typing import Optional

import numpy as np
from neuroconv.datainterfaces import ExtractSegmentationInterface
from neuroconv.tools.nwb_helpers import get_module
from neuroconv.utils import (
    FilePathType,
    OptionalFilePathType,
    calculate_regular_series_rate,
)
from pynwb import NWBFile
from ndx_extract import EXTRACTSegmentation

from fee_lab_to_nwb.scherrer_ophys.scherrerophyssegmentationextractor import (
    ScherrerOphysSegmentationExtractor,
)
from fee_lab_to_nwb.scherrer_ophys.utils import (
    get_timestamps_from_csv,
    shift_timestamps_to_start_from_zero,
)


class ScherrerOphysSegmentationInterface(ExtractSegmentationInterface):
    """Data interface for ExtractSegmentationExtractor."""

    Extractor = ScherrerOphysSegmentationExtractor

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

    def add_image_segmentation(self, nwbfile: NWBFile, metadata: dict) -> NWBFile:
        """
        Adds the image segmentation specified by the metadata to the nwb file.
        The image segmentation that is added contains the configuration parameters
        from the EXTRACT output.
        """
        image_segmentation_name = metadata["Ophys"]["ImageSegmentation"]["name"]
        extract_segmentation_kwargs = self.get_extract_segmentation_kwargs()
        image_segmentation = EXTRACTSegmentation(
            name=image_segmentation_name,
            **extract_segmentation_kwargs,
        )

        ophys = get_module(nwbfile, "ophys", "contains optical physiology processed data")
        ophys.add(image_segmentation)
        return nwbfile

    def get_extract_segmentation_kwargs(self):
        """
        Returns the configuration parameters from the segmentation extractor in a format
        specified in the EXTRACTSegmentation class.
        """
        config = self.segmentation_extractor.config
        extract_segmentation_kwargs = dict()

        docval_args = EXTRACTSegmentation.__init__.__docval__["args"]
        for docval_arg in docval_args:
            if docval_arg["name"] not in config:
                continue
            config_name = docval_arg["name"]
            config_value = config[config_name]
            if isinstance(config_value, np.ndarray):
                if len(config_value) > 1 and not np.any(config_value):
                    # Skipping writing empty datasets
                    continue
                if len(config_value) == 1:
                    config_value = config_value[0]
            if docval_arg["type"] == bool:
                config_value = bool(config_value)

            if not isinstance(config_value, docval_arg["type"]):
                raise ValueError(
                    f"The data type {type(config_value)} for '{config_name}' does not match "
                    f"the expected {docval_arg['type']} type."
                    f"If this is intended, please open an issue at https://github.com/catalystneuro/ndx-extract/issues."
                )
            extract_segmentation_kwargs[config_name] = config_value

        return extract_segmentation_kwargs

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: dict,
        nwbfile_path: OptionalFilePathType = None,
        overwrite: bool = False,
        stub_test: bool = False,
        stub_frames: int = 100,
        include_roi_centroids: bool = True,
        include_roi_acceptance: bool = True,
        mask_type: Optional[str] = "image",
        iterator_options: Optional[dict] = None,
        compression_options: Optional[dict] = None,
    ):

        self.add_image_segmentation(nwbfile=nwbfile, metadata=metadata)

        super().run_conversion(
            nwbfile_path=nwbfile_path,
            nwbfile=nwbfile,
            metadata=metadata,
            overwrite=overwrite,
            stub_test=stub_test,
            stub_frames=stub_frames,
            include_roi_centroids=include_roi_centroids,
            include_roi_acceptance=include_roi_acceptance,
            mask_type=mask_type,
            iterator_options=iterator_options,
            compression_options=compression_options,
        )
