"""
PlayView: Save a viewport for single-view playback mode.

import ita_PlayView
#reload(ita_PlayView)  # To reset default
ita_PlayView.init()

(c) Jeffrey "italic" Hoover
italic DOT rendezvous AT gmail DOT com
30 October 2016

Licensed under the Apache 2.0 license.
This script can be used for non-commercial
and commercial projects free of charge.
For more information, visit:
https://www.apache.org/licenses/LICENSE-2.0
"""

import logging
import sys
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

sys.stdout = sys.__stdout__
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

windowID = 'PlayView'
helpID = 'PlayViewHelp'
custom_viewport = ""  # Saves panel name for future playback


def play_button(*args):
    """Play functionality."""
    return mel.eval(
        "undoInfo -stateWithoutFlush off;"
        "playButtonForward;"
        "undoInfo -stateWithoutFlush on;"
    )


def play_view(view):
    """Play with specified viewport."""
    cmds.setFocus(view)
    destroy_window()
    play_button()


def play_view_caller(make_default, view, *args):
    """
    Caller to make use of Default checkbox.
    Ultimately call play_view() to play with specific view.
    """
    if cmds.checkBox(make_default, q=True, v=True) is True:
        global custom_viewport
        custom_viewport = view
        log.info("Default viewport for playback is now {}.".format(custom_viewport))
    play_view(view)


def gui(ctrl, pWindowTitle, winID, TLC, *args):
    """Draw window."""
    win_draw = cmds.window(
        winID,
        title=pWindowTitle,
        titleBar=False,
        sizeable=False,
        resizeToFitChildren=True,
        tlc=TLC,
        wh=(250, 150)
    )
    rowcol = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnWidth=[(1, 245)],
        columnOffset=[(1, 'both', 5)]
    )
    cmds.separator(h=5, style='none')
    cmds.text(label='Select a viewport to play from.')
    cmds.separator(h=5, style='none')
    cmds.rowLayout(
        parent=rowcol,
        numberOfColumns=3,
        columnAttach=[
            (1, 'both', 0),
            (2, 'both', 5),
            (3, 'both', 0)
        ],
        columnWidth=[
            (1, 75),  # Total == 250 - margins
            (2, 90),
            (3, 75)
        ]
    )
    cmds.button(label='Help', command=help_call)
    makeDefault = cmds.checkBox(label='Make Default')
    cmds.button(label='Cancel', command=destroy_window)

    cmds.separator(parent=rowcol, h=1, style='none')

    lconfig = get_layout_config(ctrl)
    lconfigarray = get_layout_child_array(ctrl)

    log.debug("Layout config: {}".format(lconfig))
    log.debug("Children: {}".format(lconfigarray))

    button_grid(rowcol, lconfigarray, makeDefault, lconfig)

    cmds.showWindow()

    cmds.window(win_draw, e=True, tlc=TLC)


def button_grid(parent, child_array, make_default, layout_config=None, *args):
    """UI grid based on layout from get_layout_config()."""

    RC = cmds.columnLayout(p=parent)
    cmds.rowLayout(parent=RC, nc=1)
    cmds.separator(h=5, style='none')

    if layout_config == "single":
        # 3*3, center button
        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

    elif layout_config == "quad":
        # 4*4
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

    elif layout_config == "horizontal2":
        # 3*4, center 2 buttons
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

    elif layout_config == "vertical2":
        # 4*3, center 2 buttons
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

    elif layout_config == "horizontal3":
        # 3*5, center 3 buttons
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

    elif layout_config == "vertical3":
        # 5*3, center 3 buttons
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

    elif layout_config == "top3":
        # 4*4, top 2, buttom 1
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=child_array[2])
        cmds.separator(h=5, style='none')

    elif layout_config == "left3":
        # 4*4
        row1 = cmds.rowLayout(p=RC, nc=4)

        col1 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col1, style='none')

        col2 = cmds.columnLayout(p=row1)
        cmds.separator(p=col2, h=5, style='none')
        cmds.button(p=col2, label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(p=col2, label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(p=col2, h=5, style='none')

        col3 = cmds.columnLayout(p=row1)
        cmds.separator(p=col3, h=5, style='none')
        cmds.button(p=col3, label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(p=col3, h=5, style='none')

        col4 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col4, style='none')

    elif layout_config == "bottom3":
        # 4*4
        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

    elif layout_config == "right3":
        # 4*4
        row1 = cmds.rowLayout(p=RC, nc=4)

        col1 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col1, style='none')

        col2 = cmds.columnLayout(p=row1)
        cmds.separator(p=col2, h=5, style='none')
        cmds.button(p=col2, label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(p=col2, h=5, style='none')

        col3 = cmds.columnLayout(p=row1)
        cmds.separator(p=col3, h=5, style='none')
        cmds.button(p=col3, label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.button(p=col3, label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(p=col3, h=5, style='none')

        col4 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col4, style='none')

    elif layout_config == "horizontal4":
        # 3*6
        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.separator(h=5, style='none')

    elif layout_config == "vertical4":
        # 6*3
        cmds.rowLayout(parent=RC, nc=6)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.separator(h=5, style='none')

    elif layout_config == "top4":
        # 5*4
        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.separator(h=5, style='none')

    elif layout_config == "left4":
        # 4*5
        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')

    elif layout_config == "bottom4":
        # 5*4
        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

    elif layout_config == "right4":
        # 4*5
        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[0]))
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view_caller, make_default, child_array[3]))
        cmds.separator(h=5, style='none')

    cmds.rowLayout(parent=RC, nc=1)
    cmds.separator(h=5, style='none')

    return RC


