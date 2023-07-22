# metadataToCamera

A custom Nuke node to convert OpenEXR metadata to a Nuke Camera node.

![main-visual.png](main-visual.png)

Metadata format supported :

- Redshift
  - `exr/rs/camera/transform`
  - `exr/rs/camera/aperture`
  - `exr/rs/camera/nearPlane`
  - `exr/rs/camera/farPlane`
  - `exr/rs/camera/DOFFocusDistance`

- Arnold 
  - `exr/worldToCamera`
  - `exr/CameraFilmApertureHorizontal`
  - `exr/CameraFilmApertureVertical`
  - `exr/CameraFocalLength`
  - `exr/arnold/camera/near_clip`
  - `exr/arnold/camera/far_clip`

# Install

Pick the script corresponding to your render-engine :

- arnold : [tool-metadataToCamera.nk](tool-metadataToCamera.nk)
- redshift : [tool-metadataToCamera-redshift.nk](tool-metadataToCamera-redshift.nk)

_You don't need the python script you can find in this directory, it is already
included in the node's button._


# Usage

See the node as Camera node with an extra input.

- Connect that extra `image` input to your stream with metadata.
- You should see the `focal length` change value.
- You can then connect the node to a `Scene` node, a `ScanlineRender`, ...

## Arnold/Baking

The nodes work "live", means the metadata change, the camera will update.
But for the Arnold node this process is achieved via sampling rgb channels in a TCL expressions, which
sometimes doesn't always evaluate and can be a bit unstable.

If you need stability you can bake the node to a real Nuke Camera :

- Click on the `Bake To Camera` button
- Select the frame range to bake the animation of the camera (and optionaly the views)
- Validate and wait  few second for the bake
- You should find a new Camera node per view created.

# Faq

> Does it work with Nuke non-commercial ?

Yes the live approach works in non-commercial. The Bake button does not (python node limitation).

> I don't see any change on the camera, it's still at the center of the world.

As mentionned sampling in TCL expressions can be quite unstable, just move
the timeline a bit or try to edit a knob value to force an update of the camera.

If this does not solve your issue this means you might have missing metadata.

> Why does the focal length doesn't match with the original camera

As mentioned the `focal length`, `horizontal aperture`, `vertical aperture` will
not match your original camera, but they will still produce the same "viewport"
when you use the camera.

# Developer

## Update the python script

- update the code in the py file next to this README
- increment version at top
- execute the following code :

```python
from pathlib import Path

baker_script = Path("./tool-metadataToCamera-baker.py")
baker_script = baker_script.read_text()
nuke_formatted = repr(baker_script).replace('"', '\\"')
print(nuke_formatted)
```

- open the `.nk` file
- copy the line printed in the console and paste it in the `Bake To Camera` knob `T` value
- increment node version in the .nk