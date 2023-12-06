# python 3
import logging
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)
THIS_DIR = Path(__file__).parent


class BuildPaths:
    src_btn_script = THIS_DIR / "btn-script-template.py"
    assert src_btn_script.exists()

    src_gizmo = THIS_DIR / "ImageCropDivide-template.nk"
    assert src_gizmo.exists()

    src_pass_nk = THIS_DIR / "Write-pass-template.nk"
    assert src_pass_nk.exists()

    src_write_nk = THIS_DIR / "Write-master-template.nk"
    assert src_write_nk.exists()

    build_dir = THIS_DIR.parent
    build_gizmo = build_dir / "ImageCropDivide.nk"


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


def build_python_script() -> str:
    base_script = BuildPaths.src_btn_script.read_text("utf-8")

    nuke_pass_template = BuildPaths.src_pass_nk.read_text("utf-8")
    nuke_write_template = BuildPaths.src_write_nk.read_text("utf-8")

    base_script = base_script.replace(
        '"%PASS_NUKE_TEMPLATE%"',
        repr(nuke_pass_template),
    )
    base_script = base_script.replace(
        '"%WRITE_MASTER_NUKE_TEMPLATE%"',
        repr(nuke_write_template),
    )
    return sanitize_nuke_script(base_script)


def build():
    LOGGER.info(f"build started")
    base_gizmo = BuildPaths.src_gizmo.read_text("utf-8")
    btn_py_script = build_python_script()

    new_gizmo = []

    for line_index, line in enumerate(base_gizmo.split("\n")):
        if "%ICD_SCRIPT%" in line:
            line = line.replace("%ICD_SCRIPT%", btn_py_script)
            LOGGER.debug(f"replaced ICD_SCRIPT")

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
