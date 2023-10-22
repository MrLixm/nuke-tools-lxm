# gamut_convert

In its current state, it is only a python module with no dependency on nuke.

The module allow to generate a 3x3 conversion matrix between 2 colorspaces gamuts :

- no dependency
- single module
- python 2 compatible
- some unit tests
- DOES NOT implement chromatic adaptation (was not needed in my use-case)

```python
import gamut_convert

# sRGB
gamut_src = gamut_convert.Gamut(
    chromaticities=((0.64, 0.33),(0.3, 0.6), (0.15, 0.06)),
    whitepoint=(0.3127, 0.329),
)
# sRGB compressed
gamut_dest =gamut_convert.Gamut(
    chromaticities=((0.502, 0.32),(0.306, 0.46), (0.21, 0.17)),
    whitepoint=(0.3127, 0.329),
)
matrix = gamut_convert.get_conversion_matrix(gamut_src, gamut_dest)
print(matrix.as_2Dlist())
```