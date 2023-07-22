# ![Nuke](./img/header.jpg)

Collections of resources I made for Foundry's Nuke software.

# Content

_this table might not be always up-to-date_

| tool                                                                        | description                                                                | type          |
|-----------------------------------------------------------------------------|----------------------------------------------------------------------------|---------------|
| [NodeToText](src/i-o/NodeToText)                                            | Convert the selected nodes knobs:values to a .json.                        | script        |
| [metadataToCamera](src/nodes/metadataToCamera)                              | A custom Nuke node to convert OpenEXR metadata to a Nuke Camera node.      | nodes         |
| [imageCropDivide](src/transforms/imageCropDivide)                           | From given maximum dimensions, divide an input image into multiples crops. | nodes, script |
| [contrast-linear-ocio.expr](src/nodes/grading/contrast-linear-ocio.expr.nk) | contrast on linear encoded imagery based on the OCIO implementation        | nodes         |
| [contrast-log-ocio.expr](src/nodes/grading/contrast-log-ocio.expr.nk)       | contrast on log encoded imagery based on the OCIO implementation           | nodes         |
| [ocio-saturation.expr](src/nodes/grading/ocio-saturation.expr.nk)           | saturation with variable weights also based on OCIO implementation         | nodes         |

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