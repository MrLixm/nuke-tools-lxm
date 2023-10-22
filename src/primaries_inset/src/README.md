# src

code here need to be "compiled" to be usable. This is achieved by executing
the `build.py` file.

# build instructions

## requires

- python-3
- `gamut_convert` module to be accesible in the `PYTHONPATH`

## usage

- run `build.py`
- check result which is `../PrimariesInset.nk` defined by `BUILD_GIZMO` variable

# developing

## gizmos

Gizmos in this directory for a hierarchy :

`CIExyPoint.nk` > `GamutPlot.nk` > `GamutInset.nk` > `PrimariesInset.nk`

This mean that in theory editing `CIExyPoint` woudl need to **manually** propagate the 
changes to all the upstream files.

