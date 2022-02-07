from os import PathLike
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import starfile

import typer

from .dask import create_cluster
from .mdoc import prepare_mdoc_dataframe
from .stack_images import stack_image_files, stack_image_files_mmap
from .utils import basename, write_rawtlt, write_metadata

cli = typer.Typer()


def tiltstack(
    tilt_image_files: List[PathLike],
    mdoc_files: List[PathLike],
    ts_directory: PathLike,
    dose_per_tilt: Optional[float] = None,
    cluster_specification: Optional[PathLike] = None,
    n_workers: Optional[int] = 4,
):
    # set up cluster if specified
    if cluster_specification is not None:
        cluster = create_cluster(cluster_specification)
        cluster.scale(n_workers)

    #  create output directory
    tilt_series_directory = Path(ts_directory) / "tilt_series"
    tilt_series_directory.mkdir(parents=True, exist_ok=True)

    # set up delayed computation
    for mdoc_file in mdoc_files:
        process_one_tilt_series(
            mdoc_file=mdoc_file,
            tilt_image_files=tilt_image_files,
            tilt_series_directory=tilt_series_directory,
            dose_per_tilt=dose_per_tilt,
        )
    return


@cli.command()
def tiltstack_relion(
    micrographs_star_file: Path = typer.Option(..., prompt=True),
    mdoc_file_pattern: str = typer.Option(..., prompt=True),
    output_directory: Path = typer.Option(..., prompt=True),
    dose_per_tilt: Optional[float] = None,
    cluster_specification: Optional[Path] = None,
):
    star = starfile.read(micrographs_star_file)
    tilt_image_files = star["micrographs"]["rlnMicrographName"]
    mdoc_files = list(Path().glob(mdoc_file_pattern))
    print(mdoc_files)
    tiltstack(
        tilt_image_files=tilt_image_files,
        mdoc_files=mdoc_files,
        ts_directory=output_directory,
        dose_per_tilt=dose_per_tilt,
        cluster_specification=cluster_specification
    )


def process_one_tilt_series(
        mdoc_file,
        tilt_image_files,
        tilt_series_directory,
        dose_per_tilt
):
    ts_basename = basename(mdoc_file)
    ts_directory = tilt_series_directory / ts_basename
    ts_directory.mkdir(parents=True, exist_ok=True)

    ts_metadata_file = ts_directory / f"{ts_basename}.csv"
    ts_file = ts_directory / f"{ts_basename}.mrc"
    ts_raw_angles_file = ts_directory / f"{ts_basename}.rawtlt"

    mdoc_df = prepare_mdoc_dataframe(
        mdoc_file=mdoc_file,
        tilt_image_files=tilt_image_files,
        dose_per_tilt=dose_per_tilt
    )
    write_rawtlt(mdoc_df=mdoc_df, filename=ts_raw_angles_file)
    write_metadata(mdoc_df=mdoc_df, filename=ts_metadata_file)
    stack_tilt_series(mdoc_df=mdoc_df, output_filename=ts_file)


def stack_tilt_series(
    mdoc_df: pd.DataFrame,
    output_filename: Optional[PathLike] = None,
) -> Union[np.ndarray, None]:
    if output_filename is None:
        tilt_series = stack_image_files(mdoc_df["matched_filename"])
        return tilt_series
    else:
        stack_image_files_mmap(
            image_files=mdoc_df["matched_filename"],
            output_filename=output_filename
        )


