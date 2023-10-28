import logging

import nuke

LOGGER = logging.getLogger(__name__)

PRESETS = {
    "ACES2065-1": {
        "chromaticities": ((0.7347, 0.2653), (0.0, 1.0), (0.0001, -0.077)),
        "whitepoint": (0.32168, 0.33767),
    },
    "ACEScg": {
        "chromaticities": ((0.713, 0.293), (0.165, 0.83), (0.128, 0.044)),
        "whitepoint": (0.32168, 0.33767),
    },
    "ACESproxy": {
        "chromaticities": ((0.713, 0.293), (0.165, 0.83), (0.128, 0.044)),
        "whitepoint": (0.32168, 0.33767),
    },
    "ARRI Wide Gamut 3": {
        "chromaticities": ((0.684, 0.313), (0.221, 0.848), (0.0861, -0.102)),
        "whitepoint": (0.3127, 0.329),
    },
    "ARRI Wide Gamut 4": {
        "chromaticities": ((0.7347, 0.2653), (0.1424, 0.8576), (0.0991, -0.0308)),
        "whitepoint": (0.3127, 0.329),
    },
    "Adobe RGB (1998)": {
        "chromaticities": ((0.64, 0.33), (0.21, 0.71), (0.15, 0.06)),
        "whitepoint": (0.3127, 0.329),
    },
    "Adobe Wide Gamut RGB": {
        "chromaticities": ((0.7347, 0.2653), (0.1152, 0.8264), (0.1566, 0.0177)),
        "whitepoint": (0.3457, 0.3585),
    },
    "Blackmagic Wide Gamut": {
        "chromaticities": (
            (0.717722, 0.317118),
            (0.228041, 0.861569),
            (0.100584, -0.082045),
        ),
        "whitepoint": (0.312717, 0.329031),
    },
    "DCI-P3": {
        "chromaticities": ((0.68, 0.32), (0.265, 0.69), (0.15, 0.06)),
        "whitepoint": (0.314, 0.351),
    },
    "DCI-P3-P": {
        "chromaticities": ((0.74, 0.27), (0.22, 0.78), (0.09, -0.09)),
        "whitepoint": (0.314, 0.351),
    },
    "DJI D-Gamut": {
        "chromaticities": ((0.71, 0.31), (0.21, 0.88), (0.09, -0.08)),
        "whitepoint": (0.3127, 0.329),
    },
    "DRAGONcolor": {
        "chromaticities": (
            (0.758656, 0.330355),
            (0.294924, 0.708053),
            (0.085962, -0.045879),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "DRAGONcolor2": {
        "chromaticities": (
            (0.758656, 0.330356),
            (0.294924, 0.708053),
            (0.144169, 0.050357),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "DaVinci Wide Gamut": {
        "chromaticities": ((0.8, 0.313), (0.1682, 0.9877), (0.079, -0.1155)),
        "whitepoint": (0.3127, 0.329),
    },
    "Display P3": {
        "chromaticities": ((0.68, 0.32), (0.265, 0.69), (0.15, 0.06)),
        "whitepoint": (0.3127, 0.329),
    },
    "F-Gamut": {
        "chromaticities": ((0.708, 0.292), (0.17, 0.797), (0.131, 0.046)),
        "whitepoint": (0.3127, 0.329),
    },
    "FilmLight E-Gamut": {
        "chromaticities": ((0.8, 0.3177), (0.18, 0.9), (0.065, -0.0805)),
        "whitepoint": (0.3127, 0.329),
    },
    "ITU-R BT.2020": {
        "chromaticities": ((0.708, 0.292), (0.17, 0.797), (0.131, 0.046)),
        "whitepoint": (0.3127, 0.329),
    },
    "ITU-R BT.709": {
        "chromaticities": ((0.64, 0.33), (0.3, 0.6), (0.15, 0.06)),
        "whitepoint": (0.3127, 0.329),
    },
    "P3-D65": {
        "chromaticities": ((0.68, 0.32), (0.265, 0.69), (0.15, 0.06)),
        "whitepoint": (0.3127, 0.329),
    },
    "ProPhoto RGB": {
        "chromaticities": ((0.7347, 0.2653), (0.1596, 0.8404), (0.0366, 0.0001)),
        "whitepoint": (0.3457, 0.3585),
    },
    "REDWideGamutRGB": {
        "chromaticities": (
            (0.780308, 0.304253),
            (0.121595, 1.493994),
            (0.095612, -0.084589),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "REDcolor": {
        "chromaticities": (
            (0.701059, 0.330181),
            (0.298811, 0.625169),
            (0.135039, 0.035262),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "REDcolor2": {
        "chromaticities": (
            (0.897407, 0.330776),
            (0.296022, 0.684636),
            (0.0998, -0.023001),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "REDcolor3": {
        "chromaticities": (
            (0.702599, 0.330186),
            (0.295782, 0.689748),
            (0.111091, -0.004332),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "REDcolor4": {
        "chromaticities": (
            (0.702598, 0.330185),
            (0.295782, 0.689748),
            (0.144459, 0.050838),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "S-Gamut": {
        "chromaticities": ((0.73, 0.28), (0.14, 0.855), (0.1, -0.05)),
        "whitepoint": (0.3127, 0.329),
    },
    "S-Gamut3": {
        "chromaticities": ((0.73, 0.28), (0.14, 0.855), (0.1, -0.05)),
        "whitepoint": (0.3127, 0.329),
    },
    "S-Gamut3.Cine": {
        "chromaticities": ((0.766, 0.275), (0.225, 0.8), (0.089, -0.087)),
        "whitepoint": (0.3127, 0.329),
    },
    "V-Gamut": {
        "chromaticities": ((0.73, 0.28), (0.165, 0.84), (0.1, -0.03)),
        "whitepoint": (0.3127, 0.329),
    },
    "Venice S-Gamut3": {
        "chromaticities": (
            (0.740464, 0.279364),
            (0.089241, 0.89381),
            (0.110488, -0.052579),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "Venice S-Gamut3.Cine": {
        "chromaticities": (
            (0.775902, 0.274502),
            (0.188683, 0.828685),
            (0.101337, -0.089188),
        ),
        "whitepoint": (0.3127, 0.329),
    },
    "sRGB": {
        "chromaticities": ((0.64, 0.33), (0.3, 0.6), (0.15, 0.06)),
        "whitepoint": (0.3127, 0.329),
    },
}


def main(node, knob):
    # type: (nuke.Node, nuke.Knob) -> None

    logprefix = "(node<{}>)".format(node.name())

    preset_name = node["colorspace_preset"].value()  # type: str
    if preset_name not in PRESETS:
        raise ValueError(
            "Selected preset name {} is not supported. "
            "This might be a developer mistake.".format(preset_name)
        )
    preset = PRESETS[preset_name]
    chromaticities = preset["chromaticities"]
    whitepoint = preset["whitepoint"]

    LOGGER.debug("{} asked preset {}".format(logprefix, preset_name))
    LOGGER.debug("{} setting chromaticities={}".format(logprefix, chromaticities))
    LOGGER.debug("{} setting whitepoint={}".format(logprefix, whitepoint))

    node["primary_r"].setValue(list(chromaticities[0]))
    node["primary_g"].setValue(list(chromaticities[1]))
    node["primary_b"].setValue(list(chromaticities[2]))
    node["whitepoint"].setValue(list(whitepoint))


main(nuke.thisNode(), nuke.thisKnob())
