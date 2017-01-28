#!/usr/autodesk/maya/bin/mayapy
# encoding: utf-8

"""
ConMan2: A tool to create and manage constraints for rigging and animation.

WARNING: NOT COMPATIBLE WITH ORIGINAL CONMAN
ConMan uses maya.cmds
ConMan2 uses pymel and Qt
"""

import os
import pickle
import base64
import pymel.core as pmc
import maya.cmds as cmds
import maya.api.OpenMaya as om
from utils.qtshim import QtCore
from utils.mayautils import get_maya_window, UndoChunk
from ConManUI import ConManWindow

if __name__ == "__main__":
    import logging
else:
    import pymel.internal.plogging as logging
LogPath = os.path.dirname(__file__)
LogFile = os.path.join(LogPath, "conman_log.log")
LogHandler = logging.FileHandler(LogFile)
LogFormat = logging.Formatter(
    "## %(levelname)s ## %(name)s.%(funcName)s ##\n"
    "%(message)s\n"
)
logging.basicConfig(level=logging.DEBUG, filename=LogFile, filemode='w')

log = logging.getLogger(__name__)
LogHandler.setFormatter(LogFormat)
log.addHandler(LogHandler)
log.setLevel(logging.DEBUG)


# Global Data =================================================================

_CMan = None
callback_list = []


# General Constraint Funtionality =============================================

@QtCore.Slot()
def create_con(conType, Offset, mOffset, weight, skipT, skipR, skipS):
    """Pass options from UI to constraint creator and data storage."""
    selection = pmc.ls(sl=True, type="transform")

    if len(selection) > 1:
        # Get selected objects
        obj = selection[-1]
        sel_objs = selection[:-1]

        log.debug("Selection: {}".format(selection))
        log.debug("Active object: {}".format(obj))
        log.debug("Target objects: {}".format(sel_objs))

        # with UndoChunk():
        # Create constraint
        conObj = create_constraint(
            conType, obj, sel_objs,
            Offset, mOffset, weight,
            skipT, skipR, skipS
        )
        log.debug("Constraint object: {}".format(conObj))

        # Save data
        con_data = {
            "type": conType,
            "object": obj,
            "target": sel_objs,
            "con_node": conObj
        }
        _CMan.populate_list(con_data)

    else:
        log.error("Select two or more objects to create a constraint")


@QtCore.Slot()
def add_con():
    """Save existing constraint and its data."""
    con_types = (
        pmc.nodetypes.ParentConstraint,
        pmc.nodetypes.PointConstraint,
        pmc.nodetypes.OrientConstraint,
        pmc.nodetypes.ScaleConstraint
    )
    for obj in pmc.ls(sl=True):
        log.debug("Selected node: {}".format(str(obj)))
        if type(obj) in con_types:
            con_data = get_data(obj)
            _CMan.populate_list(con_data)

        else:
            log.warning(
                "Selected node not a supported constraint. "
                "Select a parent, point, orient or scale "
                "constraint to add it the tracker."
            )


@QtCore.Slot()
def remove_con(con_node):
    """Delete constraint node from the scene."""
    log.debug("Deleting constraint node...")
    try:
        pmc.delete(con_node)
        log.debug("Deleted constraint")
    except:
        log.debug("Constraint node not found")


@QtCore.Slot()
def sel_con_node(node):
    """Select constrained node in the scene."""
    log.debug("Selecting: {}".format(node))
    pmc.select(node)


def create_constraint(ctype, actObj, selObjs,
                      offset, mOffset, weight,
                      skipT=['none'], skipR=['none'], skipS=['none']
                      ):
    """Create constraint with given options."""
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


def rename_cb(arg=None):
    """Callback to force resorting of the UI list on object rename."""
    _CMan.RenameSig.emit()
    _CMan.ObjList.sortItems(order=QtCore.Qt.AscendingOrder)


# Switch Weight ===============================================================

@QtCore.Slot()
def switch_off(con_node):
    """Turn off all constraint weight."""
    con_node = con_node[0]
    with UndoChunk():
        for tgt in con_node.getTargetList():
            con_node.setWeight(0, tgt)


@QtCore.Slot()
def switch_single(con_tup):
    """Switch constraint weight to a single defined target."""
    con_node = con_tup[0]
    sel_tgt = con_tup[1]

    with UndoChunk():
        for tgt in con_node.getTargetList():
            if tgt == sel_tgt:
                con_node.setWeight(1, tgt)
            else:
                con_node.setWeight(0, tgt)


@QtCore.Slot()
def switch_all(con_node):
    """Turn on all constraint weight."""
    con_node = con_node[0]
    with UndoChunk():
        for tgt in con_node.getTargetList():
            con_node.setWeight(1, tgt)


