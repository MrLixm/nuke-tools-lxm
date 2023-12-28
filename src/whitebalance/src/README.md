# src

code here need to be "compiled" to be usable. This is achieved by executing
the `build.py` file.

# build instructions

## build-requires

- python-3
- any nuke version (including non-commercial)

## build-usage

- take the blink script at root and import them into a nuke scene
- make sure to compile the blink script
- add a new user `python button` knob
- use the following code inside :
    ```python
    node = nuke.thisNode()
    print(repr(node["kernelSource"].getValue()))
    print()
    print(repr(node["KernelDescription"].getValue()))
    ```
- execute the button and check the result in the Script Editor
- copy the first line (kernelSource) and paste into a new file named `WhiteBalance.blink.src`
  - think to remove the first and trailling quote `'`
- do the same for the second line (KernelDescription) :
  - new `WhiteBalance.blink.desc` file
  - think to remove the first and trailling quote `'`
- run `build.py`
- check result which is `../WhiteBalance.nk` defined by `BuildPaths.build_gizmo` variable (in build.py)

You need to perform the manipulation again **everytime** the blink script 
is modified.
