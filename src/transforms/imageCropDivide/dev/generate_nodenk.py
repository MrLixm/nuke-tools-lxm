"""
python>3
"""
import os.path

BASE = """
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

MODULE_BUTTON_PATH = os.path.abspath(os.path.join("..", "button.py"))
NODENK_PATH = os.path.abspath(os.path.join("..", "node.nk"))


def run():

    with open(MODULE_BUTTON_PATH, "r") as f:
        script = f.read()

    # sanitize for nuke
    script = script.replace("\\", r'\\')
    script = script.split("\n")
    script = r"\n".join(script)
    script = script.replace("\"", r'\"')
    script = script.replace("{", r'\{')
    script = script.replace("}", r'\}')

    node_content = BASE.replace("$SCRIPT$", script)

    with open(NODENK_PATH, "w") as f:
        f.write(node_content)
    print(f"[{__name__}][run] node.nk file written to {NODENK_PATH}")

    print(f"[{__name__}][run] Finished.")
    return


if __name__ == '__main__':
    run()
