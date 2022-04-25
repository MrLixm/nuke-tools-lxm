"""
python>3
"""
import os.path
import re
from pathlib import Path

VERSION = 7

BASE = r"""
set cut_paste_input [stack 0]
version 12.2 v5
push $cut_paste_input
Group {
 name imageCropDivide
 tile_color 0x5c3d84ff
 note_font_size 25
 note_font_color 0xffffffff
 selected true
 xpos 411
 ypos -125
 addUserKnob {20 User}
 addUserKnob {3 width_max}
 addUserKnob {3 height_max -STARTLINE}
 addUserKnob {3 width_source}
 addUserKnob {3 height_source -STARTLINE}
 addUserKnob {26 "" +STARTLINE}
 addUserKnob {22 icd_script l "Copy Setup to ClipBoard" T "$SCRIPT$" +STARTLINE}
 addUserKnob {26 info l " " T "press ctrl+v in the nodegraph after clicking the above button"}
 addUserKnob {20 Info}
 addUserKnob {26 infotext l "" +STARTLINE T "2022 - Liam Collod<br> Visit <a style=\"color:#fefefe;\" href=\"https://github.com/MrLixm/Foundry_Nuke/tree/main/src/transforms/imageCropDivide\">the GitHub repo</a> "}
 addUserKnob {26 "" +STARTLINE}
 addUserKnob {26 versiontext l "" T "version $VERSION$"}
}
 Input {
  inputs 0
  name Input1
  xpos 0
 }
 Output {
  name Output1
  xpos 0
  ypos 300
 }
end_group
"""

MODULE_BUTTON_PATH = Path("..") / "button.py"
NODENK_PATH = Path("..") / "node.nk"


def increment_version():

    this = Path(__file__)
    this_code = this.read_text(encoding="utf-8")

    version = re.search(r"VERSION\s*=\s*(\d+)", this_code)
    assert version, f"Can't find <VERSION> in <{this}> !"
    new_version = int(version.group(1)) + 1
    new_code = f"VERSION = {new_version}"
    new_code = this_code.replace(version.group(0), str(new_code))
    this.write_text(new_code, encoding="utf-8")

    print(f"[{__name__}][increment_version] Incremented {this} to {new_version}.")
    return


def run():

    increment_version()

    btnscript = MODULE_BUTTON_PATH.read_text(encoding="utf-8")

    # sanitize for nuke
    btnscript = btnscript.replace("\\", r'\\')
    btnscript = btnscript.split("\n")
    btnscript = r"\n".join(btnscript)
    btnscript = btnscript.replace("\"", r'\"')
    btnscript = btnscript.replace("{", r'\{')
    btnscript = btnscript.replace("}", r'\}')

    node_content = BASE.replace("$SCRIPT$", btnscript)
    node_content = node_content.replace("$VERSION$", str(VERSION+1))

    NODENK_PATH.write_text(node_content, encoding="utf-8")
    print(f"[{__name__}][run] node.nk file written to {NODENK_PATH}")

    print(f"[{__name__}][run] Finished.")
    return


if __name__ == '__main__':
    # print(__file__)
    run()
