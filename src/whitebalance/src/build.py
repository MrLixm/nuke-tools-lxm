# python 3
import logging
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)
THIS_DIR = Path(__file__).parent


class BuildPaths:
    src_blink_script = THIS_DIR / "WhiteBalance.blink"
    assert src_blink_script.exists()

    src_gizmo = THIS_DIR / "WhiteBalance-template.nk"
    assert src_gizmo.exists()

    build_dir = THIS_DIR.parent
    build_gizmo = build_dir / "WhiteBalance.nk"


def sanitize_nuke_script(script: str, convert_new_lines=True) -> str:
    if convert_new_lines:
        newscript = script.replace("\\", r"\\")
        newscript = newscript.split("\n")
        newscript = r"\n".join(newscript)
    else:
        newscript = script.split(r"\n")
        newscript = [line.replace("\\", r"\\") for line in newscript]
        newscript = r"\n".join(newscript)

    newscript = newscript.replace('"', r"\"")
    newscript = newscript.replace("{", r"\{")
    newscript = newscript.replace("}", r"\}")
    newscript = newscript.replace("[", r"\[")
    return newscript


def build():
    LOGGER.info(f"build started")
    base_gizmo = BuildPaths.src_gizmo.read_text("utf-8")

    blink_source = BuildPaths.src_blink_script.with_suffix(".blink.src")
    assert blink_source.exists()
    blink_source = blink_source.read_text()
    blink_source = sanitize_nuke_script(blink_source, False)

    blink_desc = BuildPaths.src_blink_script.with_suffix(".blink.desc")
    assert blink_desc.exists()
    blink_desc = blink_desc.read_text()
    blink_desc = sanitize_nuke_script(blink_desc, False)

    new_gizmo = []

    for line_index, line in enumerate(base_gizmo.split("\n")):
        if "%BLINK_SRC%" in line:
            line = line.replace("%BLINK_SRC%", blink_source)
            LOGGER.debug(f"replaced BLINK_SRC")
        elif "%BLINK_DESC%" in line:
            line = line.replace("%BLINK_DESC%", blink_desc)
            LOGGER.debug(f"replaced BLINK_DESC")

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
