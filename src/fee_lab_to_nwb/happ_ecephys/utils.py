from datetime import datetime

import pandas as pd
from neuroconv.utils import FilePathType


def parse_session_date(session_date: str) -> datetime:
    for date_format in ["%y%m%d", "%y%d%m"]:
        try:
            return datetime.strptime(session_date, date_format)
        except ValueError:
            continue
    raise ValueError("No valid date format found.")


def get_motif_syllables_table_for_session_date(
    file_path: FilePathType,
    session_date: str,
    sheet_names: list = None,
    recording_date_column_name: str = "Recording Date",
    stimulus_date_column_name: str = "Stim",
) -> pd.DataFrame:
    if sheet_names is None:
        sheet_names = ["session repository", "motif_syllable_mapping"]
    dataset_log = pd.read_excel(file_path, sheet_name=sheet_names)
    session_table = dataset_log["session repository"]
    syllables_table = dataset_log["motif_syllable_mapping"]

    # Parse the date of the session and match it with a recording date from the session repository table.
    session_date_dt = parse_session_date(session_date=session_date)
    stim_date = session_table.loc[
        session_table[recording_date_column_name] == session_date_dt, stimulus_date_column_name
    ]
    # The syllables table is filtered for this stimulus date
    syllables_table_for_this_session = syllables_table.loc[syllables_table[stimulus_date_column_name].isin(stim_date)]

    return syllables_table_for_this_session
