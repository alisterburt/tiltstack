from pathlib import Path
from os import PathLike

import pandas as pd


def basename(path: Path):
    while path.stem != str(path):
        path = Path(path.stem)
    return path


def write_rawtlt(mdoc_df: pd.DataFrame, filename: PathLike):
    tilt_angles = mdoc_df["tilt_angle"]
    tilt_angles.to_csv(filename, index=False, header=False)


def write_metadata(mdoc_df: pd.DataFrame, filename: PathLike):
    mdoc_df.to_csv(filename, index=False, header=True)