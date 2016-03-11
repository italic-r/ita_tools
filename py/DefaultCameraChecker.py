'''
Copyright Jeffrey "Italic_" Hoover 2016

This script is licensed under the Apache 2.0 license.
See details of this license here:
https://www.apache.org/licenses/LICENSE-2.0

To use the script, run:
import DefaultCameraChecker
reload(DefaultCameraChecker)

For help, call:
DefaultCameraChecker.helpCall()
or open the help from the script UI.

Jeffrey "Italic_" Hoover
11 March 2016
v1.0
'''

import maya.cmds as cmds
import maya.mel as mel
from functools import partial


# Maya's stock camera names from hotbox marking menu
stockCamNames = ["persp", "left", "right", "top", "bottom", "front", "back"]
windowID = 'perspPlayBlast'
helpID = 'perspPlayBlastHelp'


def draw_warning(pWindowTitle, pbContinue):
    destroyWindow()

    cmds.window(windowID,
                title=pWindowTitle,
                sizeable=True,
                resizeToFitChildren=True)

    rowcol = cmds.rowColumnLayout(numberOfColumns=1,
                                  columnWidth=[(1, 250)],
                                  columnOffset=[(1, 'both', 3)]
                                  )

    cmds.text(label='You are trying to playblast from a default camera!')

    cmds.separator(h=10, style='none')

    cmds.rowLayout(parent=rowcol,
                   numberOfColumns=4,
                   columnAttach=[(1, 'left', 3),
                                 (2, 'both', 3),
                                 (3, 'left', 3),
                                 (4, 'right', 10)],
                   columnWidth=[(1, 250/4),
                                (2, 250/4),
                                (3, 250/4),
                                (4, 250/4)]
                   )
    cmds.button(label='Help', command=helpCall)
    perspToggle = cmds.checkBox(label='Persp')
    cmds.button(label='OK!', command=partial(pbContinue, perspToggle))
    cmds.button(label='Cancel', command=destroyWindow)

    cmds.showWindow()


def pbContinue(perspToggle, *args):
    activepanel = cmds.getPanel(withFocus=True)
    if cmds.checkBox(perspToggle, query=True, value=True) is True:
        cam = cmds.modelEditor(activepanel, query=True, camera=True)
        cmds.lookThru(activepanel, 'persp')
        blast()
        cmds.lookThru(activepanel, cam)

    else:
        blast()

    destroyWindow()


def blast(*args):
    fileNameLong = cmds.file(query=True, sceneName=True, shortName=True)

    if fileNameLong == "":
        fileNameLong = "untitled"
    else:
        fileNameLong = cmds.file(query=True, sceneName=True, shortName=True)

    fileNameShort = fileNameLong.split(".")

    TimeRange = mel.eval('$tmpVar=$gPlayBackSlider')
    SoundNode = cmds.timeControl(TimeRange, query=True, sound=True)

    if cmds.ls(renderResolutions=True):
        ResX = cmds.getAttr("defaultResolution.width")
        ResY = cmds.getAttr("defaultResolution.height")

        cmds.playblast(filename=("movies/" + fileNameShort[0] + ".mov"),
                       forceOverwrite=True, format="qt", compression="png",
                       offScreen=True, width=ResX, height=ResY, quality=100,
                       percent=100, sound=SoundNode)

    else:
        cmds.error("No resolution data in file. Please set resolution and save.")


def helpCall(*args):
    """Open a text window with help information."""
    helpText = (
        'Default Camera Checker: A tool to check if you\'re playblasting\n'
        'from a Maya default camera.\n'
        '\n'
        'If your active viewport does not use one of Maya\'s default \n'
        'cameras, it will automatically playblast to file. If your camera\n'
        'is any default camera, the tool will give options for blastable\n'
        'cameras.\n'
        '"OK!" initiates playblast.\n'
        '"Cancel" simply closes these windows.\n'
        '"Help" opens this help window.\n'
        '"Persp" enables temporary toggling between the current\n'
        'active camera (setting disabled) and the default persp\n'
        'camera (setting enabled). Viewport is temporarily switched to\n'
        'the persp camera for playblast and reverted when finished.\n'
        '\n'
        'by Jeffrey "Italic_" Hoover'
        )

    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

    cmds.window(helpID,
                title='DefaultCameraCheckerHelp',
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


def destroyWindow(*args):
    """If perspPlayBlast windows exist, destroy them."""
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)


def check_camera_name():
    activepanel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(typeOf=activepanel) != 'modelPanel':
        return None

    elif cmds.getPanel(typeOf=activepanel) == 'modelPanel':
        cam = cmds.modelEditor(activepanel, query=True, camera=True)
        if cam == 'persp':
            return "persp"
        elif cam in stockCamNames:
            return True
        else:
            return False

    else:
        return None


def init():
    if check_camera_name() is False:
        destroyWindow()
        blast()
    elif check_camera_name() == "persp":
        draw_warning('DefaultCameraChecker', pbContinue)
    elif check_camera_name() is True:
        draw_warning('DefaultCameraChecker', pbContinue)
    else:
        cmds.warning("Activate a viewport and try again.")

init()
