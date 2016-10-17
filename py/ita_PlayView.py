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

windowID = 'PlayView'
helpID = 'PlayViewHelp'
custom_viewport = ""  # Saves modelPanel name for future playback


def get_layout_config(window):
    pass


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

    cmds.showWindow()


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
    if cmds.playbackOptions(q=True, v=True) == "all":
        return False
    else:
        return True
