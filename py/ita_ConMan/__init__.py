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

try:
    import pymel.internal.plogging as logging
except ImportError:
    import logging

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


# Add, Remove, Select Constraints =============================================

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

        with UndoChunk():
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
    with UndoChunk():
        pmc.delete(con_node)
        log.debug("Deleted constraint")


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


@QtCore.Slot()
def sel_con_node(node):
    """Select constrained node in the scene."""
    log.debug("Selecting: {}".format(node))
    pmc.select(node)


# Switch Weight ===============================================================


@QtCore.Slot()
def switch_single(con_tup):
    """Switch constraint weight to a single defined target."""
    log.debug("Switching single...")
    MVis, Key, con_node, obj, targets, sel_tgt = con_tup[0:6]

    log.debug(con_tup)

    attr_list = get_connected_attr(con_node, obj)
    weight_list = get_weight_attr(con_node)
    offset_list = get_offset_attr(con_node)
    obj_mat = obj.getMatrix(worldSpace=True)

    log.debug("Attr list: {}".format(attr_list))
    log.debug("Weight list: {}".format(weight_list))
    log.debug("Offset list: {}".format(offset_list))
    log.debug("Object matrix: {}".format(obj_mat))

    with UndoChunk():
        if not MVis and not Key:
            try:
                # Blend attr
                get_blend_attr(con_node).set(1)
            except:
                pass

            # Weight attr
            for tgt in con_node.getTargetList():
                log.debug("Target: {}".format(tgt))
                con_node.setWeight(1, tgt) if tgt == sel_tgt else con_node.setWeight(0, tgt)

        elif MVis and not Key:
            try:
                # Blend attr
                get_blend_attr(con_node).set(1)
            except:
                pass

            # Weight attr
            for tgt in con_node.getTargetList():
                log.debug("Target: {}".format(tgt))
                con_node.setWeight(1, tgt) if tgt == sel_tgt else con_node.setWeight(0, tgt)

            # Update offset
            obj.setMatrix(obj_mat, worldSpace=True)
            update_offset(con_node, targets)

        elif MVis and Key:
            # Weight attr
            for pair in zip(weight_list, con_node.getTargetList()):
                log.debug(pair)
                if pair[1] == sel_tgt:
                    con_node.setWeight(1, pair[1])
                    key_attr(pair[0], new_value=1, copy_previous=True)
                else:
                    con_node.setWeight(0, pair[1])
                    key_attr(pair[0], new_value=0, copy_previous=True)

            obj.setMatrix(obj_mat, worldSpace=True)
            # Key constrained attributes
            for attr in attr_list:
                log.debug("Attr: {}".format(attr))
                key_attr(attr)
            # Update offset
            update_offset(con_node, targets)

            # Key offsets
            for attr in offset_list:
                log.debug("Offset: {}".format(attr))
                key_attr(attr, copy_previous=True)

            # Blend attr
            blend_attr = get_blend_attr(con_node)
            blend_attr.set(1)
            key_attr(blend_attr, new_value=1, copy_previous=True)

        elif not MVis and Key:
            # Weight attr
            for pair in zip(weight_list, con_node.getTargetList()):
                log.debug(pair)
                if pair[1] == sel_tgt:
                    con_node.setWeight(1, pair[1])
                    key_attr(pair[0], new_value=1, copy_previous=True)
                else:
                    con_node.setWeight(0, pair[1])
                    key_attr(pair[0], new_value=0, copy_previous=True)

            # Key constrained attributes
            for attr in attr_list:
                log.debug("Attr: {}".format(attr))
                key_attr(attr)

            # Blend attr
            blend_attr = get_blend_attr(con_node)
            blend_attr.set(1)
            key_attr(blend_attr, new_value=1, copy_previous=True)


@QtCore.Slot()
def switch_off(con_tup):
    """Turn off all constraint weight."""
    log.debug("Switching off...")
    _do_switch_on_off(con_tup, 0)


@QtCore.Slot()
def switch_all(con_tup):
    """Turn on all constraint weight."""
    log.debug("Switching all...")
    _do_switch_on_off(con_tup, 1)


def _do_switch_on_off(con_tup, val):
    """Switch weight fully on or off."""
    MVis, Key, con_node, obj, targets = con_tup[0:5]

    log.debug(con_tup)

    attr_list = get_connected_attr(con_node, obj)
    weight_list = get_weight_attr(con_node)
    offset_list = get_offset_attr(con_node)
    obj_mat = obj.getMatrix(worldSpace=True)

    log.debug("Attr list: {}".format(attr_list))
    log.debug("Weight list: {}".format(weight_list))
    log.debug("Offset list: {}".format(offset_list))
    log.debug("Object matrix: {}".format(obj_mat))

    with UndoChunk():
        if not MVis and not Key:
            try:
                # Blend attr
                get_blend_attr(con_node).set(val)
            except:
                pass

            # Weight attr
            for tgt in con_node.getTargetList():
                con_node.setWeight(val, tgt)

        elif MVis and not Key:
            try:
                # Blend attr
                get_blend_attr(con_node).set(val)
            except:
                pass

            # Weight attr
            for tgt in con_node.getTargetList():
                con_node.setWeight(val, tgt)

            # Update offset
            obj.setMatrix(obj_mat, worldSpace=True)
            update_offset(con_node, targets)

        elif MVis and Key:
            # Weight attr
            for pair in zip(weight_list, con_node.getTargetList()):
                log.debug(pair)
                con_node.setWeight(val, pair[1])
                key_attr(pair[0], new_value=val, copy_previous=True)

            obj.setMatrix(obj_mat, worldSpace=True)
            # Key constrained attributes
            for attr in attr_list:
                key_attr(attr)
            # Update offset
            update_offset(con_node, targets)

            # Key offsets
            for attr in offset_list:
                key_attr(attr)

            # Blend attr
            blend_attr = get_blend_attr(con_node)
            blend_attr.set(val)
            key_attr(blend_attr, new_value=val, copy_previous=True)

        elif not MVis and Key:
            # Weight attr
            for pair in zip(weight_list, con_node.getTargetList()):
                log.debug(pair)
                con_node.setWeight(val, pair[1])
                key_attr(pair[0], new_value=val, copy_previous=True)

            # Key constrained attributes
            for attr in attr_list:
                key_attr(attr, copy_previous=True)

            # Blend attr
            blend_attr = get_blend_attr(con_node)
            blend_attr.set(val)
            key_attr(blend_attr, new_value=val, copy_previous=True)


