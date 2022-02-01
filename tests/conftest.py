from pathlib import Path

import pytest

TEST_DATA = Path(__file__).parent / "test_data"


@pytest.fixture
def tilt_series_mdoc_file():
    return TEST_DATA / "mdoc" / "TS_01.mrc.mdoc"


@pytest.fixture
def tilt_image_files():
    tilt_image_directory = TEST_DATA / "tilt_images"
    return sorted(list(tilt_image_directory.glob("*.mrc")))


@pytest.fixture
def motioncor_output():
    motioncor_output_directory = TEST_DATA / "motioncor_output"
    return motioncor_output_directory / "corrected_micrographs.star"
