'''
This script is licensed under the Apache 2.0 license.
See details of this license here:
https://www.apache.org/licenses/LICENSE-2.0

To use the script, run:
import cameraStack
reload(cameraStack)
'''
import maya.cmds as cmds
import functools

windowID = 'camSettingsWindow'
helpID = 'camHelpWindow'


def createUI(pWindowTitle, pGenerateCallback, pApplyCallback, pHelpCallback):

    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

    cmds.window(windowID,
                title=pWindowTitle,
                sizeable=False,
                resizeToFitChildren=True)

    cmds.rowColumnLayout(numberOfColumns=3,
                         columnWidth=[(1, 55), (2, 75), (3, 60)],
                         columnOffset=[(1, 'left', 3),
                                       (2, 'right', 3),
                                       (3, 'left', 3)])

    # First row - focal length
    cmds.button(label='Help', command=pHelpCallback)
    cmds.text(label='Focal Length:')
    camFocLenField = cmds.floatField(value=35.0)

    # Second row - name
    cmds.separator(h=10, style='none')
    cmds.text(label='Name:')
    camNameField = cmds.textField(text='shot')

    # Third row - separators only
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')

    # Fourth row - buttons only
    cmds.button(label='Generate',
                command=functools.partial(pGenerateCallback))

    cmds.button(label='Apply',
                command=functools.partial(pApplyCallback,
                                          camFocLenField,
                                          camNameField))

    def cancelCallback(*pArgs):
        if cmds.window(windowID, exists=True):
            cmds.deleteUI(windowID)
        if cmds.window(helpID, exists=True):
            cmds.deleteUI(helpID)

    cmds.button(label='Cancel', command=cancelCallback)

    cmds.showWindow()


def helpCallback(*pArgs):
    helpText = 'Camera Stack: a camera generator for handheld motion.\n'\
               '\n'\
               '"Apply" creates a new stack at the scene origin with\n'\
               'specified focal length.\n'\
               '"Generate" creates a stack based on the currently selected\n'\
               'camera(s), prefixing generated names with original\n'\
               'camera name.\n'\
               'Both operations connect focal length and film back\n'\
               'attributes to the main camera. Namespaces are handled\n'\
               'through the name query. To make a new namespace, you\n'\
               'will need to create one in the namespace editor.\n'\
               '\n'\
               'by Jeffrey "Italic_" Hoover'

    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

    cmds.window(helpID,
                title='CamStackHelp',
                widthHeight=[300, 175],
                sizeable=True,
                resizeToFitChildren=True)
    cmds.columnLayout(width=300)
    cmds.scrollField(wordWrap=True,
                     text=helpText,
                     editable=False,
                     width=300,
                     height=175,
                     font='smallPlainLabelFont')

    cmds.showWindow()


def generateCallback(pCamNameExists, *pArgs):
    # Create stack based on selected camera
    selectedCam = cmds.ls(selection=True)

    if selectedCam is not None:
        camList = []
        for cams in selectedCam:
            if cmds.listRelatives(cams, shapes=True,
                                  type='camera') is not None:
                camList.append(cams)
            else:
                continue

        if camList != []:
            for item in camList:

                camFocLen = cmds.getAttr(item + '.focalLength')
                camHoFiAp = cmds.getAttr(item + '.horizontalFilmAperture')
                camVeFiAp = cmds.getAttr(item + '.verticalFilmAperture')

                print('Focal length: %s\n'
                      'Horizontal Film Aperture: %s\n'
                      'Vertical Film Aperture: %s') % (camFocLen,
                                                       camHoFiAp,
                                                       camVeFiAp)
                # Main mover
                camMover = cmds.circle(name=item + '_cam_move_all',
                                       normal=[0, 1, 0],
                                       center=[0, 0, 0],
                                       radius=1.5,
                                       sweep=360,
                                       sections=8)

                # Beauty cam - basic camera moves
                mainCam = item
                cmds.select(mainCam)
                mainCam = cmds.rename(item + '_main')
                cmds.parent(mainCam, camMover)

                # Handheld1 - first layer of handheld motion
                cmds.camera(displayGateMask=True,
                            filmFit='overscan',
                            overscan=1.0)

                handCam1 = cmds.rename(item + '_handheld_1')
                cmds.parent(handCam1, mainCam, relative=True)

                cmds.connectAttr((mainCam + '.focalLength'),
                                 (handCam1 + '.focalLength'))
                cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                                 (handCam1 + '.horizontalFilmAperture'))
                cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                                 (handCam1 + '.verticalFilmAperture'))
                cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                                 (handCam1 + '.lensSqueezeRatio'))

                cmds.hide()

                # Handheld2 - second layer of handheld motion
                cmds.camera(displayGateMask=True,
                            filmFit='overscan',
                            overscan=1.0)

                handCam2 = cmds.rename(item + '_handheld_2')
                cmds.parent(handCam2, handCam1, relative=True)

                cmds.connectAttr((mainCam + '.focalLength'),
                                 (handCam2 + '.focalLength'))
                cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                                 (handCam2 + '.horizontalFilmAperture'))
                cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                                 (handCam2 + '.verticalFilmAperture'))
                cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                                 (handCam2 + '.lensSqueezeRatio'))

                # Shake1 - first layer of shake vibration
                cmds.camera(displayGateMask=True,
                            filmFit='overscan',
                            overscan=1.0)

                shakeCam1 = cmds.rename(item + '_shake_1')
                cmds.parent(shakeCam1, handCam2, relative=True)

                cmds.connectAttr((mainCam + '.focalLength'),
                                 (shakeCam1 + '.focalLength'))
                cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                                 (shakeCam1 + '.horizontalFilmAperture'))
                cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                                 (shakeCam1 + '.verticalFilmAperture'))
                cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                                 (shakeCam1 + '.lensSqueezeRatio'))

                # Shake2 - second layer of shake vibration
                cmds.camera(displayGateMask=True,
                            filmFit='overscan',
                            overscan=1.0)

                shakeCam2 = cmds.rename(item + '_shake_2')
                cmds.parent(shakeCam2, shakeCam1, relative=True)

                cmds.connectAttr((mainCam + '.focalLength'),
                                 (shakeCam2 + '.focalLength'))
                cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                                 (shakeCam2 + '.horizontalFilmAperture'))
                cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                                 (shakeCam2 + '.verticalFilmAperture'))
                cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                                 (shakeCam2 + '.lensSqueezeRatio'))

                cmds.select(mainCam, replace=True)

            if cmds.window(windowID, exists=True):
                cmds.deleteUI(windowID)
            if cmds.window(helpID, exists=True):
                cmds.deleteUI(helpID)

        else:
            cmds.warning("Please select your camera(s) and generate again.")

    else:
        cmds.warning("Please select your camera(s) and generate again.")


