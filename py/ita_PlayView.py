"""
# Window ID strings only
cmds.lsUI(windows)
Primary window: "MayaWindow"

# Get top-left corner coordinates and width/height of window
cmds.window(windowname, q, topLeftCorner, widthHeight)

# Visible panels only
cmds.getPanel(vis=True)

# Full path of panel + control + window
p = cmds.panel(panelname, q, control)
# Only parent controls + window
ctrl = "|".join(p.split("|")[:-1])

# Layout preset to determine button layout
cmds.paneLayout(controlname, q, configuration, activePane, activePaneIndex, parent)
    "single",
    "horizontal2", "vertical2",
    "horizontal3", "vertical3",
    "top3", "left3", "bottom3", "right3",
    "horizontal4", "vertical4", "top4", "left4", "bottom4", "right4",
    "quad"

# Similar to paneLayout
cmds.layout(layoutname, q, configuration)

# Explicitly set focus to a particular panel - do not use window or layout names
cmds.setFocus('modelPanel1')

place a window + button at center of each window, without frame?
for w in windows:
    get layout config,
    make single window,
    button grid layout to match,
    any button closes all windows
"""

import maya.cmds as cmds
import maya.mel as mel
from functools import partial

windowID = 'PlayView'
helpID = 'PlayViewHelp'
custom_viewport = ""  # Saves modelPanel name for future playback


def draw_window_main(pWindowTitle):
    """Draw the main window."""
    destroy_window()

    cmds.window(
        windowID,
        title=pWindowTitle,
        sizeable=False,
        resizeToFitChildren=True
    )
    rowcol = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnWidth=[(1, 245)],
        columnOffset=[(1, 'both', 5)]
    )
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

    cmds.separator(parent=rowcol, h=5, style='none')

    # lconfig = get_layout_config(control)
    # button_grid(lconfig)

    cmds.showWindow()


def get_layout_config(control):
    """Get layout's configuration."""
    return cmds.paneLayout(control, q=True, configuration=True)


def play_view(default=False, view):
    """Play with specific viewport."""


def button_grid(layout_config=None, default=False, *args):
    """Make a UI grid layout based on result from get_layout_config()."""

    if layout_config == "single":
        # 3*3, center button
        RC = cmds.columnLayout()
        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "quad":
        # 4*4
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "horizontal2":
        # 3*4, center 2 buttons
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "vertical2":
        # 4*3, center 2 buttons
        RC = cmds.rowColumnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "horizontal3":
        # 3*5, center 3 buttons
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)

        return RC
    elif layout_config == "vertical3":
        # 5*3, center 3 buttons
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "top3":
        # 4*4, top 2, buttom 1
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=args[2])
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "left3":
        # 4*4
        RC = cmds.columnLayout()
        row1 = cmds.rowLayout(nc=4)

        col1 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col1, style='none')

        col2 = cmds.columnLayout(p=row1)
        cmds.separator(p=col2, h=5, style='none')
        cmds.button(p=col2, label="", command=partial(play_view, default, args[0]))
        cmds.button(p=col2, label="", command=partial(play_view, default, args[2]))
        cmds.separator(p=col2, h=5, style='none')

        col3 = cmds.columnLayout(p=row1)
        cmds.separator(p=col3, h=5, style='none')
        cmds.button(p=col3, label="", command=partial(play_view, default, args[1]))
        cmds.separator(p=col3, h=5, style='none')

        col4 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col4, style='none')

        return RC
    elif layout_config == "bottom3":
        # 4*4
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
        pass
    elif layout_config == "right3":
        # 4*4
        RC = cmds.columnLayout()
        row1 = cmds.rowLayout(nc=4)

        col1 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col1, style='none')

        col2 = cmds.columnLayout(p=row1)
        cmds.separator(p=col2, h=5, style='none')
        cmds.button(p=col2, label="", command=partial(play_view, default, args[0]))
        cmds.separator(p=col2, h=5, style='none')

        col3 = cmds.columnLayout(p=row1)
        cmds.separator(p=col3, h=5, style='none')
        cmds.button(p=col3, label="", command=partial(play_view, default, args[1]))
        cmds.button(p=col3, label="", command=partial(play_view, default, args[2]))
        cmds.separator(p=col3, h=5, style='none')

        col4 = cmds.columnLayout(p=row1, cw=5)
        cmds.separator(p=col4, style='none')

        return RC
    elif layout_config == "horizontal4":
        # 3*6
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "vertical4":
        # 6*3
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=6)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "top4":
        # 5*4
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "left4":
        # 4*5
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=4)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "bottom4":
        # 5*4
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=3)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC
    elif layout_config == "right4":
        # 4*5
        RC = cmds.columnLayout()

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[1]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[0]))
        cmds.button(label="", command=partial(play_view, default, args[2]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=5)
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.separator(h=5, style='none')
        cmds.button(label="", command=partial(play_view, default, args[3]))
        cmds.separator(h=5, style='none')

        cmds.rowLayout(parent=RC, nc=1)
        cmds.separator(h=5, style='none')

        return RC


def get_window_center(window):
    """Get window's center position."""
    WH = [l // 2 for l in cmds.window(window, q=True, wh=True)]
    TLC = cmds.window(window, q=True, tlc=True)
    return [sum(x) for x in zip(WH, TLC)]


def help_call(*args):
    """Open a text window with help information."""
    helpText = (
        'PlayView: Always play a specific viewport.\n'
        'by Jeffrey "italic" Hoover'
    )

    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

    cmds.window(helpID,
                title='PlayViewHelp',
                widthHeight=[300, 200],
                sizeable=True,
                resizeToFitChildren=True)
    cmds.columnLayout(width=300)
    cmds.scrollField(wordWrap=True,
                     text=helpText,
                     editable=False,
                     width=300,
                     height=200,
                     font='smallPlainLabelFont')

    cmds.showWindow()


def destroy_window(*args):
    """If PlayView windows exist, destroy them."""
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)


def prefs_play_all(*args):
    """Check user prefs for viewport playback type."""
    if cmds.playbackOptions(q=True, v=True) == "all":
        return False
    else:
        return True


def init():
    """Funtion to call to start the script."""
