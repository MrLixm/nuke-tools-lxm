# VERSION = 5
# python2-3 compatible

import logging

import nuke

LOGGER = logging.getLogger(__name__)


def askUserFramerangeAndViews():
    """
    Open a dialog for the user to specify a frame range and views to use.

    Returns:
        (tuple[nuke.FrameRange, list[str]]): a FrameRange and a list of views
    """
    currentFrameStart = nuke.root().firstFrame()
    currentFrameEnd = nuke.root().lastFrame()
    result = nuke.getFramesAndViews(
        "Specify Frame Range for Baking",
        "{}-{}".format(currentFrameStart, currentFrameEnd),
    )
    views = result[1]  # type: list[str]
    frameRange = nuke.FrameRange(result[0])
    return frameRange, views


def getCameraMatrixFromMetadata(node, frame, view):
    """

    Args:
        node(nuke.Node): node to retrieve metadata from
        frame(int): frame number to retrieve metadata at
        view(str): name of the view to retrieve metadata from

    Returns:
        (nuke.math.Matrix4): nuke Matrix4 instance
    """
    metadata = node.metadata(
        key="exr/worldToCamera",
        time=frame,
        view=view,
    )  # type: list[float]

    matrix = nuke.math.Matrix4()

    if metadata and len(metadata) == 16:
        for index, i in enumerate(metadata):
            matrix[index] = i

        matrix.transpose()
        # invert z axis
        matrix.scale(1, 1, -1)
        matrix = matrix.inverse()

    else:
        matrix.makeIdentity()

    return matrix


def bakeCamera(metadataToCameraNode, frameRange, view="left"):
    """

    Args:
        metadataToCameraNode(nuke.Group): custom gizmo to bake the internal camera
        frameRange(nuke.FrameRange): nuke FrameRange
        view(str): name of the view to create the new baked camera for

    Returns:
        (nuke.Node): the new camera node
    """
    LOGGER.info(
        "Starting bake for {} with frame range={} with view={}".format(
            metadataToCameraNode.fullName(), frameRange, view
        )
    )

    metadataSource = metadataToCameraNode.input(2)  # type: nuke.Node

    currentCamera = [
        node for node in metadataToCameraNode.nodes() if "Camera" in node.Class()
    ]
    if not currentCamera:
        raise RuntimeError(
            "Missing camera in node {} !?".format(metadataToCameraNode.fullName())
        )
    currentCamera = currentCamera[0]

    with metadataToCameraNode.parent():
        newCamera = nuke.nodes.Camera2(
            name="CameraFromMetadata_{}".format(view)
        )  # type: nuke.Node

    newCamera["useMatrix"].setValue(True)
    for matrixIndex in range(16):
        newCamera["matrix"].setAnimated(matrixIndex)

    knobToCopy = [
        "focal",
        "haperture",
        "vaperture",
        "near",
        "far",
        "fstop",
        "focal_point",
    ]

    for frame in frameRange:
        for knobName in knobToCopy:
            sourceKnob = currentCamera.knob(knobName)
            if sourceKnob.isAnimated():
                newCamera[knobName].setAnimated()
                newCamera[knobName].setValueAt(sourceKnob.value(), frame)
            else:
                newCamera[knobName].setValue(sourceKnob.value())

        cameraMatrix = getCameraMatrixFromMetadata(
            node=metadataSource,
            frame=frame,
            view=view,
        )

        for matrixIndex in range(16):
            newCamera.knob("matrix").setValueAt(
                cameraMatrix[matrixIndex],
                frame,
                matrixIndex,
            )

    return newCamera


def main():
    import sys

    # in case the root logger has not been configured, else does nothing.
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-7s | %(asctime)s [%(name)s]%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    node = nuke.thisNode()
    frameRange, views = askUserFramerangeAndViews()
    for view in views:
        newCamera = bakeCamera(node, frameRange=frameRange, view=view)
        LOGGER.info("Finished bake newCamera={}".format(newCamera.fullName()))


main()
