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


def set_key_values(anim_curve=None, data=None):
    for (ind, val) in enumerate(data):
        anim_curve.setValue(ind, val)


def get_key_values(anim_curve=None):
    return [anim_curve.getValue(ind) for ind in range(anim_curve.numKeys() - 1)]


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


def show():
    global _Butter
    if _Butter is None:
        log.info("Initializing Butter")
        _Butter = ButterWindow(parent=get_maya_window())
        # Register connections
    _Butter.show()


if __name__ == '__main__':
    pass
