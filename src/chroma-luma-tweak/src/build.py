# python 3
import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import colour
import numpy

LOGGER = logging.getLogger(__name__)
THIS_DIR = Path(__file__).parent


class BuildPaths:
    src_gizmo = THIS_DIR / "ChromaLumaTweak-template.nk"
    assert src_gizmo.exists()

    src_saturation_gizmo = (
        THIS_DIR.parent.parent / "ocio-saturation" / "ocio-saturation.expr.nk"
    )
    assert src_saturation_gizmo.exists(), src_saturation_gizmo

    build_dir = THIS_DIR.parent
    build_gizmo = build_dir / "ChromaLumaTweak.nk"


def _get_BT2020_10deg_primaries() -> numpy.ndarray:
    # reference: Troy Sobotka
    BT2020_spectral = numpy.array([630, 532, 467])
    BT2020_XYZ_CIE_2012_10d = colour.MSDS_CMFS["CIE 2012 10 Degree Standard Observer"][
        BT2020_spectral
    ]
    BT2020_xyY_CIE_2012_10d = colour.XYZ_to_xyY(BT2020_XYZ_CIE_2012_10d)
    BT2020_primaries_CIE_2012_10d = BT2020_xyY_CIE_2012_10d[..., 0:2]
    return BT2020_primaries_CIE_2012_10d


def get_colorspace_preset() -> str:
    COLORSPACES = {
        "sRGB (native)": ("sRGB", None),
        "Adobe RGB (1998) (native)": ("Adobe RGB (1998)", None),
        "DCI-P3 (native)": ("DCI-P3", None),
        "P3 (D65)": ("DCI-P3", "D65"),
        "ACEScg (native)": ("ACEScg", None),
        "ACES2065-1 (native)": ("ACES2065-1", None),
        "BT.2020 (native)": ("ITU-R BT.2020", None),
        "BT.2020 CIE 2012 10degrees (D65)": (_get_BT2020_10deg_primaries(), "D65"),
        "FilmLight E-Gamut (native)": ("FilmLight E-Gamut", None),
        "ARRI Wide Gamut 3 (native)": ("ARRI Wide Gamut 3", None),
        "ARRI Wide Gamut 4 (native)": ("ARRI Wide Gamut 4", None),
        "REDcolor4 (native)": ("REDcolor4", None),
        "Blackmagic Wide Gamut (native)": ("Blackmagic Wide Gamut", None),
        "DaVinci Wide Gamut (native)": ("DaVinci Wide Gamut", None),
    }

    ILLUMINANTS = colour.CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]

    node = []

    for label, colorspace_data in COLORSPACES.items():
        colorspace_primaries_id = colorspace_data[0]
        colorspace_whitepoint_id = colorspace_data[1]

        colorspace_whitepoint = None

        if colorspace_whitepoint_id:
            colorspace_whitepoint = ILLUMINANTS[colorspace_whitepoint_id]

        if isinstance(colorspace_primaries_id, str):
            colorspace: colour.RGB_Colourspace = colour.RGB_COLOURSPACES[
                colorspace_primaries_id
            ]
            colorspace_primaries = colorspace.primaries

            if not colorspace_whitepoint_id:
                colorspace_whitepoint = colorspace.whitepoint

        elif isinstance(colorspace_primaries_id, numpy.ndarray):
            colorspace_primaries = colorspace_primaries_id

        else:
            raise TypeError(colorspace_primaries_id)

        if colorspace_whitepoint is None:
            raise ValueError("Unspecified whitepoint")

        weights = colour.normalised_primary_matrix(
            colorspace_primaries,
            colorspace_whitepoint,
        )
        weights = "({}, {}, {})".format(*numpy.ravel(weights)[3:6])
        safe_name = re.sub(r"\W", "", label)
        nuke_knob = f'addUserKnob {{22 set_{safe_name} l "{label}" +STARTLINE T "n=nuke.thisNode()[\'weights\'].setValue({weights})"}}'
        node.append(nuke_knob)

    return "\n".join(node).rstrip("\n")


