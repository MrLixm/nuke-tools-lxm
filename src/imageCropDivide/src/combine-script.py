import abc
import logging
import os
import subprocess
import sys

import nuke

LOGGER = logging.getLogger(__name__)


class BaseCombineMethod:
    name = ""

    def __init__(self, *args, **kwargs):
        if not self.name:
            raise NotImplementedError("name attribute must be implemented")

    @abc.abstractmethod
    def run(
        self,
        directory,
        combined_filename,
        delete_crops,
        target_width,
        target_height,
    ):
        """

        Args:
            directory(str): filesystem path to an existing directory with file inside
            combined_filename(str): valid filesystem file name without extension
            delete_crops(bool): True to delete crops once combined
            target_width(int): taregt width of the combined image
            target_height(int): taregt height of the combined image

        Returns:
            str: filesystem path to the combined file created
        """
        pass


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


class OiiotoolCombineMethod(BaseCombineMethod):
    name = "oiiotool executable"

    def __init__(self, oiiotool_path=None, *args, **kwargs):
        super(OiiotoolCombineMethod, self).__init__()
        if oiiotool_path:
            self._oiiotool_path = oiiotool_path
        else:
            self._oiiotool_path = os.getenv("OIIOTOOL")

        if not self._oiiotool_path:
            raise ValueError("No oiiotool path found.")
        if not os.path.exists(self._oiiotool_path):
            raise ValueError(
                "Oiiotool path provide doesn't exist: {}".format(oiiotool_path)
            )

    def run(
        self,
        directory,
        combined_filename,
        delete_crops,
        target_width,
        target_height,
    ):
        src_files = find_crop_images_in_dir(directory)
        src_ext = os.path.splitext(src_files[0])[1]
        if not src_files:
            raise ValueError(
                "Cannot find crops files to combine in {}".format(directory)
            )

        dst_file = os.path.join(directory, "{}{}".format(combined_filename, src_ext))

        src_files = sort_crops_paths_topleft_rowcolumn(src_files)
        tiles_size = get_grid_size(src_files)

        command = [self._oiiotool_path]
        command += src_files
        # https://openimageio.readthedocs.io/en/latest/oiiotool.html#cmdoption-mosaic
        # XXX: needed so hack explained under works
        command += ["--metamerge"]
        command += ["--mosaic", "{}x{}".format(tiles_size[0], tiles_size[1])]
        command += ["--cut", "0,0,{},{}".format(target_width - 1, target_height - 1)]
        # XXX: hack to preserve metadata that is lost with the mosaic operation
        command += ["-i", src_files[0], "--chappend"]
        command += ["-o", dst_file]

        LOGGER.info("about to call oiiotool with {}".format(command))
        subprocess.check_call(command)

        if not os.path.exists(dst_file):
            raise RuntimeError(
                "Unexpected issue: combined file doesn't exist on disk at <{}>"
                "".format(dst_file)
            )

        if delete_crops:
            for src_file in src_files:
                os.unlink(src_file)

        return dst_file


class PillowCombineMethod(BaseCombineMethod):
    name = "python Pillow library"

    def __init__(self, *args, **kwargs):
        super(PillowCombineMethod, self).__init__()
        # expected to raise if PIL not available
        from PIL import Image

    def run(
        self,
        directory,
        combined_filename,
        delete_crops,
        target_width,
        target_height,
    ):
        from PIL import Image

        src_files = find_crop_images_in_dir(directory)
        src_files = sort_crops_paths_topleft_rowcolumn(src_files)
        column_number, row_number = get_grid_size(src_files)

        src_ext = os.path.splitext(src_files[0])[1]
        dst_file = os.path.join(directory, "{}{}".format(combined_filename, src_ext))

        images = [Image.open(filepath) for filepath in src_files]
        # XXX: assume all crops have the same size
        tile_size = images[0].size

        # XXX: we use an existing image for our new image so we preserve metadata
        combined_image = Image.open(src_files[0])
        buffer_image = Image.new(
            mode=combined_image.mode, size=(target_width, target_height)
        )
        # XXX: part of the hack to preserve metadata, we do that because image.resize sucks
        #  and doesn't return an exact copy of the initial instance
        combined_image.im = buffer_image.im
        combined_image._size = buffer_image._size
        image_index = 0

        for column_index in range(column_number):
            for row_index in range(row_number):
                image = images[image_index]
                image_index += 1
                coordinates = (tile_size[0] * row_index, tile_size[1] * column_index)
                combined_image.paste(image, box=coordinates)

        save_kwargs = {}
        if src_ext.startswith(".jpg"):
            save_kwargs = {
                "quality": "keep",
                "subsampling": "keep",
                "qtables": "keep",
            }

        combined_image.save(fp=dst_file, **save_kwargs)

        if delete_crops:
            for src_file in src_files:
                os.unlink(src_file)

        return dst_file


COMBINE_METHODS = [
    OiiotoolCombineMethod,
    PillowCombineMethod,
]


def run():
    LOGGER.info("[run] Started.")

    export_dir = nuke.thisNode()["export_directory"].getValue()  # type: str
    combined_filename = nuke.thisNode()["combined_filename"].getValue()  # type: str
    delete_crops = nuke.thisNode()["delete_crops"].getValue()  # type: bool
    oiiotool_path = nuke.thisNode()["oiiotool_path"].getValue()  # type: str
    width_source = int(nuke.thisNode()["width_source"].getValue())  # type: int
    height_source = int(nuke.thisNode()["height_source"].getValue())  # type: int

    if not export_dir or not os.path.isdir(export_dir):
        raise ValueError(
            "Invalid export directory <{}>: not found on disk.".format(export_dir)
        )

    combine_instance = None

    for combine_method_class in COMBINE_METHODS:
        try:
            combine_instance = combine_method_class(oiiotool_path=oiiotool_path)
        except Exception as error:
            LOGGER.debug("skipping class {}: {}".format(combine_method_class, error))

    if not combine_instance:
        raise RuntimeError(
            "No available method to combine the renders found. Available methods are:\n{}"
            "\nSee documentation for details."
            "".format([method.name for method in COMBINE_METHODS])
        )

    LOGGER.info("[run] about to combine directory {} ...".format(export_dir))
    combined_filepath = combine_instance.run(
        directory=export_dir,
        delete_crops=delete_crops,
        combined_filename=combined_filename,
        target_width=width_source,
        target_height=height_source,
    )
    nuke.message("Successfully created combine file: {}".format(combined_filepath))
    LOGGER.info("[run] Finished.")


# remember: this modifies the root LOGGER only if it never has been before
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-7s | %(asctime)s [%(name)s] %(message)s",
    stream=sys.stdout,
)
run()
