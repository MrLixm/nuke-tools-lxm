# python 3
"""
Combine multiple python modules so they can be used in a nuke node python callback.
"""
import logging
import sys
from pathlib import Path
import gamut_convert

LOGGER = logging.getLogger(__name__)

GAMUT_CONVERT_PATH = Path(gamut_convert.__file__)
assert GAMUT_CONVERT_PATH.exists()

KNOB_CALLBACK_PATH = (
    Path(__file__).parent / "PrimariesInset" / "knob-changed-callback.py"
)
assert KNOB_CALLBACK_PATH.exists()

PRESET_SCRIPT_PATH = (
    Path(__file__).parent / "PrimariesInset" / "colorspace-preset-script.py"
)
assert PRESET_SCRIPT_PATH.exists()

GIZMO_PATH = Path(__file__).parent / "PrimariesInset" / "PrimariesInset.nk"
assert GIZMO_PATH.exists()

BUILD_PATH = Path(__file__).parent.parent
BUILD_GIZMO = BUILD_PATH / "PrimariesInset.nk"


def sanitize_nuke_script(script: str) -> str:
    newscript = script.replace("\\", r"\\")
    newscript = newscript.split("\n")
    newscript = r"\n".join(newscript)
    newscript = newscript.replace('"', r"\"")
    newscript = newscript.replace("{", r"\{")
    newscript = newscript.replace("}", r"\}")
    return newscript


def build_callback_string() -> str:
    base_script = GAMUT_CONVERT_PATH.read_text("utf-8")
    nuke_script = KNOB_CALLBACK_PATH.read_text("utf-8")
    # remove gamut-convert imports
    nuke_script = "\n".join(
        [
            line
            for line in nuke_script.split("\n")
            if not line.startswith("from gamut_convert")
        ]
    )
    combined_script = base_script + "\n" + nuke_script
    return sanitize_nuke_script(combined_script)


def build_preset_script() -> str:
    base_script = PRESET_SCRIPT_PATH.read_text("utf-8")
    return sanitize_nuke_script(base_script)


def build():
    LOGGER.info(f"build started")
    base_gizmo = GIZMO_PATH.read_text("utf-8")
    knob_callback = build_callback_string()
    preset_script = build_preset_script()

    new_gizmo = []
    callback_added = False
    preset_added = False

    for line_index, line in enumerate(base_gizmo.split("\n")):
        if line.startswith(" knobChanged") and not callback_added:
            line = f' knobChanged "{knob_callback}"'
            callback_added = True
            LOGGER.debug(f"found knobChanged at line {line_index}")

        elif "22 preset_apply" in line and not preset_added:
            line = f' addUserKnob {{22 preset_apply l apply -STARTLINE T "{preset_script}"}}'
            preset_added = True
            LOGGER.debug(f"found preset_apply at line {line_index}")

        new_gizmo.append(line)

    new_gizmo = "\n".join(new_gizmo)
    LOGGER.info(f"writting {BUILD_GIZMO}")
    BUILD_GIZMO.write_text(new_gizmo, "utf-8")
    LOGGER.info("build finished")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    build()
