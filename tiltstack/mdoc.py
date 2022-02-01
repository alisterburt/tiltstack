from os import PathLike
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from thefuzz import process


def match_tilt_image_filenames(
    tilt_image_files: List[PathLike], mdoc_df: pd.DataFrame
) -> pd.DataFrame:
    """"""
    tilt_image_file_basenames = [Path(f).stem for f in tilt_image_files]
    mdoc_df["mdoc_tilt_image_basename"] = mdoc_df["sub_frame_path"].apply(
        lambda x: Path(str(x).split("\\")[-1]).stem
    )
    tilt_image_basename_to_full = {
        tilt_image_file_basenames[i]: tilt_image_files[i]
        for i in range(len(tilt_image_files))
    }
    matched_filenames = []
    for mdoc_tilt_image_filename in mdoc_df["mdoc_tilt_image_basename"]:
        match, _ = process.extractOne(
            query=mdoc_tilt_image_filename,
            choices=tilt_image_file_basenames,
        )
        matched_file = tilt_image_basename_to_full[match]
        matched_filenames.append(matched_file)
    mdoc_df["matched_filename"] = matched_filenames
    return mdoc_df


def add_pre_exposure_dose(
    mdoc_df: pd.DataFrame, dose_per_tilt: Optional[float] = None
) -> pd.DataFrame:
    if dose_per_tilt is not None:
        pre_exposure_dose = dose_per_tilt * np.arange(len(mdoc_df))
    else:  # all zeros if exposure dose values not present in mdoc
        pre_exposure_dose = [0] * len(mdoc_df)

    if "exposure_dose" not in mdoc_df.columns:
        mdoc_df["pre_exposure_dose"] = pre_exposure_dose
    elif (mdoc_df["exposure_dose"] == 0).all():
        mdoc_df["pre_exposure_dose"] = pre_exposure_dose
    else:
        mdoc_df["pre_exposure_dose"] = np.cumsum(mdoc_df["exposure_dose"].to_numpy())
    return mdoc_df
