#!/usr/autodesk/maya/bin/mayapy
# encoding: utf-8

"""
ConMan2: A tool to create, track and manage constraints.

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
from sys import exit
from utils.qtshim import QtCore
from utils.mayautils import UndoChunk, get_maya_window
from ConManUI import ConManWindow

ConManDir = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s: %(message)s",
    filename=os.path.join(ConManDir, "conman_log.log"), filemode='w'
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

supportedVersion = 2016
currentVersion = int(cmds.about(version=True).split(" ")[0])
if currentVersion < supportedVersion:
    log.error("Maya 2016+ required.")
    exit()
log.info("Maya 2016+ detected")

# =============================================================================

_CMan = None
ConItemList = {}


@QtCore.Slot()
def create_con_call(conType, Offset, mOffset, weight, skipT, skipR, skipS):
    """
    Called by create buttons.
    Gather required data:
        Active obj + UUID
        Selected objs + UUID list
        Constraint type
        Option values (axes, weight, offset)
    Create constraint
    Save data
    """
    # Get scene data
    selection = pmc.ls(sl=True, type="transform")
    actObj = selection[-1]
    actObjU = get_uuid_list(selection[-1:])[0]
    selObjs = selection[:-1]
    selObjsU = get_uuid_list(selObjs)
    # conType is passed into the function

    log.debug(selection)
    log.debug(str(actObj))
    log.debug(str(actObjU))
    log.debug(selObjs)
    log.debug(selObjsU)
    log.debug(conType)

    # Get UI data
    log.debug(Offset)
    log.debug(mOffset)
    log.debug(weight)
    log.debug(skipT)
    log.debug(skipR)
    log.debug(skipS)

    # Create constraint
    create_constraint(conType, actObj, selObjs, Offset, mOffset, weight, skipT, skipR, skipS)

    # Save data
    _CMan.ObjList.addItem(str(actObj) + " | " + conType)


def get_uuid_list(selObjs):
    selObjsU = [cmds.ls(str(obj), uuid=True)[0] for obj in selObjs]
    return selObjsU


def create_constraint(
    ctype, actObj, selObjs,
    offset, maintain_offset, weight,
    skipT=['none'], skipR=['none'], skipS=['none']
):
    # FIXME: UndoChunk exits with error
    # with UndoChunk:
    if ctype == "Parent":
        pmc.parentConstraint(
            selObjs, actObj,
            mo=maintain_offset,
            weight=weight
        )
    elif ctype == "Point":
        pmc.pointConstraint(
            selObjs, actObj,
            mo=maintain_offset, offset=offset,
            weight=weight
        )
    elif ctype == "Orient":
        pmc.orientConstraint(
            selObjs, actObj,
            mo=maintain_offset, offset=offset,
            weight=weight
        )
    elif ctype == "Scale":
        pmc.scaleConstraint(
            selObjs, actObj,
            mo=maintain_offset, offset=offset,
            weight=weight
        )


#===============================================================================
# class ConListItem():
#     """Object to hold constraint data: type, active object, target objects."""
#
#     def __init__(self, con_type, conNode, actObj, selobjs):
#         self.type = con_type
#         self.obj = actObj
#         self.target = selobjs
#         self.constraint = conNode
#         # self.target_uuid = [cmds.ls(str(obj), uuid=True)[0] for obj in self.target]
#         # self.con_uuid = cmds.ls(str(self.constraint), uuid=True)[0]
#
#     def uuid(self):
#         return cmds.ls(str(self.obj), uuid=True)
#===============================================================================


def pickle_read():
    """Read pickled data from scene's fileInfo attribute."""
    global ConItemList
    sceneInfo = pmc.fileInfo("CMan_data", q=True)
    decoded = base64.b64decode(sceneInfo)
    unpickled = pickle.loads(decoded)
    ConItemList = unpickled

    log.debug(str(sceneInfo))
    log.debug(str(decoded))
    log.debug([key for key in ConItemList.keys()])


def pickle_write():
    """Write pickled data into scene's fileInfo attribute."""
    pickled = pickle.dumps(ConItemList)
    encoded = base64.b64encode(pickled)
    sceneInfo = pmc.fileInfo("CMan_data", encoded)


def show():
    global _CMan
    if _CMan is None:
        maya_window = get_maya_window()
        _CMan = ConManWindow(parent=maya_window)
        _CMan.OptionsSig.connect(create_con_call)
        _CMan.setupUi()
    _CMan.show()


def _pytest():
    show()
    #===========================================================================
    # loc1 = pmc.spaceLocator()  # Target
    # loc2 = pmc.spaceLocator()  # Target
    # loc3 = pmc.spaceLocator()  # To be constrained
    # pmc.select(loc1, loc2, loc3)
    # create_con_call("Parent")
    # pConst = pmc.parentConstraint(loc1, loc2, loc3)  # [Targets,] active, options...
    #===========================================================================

    #===========================================================================
    # show()
    # global ConItemList
    # ConItemList[(str(loc), "Parent")] = ConListItem("Parent", pConst, loc, pConst.getTargetList())
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
