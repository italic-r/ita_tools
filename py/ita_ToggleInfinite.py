#!/bin/env python
# encoding: utf-8

"""
ToggleInfinite: Toggle pre- and post-infinity curve types.

Assign to a hotkey as:
import ita_ToggleInfinite
ita_ToggleInfinite.main()

License: Apache 2.0
Commercial and non-commercial use encouraged.
"""


import maya.cmds as cmds


def main():
    """
    Available types:
    constant, linear, cycle, cycleRelative, oscillate
    """
    if "cycle" in set(cmds.setInfinity(q=True, preInfinite=True)):
        print("Setting pre- and post-infinite to CONSTANT")
        cmds.setInfinity(preInfinite="constant", postInfinite="constant")
    else:
        print("Setting pre- and post-infinite to CYCLE WITHOUT OFFSET")
        cmds.setInfinity(preInfinite="cycle", postInfinite="cycle")
