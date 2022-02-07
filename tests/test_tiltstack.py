from pathlib import Path

import numpy as np

from tiltstack.io_utils import read_mrc
from tiltstack.tiltstack import stack_tilt_series, tiltstack_relion
from tiltstack.utils import basename


def test_stack(mdoc_df, tilt_image_files):
    tilt_series = stack_tilt_series(mdoc_df=mdoc_df)
    assert isinstance(tilt_series, np.ndarray)
    assert tilt_series.shape == (41, 10, 10)
    # image at idx 20 should be the zero degree image
    # zero degree image is first in tilt image file list
    assert np.allclose(tilt_series[20], read_mrc(tilt_image_files[0]))


def test_tiltstack_relion(
    motioncor_output, test_data_directory, tmpdir, tilt_image_files
):
    relative_path = test_data_directory.relative_to(Path().absolute())
    mdoc_file_pattern = f"{relative_path}/mdoc/*.mdoc"
    tiltstack_relion(
        micrographs_star_file=motioncor_output,
        mdoc_file_pattern=mdoc_file_pattern,
        output_directory=tmpdir,
        dose_per_tilt=3,
    )
    tilt_series_basename = 'TS_01'
    output_file = Path(tmpdir) / "tilt_series" / tilt_series_basename / f"{tilt_series_basename}.mrc"
    assert output_file.exists()
    tilt_series = read_mrc(output_file)
    assert np.allclose(tilt_series[20], read_mrc(tilt_image_files[0]))
