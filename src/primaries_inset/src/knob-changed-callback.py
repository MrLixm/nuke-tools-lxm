import logging

import nuke
from gamut_convert import Gamut
from gamut_convert import get_conversion_matrix

LOGGER = logging.getLogger(__name__)

COLORSCIENCE_KNOBS = [
    "primary_r",
    "primary_g",
    "primary_b",
    "whitepoint",
    "inset",
    "inset_r",
    "inset_g",
    "inset_b",
    "whitepoint_offset_x",
    "whitepoint_offset_y",
]


def main(node, knob):
    # type: (nuke.Node, nuke.Knob) -> None
    if knob.name() not in COLORSCIENCE_KNOBS:
        return

    primary_r = tuple(node["primary_r"].getValue())  # type: tuple[float, float]
    primary_g = tuple(node["primary_g"].getValue())  # type: tuple[float, float]
    primary_b = tuple(node["primary_b"].getValue())  # type: tuple[float, float]
    chromaticities = (primary_r, primary_g, primary_b)
    whitepoint = tuple(node["whitepoint"].getValue())  # type: tuple[float, float]
    src_gamut = Gamut(chromaticities, whitepoint)

    primary_r = tuple(node["primary_r_inset"].getValue())  # type: tuple[float, float]
    primary_g = tuple(node["primary_g_inset"].getValue())  # type: tuple[float, float]
    primary_b = tuple(node["primary_b_inset"].getValue())  # type: tuple[float, float]
    chromaticities = (primary_r, primary_g, primary_b)
    whitepoint = tuple(node["whitepoint_inset"].getValue())  # type: tuple[float, float]
    dst_gamut = Gamut(chromaticities, whitepoint)

    matrix = get_conversion_matrix(src_gamut, dst_gamut)
    matrix = matrix.as_2Dlist()
    matrix_flat = sum(matrix, [])

    LOGGER.debug("setting node {} with matrix {}".format(node.name(), matrix))
    matrix_knob = node["matrix"]
    matrix_knob.setValue(matrix_flat)


main(nuke.thisNode(), nuke.thisKnob())
