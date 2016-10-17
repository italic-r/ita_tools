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

place a window + button at center of each window, without frame?
for w in windows:
    get layout config,
    make single window,
    button grid layout to match,
    any button closes all windows
"""


def draw_window_main(pWindowTitle):
    """Draw the warning window."""
    # destroy_window()

    cmds.window(
        windowID,
        title=pWindowTitle,
        sizeable=True,
        resizeToFitChildren=True
    )

    rowcol = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnWidth=[(1, 250)],
        columnOffset=[(1, 'both', 5)]
    )

    cmds.text(label='You are trying to playblast from a default camera!')
    cmds.separator(h=10, style='none')
    cmds.rowLayout(
        parent=rowcol,
        numberOfColumns=3,
        columnAttach=[(1, 'left', 1),
                      (2, 'left', 1),
                      (3, 'both', 1)],
        columnWidth=[(1, 35),  # Total == 250 - margins
                     (2, 85),
                     (3, 112)]
    )
    cmds.button(label='Help')
    makeDefault = cmds.checkBox(label='Make Default')

    makeDefaultMenu = cmds.optionMenu(label='')
    cmds.menuItem(label='')

    cmds.rowLayout(
        parent=rowcol,
        numberOfColumns=3,
        columnAttach=[
            (1, 'both', 2),
            (2, 'both', 2),
            (3, 'both', 2)
        ],
        columnWidth=[
            (1, 123),
            (2, 50),
            (3, 60)
        ]
    )
    cmds.separator(h=10, style='none')
    cmds.button(label='OK!')
    cmds.button(label='Continue')

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
