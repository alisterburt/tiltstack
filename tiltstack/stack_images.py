from os import PathLike
from typing import List

import mrcfile
import numpy as np

from tiltstack.io_utils import get_image_shape, get_pixel_size, read_mrc


def stack_image_files(image_files: List[PathLike]) -> np.ndarray:
    n_images = len(image_files)
    _, h, w = get_image_shape(image_files[0])
    stack_shape = (n_images, h, w)
    stack = np.empty(shape=stack_shape, dtype=np.float16)
    for idx, image_file in enumerate(image_files):
        stack[idx] = read_mrc(image_file)
    return stack


def stack_image_files_mmap(image_files: List[PathLike], output_filename: PathLike):
    n_images = len(image_files)
    _, h, w = get_image_shape(image_files[0])
    stack_shape = (n_images, h, w)
    mrc = mrcfile.new_mmap(output_filename, shape=stack_shape, mrc_mode=12)
    for idx, image_file in enumerate(image_files):
        mrc.data[idx] = read_mrc(image_file)
    pixel_size = get_pixel_size(image_files[0])
    mrc.voxel_size = (pixel_size, pixel_size, 0)
    mrc.close()
