#!/usr/autodesk/maya/bin/mayapy
# encoding: utf-8

"""
ConMan2: A tool to create and manage constraints for rigging and animation.

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
from utils.mayautils import get_maya_window  # , UndoChunk
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
ConItemList = {}
callback_list = []


class ConListItem():
    """Object to hold constraint data."""

    def __init__(self, con_type, conObj, actObj, selobjs):
        self._type = con_type
        self._obj = actObj
        self._target = selobjs
        self._constraint = conObj
        self._entry_label = "{} | {} | {}".format(
            str(self._obj),
            self._type,
            str(self._constraint)
        )

    @property
    def con_type(self):
        return self._type

    @property
    def obj(self):
        return self._obj

    @property
    def target(self):
        return self._target

    @property
    def con_node(self):
        return self._constraint


def store_item(conUUID, conType, conObj, actObj, selObjs):
    global ConItemList
    ConItemList[conUUID] = ConListItem(conType, conObj, actObj, selObjs)


def conlist_clear(arg=None):
    global ConItemList
    ConItemList.clear()


# =============================================================================


@QtCore.Slot()
def create_con_call(conType, Offset, mOffset, weight, skipT, skipR, skipS):
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
        store_item(conUUID, conType, conObj, actObj, selObjs)

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

            # Constraint outputs should only be itself (weight attribute)
            # and the constrained object (channel output)
            actObj = list(set(obj.destinations()))
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
            store_item(conUUID, conType, obj, actObj, selObjs)

        else:
            log.info(
                "Selected node not a supported constraint. "
                "Select a parent, point, orient or scale "
                "constraint to add it the tracker."
            )


@QtCore.Slot()
def remove_con(con_node):
    log.debug("Deleting constraint node...")
    try:
        con_node_uuid = str(cmds.ls(str(con_node), uuid=True)[0])
        pmc.delete(con_node)

        global ConItemList
        del ConItemList[con_node_uuid]

        log.debug("Deleted constraint.")

    except KeyError:
        log.debug("Could not remove constraint.")
        log.debug("Con UUID not a key in ConItemList")


@QtCore.Slot()
def sel_con_node(node):
    log.debug("Selecting: {}".format(node))
    pmc.select(node)


def create_constraint(ctype, actObj, selObjs,
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


def pickle_read(arg=None):
    """Read pickled data from scene's fileInfo attribute."""
    log.debug("Reading pickle...")
    try:
        global ConItemList
        sceneInfo = pmc.fileInfo("CMan_data", q=True)
        decoded = base64.b64decode(sceneInfo)
        unpickled = pickle.loads(decoded)
        ConItemList = unpickled

        _CMan.clear_list()

        for k, v in ConItemList.iteritems():
            try:
                cmds.ls(k)
                con_data = {
                    "type": v.con_type,
                    "object": v.obj,
                    "target": v.target,
                    "con_node": v.con_node
                }
                _CMan.populate_list(con_data)
            except MayaNodeError:
                pass

        log.debug(ConItemList.keys())

        log.debug("Reading pickle success")
    except KeyError:
        log.debug("No data found.")


@QtCore.Slot()
def pickle_write(arg=None):
    """Write pickled data into scene's fileInfo attribute."""
    log.debug("Writing pickle...")

    pickled = pickle.dumps(ConItemList)
    encoded = base64.b64encode(pickled)
    pmc.fileInfo("CMan_data", encoded)
    cmds.file(modified=True)

    log.debug("Writing pickle success")


# =============================================================================


def register_connections():
    log.debug("Registering signal connections and callbacks...")

    _CMan.OptionsSig.connect(create_con_call)
    _CMan.AddSig.connect(add_con_call)
    _CMan.DelSig.connect(remove_con)
    _CMan.SelSig.connect(sel_con_node)
    _CMan.CloseSig.connect(pickle_write)
    #===========================================================================
    # _CMan.CloseSig.connect(unregister_callbacks)
    #===========================================================================


def register_callbacks():
    pkl_write_cb = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, pickle_write)
    pkl_read_cb = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, pickle_read)
    list_clear_cb = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew, _CMan.clear_list)
    conlist_clear_cb = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew, conlist_clear)

    global callback_list
    callback_list = [
        pkl_write_cb, pkl_read_cb,
        list_clear_cb, conlist_clear_cb
    ]


def unregister_callbacks():
    log.debug("Unregistering callbacks...")
    om.MSceneMessage.removeCallbacks(callback_list)


def show():
    global _CMan
    if _CMan is None:
        maya_window = get_maya_window()
        _CMan = ConManWindow(parent=maya_window)
        register_connections()
        pickle_read()
    register_callbacks()
    _CMan.show()


if __name__ == "__main__":
    """Run"""
    show()
