# encoding: utf-8

import logging
from sys import exit
import pymel.core as pmc
from pymel import versions
from maya import OpenMaya as om
import maya.cmds as cmds
from utils.mayautils import UndoChunk, get_maya_window
from ConManUI import Ui_ConManWindow

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s",
    filename="conman_log.log", filemode='w'
)
log = logging.getLogger(__name__)

supportedVersion = 2016
currentVersion = int(cmds.about(version=True).split(" ")[0])
if currentVersion < supportedVersion:
    log.error("Maya 2016+ required.")
    exit()
log.info("Maya 2016+ detected")

# =============================================================================

_CMan = None


def create_constraint(ctype, actObj, selObjs, maintain_offset, offset):
    with UndoChunk:
        if ctype == "Parent":
            pmc.parentConstraint(actObj, selObjs)
        elif ctype == "Point":
            pmc.pointConstraint(actObj, selObjs)
        elif ctype == "Orient":
            pmc.orientConstraint(actObj, selObjs)
        elif ctype == "Scale":
            pmc.scaleConstraint(actObj, selObjs)


class ConListItem():
    """Object to hold constraint data: type, active object, target objects."""

    def __init__(self, con_type, actObj, selobjs):
        self.type = con_type
        self.obj = actObj
        self.target = selobjs


def show():
    global _CMan
    if _CMan is None:
        maya_window = get_maya_window()
        _CMan = Ui_ConManWindow(maya_window)
        _CMan.setupUi()
    _CMan.show()


def _pytest():
    ctype = "Parent"
    ctargets = ["nurbsCurve1", "locator1"]
    cactive = "PaConst1"
    clist1 = ConListItem(ctype, cactive, ctargets)
    print(
        clist1.type,
        clist1.obj,
        clist1.target,
    )

if __name__ == "__main__":
    _pytest()