def get_blend_attr(con_node):
    """Get blend attribute on the object."""
    node_connections = set(pmc.listConnections(con_node, source=False, destination=True))
    for node in node_connections:
        if isinstance(node, pmc.nodetypes.PairBlend):
            return node.weight.inputs(source=True, destination=False, plugs=True)[0]


def get_connected_attr(con_node, obj):
    """Get a list of node connections to key."""
    node_connections = set(pmc.listConnections(con_node, source=False, destination=True))
    for node in node_connections:
        if node == obj:
            attr_list = pmc.listConnections(con_node, source=False, destination=True, plugs=True)
        elif isinstance(node, pmc.nodetypes.PairBlend):
            attr_list = pmc.listConnections(node, source=False, destination=True, plugs=True)
    return attr_list


def get_weight_attr(con_node):
    """Get list of weight attributes."""
    attr_list = con_node.getWeightAliasList()
    # for node in set(pmc.listConnections(con_node, source=False, destination=True)):
    #     if isinstance(node, pmc.nodetypes.PairBlend):
    #         attr_list.extend(node.weight.inputs(source=True, destination=False, plugs=True))
    return attr_list


def get_offset_attr(con_node):
    """Get list of offset attributes for maintaining offset."""
    attr_list = []
    if isinstance(con_node, pmc.nodetypes.ParentConstraint):
        for ind, tgt in enumerate(con_node.getTargetList()):
            attr_list.append(pmc.PyNode(con_node.tg[ind].targetOffsetTranslate))
            attr_list.append(pmc.PyNode(con_node.tg[ind].targetOffsetRotate))
    else:
        attr_list.append(pmc.PyNode(con_node.offset))
    return attr_list


def key_attr(attr, new_value=None, copy_previous=None):
    """Key given attr on previous and current frame."""
    log.debug("Keying attr...")

    cur_time = pmc.currentTime(q=True)

    log.debug("Attr: {}".format(attr))
    log.debug("New value: {}".format(new_value))
    log.debug("Copy previous: {}".format(copy_previous))
    log.debug("Time: {}".format(cur_time))

    if copy_previous:
        prev_key_time = pmc.findKeyframe(attr, which="previous")
        prev_key_value = attr.get(t=prev_key_time)
        prev_key = pmc.copyKey(attr, t=prev_key_time)

        log.debug("Previous key time: {}".format(prev_key_time))
        log.debug("Previous key value: {}".format(prev_key_value))

        # If a key did not exist
        if prev_key == 0:
            pmc.setKeyframe(attr, t=(cur_time - 1))
        # If a key exists
        elif prev_key == 1:
            pmc.pasteKey(attr, t=(cur_time - 1))
    else:
        pmc.setKeyframe(attr, t=(cur_time - 1))

    if new_value:
        pmc.setKeyframe(attr, t=cur_time, v=new_value)
        attr.set(new_value)
    else:
        pmc.setKeyframe(attr, t=cur_time)


def update_offset(con_node, targets):
    """Update offset of given constraint."""
    if isinstance(con_node, pmc.nodetypes.ParentConstraint):
        pmc.parentConstraint(targets, con_node, e=True, maintainOffset=True)
    elif isinstance(con_node, pmc.nodetypes.PointConstraint):
        pmc.pointConstraint(targets, con_node, e=True, maintainOffset=True)
    elif isinstance(con_node, pmc.nodetypes.OrientConstraint):
        pmc.orientConstraint(targets, con_node, e=True, maintainOffset=True)
    elif isinstance(con_node, pmc.nodetypes.ScaleConstraint):
        pmc.scaleConstraint(targets, con_node, e=True, maintainOffset=True)


# Constraint Data =============================================================

def get_object(con_node):
    """Get constrained object."""
    obj_list = []

    node_connections = set(pmc.listConnections(con_node, source=False, destination=True))
    for node in node_connections:
        if isinstance(node, pmc.nodetypes.PairBlend):
            obj_list.extend(set(pmc.listConnections(node, source=False, destination=True)))
        else:
            obj_list.extend(set(pmc.listConnections(con_node, source=False, destination=True)))

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


def rename_cb(clientData=None):
    """Callback to force resorting of the UI list on object rename."""
    _CMan.RenameSig.emit()
    _CMan.ObjList.sortItems(order=QtCore.Qt.AscendingOrder)


def obj_add_remove_cb(mobj, clientData=None):
    """Callback to check stale data."""
    mFnHandle = om.MFnDagNode(mobj)
    _CMan.ExistSig.emit((mFnHandle, clientData))


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
    obj_rem_cb = om.MDGMessage.addNodeRemovedCallback(
        obj_add_remove_cb, "transform", clientData=False)
    obj_add_cb = om.MDGMessage.addNodeAddedCallback(
        obj_add_remove_cb, "transform", clientData=True)

    global callback_list
    callback_list = [pkl_write_cb, pkl_read_cb,
                     list_clear_cb, obj_name_change_cb,
                     obj_rem_cb, obj_add_cb]


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
