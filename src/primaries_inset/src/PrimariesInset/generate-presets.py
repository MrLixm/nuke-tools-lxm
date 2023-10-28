import logging

import colour

LOGGER = logging.getLogger(__name__)


PRESETS_NAMES = [
    "ACES2065-1",
    "ACEScg",
    "ACESproxy",
    "ARRI Wide Gamut 3",
    "ARRI Wide Gamut 4",
    "Adobe RGB (1998)",
    "Adobe Wide Gamut RGB",
    "Blackmagic Wide Gamut",
    "DCI-P3",
    "DCI-P3-P",
    "DJI D-Gamut",
    "DRAGONcolor",
    "DRAGONcolor2",
    "DaVinci Wide Gamut",
    "Display P3",
    "F-Gamut",
    "FilmLight E-Gamut",
    "ITU-R BT.2020",
    "ITU-R BT.709",
    "P3-D65",
    "ProPhoto RGB",
    "REDWideGamutRGB",
    "REDcolor",
    "REDcolor2",
    "REDcolor3",
    "REDcolor4",
    "S-Gamut",
    "S-Gamut3",
    "S-Gamut3.Cine",
    "V-Gamut",
    "Venice S-Gamut3",
    "Venice S-Gamut3.Cine",
    "sRGB",
]

DECIMALS_PRECISION = 6


def generate_knob() -> str:
    presets = list(PRESETS_NAMES)
    presets.sort()
    presets = [f'"{preset}"' if " " in preset else preset for preset in presets]
    presets = " ".join(presets)
    return f"addUserKnob {{4 colorspace_preset l Preset M {{{presets}}}}}"


def get_preset_data(preset_name: str) -> dict:
    colorspace: colour.RGB_Colourspace = colour.RGB_COLOURSPACES[preset_name]
    ch = colorspace.primaries
    chromaticities = (
        (
            round(ch[0][0].item(), DECIMALS_PRECISION),
            round(ch[0][1].item(), DECIMALS_PRECISION),
        ),
        (
            round(ch[1][0].item(), DECIMALS_PRECISION),
            round(ch[1][1].item(), DECIMALS_PRECISION),
        ),
        (
            round(ch[2][0].item(), DECIMALS_PRECISION),
            round(ch[2][1].item(), DECIMALS_PRECISION),
        ),
    )
    whitepoint = (
        round(colorspace.whitepoint[0].item(), DECIMALS_PRECISION),
        round(colorspace.whitepoint[1].item(), DECIMALS_PRECISION),
    )
    return {"chromaticities": chromaticities, "whitepoint": whitepoint}


def main():
    LOGGER.info("started")
    knob = generate_knob()
    print(knob)
    print("")
    presets_data = {preset: get_preset_data(preset) for preset in PRESETS_NAMES}
    print(presets_data)

    LOGGER.info("finished")


if __name__ == "__main__":
    main()
