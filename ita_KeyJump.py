"""
Jump between keys displayed in the graph editor.

This allows jumping between keys on pinned curves or a group of curves on a selected object.

import ita_KeyJump
ita_KeyJump.next()
ita_KeyJump.prev()

(c) Jeffrey "italic" Hoover
italic DOT rendezvous AT gmail DOT com

Licensed under the Apache 2.0 license.
This script can be used for non-commercial
and commercial projects free of charge.
For more information, visit:
https://www.apache.org/licenses/LICENSE-2.0
"""


import pymel.core as pmc
import pymel.internal.plogging as logging

logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


def get_curves(direction=None):
    curves = pmc.animCurveEditor("graphEditor1GraphEd", q=True, curvesShown=True)
    log.debug(curves)
    if not curves:
        return []
    displayed_curves = [
        ("_".join(x.split("_")[:-1]), x.split("_")[-1])
        for x in curves
    ]
    log.debug(displayed_curves)
    keys = list(set(pmc.findKeyframe(x[0], attribute=x[1], which=direction) for x in displayed_curves))
    keys.sort()
    log.debug(keys)
    return keys


def next():
    keys = get_curves(direction="next")
    if keys:
        pmc.currentTime(keys[0])


def prev():
    keys = get_curves(direction="previous")
    if keys:
        pmc.currentTime(keys[-1])
