# ![Nuke](./img/header.jpg)

Collections of resources I made for Foundry's Nuke software.

# Content

_this table might not be always up-to-date_

| tool                                             | description                                                                | type          | tag                                                         |
|--------------------------------------------------|----------------------------------------------------------------------------|---------------|-------------------------------------------------------------|
| [nodeToText](src/nodeToText)                     | Convert the selected nodes knobs:values to a .json.                        | script        | ![i-o](https://img.shields.io/badge/i--o-9a52dd)            |
| [metadataToCamera](src/metadataToCamera)         | A custom Nuke node to convert OpenEXR metadata to a Nuke Camera node.      | nodes         | ![i-o](https://img.shields.io/badge/i--o-9a52dd)            |
| [imageCropDivide](src/imageCropDivide)           | From given maximum dimensions, divide an input image into multiples crops. | nodes, script | ![transform](https://img.shields.io/badge/transform-4c78a6) |
| [ocio-contrast-linear](src/ocio-contrast-linear) | contrast on linear encoded imagery based on the OCIO implementation        | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [ocio-contrast-log](src/ocio-contrast-log)       | contrast on log encoded imagery based on the OCIO implementation           | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |
| [ocio-saturation](src/ocio-saturation)           | saturation with variable weights also based on OCIO implementation         | nodes         | ![grading](https://img.shields.io/badge/grading-43896b)     |

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