from os import PathLike
from pathlib import Path
from typing import List, Optional, Tuple, Union

import mdocfile
import numpy as np
import pandas as pd
import starfile

import dask

from .dask import create_cluster
from .mdoc import add_pre_exposure_dose, match_tilt_image_filenames
from .stack_images import stack_image_files, stack_image_files_mmap


def tiltstack(
    tilt_image_files: List[PathLike],
    mdoc_files: List[PathLike],
    output_directory: PathLike,
    dose_per_tilt: Optional[float] = None,
    cluster_specification: Optional[PathLike] = None,
    n_workers: Optional[int] = 4,
):
    # set up cluster if specified
    if cluster_specification is not None:
        cluster = create_cluster(cluster_specification)
        cluster.scale(n_workers)

    #  create output directory
    tilt_series_directory = Path(output_directory) / "tilt_series"
    tilt_series_directory.mkdir(parents=True, exist_ok=True)

    # set up delayed computation
    lazy_metadata = []
    for mdoc_file in mdoc_files:
        tilt_series_basename = Path(mdoc_file).stem
        output_filename = tilt_series_directory / f"{tilt_series_basename}.mrc"
        metadata_df = dask.delayed(stack_tilt_series)(
            tilt_image_files=tilt_image_files,
            mdoc_file=mdoc_file,
            output_filename=output_filename,
            dose_per_tilt=dose_per_tilt,
        )
        lazy_metadata.append(metadata_df)

    # execute (on cluster resources if available)
    result_dfs = [metadata_df.compute() for metadata_df in lazy_metadata]
    result_dfs = pd.concat(result_dfs, axis=0)
    return result_dfs


def tiltstack_relion(
    micrographs_star_file: PathLike,
    mdoc_files: List[PathLike],
    output_directory: PathLike,
    dose_per_tilt: Optional[float] = None,
    cluster_specification: Optional[PathLike] = None,
):
    star = starfile.read(micrographs_star_file)
    tilt_image_files = star["micrographs"]["rlnMicrographName"]
    metadata = tiltstack(
        tilt_image_files=tilt_image_files,
        mdoc_files=mdoc_files,
        output_directory=output_directory,
        dose_per_tilt=dose_per_tilt,
    )
    # write out metadata


def stack_tilt_series(
    tilt_image_files: List[PathLike],
    mdoc_file: PathLike,
    output_filename: Optional[PathLike] = None,
    dose_per_tilt: Optional[float] = None,
) -> Union[Tuple[np.ndarray, pd.DataFrame], pd.DataFrame]:
    df = mdocfile.read(mdoc_file)
    df = df.sort_values(by="date_time", ascending=True)
    df = add_pre_exposure_dose(mdoc_df=df, dose_per_tilt=dose_per_tilt)
    df = df.sort_values(by="tilt_angle", ascending=True)
    df = match_tilt_image_filenames(tilt_image_files, mdoc_df=df)
    if output_filename is not None:
        stack_image_files_mmap(
            image_files=df["matched_filename"], output_filename=output_filename
        )
        return df
    else:
        tilt_series = stack_image_files(df["matched_filename"])
        return tilt_series, df
