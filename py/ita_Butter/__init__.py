"""
ita_Butter: A Butterworth filter for Maya's animation curves.

import ita_Butter
ita_Butter.show()
"""

import pymel.core as pmc
import maya.api.OpenMaya as om

from utils.qtshim import QtCore, logging
from utils.mayautils import get_maya_window, UndoChunk
from ButterUI import ButterWindow
import scipy_interface


LogHandler = logging.StreamHandler()
LogFormat = logging.Formatter(
    "%(levelname)s: %(name)s.%(funcName)s -- %(message)s"
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
LogHandler.setFormatter(LogFormat)
log.addHandler(LogHandler)
log.setLevel(logging.DEBUG)


# Global Data =================================================================

_Butter = None
_CurveDict = None
_SceneFPS = 24.0
_FilterOrder = 2
_FramerateMap = {
    "game": 15,
    "film": 24,
    "pal": 25,
    "ntsc": 30,
    "show": 48,
    "palf": 50,
    "ntscf": 60,
    "2fps": 2,
    "3fps": 3,
    "4fps": 4,
    "5fps": 5,
    "2fps": 2,
    "3fps": 3,
    "4fps": 4,
    "5fps": 5,
    "6fps": 6,
    "8fps": 8,
    "10fps": 10,
    "12fps": 12,
    "16fps": 16,
    "20fps": 20,
    "40fps": 40,
    "75fps": 75,
    "80fps": 80,
    "100fps": 100,
    "120fps": 120,
    "125fps": 125,
    "150fps": 150,
    "200fps": 200,
    "240fps": 240,
    "250fps": 250,
    "300fps": 300,
    "375fps": 375,
    "400fps": 400,
    "500fps": 500,
    "600fps": 600,
    "750fps": 750,
    "1200fps": 1200,
    "1500fps": 1500,
    "2000fps": 2000,
    "3000fps": 3000,
    "6000fps": 6000

}


# Data builders ===============================================================

def construct_settings():
    global _CurveDict
    global _SceneFPS

    _CurveDict = build_key_dict()
    _SceneFPS = _FramerateMap[pmc.currentUnit(q=True, time=True)]


def set_key_values(anim_curve=None, data=None):
    for (ind, val) in enumerate(data):
        anim_curve.setValue(ind, val)


def get_key_values(anim_curve=None):
    return [anim_curve.getValue(ind) for ind in range(anim_curve.numKeys())]


def build_key_dict():
    crv_dict = dict()
    for crv in get_curves():
        crv_dict[crv] = get_key_values(crv)
    return crv_dict


def get_curves():
    if pmc.keyframe(q=True, sl=True, name=True):
        crvs = [pmc.nodetypes.AnimCurve(crv) for crv in pmc.keyframe(q=True, sl=True, name=True)]
    else:
        crvs = [pmc.nodetypes.AnimCurve(crv) for crv in pmc.animCurveEditor("graphEditor1GraphEd", q=True, curvesShown=True)]
    return crvs


# Undo queue stacking =========================================================

@QtCore.Slot()
def __open_undo_queue():
    """Open UndoQueue stack and collect settings."""
    pmc.undoInfo(openChunk=True)
    construct_settings()


@QtCore.Slot()
def __close_undo_queue():
    """Close UndoQueue stack."""
    pmc.undoInfo(closeChunk=True)


# Scipy =======================================================================

@QtCore.Slot()
def scipy_send(low, high, pass_type):
    low = low * 0.01
    high = high * 0.01
    if _CurveDict:
        for (crv, data) in _CurveDict.iteritems():
            b, a = scipy_interface.create_filter(_SceneFPS, low, high, _FilterOrder, pass_type=pass_type)
            new_curve = scipy_interface.filter_list(b, a, data)

            log.debug("{}".format(data))
            log.debug("{}".format(new_curve))

            with UndoChunk():
                set_key_values(anim_curve=crv, data=new_curve)


def set_connections():
    _Butter.SliderClickSig.connect(__open_undo_queue)
    _Butter.SliderReleaseSig.connect(__close_undo_queue)
    _Butter.SliderMinChangedSig.connect(scipy_send)
    _Butter.SliderMaxChangedSig.connect(scipy_send)


def show():
    global _Butter
    if _Butter is None:
        log.info("Initializing Butter")
        _Butter = ButterWindow(parent=get_maya_window())
        set_connections()
    _Butter.show()


if __name__ == '__main__':
    pass
