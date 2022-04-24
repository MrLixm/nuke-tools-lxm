"""
version=1
author=Liam Collod
last_modified=24/04/2022
python>2.7

[What]

From given maximum dimensions, divide an input image into multiples crops.
Each crop "pass" have a write setup created.

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
import sys

try:
    import nuke
except:
    pass

import imageCropDivide


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


logger = setup_logging("cropAndWrite", logging.DEBUG)


PASS_METADATA_PATH = "_nuke/passName"
"Metadata key name. Used in write nodes for a flexible pass setup."


def run():

    # width_max = nuke.thisNode()["width_max"].getValue()
    # height_max = nuke.thisNode()["height_max"].getValue()
    # width_source = nuke.thisNode()["width_source"].getValue()
    # height_source = nuke.thisNode()["height_source"].getValue()
    # input_node = nuke.thisNode()["input_node"]

    width_max = 1920
    height_max = 1080
    width_source = 3580
    height_source = 2560

    cg = imageCropDivide.CropGenerator(
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
        widthi, heighti = cropnode.identifier.split("x")
        widthi = int(widthi) + 1  # start at 0 so offset
        heighti = int(heighti) + 1
        cropnode.reformat = True
        str_cropnode = str(cropnode)[:-2]  # remove the 2 last character "}\n"
        str_cropnode += " name Crop_{}_\n".format(cropnode.identifier)
        str_cropnode += " xpos {}\n ypos {}\n".format(pos_x, pos_y)
        str_cropnode += "}\n"
        out += str_cropnode
        pos_y += 125

        # ModifyMetadata node
        out += "ModifyMetaData {\n"
        out += " metadata {{{{set {} {}}}}}\n".format(PASS_METADATA_PATH, cropnode.identifier)
        out += " xpos {}\n ypos {}\n".format(pos_x, pos_y)
        out += "}\n"
        pos_y += 125

        # Write node cloning system
        if id_write_master:
            out += "clone ${} {{\n xpos {}\n ypos {}\n}}\n".format(id_write_master, pos_x, pos_y)
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

    # Write to nk file
    path = "nodegraph.nk"
    with open(path, "w") as f:
        f.write(out)
    logger.info("[run] Writed {}.".format(path))

    logger.info("[run] Finished.")
    return


if __name__ == '__main__':
    run()