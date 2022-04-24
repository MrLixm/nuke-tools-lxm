"""
version=2
author=Liam Collod
last_modified=24/04/2022
python>2.7
dependencies={
    nuke=*
}

[What]

From given maximum dimensions, divide an input image into multiples crops.
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
except:
    pass

try:
    import nuke
except:
    nuke = None


def setup_logging(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)7s] %(name)30s // %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)

    return logger


logger = setup_logging("imageCropDivide.button", logging.DEBUG)

PASS_METADATA_PATH = "_nuke/passName"
"Metadata key name. Used in write nodes for a flexible pass setup."


class CropNode:
    """
    When creating an instance no node is created in the Nuke nodegraph. Call update()
    to create the node and access it.

    Args:
        x_start(int):
        x_end(int):
        y_start(int):
        y_end(int):
        identifier(str): allow to identify a crop among an array of crop.
            Must be safe to use in a nuke node name
        reformat(bool): enable the reformat option on the crop node if true
    """

    def __init__(self, x_start, x_end, y_start, y_end, identifier, reformat=False):

        self.identifier = identifier
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.reformat = reformat

        self.node = None

        return

    def __repr__(self):
        return "{} : x[{} -> {}] - y[{} -> {}]".format(
            super(CropNode, self).__repr__(),
            self.x_start, self.x_end, self.y_start, self.y_end
        )

    def __str__(self):
        """
        Returns:
            str: node formatted as .nk format
        """
        out = "Crop {\n"
        out += " box {{{} {} {} {}}}\n".format(self.x, self.y, self.width, self.height)
        out += " reformat {}\n".format(str(self.reformat).lower())
        out += "}\n"
        return out

    @property
    def width(self):
        return self.x_end - self.x_start

    @property
    def height(self):
        return self.y_end - self.y_start

    @property
    def x(self):
        return self.x_start

    @property
    def y(self):
        return self.y_start

    def set_name(self, name):
        """
        Args:
            name(str):
        """
        self.node.setName(name)
        return

    def update(self):
        """
        Update the Crop Nuke node knobs with the values stored in the class instance.
        If the node was never created yet, it is created.
        """

        if self.node is None:
            self.__update = False
            self.node = nuke.createNode("Crop")
            self.__update = True
            assert self.node, "[CropNode][update] Can't create nuke node {}".format(self)

        self.node["box"].setX(self.x)
        self.node["box"].setY(self.y)
        self.node["box"].setR(self.width)
        self.node["box"].setT(self.height)
        self.node["reformat"].setValue(self.reformat)

        return


class CropGenerator:
    """

    Args:
        max_size(Tuple[int, int]): (width, height)
        source_size(Tuple[int, int]): (width, height)

    Attributes:
        width_max:
        height_max:
        width_source:
        height_source:
        crops: ordered list of CropNode instance created
    """

    def __init__(self, max_size, source_size):

        self.width_max = max_size[0]  # type: int
        self.height_max = max_size[1]  # type: int
        self.width_source = source_size[0]  # type: int
        self.height_source = source_size[1]  # type: int

        self.crops = list()  # type: List[CropNode]

        self._generate_crops()

        return

    def _get_crop_coordinates(self, crop_number, x=True):
        """
        Return a list of ``x`` or ``y``  start/end coordinates for the number of crops
        specified.

        Args:
            crop_number(int):
            x(bool): return ``x`` coordinates if true else ``y``

        Returns:
            Tuple[Tuple[int, int]]: where ((start, end), ...)
        """

        out = list()
        c = self.width_source if x else self.height_source

        for i in range(crop_number):
            start = c / crop_number * i
            end = c / crop_number * i + (c / crop_number)
            out.append((start, end))

        return tuple(out)

    def _generate_crops(self):
        """
        Create the CropNode instance stored in <crops> attribute.
        These instance still doesn't exist in the Nuke nodegraph.
        """

        width_crops_n = math.ceil(self.width_source / self.width_max)
        height_crops_n = math.ceil(self.height_source / self.height_max)

        if not width_crops_n or not height_crops_n:
            raise RuntimeError(
                "[_generate_crops] Can't find a number of crop to perform on width({})"
                " or height({}) for the following setup :\n"
                "max={}x{} ; source={}x{}".format(
                    width_crops_n, height_crops_n, self.width_max, self.height_max,
                    self.width_source, self.height_source
                )
            )

        width_crops = self._get_crop_coordinates(width_crops_n, x=True)
        height_crops = self._get_crop_coordinates(height_crops_n, x=False)

        for width_i in range(len(width_crops)):

            for height_i in range(len(height_crops)):

                crop = CropNode(
                    x_start=width_crops[width_i][0],
                    y_start=height_crops[height_i][0],
                    x_end=width_crops[width_i][1],
                    y_end=height_crops[height_i][1],
                    identifier="{}x{}".format(width_i, height_i)
                )
                self.crops.append(crop)
                logger.debug(
                    "[CropGenerator][_generate_crops] created    {}".format(crop.__repr__())
                )

            continue

        return


def register_in_clipboard(data):
    """
    Args:
        data(str):
    """

    # Check which operating system is running to get the correct copying keyword.
    if platform.system() == 'Darwin':
        copy_keyword = 'pbcopy'
    elif platform.system() == 'Windows':
        copy_keyword = 'clip'
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

    cg = CropGenerator(
        (width_max, height_max),
        (width_source, height_source),
    )

    out = str()
    out += """set cut_paste_input [stack 0]
