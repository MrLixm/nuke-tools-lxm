# ![Nuke](./img/header.jpg)

Collections of resources I made for Foundry's Nuke software.

# Content

_this table might not be always up-to-date_

| tool                                             | description                                                                | type          | tag                                                         |
|--------------------------------------------------|----------------------------------------------------------------------------|---------------|-------------------------------------------------------------|
| [nodeToText](src/nodeToText)                     | Convert the selected nodes knobs:values to a .json.                        | script        | ![i-o](https://img.shields.io/badge/i--o-9a52dd)            |
| [metadataToCamera](src/metadataToCamera)         | A custom Nuke node to convert OpenEXR metadata to a Nuke Camera node.      | nodes         | ![i-o](https://img.shields.io/badge/i--o-9a52dd)            |
| [localoRender](src/localorender)                 | A Nuke tool to replace the native Render dialog for Write nodes.           | tool          | ![i-o](https://img.shields.io/badge/i--o-9a52dd)            |
| [imageCropDivide](src/imageCropDivide)           | From given maximum dimensions, divide an input image into multiples crops. | nodes, script | ![transform](https://img.shields.io/badge/transform-4c78a6) |
| [primaries_inset](src/primaries_inset)           | colorspace remapping to ensure smooth hue reproduction (AgX like)          | nodes, blink  | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [ocio-contrast-linear](src/ocio-contrast-linear) | contrast on linear encoded imagery based on the OCIO implementation        | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [ocio-contrast-log](src/ocio-contrast-log)       | contrast on log encoded imagery based on the OCIO implementation           | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [ocio-saturation](src/ocio-saturation)           | saturation with variable weights also based on OCIO implementation         | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [hsv](src/hsv)                                   | color correction with HSV model                                            | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [whitebalance](src/whitebalance)                 | creative white balance with temperature/tint                               | nodes, blink  | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [exposure-bands](src/exposure-bands)             | generate successive bands of gradually increasing exposure                 | nodes         | ![generate](https://img.shields.io/badge/generate-3A3B9F)   |

# Utilisation

Instructions can be found :

- In a `README.md` in the resource's folder
- In the top commented section of the script.

If no instructions found assume :

- **for .nk**: 
  - you can just copy-paste the content of the file in your nuke script
  - or change the extension to `.gizmo` and put it in your nuke preferences as usual

    
# Licensing

Each `LICENSE.md` found in a directory override the upstream one. So unless
the directory specify a license, this repo is licensed under Apache 2.0 license.

Check [LICENSE.md](LICENSE.md).


# Contact

[monsieurlixm@gmail.com](mailto:monsieurlixm@gmail.com)


# Contributing

Feel free to open an issue if you spot anything that can be improved. 
Same goes for Pull-request, unless it's a very small easy fix please open an 
issue before to discuss about it.

## Tips

- generate the `tile_color` knob value from an hexadecimal color :
  ```python
  # light sky blue
  hex(int("5A82DF" + "00", 16))
  ```

- template for About section of each node

  ```shell
  addUserKnob {20 About}
  addUserKnob {26 toolName l name T TOOLNAME}
  addUserKnob {26 toolVersion l version T 1.0.0}
  addUserKnob {26 toolAuthor l author T "<a style=\"color: rgb(200,200,200);\" href=\"https://mrlixm.github.io/\">Liam Collod</a>"}
  addUserKnob {26 toolDescription l description T "some description..."}
  addUserKnob {26 toolUrl l url T "<a style=\"color: rgb(200,200,200);\" href=\"https://github.com/MrLixm/Foundry_Nuke\">https://github.com/MrLixm/Foundry_Nuke</a>"}
  ```