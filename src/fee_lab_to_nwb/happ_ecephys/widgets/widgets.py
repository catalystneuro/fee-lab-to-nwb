import numpy as np
from ipywidgets import VBox
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
from nwbwidgets.base import fig2widget

from ndx_hierarchical_behavioral_data import HierarchicalBehavioralTable
from ndx_sound import AcousticWaveformSeries
from ndx_sound.widgets import (
    plot_spectrogram,
    plot_waveform,
    play_sound,
    play_sound_widget,
)
from nwbwidgets.controllers import StartAndDurationController
from IPython.core.display_functions import clear_output, display
from nwbwidgets.timeseries import AbstractTraceWidget


def load_widgets():
    """Load AcousticWaveformWidget into nwbwidgets, to use as default visualization
    for AcousticWaveformSeries data."""
    from nwbwidgets import default_neurodata_vis_spec

    default_neurodata_vis_spec.update({AcousticWaveformSeries: MotifSoundCombinedWidget})


def get_tables(
    hierarchical_behavior_table: HierarchicalBehavioralTable,
    tables: list = None,
):
    tables = tables or []
    tables.append(hierarchical_behavior_table)
    if hasattr(hierarchical_behavior_table, "next_tier"):
        get_tables(hierarchical_behavior_table.next_tier.table, tables)
    return tables


class MotifSoundCombinedWidget(AbstractTraceWidget):
    def __init__(
        self,
        acoustic_waveform_series: AcousticWaveformSeries,
        hierarchical_behavior_table: HierarchicalBehavioralTable = None,
        foreign_time_window_controller: StartAndDurationController = None,
        **kwargs,
    ):
        hierarchical_behavior_table = (
            hierarchical_behavior_table or acoustic_waveform_series.get_ancestor("NWBFile").trials
        )
        self.tables = get_tables(hierarchical_behavior_table=hierarchical_behavior_table)

        super().__init__(
            timeseries=acoustic_waveform_series,
            foreign_time_window_controller=foreign_time_window_controller,
            **kwargs,
        )

    def set_out_fig(self):
        acoustic_waveform_series = self.controls["timeseries"].value
        self.out_fig = self.acoustic_waveform_widget()

        def on_change(change):
            time_window = self.controls["time_window"].value

            with self.out_fig.children[0]:
                clear_output(wait=True)
                self.plot_hierarchy_with_sound()
                show_inline_matplotlib_plots()

            with self.out_fig.children[1]:
                clear_output(wait=True)
                display(play_sound(acoustic_waveform_series, time_window))

        self.controls["time_window"].observe(on_change)

    def acoustic_waveform_widget(self):
        """
        Entire widget, with hierarchical data, waveform, spectrogram, and sound.
        """
        acoustic_waveform_series = self.controls["timeseries"].value
        time_window = self.controls["time_window"].value
        return VBox(
            [
                fig2widget(self.plot_hierarchy_with_sound()),
                play_sound_widget(acoustic_waveform_series, time_window),
            ]
        )

    def plot_hierarchy_with_sound(self):
        """
        Returns a figure that combines the visualization of hierarchical table time-aligned
        with the waveform and the spectrogram of the sound.
        """
        acoustic_waveform_series = self.controls["timeseries"].value
        time_window = self.controls["time_window"].value

        grid_spec = GridSpec(
            nrows=3,
            ncols=2,
            hspace=0.04,
            wspace=0.04,
            height_ratios=[2.5, 1, 5],
            width_ratios=[25, 1],
        )
        figsize = self.controls["figsize"].value if "figsize" in self.controls else None
        fig = plt.figure(figsize=figsize)

        # Add hierarchy tables figure
        ax0 = fig.add_subplot(grid_spec[0, 0])
        self.plot_hierarchy(time_window=time_window, ax=ax0)

        # Add waveform of the sound
        ax1 = fig.add_subplot(grid_spec[1, 0])
        plot_waveform(acoustic_waveform_series, time_window=time_window, ax=ax1)

        # Add spectrogram of the sound
        ax2 = fig.add_subplot(grid_spec[2, 0])
        cax = fig.add_subplot(grid_spec[2, 1])
        plot_spectrogram(acoustic_waveform_series, time_window=time_window, ax=ax2, cax=cax)

        return fig

    def plot_hierarchy(self, time_window=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        if time_window is None:
            t_start = min(min(table["start_time"]) for table in self.tables)
            t_stop = max(max(table["stop_time"]) for table in self.tables)
        else:
            t_start = time_window[0]
            t_stop = time_window[1]

        for table_ind, table in enumerate(self.tables[::-1]):
            for start_time, stop_time, label in zip(
                table["start_time"],
                table["stop_time"],
                table["label"],
            ):

                # if event is out of bounds, skip it
                if t_start is not None and stop_time < t_start:
                    continue
                if t_stop is not None and start_time > t_stop:
                    continue

                # center labels on boundary events
                if t_start is not None and start_time < t_start:
                    start_time = t_start

                if t_stop is not None and stop_time > t_stop:
                    stop_time = t_stop

                duration = stop_time - start_time
                # Draw a rectangle for each event
                rectangle = Rectangle(
                    xy=(start_time, table_ind),
                    width=duration,
                    height=1,
                    facecolor="None",
                    edgecolor="k",
                    label=label,
                )
                ax.add_patch(rectangle)

                ax.text(
                    start_time + duration / 2,
                    table_ind + 0.5,
                    label,
                    fontsize="small" if table_ind == 0 else "medium",
                    horizontalalignment="center",
                )

        ax.set_xlim((t_start, t_stop))
        ax.set_ylim((0, len(self.tables)))

        ax.set_yticks(np.arange(len(self.tables)) + 0.5)
        ax.set_yticklabels([table.name for table in self.tables][::-1])
        ax.set_xlabel("Time (s)")
        ax.set_frame_on(False)
        ax.axes.get_xaxis().set_visible(False)

        return ax
