# src

code here need to be "compiled" to be usable. This is achieved by executing
the `build.py` file.

# build instructions

## build-requires

- python-3
- any nuke version (including non-commercial)

## build-usage

- take the 2 blink script at root and import them into a nuke scene
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
- copy the first line (kernelSource) and paste into a new file named :
  - `PrimariesInset.blink.src` if it was the Inset blink script
  - `PrimariesPlot.blink.src` if it was the Plot blink script
- do the same for the second line (KernelDescription) :
  - `PrimariesInset.blink.desc` if it was the Inset blink script
  - `PrimariesPlot.blink.desc` if it was the Plot blink script
- make sure you did it for the 2 blink scripts in the end
- run `build.py`
- check result which is `../PrimariesInset.nk` defined by `BuildPaths.build_gizmo` variable (in build.py)

You need to perform the manipulation again **everytime** one of the 2 blink script 
is modified.

# developing

## blink

- The 2 blink script share some common code, remember to modify both when a change
is made to that common code.
- remeber to upgrade the version of the top comment

## gizmo

The src gizmo can be found in [PrimariesInset](PrimariesInset) folder.

It contains the blink script with their code being dynamically replaced during build.
