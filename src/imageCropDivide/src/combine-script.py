import logging
import os
import subprocess
import sys

import nuke

LOGGER = logging.getLogger("combine-script")


def find_crop_images_in_dir(directory):
    """
    Args:
        directory(str): filesystem path to an existing directory with file inside

    Returns:
        list[str]: list of existing files
    """
    # XXX: we assume directory only contains the images we want to combine but
    #   we still perform some sanity checks just in case
    src_files = [
        os.path.join(directory, filename) for filename in os.listdir(directory)
    ]
    src_ext = os.path.splitext(src_files[0])[1]
    src_files = [
        filepath
        for filepath in src_files
        if os.path.isfile(filepath) and filepath.endswith(src_ext)
    ]
    return src_files


def sort_crops_paths_topleft_rowcolumn(crop_paths):
    """
    Change the order of the given list of images so it correspond to a list of crop
    starting from the top-left, doing rows then columns.

    Example for a 2x3 image::

        [1 2]
        [3 4]
        [5 6]

    Args:
        crop_paths: list of file paths exported by the ICD node.

    Returns:
        new list of same file paths but sorted differently.
    """

    # copy
    _crop_paths = list(crop_paths)
    _crop_paths.sort()

    _, mosaic_max_height = get_grid_size(crop_paths)

    # for a 2x3 image we need to convert like :
    # [1 4] > [1 2]
    # [2 5] > [3 4]
    # [3 6] > [5 6]
    buffer = []
    for row_index in range(mosaic_max_height):
        buffer += _crop_paths[row_index::mosaic_max_height]

    return buffer


def get_grid_size(crop_paths):
    """
    Returns:
        tuple[int, int]: (columns number, rows number).
    """
    # copy
    _crop_paths = list(crop_paths)
    _crop_paths.sort()
    # name of a file is like "0x2.jpg"
    mosaic_max = os.path.splitext(os.path.basename(_crop_paths[-1]))[0]
    mosaic_max_width = int(mosaic_max.split("x")[0])
    mosaic_max_height = int(mosaic_max.split("x")[1])
    return mosaic_max_width, mosaic_max_height


def oiiotool_combine(
    oiiotool_path,
    directory,
    combined_filepath,
    delete_crops,
    target_width,
    target_height,
):
    src_files = find_crop_images_in_dir(directory)
    src_ext = os.path.splitext(src_files[0])[1]
    if not src_files:
        raise ValueError("Cannot find crops files to combine in {}".format(directory))

    dst_file = combined_filepath + src_ext

    src_files = sort_crops_paths_topleft_rowcolumn(src_files)
    tiles_size = get_grid_size(src_files)

    command = [oiiotool_path]
    command += src_files
    # https://openimageio.readthedocs.io/en/latest/oiiotool.html#cmdoption-mosaic
    command += ["--mosaic", "{}x{}".format(tiles_size[0], tiles_size[1])]
    command += ["--cut", "0,0,{},{}".format(target_width - 1, target_height - 1)]
    command += ["-i", src_files[0], "--swap", "--pastemeta"]
    command += ["-o", dst_file]

    LOGGER.info("about to call oiiotool with {}".format(command))
    result = subprocess.run(command)
    if result.returncode:
        raise RuntimeError(
            "Could not run oiiotool command; exitcode={}".format(result.returncode)
        )

    if not os.path.exists(dst_file):
        raise RuntimeError(
            "Unexpected issue: combined file doesn't exist on disk at <{}>"
            "".format(dst_file)
        )

    if delete_crops:
        for src_file in src_files:
            LOGGER.debug("unlink({})".format(src_file))
            os.unlink(src_file)

    return dst_file


def run():
    export_dir = nuke.thisNode()["export_directory"].evaluate()  # type: str
    combined_filepath = nuke.thisNode()["combined_filepath"].evaluate()  # type: str
    delete_crops = nuke.thisNode()["delete_crops"].getValue()  # type: bool
    oiiotool_path = nuke.thisNode()["oiiotool_path"].evaluate()  # type: str
    width_source = int(nuke.thisNode()["width_source"].getValue())  # type: int
    height_source = int(nuke.thisNode()["height_source"].getValue())  # type: int

    if not export_dir or not os.path.isdir(export_dir):
        raise ValueError(
            "Invalid export directory <{}>: not found on disk.".format(export_dir)
        )
    export_dir = os.path.abspath(export_dir)

    oiiotool_path = oiiotool_path or os.getenv("OIIOTOOL")
    if not oiiotool_path:
        raise RuntimeError(
            "No OIIOTOOL environment variable found; oiiotool must then be specified in the oiiotool_path knob."
        )

    LOGGER.info(
        "combining images from '{}' to {}x{}"
        "".format(export_dir, width_source, height_source)
    )
    combined_filepath = oiiotool_combine(
        oiiotool_path=oiiotool_path,
        directory=export_dir,
        delete_crops=delete_crops,
        combined_filepath=combined_filepath,
        target_width=width_source,
        target_height=height_source,
    )
    LOGGER.info("created combined image at '{}'".format(combined_filepath))
    nuke.message("Created combined image at '{}'".format(combined_filepath))


# remember: this modifies the root LOGGER only if it never has been before
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-7s | %(asctime)s [%(name)s] %(message)s",
    stream=sys.stdout,
)
run()
