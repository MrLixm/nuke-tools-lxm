"""
VERSION=0.0.5

Author: Liam Collod
Last modified: 20/01/2022

Script for Foundry's Nuke software. (Python 2+)
Convert the selected nodes knobs:values to a .json.
The nodes must have first been configured for export using the <config_dict>.

[HowTo]

1. Make sure the node you are going to export is registered in the <config_dict>.
    If not looks at <config_dict> docstring to know how.

2. Select the nodes you want to export.

3. Execute script.

4. A file dialog will appear, give a full path to the desire dlocation of the .json file.

"""

import json
import logging
from pprint import (pformat)
import sys

import nuke


def setup_logging(level):

    logger = logging.getLogger("KnobToText")
    logger.setLevel(level)

    if not logger.handlers:
        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)7s] %(name)38s // %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)

    return logger


logger = setup_logging(logging.DEBUG)

"""config_dict (dict)
Allow to configure what kind of node the script will be able to export.

level0
    [key](str):
     identifier for node type
    
    [key:value](dict):
     data for processing
     
     Each key is just used as an identifier internally. Should correspond to 
     the type of your node. ex: Grade, Roto, myCustomNode, ...
     
     See the under to see how the value dict is built.

level1
    [key:value.key=check:value](function) : 
      function used to determine if a node correspond to current [key].
    
      Args:
          node(nuke.Node): Nuke node
      Returns:
          bool:
          Where True means the node correspond to current [key].
    [key:value.key=data:value](dict) : 
      data that will be extracted from the node (see under)
    
    There is only 2 key possible at this level : check or data.

level2
    Determine waht is exported from the node, and how it is stored in the .json
    If they key is without a $, it is assumed to be a knob's path and will
    be stored as such : {value:node.getKnob(key).value()}
    
    [key:value.key=data:value.key](str) : 
      path of the knob on the node
    [key:value.key=data:value.key:value](str) : 
      key name of the knob's value in the output dict.
    
    [key:value.key=data:value.key=$(any):value](function) :
      if the key start with a $, the exported result will be {$key:value(node)}
      the value must be a function as such :
      Args:
          node(nuke.Node): Nuke node
      Returns:
          any: the returned with be used as 
    
    [key:value.key=data:value.key=$id:value](function) : 
      special key that is mandatory.
      This dict value, once evaluated, must allow to identify the source node.
      The returned value by the function must be a string.
  
"""
config_dict = {
    
    "Camera": {
        "check": lambda node: True if "Camera" in node.Class() else False,
        "data": {
            "$id": lambda node: node.name(),
            # we use the token feature to get a special formatting of the knobs
            "$tr_order": lambda node: (
                "{}_{}".format(
                    node.knob("xform_order").value(),
                    node.knob("rot_order").value()
                )
            ),
            "translate": "translation",
            "rotate": "rotation",
            "focal": "focal"
        }
    },
    
    # this is an example with a custom group
    "lightManager": {
        "check": lambda node: True if node.knob("intensity") and node.knob(
            "temperature_value") and node.knob("copyright") else False,
        "data": {
            "$id": lambda node: "{}_{}".format(node.name(),
                                               node.knob("in").value()),
            "intensity": "intensity",
            "exposure": "exposure",
            "color": "color",
            "temperature_value": "temperature"
        }
    }
}

"""____________________________________________________________________________

    API

"""


def find_known_node(node):
    """
    Iterate through the config_dict to find to which key the given <node>
    might corresponds too.

    Returns:
        (str or None):
            config_dict key if match found else None
    """

    for known_node, node_data in config_dict.items():
        if node_data["check"](node):
            return known_node

    return None


def node_to_dict(node):
    """
    Returns:
        dict of str:
            dictionary representing the node. Contains at least the key <$id>.
    """

    # grab the corresponding config_dict data
    node_config = config_dict.get(find_known_node(node))
    if not node_config:
        raise TypeError(
            "[node_to_dict] The given node <{}> is not supported."
            "".format(node.name())
        )
    node_config = node_config["data"]

    # safety check that the required $id key has not been forgot
    if not node_config.get("$id"):
        raise ValueError(
            "[node_to_dict] <data> key from <config_dict> for node <{}> is missing the <$id> key"
            "".format(node.name())
        )

    output = dict()

    for sknob, ktarget in node_config.items():

        # process special key first
        if sknob.startswith("$"):
            output[sknob] = str(ktarget(node))
            continue

        current_knob = node.knob(sknob)
        if not current_knob:
            raise FileNotFoundError(
                "[node_to_dict] Knob <{}> on node <{}> doesn't seems to exists."
                "".format(sknob, node.name())
            )
        output[ktarget] = node.knob(sknob).value()

        continue

    return output


def get_export_path():
    """
    Returns:
        str:
            file path target of the .json. (dir+name+extension)
    """

    user_path = nuke.getFilename(
        message="Enter the export path (with .json extension)")
    if not user_path:
        raise ValueError(
            "[get_export_path] User aborted the export operation."
        )

    if not user_path.endswith(".json"):
        raise SyntaxError(
            "[get_export_path] Missing <.json> in export path <{}> given by user."
            "".format(user_path)
        )

    logger.debug(
        "[get_export_path] File will be exported to <{}>".format(user_path)
    )

    return user_path


def run():

    output = dict()

    user_sel = nuke.selectedNodes()
    for index, node in enumerate(user_sel):
        output[index] = node_to_dict(node)

    logger.debug(
        "Dict exported :\n{}".format(pformat(output, width=1, indent=4))
    )

    export_path = get_export_path()

    with open(export_path, "w") as jsonfile:
        json.dump(output, jsonfile, indent=4)

    logger.info(
        "[run] Finished.\n {} nodes exported to <{}>"
        "".format(len(user_sel), export_path)
    )
    return


# execute

run()
