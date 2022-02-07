from pathlib import Path

import pytest

from tiltstack.mdoc import prepare_mdoc_dataframe

TEST_DATA = Path(__file__).parent / "test_data"


@pytest.fixture
def test_data_directory():
    return TEST_DATA


@pytest.fixture
def tilt_series_mdoc_file():
    return TEST_DATA / "mdoc" / "TS_01.mrc.mdoc"


@pytest.fixture
def tilt_image_files():
    tilt_image_directory = TEST_DATA / "tilt_images"
    return sorted(list(tilt_image_directory.glob("*.mrc")))


@pytest.fixture
def mdoc_df(tilt_series_mdoc_file, tilt_image_files):
    return prepare_mdoc_dataframe(
        mdoc_file=tilt_series_mdoc_file,
        tilt_image_files=tilt_image_files,
        dose_per_tilt=3
    )


@pytest.fixture
def motioncor_output():
    motioncor_output_directory = TEST_DATA / "motioncor_output"
    return motioncor_output_directory / "corrected_micrographs.star"