def applyCallback(pCamFocLenField, pCamNameField, *pArgs):

    camFocLen = cmds.floatField(pCamFocLenField, query=True, value=True)
    camName = cmds.textField(pCamNameField, query=True, text=True)

    print 'Focal Length: %s' % (camFocLen)
    print 'Name: %s' % (camName)

    # Create new stack at scene origin
    camMover = cmds.circle(name=camName + '_cam_move_all',
                           normal=[0, 1, 0],
                           center=[0, 0, 0],
                           radius=1.5,
                           sweep=360,
                           sections=8)

    # Beauty cam - basic camera moves
    cmds.camera(displayGateMask=True,
                filmFit='overscan',
                focalLength=camFocLen,
                overscan=1.0)

    mainCam = cmds.rename(camName + '_main')
    cmds.parent(mainCam, camMover)

    # Handheld1 - first layer of handheld motion
    cmds.camera(displayGateMask=True,
                filmFit='overscan',
                overscan=1.0)

    handCam1 = cmds.rename(camName + '_handheld_1')
    cmds.parent(handCam1, mainCam)

    cmds.connectAttr((mainCam + '.focalLength'),
                     (handCam1 + '.focalLength'))
    cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                     (handCam1 + '.horizontalFilmAperture'))
    cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                     (handCam1 + '.verticalFilmAperture'))
    cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                     (handCam1 + '.lensSqueezeRatio'))

    cmds.hide()

    # Handheld2 - second layer of handheld motion
    cmds.camera(displayGateMask=True,
                filmFit='overscan',
                overscan=1.0)

    handCam2 = cmds.rename(camName + '_handheld_2')
    cmds.parent(handCam2, handCam1)

    cmds.connectAttr((mainCam + '.focalLength'),
                     (handCam2 + '.focalLength'))
    cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                     (handCam2 + '.horizontalFilmAperture'))
    cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                     (handCam2 + '.verticalFilmAperture'))
    cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                     (handCam2 + '.lensSqueezeRatio'))

    # Shake1 - first layer of shake vibration
    cmds.camera(displayGateMask=True,
                filmFit='overscan',
                overscan=1.0)

    shakeCam1 = cmds.rename(camName + '_shake_1')
    cmds.parent(shakeCam1, handCam2)

    cmds.connectAttr((mainCam + '.focalLength'),
                     (shakeCam1 + '.focalLength'))
    cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                     (shakeCam1 + '.horizontalFilmAperture'))
    cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                     (shakeCam1 + '.verticalFilmAperture'))
    cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                     (shakeCam1 + '.lensSqueezeRatio'))

    # Shake2 - second layer of shake vibration
    cmds.camera(displayGateMask=True,
                filmFit='overscan',
                overscan=1.0)

    shakeCam2 = cmds.rename(camName + '_shake_2')
    cmds.parent(shakeCam2, shakeCam1)

    cmds.connectAttr((mainCam + '.focalLength'),
                     (shakeCam2 + '.focalLength'))
    cmds.connectAttr((mainCam + '.horizontalFilmAperture'),
                     (shakeCam2 + '.horizontalFilmAperture'))
    cmds.connectAttr((mainCam + '.verticalFilmAperture'),
                     (shakeCam2 + '.verticalFilmAperture'))
    cmds.connectAttr((mainCam + '.lensSqueezeRatio'),
                     (shakeCam2 + '.lensSqueezeRatio'))

    cmds.select(mainCam, replace=True)

    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    if cmds.window(helpID, exists=True):
        cmds.deleteUI(helpID)

createUI('Create Camera Stack', generateCallback, applyCallback, helpCallback)
