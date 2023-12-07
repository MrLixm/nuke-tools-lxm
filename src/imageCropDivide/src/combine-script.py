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
        if not src_files:
            raise ValueError(
                "Cannot find crops files to combine in {}".format(directory)
            )

        dst_file = os.path.join(directory, "{}{}".format(combined_filename, src_ext))

        src_files.sort()
        # name of a file is like "0x2.jpg"
        mosaic_max = os.path.splitext(os.path.basename(src_files[-1]))[0]
        mosaic_max_height = int(mosaic_max.split("x")[1])

        # order of source files matter, for a 2x3 image we need to convert like :
        # [1 4] > [1 2]
        # [2 5] > [3 4]
        # [3 6] > [5 6]
        buffer = []
        for row_index in range(mosaic_max_height):
            buffer += src_files[row_index::mosaic_max_height]
        src_files = buffer

        command = [self._oiiotool_path]
        command += src_files
        # https://openimageio.readthedocs.io/en/latest/oiiotool.html#cmdoption-mosaic
        # XXX: needed so hack explained under works
        command += ["--metamerge"]
        command += ["--mosaic", mosaic_max]
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
        import Pillow

    def run(
        self,
        directory,
        combined_filename,
        delete_crops,
        target_width,
        target_height,
    ):
        # TODO
        raise NotImplementedError()


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