version 13.1 v3
push $cut_paste_input\n"""

    id_write_master = None

    for i, cropnode in enumerate(cg.crops):

        pos_x = 125 * i
        pos_y = 125

        out += "Dot {{\n xpos {}\n ypos {}\n}}\n".format(pos_x, pos_y)
        id_last = "N173200"
        out += "set {} [stack 0]\n".format(id_last)
        pos_y += 125

        # CROPNODE
        cropnode.reformat = True
        str_cropnode = str(cropnode)[:-2]  # remove the 2 last character "}\n"
        str_cropnode += " name Crop_{}_\n".format(cropnode.identifier)
        str_cropnode += " xpos {}\n ypos {}\n".format(pos_x, pos_y)
        str_cropnode += "}\n"
        out += str_cropnode
        pos_y += 125

        # ModifyMetadata node
        out += "ModifyMetaData {\n"
        out += " metadata {{{{set {} {}}}}}\n".format(PASS_METADATA_PATH,
                                                      cropnode.identifier)
        out += " xpos {}\n ypos {}\n".format(pos_x, pos_y)
        out += "}\n"
        pos_y += 125

        # Write node cloning system
        if id_write_master:
            out += "clone ${} {{\n xpos {}\n ypos {}\n}}\n".format(id_write_master,
                                                                   pos_x, pos_y)
            pos_y += 125
        else:
            id_write_master = "C171d00"
            out += "clone node7f6100171d00|Write|21972 Write {\n"
            out += " xpos {}\n ypos {}\n".format(pos_x, pos_y)
            out += " file \"[metadata {}].jpg\"".format(PASS_METADATA_PATH)
            out += " file_type jpeg\n _jpeg_quality 1\n _jpeg_sub_sampling 4:4:4\n"
            out += "}\n"
            out += "set {} [stack 0]\n".format(id_write_master)

        out += "push ${}\n".format(id_last)
        continue

    logger.info("[generate_nk] Finished.")
    return out


def run():
    """
    """
    logger.info("[run] Started.")

    width_max = nuke.thisNode()["width_max"].getValue()
    height_max = nuke.thisNode()["height_max"].getValue()
    width_source = nuke.thisNode()["width_source"].getValue()
    height_source = nuke.thisNode()["height_source"].getValue()

    assert width_max, "ValueError: width_max can't be False/None/0"
    assert height_max, "ValueError: height_max can't be False/None/0"
    assert width_source, "ValueError: width_source can't be False/None/0"
    assert height_source, "ValueError: height_source can't be False/None/0"

    nk_str = generate_nk(
        width_max=width_max,
        height_max=height_max,
        width_source=width_source,
        height_source=height_source,
    )
    register_in_clipboard(nk_str)

    logger.info("[run] Finished. Nodegraph copied to clipboard.")
    return


run()