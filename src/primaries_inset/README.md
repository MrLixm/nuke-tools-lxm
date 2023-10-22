# Primaries Inset

Create a reshaped version of a colorspace's gamut and apply it on images using
a 3x3 matrix. It is possible to visuallize the gamut transformation in a 
CIE xy graph plot.

The reshape transformation is called an "inset" as we are creating a smaller
gamut than the original.

This is the main concept behind [the AgX DRT](https://github.com/MrLixm/AgXc).


# Instructions

## Install

- Copy/paste the content of [PrimariesInset.nk](PrimariesInset.nk) in any nuke
scene.
- That's it

System :
- PrimariesInset use python code but works on non-commercial versions.
- The code _should_ be python 2 compatible but has only been tested on latest
python3 versions of Nuke.

## Usage

- Expect an image to be transformed as input.
- Select the preset corresponding to the input image's colorspace encoding.
- Click the apply button: the _primary X_ and _whitepoint_ knobs are updated.
- In the _Option_ section, start playing with the global inset.
- To see exactly how it affect the original colorspace you can click on `show` 
in the _Plot_ section : your image disapear to leave a dark squared canvas with
only a gamut visible.
- Keep playing with the _Options_ to see how it works.

# Developer

See the [./src/](./src) folder for the original files that create the final node.

## TODO

- [ ] add images in README
- [ ] fix NO_HANDLE flag issue that doesn't seems to work
- [ ] see if need to add primaries offset like for whitepoint