# Constraint Data =============================================================

def get_object(con_node):
    """Get constrained object."""
    obj_list = []
    for attr in con_node.getWeightAliasList():
        for conn in attr.connections():
            conn_output = list(set(conn.outputs()))
            conn_output.remove(con_node)
            obj_list.append(conn_output[0])

    return list(set(obj_list))[0]


def get_con_type(con_node):
    """Get type of constraint."""
    if isinstance(con_node, pmc.nodetypes.ParentConstraint):
        con_type = "Parent"
    elif isinstance(con_node, pmc.nodetypes.PointConstraint):
        con_type = "Point"
    elif isinstance(con_node, pmc.nodetypes.OrientConstraint):
        con_type = "Orient"
    elif isinstance(con_node, pmc.nodetypes.ScaleConstraint):
        con_type = "Scale"

    return con_type


def get_data(con_node):
    """Return dict of relevant constraint data based on PyNode."""
    con_data = {
        "type": get_con_type(con_node),
        "object": get_object(con_node),
        "target": con_node.getTargetList(),
        "con_node": con_node
    }
    return con_data


# Pickle ======================================================================

def pickle_read(arg=None):
    """Read pickled data from scene's fileInfo attribute."""
    log.debug("Reading pickle...")

    try:
        _CMan.clear_list()
        sceneInfo = pmc.fileInfo("CMan_data", q=True)

        # Compatability check for Maya versions <2016
        if isinstance(sceneInfo, list):
            if sceneInfo != []:
                for entry in sceneInfo:
                    if entry[0] == "CMan_data":
                        sceneInfo = entry[1]
                        break
            else:
                # Fill in bogus data to satisfy b64decode and pickle
                bogus = "a"
                pickled = pickle.dumps(bogus)
                sceneInfo = base64.b64encode(pickled)
        # End compatability check

        decoded = base64.b64decode(sceneInfo)
        DagList = pickle.loads(decoded)

        for dag in DagList:
            try:
                con_obj = pmc.ls(dag)[0]
                con_data = get_data(con_obj)
                _CMan.populate_list(con_data)
            except:
                log.debug("DAG path invalid: {}".format(dag))
        log.debug("Read pickle complete")

    except KeyError:
        log.debug("No data found")


@QtCore.Slot()
def pickle_write(arg=None):
    """Write pickled data into scene's fileInfo attribute."""
    log.debug("Writing pickle...")

    _DagList = [item.con_dag for item in _CMan.iter_list()]

    pickled = pickle.dumps(_DagList)
    encoded = base64.b64encode(pickled)
    pmc.fileInfo("CMan_data", encoded)
    cmds.file(modified=True)

    log.debug("Pickle written")


def purge_data(arg=None):
    """Purge all global data. Will be reset to empty objects."""
    log.debug("Purging global data...")
    pmc.fileInfo("CMan_data", "")
    _CMan.clear_list()
    cmds.file(modified=True)
    log.debug("Purge complete")


# Connection and Callback Registration ========================================

def register_connections():
    """Register connections between local functions and UI signals."""
    log.debug("Registering signal connections...")

    _CMan.OptionsSig.connect(create_con)
    _CMan.AddSig.connect(add_con)
    _CMan.DelSig.connect(remove_con)
    _CMan.SelSig.connect(sel_con_node)
    _CMan.CloseSig.connect(pickle_write)
    # _CMan.CloseSig.connect(unregister_cb)
    _CMan.PurgeSig.connect(purge_data)
    _CMan.SwitchOffSig.connect(switch_off)
    _CMan.SwitchSingleSig.connect(switch_single)
    _CMan.SwitchAllSig.connect(switch_all)


def register_cb():
    """Register callbacks within Maya for data management and UI updates."""
    log.debug("Registering callbacks...")

    pkl_write_cb = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeSave, pickle_write)
    pkl_read_cb = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterOpen, pickle_read)
    list_clear_cb = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeNew, _CMan.clear_list)
    obj_name_change_cb = om.MEventMessage.addEventCallback(
        "NameChanged", rename_cb)

    global callback_list
    callback_list = [
        pkl_write_cb, pkl_read_cb,
        list_clear_cb, obj_name_change_cb
    ]


def unregister_cb():
    """Unregister callbacks for reloading ConMan."""
    log.debug("Unregistering callbacks...")
    om.MSceneMessage.removeCallbacks(callback_list)


def show():
    """Init."""
    global _CMan
    if _CMan is None:
        log.debug("Initializing...")
        _CMan = ConManWindow(parent=get_maya_window())
        register_connections()
        register_cb()
    pickle_read()
    _CMan.show()


if __name__ == "__main__":
    show()
