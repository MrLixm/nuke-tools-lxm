"""
version=4
author=Liam Collod
last_modified=24/04/2022
python>2.7
dependencies={
    nuke=*
}

[What]

From given maximum dimensions, divide an input image into multiples crops.
This a combined script of <cropAndWrite> and <imageCropDivide>.
Must be executed from a python button knob.

[Use]

Must be executed from a python button knob.

[License]

Copyright 2022 Liam Collod
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import logging
import math
import platform
import subprocess
import sys

try:
    from typing import Tuple, List
except ImportError:
    pass

import nuke


LOGGER = logging.getLogger("{}.{}".format(nuke.thisNode(), nuke.thisKnob()))

# dynamically replaced on build
PASS_NUKE_TEMPLATE = "%PASS_NUKE_TEMPLATE%"
WRITE_MASTER_NUKE_TEMPLATE = "%WRITE_MASTER_NUKE_TEMPLATE%"


class CropCoordinate:
    """
    Dataclass or "struct" that just hold multipel attribute represent a crop coordinates.
    """

    def __init__(self, x_start, y_start, x_end, y_end, width_index, height_index):
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.width_index = width_index
        self.height_index = height_index


def generate_crop_coordinates(width_max, height_max, width_source, height_source):
    """
    Args:
        width_max (int): maximum allowed width for each crop
        height_max (int): maximum allowed height for each crop
        width_source (int): width of the source to crop
        height_source (int): height of the source to crop

    Returns:
        list[CropCoordinate]: list of crops to perform to match the given parameters requested
    """
    width_crops_n = math.ceil(width_source / width_max)
    height_crops_n = math.ceil(height_source / height_max)

    if not width_crops_n or not height_crops_n:
        raise RuntimeError(
            "[generate_crop_coordinates] Can't find a number of crop to perform on r({})"
            " or t({}) for the following setup :\n"
            "max={}x{} ; source={}x{}".format(
                width_crops_n,
                height_crops_n,
                width_max,
                height_max,
                width_source,
                height_source,
            )
        )

    width_crops = []

    for i in range(width_crops_n):
        start = width_source / width_crops_n * i
        end = width_source / width_crops_n * i + (width_source / width_crops_n)
        width_crops.append((start, end))

    height_crops = []

    for i in range(height_crops_n):
        start = height_source / height_crops_n * i
        end = height_source / height_crops_n * i + (height_source / height_crops_n)
        height_crops.append((start, end))

    crops = []

    # ORDER matter we are trying to get :
    # [0] > [1] >
    # [2] > [3] > ...
    # that is expected by oiiotool
    # https://openimageio.readthedocs.io/en/latest/oiiotool.html#cmdoption-mosaic
    for height_i in range(len(height_crops)):
        for width_i in range(len(width_crops)):
            crop = CropCoordinate(
                x_start=width_crops[width_i][0],
                y_start=height_crops[height_i][0],
                x_end=width_crops[width_i][1],
                y_end=height_crops[height_i][1],
                width_index=width_i,
                height_index=height_i,
            )
            crops.append(crop)

    return crops


def register_in_clipboard(data):
    """
    Args:
        data(str):
    """

    # Check which operating system is running to get the correct copying keyword.
    if platform.system() == "Darwin":
        copy_keyword = "pbcopy"
    elif platform.system() == "Windows":
        copy_keyword = "clip"
    else:
        raise OSError("Current os not supported. Only [Darwin, Windows]")

    subprocess.run(copy_keyword, universal_newlines=True, input=data)
    return


def generate_nk(
    width_max,
    height_max,
    width_source,
    height_source,
):
    """

    Args:
        width_max(int):
        height_max(int):
        width_source(int):
        height_source(int):

    Returns:
        str: .nk formatted string representing the nodegraph
    """

    crop_coordinates = generate_crop_coordinates(
        width_max,
        height_max,
        width_source,
        height_source,
    )

    out = ""

    master_write_id = "C171d00"
    pass_metadata_key = "__crop/pass_id"

    master_write = WRITE_MASTER_NUKE_TEMPLATE.replace(
        "%METADATA_KEY%", pass_metadata_key
    )
    out += "clone node7f6100171d00|Write|21972 {}\n".format(master_write)
    out += "set {} [stack 0]\n".format(master_write_id)

    for index, crop_coordinate in enumerate(
        crop_coordinates
    ):  # type: int, CropCoordinate
        pass_nk = PASS_NUKE_TEMPLATE
        pass_id = "{}x{}".format(
            crop_coordinate.width_index, crop_coordinate.height_index
        )
        pos_x = 125 * index

        pass_nk = pass_nk.replace("%PASS_ID%", str(pass_id))
        pass_nk = pass_nk.replace("%PASS_XPOS%", str(pos_x))
        pass_nk = pass_nk.replace("%WRITE_CLONE_ID%", str(master_write_id))
        pass_nk = pass_nk.replace("%METADATA_KEY%", str(pass_metadata_key))
        pass_nk = pass_nk.replace("%BOX_X%", str(crop_coordinate.x_end))
        pass_nk = pass_nk.replace("%BOX_Y%", str(crop_coordinate.y_end))
        pass_nk = pass_nk.replace("%BOX_R%", str(crop_coordinate.x_start))
        pass_nk = pass_nk.replace("%BOX_T%", str(crop_coordinate.y_start))

        out += "{}push ${}\n".format(pass_nk, master_write_id)
        continue

    LOGGER.info("[generate_nk] Finished.")
    return out


def run():
    def _check(variable, name):
        if not variable:
            raise ValueError("{} can't be False/None/0".format(name))

    LOGGER.info("[run] Started.")

    width_max = nuke.thisNode()["width_max"].getValue()
    height_max = nuke.thisNode()["height_max"].getValue()
    width_source = nuke.thisNode()["width_source"].getValue()
    height_source = nuke.thisNode()["height_source"].getValue()

    _check(width_max, "width_max")
    _check(height_max, "height_max")
    _check(width_source, "width_source")
    _check(height_source, "height_source")

    nk_str = generate_nk(
        width_max=width_max,
        height_max=height_max,
        width_source=width_source,
        height_source=height_source,
    )
    register_in_clipboard(nk_str)

    LOGGER.info("[run] Finished. Nodegraph copied to clipboard.")
    return


# remember: this modifies the root LOGGER only if it never has been before
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-7s | %(asctime)s [%(name)s] %(message)s",
)
run()
