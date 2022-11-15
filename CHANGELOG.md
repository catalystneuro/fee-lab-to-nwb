# Upcoming

### Fixes
* Add auditory data to the NWB file as stimulus instead of acquisition. [PR #37](https://github.com/catalystneuro/fee-lab-to-nwb/pull/37)
* Removed "conversion", "starting_time" and "rate" key pops from TimeSeries metadata schema when
  constructing the metadata schema for `AudioInterface`. [PR #49](https://github.com/catalystneuro/fee-lab-to-nwb/pull/49)
* Bumped `neuroconv` version to 0.2.2. [PR #52](https://github.com/catalystneuro/fee-lab-to-nwb/pull/52)

### Improvements
* Create file for tracking changes. [PR #36](https://github.com/catalystneuro/fee-lab-to-nwb/pull/36)
* Changed the `MotifInterface` to take a second argument that corresponds the file
  that contains the Audio and SpikeGLX timestamps. This file is used for synchronizing
  the motif timestamps. [PR #33](https://github.com/catalystneuro/fee-lab-to-nwb/pull/33)
* Adjusted `session_start_time` for ophys to reference the first time entry from imaging timestamps. [PR #43](https://github.com/catalystneuro/fee-lab-to-nwb/pull/43)
* Added version pins and utilize minimal dependencies from `neuroconv`. [PR #47](https://github.com/catalystneuro/fee-lab-to-nwb/pull/47)
* Renamed conversion specific files to have generic names. [PR #46](https://github.com/catalystneuro/fee-lab-to-nwb/pull/46)

### Features
* The `ScherrerOphysSegmentationInterface` is modified to write the configurations
  from EXTRACT segmentation to the NWB File. [PR #42](https://github.com/catalystneuro/fee-lab-to-nwb/pull/42)
* Created utility methods for processing the syllables duration and stimulus notes from
  the provided 'Neuropixels_Dataset_Log.xlsx'. The mapping of syllables and motifs is extracted
  from the "motif_syllable_mapping" sheet which contains for each motif the syllable name,
  its duration and the duration of silence after the syllable. The file is added to the repository,
  since it has been corrected for incorrect stimulus dates that did not match the dates in the "session repository"
  sheet. The `NWBFile` metadata is also updated with a description of the session, and
  the species of the `Subject` is added to the `metadata.yml` file. [PR #45](https://github.com/catalystneuro/fee-lab-to-nwb/pull/45)
* The `MotifInterface` is modified to add the timings of syllables along with the motifs.
  The motifs are added to the trials table and is a `HierarchicalBehavioralTable` where the
  lowest hierarchical level is the level of syllables. [PR #34](https://github.com/catalystneuro/fee-lab-to-nwb/pull/34)

### Testing
* Added auto-detector workflow for CHANGELOG.md updates. [PR #41](https://github.com/catalystneuro/fee-lab-to-nwb/pull/41)

### Documentation and visualization
* Added a note about running the conversion scripts when the package was installed from `pip`. [PR #48](https://github.com/catalystneuro/fee-lab-to-nwb/pull/48)
* Added a custom widget that combines the visualisation of the waveform and spectrogram of the sound with the motifs/syllables table.
  The widget also includes the play button for the audio. The tutorial is in `happ_ecephys/widgets/notes.md` [PR #54](https://github.com/catalystneuro/fee-lab-to-nwb/pull/54)

# v1.0.0

* The first release of fee-lab-to-nwb. [PR #31](https://github.com/catalystneuro/fee-lab-to-nwb/pull/31)
