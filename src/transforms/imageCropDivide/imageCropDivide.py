"""
version=6
author=Liam Collod
last_modified=24/04/2022
python>2.7

[What]

From given maximum dimensions, divide an input image into multiples crops.

[Use]

...

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
import sys

try:
    from typing import Tuple, List
except:
    pass

try:
    import nuke
except:
    pass


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


logger = setup_logging("imageCropDivide", logging.DEBUG)


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


def run():

    width_max = nuke.thisNode()["width_max"].getValue()
    height_max = nuke.thisNode()["height_max"].getValue()
    width_source = nuke.thisNode()["width_source"].getValue()
    height_source = nuke.thisNode()["height_source"].getValue()
    input_node = nuke.thisNode()["input_node"]

    cg = CropGenerator(
        (width_max, height_max),
        (width_source, height_source),
    )

    for cropnode in cg.crops:

        cropnode.update()
        cropnode.reformat = True
        cropnode.set_name("Crop_{}_".format(cropnode.identifier))

    logger.info("[run] Finished.")
    return


def __test():
    """
    For testing out of a Nuke context
    """

    cg = CropGenerator((1920, 1080), (3872, 2592))
    for cropnode in cg.crops:
        print(str(cropnode))
        continue

    logger.info("[__test] Finished.")
    return


if __name__ == '__main__':
    # run()
    __test()
