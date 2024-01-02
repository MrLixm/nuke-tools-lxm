# python 3
import logging
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)
THIS_DIR = Path(__file__).parent


class BuildPaths:
    script_presets = THIS_DIR / "PrimariesInset" / "colorspace-preset-script.py"
    assert script_presets.exists()

    src_gizmo = THIS_DIR / "PrimariesInset" / "PrimariesInset-template.nk"
    assert src_gizmo.exists()

    src_blink_inset = THIS_DIR / "PrimariesInset.blink"
    assert src_blink_inset.exists()

    src_blink_plot = THIS_DIR / "PrimariesPlot.blink"
    assert src_blink_plot.exists()

    build_dir = THIS_DIR.parent
    build_gizmo = build_dir / "PrimariesInset.nk"


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
    return newscript


def build_preset_script() -> str:
    base_script = BuildPaths.script_presets.read_text("utf-8")
    return sanitize_nuke_script(base_script)


def build():
    LOGGER.info(f"build started")
    base_gizmo = BuildPaths.src_gizmo.read_text("utf-8")
    preset_script = build_preset_script()

    blink_inset_source = BuildPaths.src_blink_inset.with_suffix(".blink.src")
    blink_inset_source = blink_inset_source.read_text()
    blink_inset_source = sanitize_nuke_script(blink_inset_source, False)

    blink_inset_desc = BuildPaths.src_blink_inset.with_suffix(".blink.desc")
    blink_inset_desc = blink_inset_desc.read_text()
    blink_inset_desc = sanitize_nuke_script(blink_inset_desc, False)

    blink_plot_source = BuildPaths.src_blink_plot.with_suffix(".blink.src")
    blink_plot_source = blink_plot_source.read_text()
    blink_plot_source = sanitize_nuke_script(blink_plot_source, False)

    blink_plot_desc = BuildPaths.src_blink_plot.with_suffix(".blink.desc")
    blink_plot_desc = blink_plot_desc.read_text()
    blink_plot_desc = sanitize_nuke_script(blink_plot_desc, False)

    new_gizmo = []
    preset_added = False

    for line_index, line in enumerate(base_gizmo.split("\n")):
        if "22 preset_apply" in line and not preset_added:
            line = f' addUserKnob {{22 preset_apply l apply -STARTLINE T "{preset_script}"}}'
            preset_added = True
            LOGGER.debug(f"found preset_apply at line {line_index}")

        if "%INSET_BLINK_SRC%" in line:
            line = line.replace("%INSET_BLINK_SRC%", blink_inset_source)
            LOGGER.debug(f"replaced INSET_BLINK_SRC")
        elif "%INSET_BLINK_DESC%" in line:
            line = line.replace("%INSET_BLINK_DESC%", blink_inset_desc)
            LOGGER.debug(f"replaced INSET_BLINK_DESC")
        elif "%PLOT_BLINK_SRC%" in line:
            line = line.replace("%PLOT_BLINK_SRC%", blink_plot_source)
            LOGGER.debug(f"replaced PLOT_BLINK_SRC")
        elif "%PLOT_BLINK_DESC%" in line:
            line = line.replace("%PLOT_BLINK_DESC%", blink_plot_desc)
            LOGGER.debug(f"replaced PLOT_BLINK_DESC")

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
