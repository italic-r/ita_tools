"""
ita_Butter: A Butterworth filter for Maya's animation curves.

import ita_Butter
ita_Butter.show()
"""

import pymel.core as pmc
import maya.cmds as cmds
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

if __name__ == '__main__':
    pass
