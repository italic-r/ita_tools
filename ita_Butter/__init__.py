#!/bin/python

"""
Butter: A Butterworth filter for Maya's animation curves.

This filter allows you to quickly smooth and denoise high-density animation
curves, usually from motion capture. If any curves are selected, the filter
will manipulate only selected curves. If no curves are selected, the filter
will manipulate all visible curves in the graph editor.

Quick tip: expand the window sideways for higher precision!

To load:
========
import ita_Butter
ita_Butter.show()

How to use:
==========
Enable the filter by clicking Start interactive filter.
Select your filter type from [Highpass, Bandpass, Lowpass].
Use the sliders to start filtering curves:
    Maximum filters out higher-frequency noise (smaller curve shapes).
    Minimum filters out lower-frequency noise (larger curve shapes).
Exit the filter by clicking Exit filter.
Undo or redo as necessary.

For help, see README.md or open the help through the tool interface.

----
(c) Jeffrey "italic" Hoover
italic DOT rendezvous AT gmail DOT com

Licensed under the Apache 2.0 license.
This script can be used for non-commercial
and commercial projects free of charge.
For more information, visit:
https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 2.0
__date__ = (01, "November", 2018)
__author__ = "Jeffrey 'italic' Hoover"
__license__ = "Apache 2.0"


import os
import site
from collections import OrderedDict

import pymel.core as pmc

from utils.qtshim import QtCore, logging
from utils.mayautils import get_maya_window  # UndoChunk
from ButterUI import ButterWindow

deps_path = os.path.join(os.path.dirname(__file__), 'deps')
site.addsitedir(deps_path)

import scipy_interface


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
log.setLevel(logging.WARN)


# Global Data =================================================================

_Butter = None
_CurveDict = None
_FilterOrder = 4


# Data builders ===============================================================

def __reset_settings():
    global _CurveDict
    _CurveDict = None


def __construct_settings():
    global _CurveDict
    _CurveDict = __build_key_dict()


def __set_key_values(anim_curve=None, data=None):
    # type: (pmc.nodetypes.AnimCurve, Dict[int, float]) -> None
    for (ind, val) in data.iteritems():
        anim_curve.setValue(ind, val)


def __get_key_values(anim_curve=None):
    # type: (pmc.nodetypes.AnimCurve) -> Dict[int, float]
    unordered = {
        k: anim_curve.getValue(k)
        for k in pmc.keyframe(anim_curve, q=True, sl=True, indexValue=True)
    }
    return OrderedDict(sorted(unordered.iteritems(), key=lambda x: x[0]))


def __build_key_dict():
    # type: () -> Dict[pmc.nodetypes.AnimCurve, Dict[int, float]]
    return {crv: __get_key_values(crv) for crv in __get_curves()}


def __get_curves():
    # type: () -> List[pmc.nodetypes.AnimCurve]
    available_curves = \
        pmc.keyframe(q=True, sl=True, name=True) or \
        pmc.animCurveEditor("graphEditor1GraphEd", q=True, curvesShown=True) or \
        []

    return [pmc.nodetypes.AnimCurve(crv) for crv in available_curves]


# Undo queue stacking =========================================================

@QtCore.Slot()
def __open_undo_queue():
    """Open UndoQueue stack and collect settings."""
    pmc.undoInfo(openChunk=True)
    __construct_settings()


@QtCore.Slot()
def __close_undo_queue():
    """Close UndoQueue stack."""
    pmc.undoInfo(closeChunk=True)
    __reset_settings()


# Scipy =======================================================================

@QtCore.Slot()
def scipy_send(low, high, pass_type):
    # type: (float, float, str) -> None
    """Send data to Scipy and get filter parameters and filtered data."""
    low = low * 0.00001   # Subject to fine-tuning
    high = high * 0.001  # Subject to fine-tuning
    if _CurveDict:
        b, a = scipy_interface.create_filter(low, high, _FilterOrder, pass_type=pass_type)
        for (crv, kmap) in _CurveDict.iteritems():
            keys = kmap.keys()
            vals = kmap.values()

            new_vals = scipy_interface.filter_list(b, a, vals)

            log.debug("Order:    {}".format(_FilterOrder))
            log.debug("Pass:     {}".format(pass_type))
            log.debug("Original: {}".format(vals))
            log.debug("Filtered: {}".format(new_vals))

            __set_key_values(anim_curve=crv, data=dict(zip(keys, new_vals)))


def __set_connections():
    _Butter.FilterStartSig.connect(__open_undo_queue)
    _Butter.FilterEndSig.connect(__close_undo_queue)
    _Butter.SliderMinChangedSig.connect(scipy_send)
    _Butter.SliderMaxChangedSig.connect(scipy_send)


def show():
    """Start Butter and show window."""
    global _Butter
    if _Butter is None:
        log.info("Initializing Butter")
        _Butter = ButterWindow(parent=get_maya_window())
        __set_connections()
    _Butter.show()


if __name__ == '__main__':
    show()
