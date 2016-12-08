#!/usr/autodesk/maya/bin/mayapy
# encoding: utf-8

"""
ConMan2: A tool to create, track and manage constraints for rigging and animation.

WARNING: NOT COMPATIBLE WITH ORIGINAL CONMAN
ConMan uses maya.cmds
ConMan2 uses pymel and Qt
"""

import os
import logging
import pickle
import base64
import pymel.core as pmc
import maya.cmds as cmds
import maya.api.OpenMaya as om
from sys import exit
from utils.qtshim import QtCore
from utils.mayautils import UndoChunk, get_maya_window
from ConManUI import ConManWindow

# Set up logging
ConManDir = os.path.dirname(__name__)
LogFormat = "%(levelname)s: %(message)s"
LogFile = os.path.join(ConManDir, "conman_log.log")
logging.basicConfig(
    level=logging.DEBUG, format=LogFormat,
    filename=LogFile, filemode='w'
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Version check - only supporting 2016+
supportedVersion = 2016
currentVersion = int(cmds.about(version=True).split(" ")[0])
if currentVersion < supportedVersion:
    log.error("Maya 2016+ required.")
    exit()
log.info("Maya 2016+ detected")

# =============================================================================

_CMan = None
#===============================================================================
# ConItemList = {}
#
#
# def store_item(conUUID, conType, conObj, actObj, selObjs):
#     global ConItemList
#     ConItemList[conUUID] = ConListItem(conType, conObj, actObj, selObjs)
#===============================================================================


@QtCore.Slot()
def create_con_call(conType, Offset, mOffset, weight, skipT, skipR, skipS):
    """
    Called by create buttons.
    Gather required data:
        Active obj
        Selected objs
        Constraint type
        Option values (axes, weight, offset)
    Create constraint
    Save data
    """

    selection = pmc.ls(sl=True, type="transform")

    if len(selection) >= 2:
        # Get scene data
        actObj = selection[-1]
        selObjs = selection[:-1]

        log.debug("Selection: {}".format(selection))
        log.debug("Active object: {}".format(actObj))
        log.debug("Target objects: {}".format(selObjs))

        # with UndoChunk():
        # Create constraint
        conObj = create_constraint(
            conType, actObj, selObjs,
            Offset, mOffset, weight,
            skipT, skipR, skipS
        )
        conUUID = cmds.ls(str(conObj), uuid=True)[0]
        log.debug("Constraint object: {}".format(conObj))

        # Save data
        con_data = {
            "type": conType,
            "object": actObj,
            "target": selObjs,
            "con_node": conObj
        }
        _CMan.populate_list(con_data)

    else:
        log.error("Select two or more objects to create a constraint...")


@QtCore.Slot()
def add_con_call():
    con_types = (
        pmc.nodetypes.ParentConstraint,
        pmc.nodetypes.PointConstraint,
        pmc.nodetypes.OrientConstraint,
        pmc.nodetypes.ScaleConstraint
    )
    for obj in pmc.ls(sl=True):
        log.debug("Selected node: {}".format(str(obj)))
        if type(obj) in con_types:
            if isinstance(obj, pmc.nodetypes.ParentConstraint):
                conType = "Parent"
            elif isinstance(obj, pmc.nodetypes.PointConstraint):
                conType = "Point"
            elif isinstance(obj, pmc.nodetypes.OrientConstraint):
                conType = "Orient"
            elif isinstance(obj, pmc.nodetypes.ScaleConstraint):
                conType = "Scale"

            actObj = list(set(obj.destinations()))  # Constraint outputs should only be itself (weight attribute) and the constrained object (channel output)
            actObj.remove(obj)
            actObj = actObj[0]
            selObjs = obj.getTargetList()
            conUUID = cmds.ls(str(obj), uuid=True)[0]

            log.debug("Active obj: {}".format(str(actObj)))
            log.debug("Targets: {}".format(selObjs))
            log.debug("conUUID: {}".format(conUUID))

            con_data = {
                "type": conType,
                "object": actObj,
                "target": selObjs,
                "con_node": obj
            }
            _CMan.populate_list(con_data)

        else:
            log.info(
                "Selected node not a supported constraint. "
                "Select a parent, point, orient or scale "
                "constraint to add it the tracker."
            )


@QtCore.Slot()
def sel_con_node(node):
    log.debug("Selecting: {}".format(node))
    pmc.select(node)


def create_constraint(
    ctype, actObj, selObjs,
    offset, mOffset, weight,
    skipT=['none'], skipR=['none'], skipS=['none']
):
    if ctype == "Parent":
        cObj = pmc.parentConstraint(
            selObjs, actObj,
            mo=mOffset, skipTranslate=skipT, skipRotate=skipR,
            weight=weight
        )
    elif ctype == "Point":
        cObj = pmc.pointConstraint(
            selObjs, actObj,
            mo=mOffset, offset=offset, skip=skipT,
            weight=weight
        )
    elif ctype == "Orient":
        cObj = pmc.orientConstraint(
            selObjs, actObj,
            mo=mOffset, offset=offset, skip=skipR,
            weight=weight
        )
    elif ctype == "Scale":
        cObj = pmc.scaleConstraint(
            selObjs, actObj,
            mo=mOffset, offset=offset, skip=skipS,
            weight=weight
        )

    log.debug("Created constraint: {}".format(cObj))
    return cObj

# =============================================================================


def pickle_read():
    """Read pickled data from scene's fileInfo attribute."""
    sceneInfo = pmc.fileInfo("CMan_data", q=True)
    decoded = base64.b64decode(sceneInfo)
    unpickled = pickle.loads(decoded)
    ConItemList = unpickled

    log.debug(str(sceneInfo))
    log.debug(str(decoded))
    log.debug(ConItemList.keys())


def pickle_write():
    """Write pickled data into scene's fileInfo attribute."""
    pickled = pickle.dumps(ConItemList)
    encoded = base64.b64encode(pickled)
    sceneInfo = pmc.fileInfo("CMan_data", encoded)

# =============================================================================


def register():
    _CMan.OptionsSig.connect(create_con_call)
    _CMan.AddSig.connect(add_con_call)
    _CMan.SelSig.connect(sel_con_node)
    #===========================================================================
    # om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, pickle_write)
    # om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, pickle_read)
    #===========================================================================


def show():
    global _CMan
    if _CMan is None:
        maya_window = get_maya_window()
        _CMan = ConManWindow(parent=maya_window)
        register()
    _CMan.show()


def _pytest():
    """"""
    #===========================================================================
    # show()
    # _CMan.ObjList.clear()
    # _CMan.ObjList.addItem(str(pConst))
    # _CMan.ObjList.addItems(
    #     ["testline1", "testline2", "testline3", "testline4", "testline5",
    #      "testline6", "testline7", "testline8", "testline9", "testline10",
    #      "testline11", "testline12", "testline13", "testline14", "testline15"]
    # )
    # _CMan.MenuSwitchTarget.clear()
    # _CMan.populate_menu([str(obj) for obj in pConst.getTargetList()])
    #===========================================================================


if __name__ == "__main__":
    """Run"""
    _pytest()