def _get_nuke_syntax_topnode_lines(nuke_script: list[str]) -> tuple[int, int]:
    """
    From a nuke script return the line on that start and end the initialization of the
    top node. Example::

        0 # header comment
        1 Group {
        2  name myGroup
        3  someKnob {{tcl expression}}
        4 }
        5 end_group
        6 Dot {
        7 }

    will return (1,4)

    Args:
        nuke_script: nuke syntax as list of lines

    Returns:
        index of start line, index of end line
    """
    start_index = -1
    end_index = -1
    brack_open_count = 0

    for line_index, line in list(enumerate(nuke_script)):
        if line.strip(" ").startswith("#"):
            continue

        if "{" in line and start_index == -1:
            start_index = line_index
            brack_open_count = 1
            continue

        brack_open_count += line.count("{")
        # remove escaped brackets that doesn't count
        brack_open_count -= line.count(r"\{")

        brack_open_count -= line.count("}")
        # add back escaped brackets that doesn't count
        brack_open_count += line.count(r"\}")

        if brack_open_count == 0:
            end_index = line_index
            break

    return start_index, end_index


def _override_nuke_node_knobs(
    nuke_node: list[str],
    overrides: dict[str, str],
) -> list[str]:
    """
    Parser that is able to override knobs values on a nuke node provided as list of lines.

    Args:
        nuke_node:
            as list of lines.
        overrides:
            knobs override to apply where key="knob name" and value="new knob value".
            One must avoid to create a key named "addUserKnob" !!

    Returns:
        nuke_node with overrides, still as list of lines
    """
    new_node = list(nuke_node)  # make a copy
    _overrides = dict(overrides)  # make a copy

    # // we replace existing knob assignation by our overrides :
    for line_index, line in enumerate(new_node):
        # we stop parsing at the end of the first top node definition
        if line.startswith("}"):
            break

        for override_name, overrides_value in overrides.items():
            if re.match(rf"\s*{override_name}\s", line.strip(" ")):
                new_node[line_index] = f" {override_name} {overrides_value}"
                # we cannot pop a dict we are iterating over, so pop the copy
                _overrides.pop(override_name)

    _, node_end_init_index = _get_nuke_syntax_topnode_lines(new_node)

    # // we add leftover overrides that were not initally set on the node
    for override_name, overrides_value in _overrides.items():
        new_node.insert(node_end_init_index, f" {override_name} {overrides_value}")

    return new_node


def _replace_variable_in_line(
    line: str, name: str, new_lines: list[str]
) -> Optional[list[str]]:
    """
    Replace the given variable with the given lines.

    If the variable is not in the line, None is returned.

    Also handle the system to override nuke knobs defined in the variable "suffix"::

        %VAR_NAME:{"knob name": "knob value", ...}%
    """
    if not line.strip(" ").startswith(f"%{name}"):
        return None

    new_lines = list(new_lines)  # make a copy

    override_pattern = re.compile(r"\s*%(?P<name>\w+):?(?P<overrides>.*)%")
    overrides: Optional[str] = override_pattern.search(line).group("overrides")
    if overrides:
        overrides: Optional[dict] = json.loads(overrides)
        LOGGER.debug(f"({name}): applying overrides {overrides}")
        new_lines = _override_nuke_node_knobs(new_lines, overrides)

    # calculate how much the variable is indented in the original line
    indent = len(line) - len(line.lstrip(" "))
    # add the indent calculated previously to each line
    return [" " * indent + new_line for new_line in new_lines]


def build():
    LOGGER.info(f"build started")
    base_gizmo = BuildPaths.src_gizmo.read_text("utf-8")
    saturation_gizmo = BuildPaths.src_saturation_gizmo.read_text("utf-8").rstrip("\n")
    colorspace_presets = get_colorspace_preset()

    new_gizmo = []

    for line_index, line in enumerate(base_gizmo.split("\n")):
        new_lines = _replace_variable_in_line(
            line,
            name="NODE_Saturation",
            new_lines=saturation_gizmo.split("\n"),
        )
        new_lines = new_lines or _replace_variable_in_line(
            line,
            name="NODE_Presets",
            new_lines=colorspace_presets.split("\n"),
        )
        if new_lines:
            new_gizmo += new_lines
        else:
            new_gizmo.append(line)

    new_gizmo = "\n".join(new_gizmo)
    LOGGER.info(f"writting {BuildPaths.build_gizmo}")
    BuildPaths.build_gizmo.write_text(new_gizmo, "utf-8")
    LOGGER.info("build finished")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    build()