def help_call(*args):
    """Open a text window with help information."""
    helpText = (
        'PlayView: Always play a specific viewport.\n'
        'by Jeffrey "italic" Hoover'
    )

    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

    cmds.window(
        helpID,
        title='PlayViewHelp',
        widthHeight=[300, 200],
        sizeable=True,
        resizeToFitChildren=True
    )
    cmds.columnLayout(width=300)
    cmds.scrollField(
        wordWrap=True,
        text=helpText,
        editable=False,
        width=300,
        height=200,
        font='smallPlainLabelFont'
    )

    cmds.showWindow()


def draw_PlayView(pWindowTitle, *args):
    wInd = 0
    WH = [-125, -75]  # Window dimensions are 250*150, negated for addition
    # XXX
    # save window + config in dict
    # loop dict and create window for each key (window + config/ctrl/layout)
    for panel in cmds.getPanel(vis=True):
        for w in get_windows():
            if cmds.panel(panel, q=True, control=True).startswith(w):
                WC = get_window_center(w)
                WH.reverse()
                TLC = [sum(x) for x in zip(WC, WH)]

                ctrl = cmds.panel(panel, q=True, control=True)
                gui(ctrl, pWindowTitle, "{}{}".format(windowID, wInd), TLC)
                wInd += 1

                log.debug("Window: {}{}".format(windowID, wInd))
                log.debug("Control: {}".format(ctrl))
                log.debug("Panel: {}".format(panel))


def get_windows(*args):
    """Get all available windows."""
    return cmds.lsUI(windows=True)


def get_window_center(window, *args):
    """Get window's center position."""
    WH = [l // 2 for l in cmds.window(window, q=True, wh=True)]
    WH.reverse()
    TLC = cmds.window(window, q=True, tlc=True)
    return [sum(x) for x in zip(TLC, WH)]


def get_layout(window, *args):
    """Get layout of given window. By bob.w"""
    for widget in sorted(cmds.lsUI(long=True, controlLayouts=True)):
        if widget.startswith(window):
            yield widget


def get_layout_control(ctrl, *args):
    """Get layout's control."""
    return "|".join(ctrl.split("|")[:-1])


def get_layout_config(ctrl, *args):
    """Get layout's configuration."""
    control = get_layout_control(ctrl)
    ctrllayout = cmds.paneLayout(control, q=True, configuration=True)
    return ctrllayout


def get_layout_child_array(ctrl, *args):
    """Get layout's child array."""
    control = get_layout_control(ctrl)
    return cmds.paneLayout(control, q=True, childArray=True)


def destroy_window(*args):
    """If PlayView windows exist, destroy them."""
    for w in get_windows():
        if w.startswith(windowID):
            cmds.deleteUI(w)
    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)


def prefs_play_all(*args):
    """Check user prefs for viewport playback type."""
    return cmds.playbackOptions(q=True, v=True) == "active"


def init(*args):
    """Funtion to call to start the script."""
    destroy_window()
    if not prefs_play_all():
        play_button()
    else:
        if cmds.play(q=True, state=True) is True:
            play_button()
        else:
            if custom_viewport == "":
                draw_PlayView('PlayView')
            else:
                play_view(custom_viewport)
