import pandas as pd
from neuroconv.utils import FilePathType
from numpy import datetime64


def create_session_table(
    file_path: str,
    sheet_names: list = [
        "session repository",
        "mappings",
    ],
):
    dataset_log = pd.read_excel(
        file_path,
        sheet_name=sheet_names,
    )
    session_table = dataset_log["session repository"]
    mappings_table = dataset_log["mappings"]

    # Match stimulus dates from syllables table to session names
    # Create session name from 'Recording Date'
    recording_dates = session_table["Recording Date"].dt.strftime("%Y%m%d")
    # Most session names are in {bird_id}_{YYmmDD} format
    bird_ids = session_table["Bird"].astype(str)
    recording_dates = recording_dates.astype(str).apply(lambda x: x[2:])
    session_table["session_name_id"] = bird_ids + "_" + recording_dates

    bird_ids_from_mappings = mappings_table["Session Name"].apply(lambda x: x.split("_")[0])

    dates_from_mappings = mappings_table["Session Name"].apply(lambda x: x.split("_")[1])

    # Unify exceptions that follow {bird_id}_{YYDDmm} format
    date_exceptions = dates_from_mappings.loc[mappings_table["Experiment Type"] == "Timing"]
    dates = date_exceptions.apply(lambda x: ("").join([x[:2], x[-2:], x[2:4]]))
    dates_from_mappings.loc[mappings_table["Experiment Type"] == "Timing"] = dates

    mappings_table["session_name_id"] = bird_ids_from_mappings + "_" + dates_from_mappings

    session_table_with_mappings = pd.merge(
        left=mappings_table,
        right=session_table,
        on="session_name_id",
        how="left",
    )

    return session_table_with_mappings


def get_syllables_table_for_stim_date(
    file_path: FilePathType,
    stim_date: datetime64,
    sheet_name: str = "motif_syllable_mapping",
):
    syllables_table = pd.read_excel(file_path, sheet_name=sheet_name)
    return syllables_table.loc[syllables_table["Stim Date"] == stim_date]
