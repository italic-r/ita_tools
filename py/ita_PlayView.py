import maya.cmds as cmds
import maya.mel as mel

windowID = 'PlayView'
helpID = 'PlayViewHelp'
custom_viewport = ""  # Saves modelEditor name for future playback

"""
cmds.lsUI(windows=True)
Primary window: "MayaWindow"

cmds.panel(panelname, q=True, control=True)

cmds.paneLayout(controlname, q=True, configuration=True)
    "single",
    "horizontal2", "vertical2",
    "horizontal3", "vertical3",
    "top3", "left3", "bottom3", "right3",
    "horizontal4", "vertical4", "top4", "left4", "bottom4", "right4",
    "quad"

cmds.layout(layoutname, q=True, configuration=True) == "single"

cmds.window(windowname, q=True, tlc=True, wh=True)

cmds.setFocus(panelname)

scale elements by 0.15 (1920/1080 -> 288/162)

"""


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
