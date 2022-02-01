import os
from typing import Tuple

import mrcfile
import numpy as np


def read_mrc(filename: os.PathLike) -> np.ndarray:
    with mrcfile.open(filename) as mrc:
        data = mrc.data
    return data


def get_pixel_size(filename: os.PathLike) -> float:
    with mrcfile.open(filename, header_only=True) as mrc:
        pixel_size = mrc.voxel_size.x
    return pixel_size


def get_image_shape(filename: os.PathLike) -> Tuple[int, int, int]:
    with mrcfile.open(filename, header_only=True) as mrc:
        nz, ny, nx = mrc.header.nz, mrc.header.ny, mrc.header.nx
    return int(nz), int(ny), int(nx)
