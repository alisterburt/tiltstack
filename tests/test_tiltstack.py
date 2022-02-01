from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tiltstack.io_utils import read_mrc
from tiltstack.tiltstack import stack_tilt_series, tiltstack_relion


def test_stack(tilt_series_mdoc_file, tilt_image_files):
    tilt_series, metadata_df = stack_tilt_series(
        tilt_image_files=tilt_image_files, mdoc_file=tilt_series_mdoc_file
    )
    assert isinstance(tilt_series, np.ndarray)
    assert isinstance(metadata_df, pd.DataFrame)
    assert tilt_series.shape == (41, 10, 10)
    # image at idx 20 should be the zero degree image
    # zero degree image is first in tilt image file list
    assert np.allclose(tilt_series[20], read_mrc(tilt_image_files[0]))


def test_tiltstack_relion(
    motioncor_output, tilt_series_mdoc_file, tmpdir, tilt_image_files
):
    tiltstack_relion(
        micrographs_star_file=motioncor_output,
        mdoc_files=[tilt_series_mdoc_file],
        output_directory=tmpdir,
        dose_per_tilt=3,
    )
    tilt_series_basename = Path(tilt_series_mdoc_file).stem
    output_file = Path(tmpdir) / "tilt_series" / f"{tilt_series_basename}.mrc"
    assert output_file.exists()
    tilt_series = read_mrc(output_file)
    assert np.allclose(tilt_series[20], read_mrc(tilt_image_files[0]))
