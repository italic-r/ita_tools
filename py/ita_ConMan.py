# encoding: utf-8

"""
Constraint Manager: create and track constraints for rigging and animation.

THIS SCRIPT IS BETA!

import ita_ConMan
reload(ita_ConMan)

Create constraints (parent, point, orient, scale) with the given options.
Remove a constraint from the list with the trash icon; delete from the
scene with double click.

Switch constraint targets in the second section. Select a constraint, then a
    target in the dropdown menu.
"OFF" turns off all weights and blend attributes.
"ON" turns on all weights and blend attributes.
"SWITCH" activates a single target and blend attributes and deactivates the rest.

Maintain Visual Transforms: Update constraint offsets to maintain the object's
world-space transforms.

Key: Animate the switch across two frames (current and immediately previous).

Constraint data is saved in the scene file.

WARNING: THIS IS NOT UNDO-ABLE! ================================================
Clean Stale: Remove old data of non-existant objects. Any data not shown in the list is removed.
Purge: Remove ALL saved constraint data from the scene.
WARNING: THIS IS NOT UNDO-ABLE! ================================================

LIMITATIONS AND KNOWN ISSUES:
-- Undo: Undo is supported. If needed, undo and re-run the script. ConMan will
   recognize the old data exists again and repopulate the tracked list.
-- This tool supports only one parent constraint at a time. Maya supports
   multiple parent constraints and one of any other kind.
-- UI does not update properly when removing constraints. Click a list item or
   (un)collapse a section to refresh the UI.
-- Maintain Visual Transforms: Currently updates offsets in the constraint
   node. Enable keying to save old offsets during switching.


(c) Jeffrey "italic" Hoover
italic DOT rendezvous AT gmail DOT com

Licensed under the Apache 2.0 license.
This script can be used for non-commercial
and commercial projects free of charge.
For more information, visit:
https://www.apache.org/licenses/LICENSE-2.0
"""


import maya.cmds as cmds
import maya.OpenMaya as om
import sys
import base64
import pickle
from collections import namedtuple
from functools import partial


class ConstraintManager(object):

    def __init__(self):
        self.supportedVersion = 2016
        self.currentVersion = int(cmds.about(version=True).split(" ")[0])
        if self.currentVersion < self.supportedVersion:
            om.MGlobal.displayError("Maya version unsupported. Use 2016 or newer (requires node UUID).")
            sys.exit()

        # Script Properties
        self.name = "ConstraintManager"
        self.window = self.name + "Window"
        self.helpWindow = self.name + "Help"

        # Initial property states
        self.ConstList = {}

        # Dimensions and margins
        self.scrollBarThickness = 10
        self.textScrollLayoutLineHeight = 14
        self.textScrollLayoutLineHeightMin = 75
        self.textScrollLayoutLineHeightMax = 150
        self.buttonwidth = 235
        self.buttonheight01 = 30
        self.rowspacing = 2
        self.rowmargin = 2
        self.rowwidth = self.buttonwidth - (self.rowmargin * 8)

        self.backgroundColor = (0.15, 0.15, 0.15)
        self.backgroundColorBtn = (0.35, 0.35, 0.35)

        self.windowHeight = 167
        self.windowWidth = 248

        # Help annotations
        self.helpTextList = "Double click to select constrained object."
        self.helpAddConst = "Add existing constraint to the list. \nSelect constraint node, then press button to add"
        self.helpConstRemove = "Remove constraint from list. \nDouble-click to remove from scene."
        self.helpSwitchList = "Select an object to switch to."
        self.helpSwitchOff = "Turn OFF all constraint weights."
        self.helpSwitchAll = "Turn ON all constraint weights."
        self.helpSwitchObj = "Switch influence to this object."
        self.helpVisTrans = "Keep the object in its initial position after \nswitching using constraint offsets."
        self.helpSwitchKey = "Keyframe target switching. \nCurrent configuration keyed on previous frame. \nSwitch keyed on current frame."
        self.helpCleanData = "Clean saved constraint data. \nRemoves stale data from file."
        self.helpPurgeData = "Purge constraint data. \nRemoves all constraint data from \nfile and Python variables. \nWARNING: NOT UNDO-ABLE!"
        self.helpHelpWindow = "Open a help window."

        self.DestroyUI()
        self.ShowUI()

        # Cleans stale data before file save; prevents compounding stale data across sessions.
        om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, partial(self.CleanData, arg="Clean"))

    def ShowUI(self):
        self.window = cmds.window(
            self.window, title="Constraint Manager",
            ret=False, rtf=True, s=False
        )

        # Main window column
        cmds.scrollLayout(
            self.name + "WinCol",
            horizontalScrollBarThickness=self.scrollBarThickness,
            verticalScrollBarThickness=self.scrollBarThickness
        )
        ScrollCol = self.name + "ScrollBox"
        cmds.columnLayout(
            ScrollCol, parent=self.name + "WinCol",
            co=('both', self.rowmargin), rs=self.rowspacing, adj=1
        )

        # Constraint List
        self.itemList = cmds.textScrollList(
            self.name + 'ScrollList', parent=ScrollCol,
            h=self.textScrollLayoutLineHeightMin, w=self.buttonwidth,
            bgc=self.backgroundColorBtn, ams=0,
            ann=self.helpTextList,
            sc=self.UpdateUI,
            dcc=self.ConstSel
        )
        #
        numButtons = 6
        colWidth = self.buttonwidth / numButtons
        cmds.rowColumnLayout(
            parent=self.name + "ScrollBox",
            w=self.buttonwidth, nc=numButtons
        )
        cmds.iconTextButton(
            l="Add", image="pickHandlesComp.png",
            h=self.buttonheight01, w=colWidth,
            c=self.AddConst,
            ann=self.helpAddConst,
            # enable=False
        )
        cmds.iconTextButton(
            l="Parent", image="parentConstraint.png",
            h=self.buttonheight01, w=colWidth,
            c=partial(self.CreateConst, arg="Parent"),
            ann="Create parent constraint with options below"
        )
        cmds.iconTextButton(
            l="Point", image="posConstraint.png",
            h=self.buttonheight01, w=colWidth,
            c=partial(self.CreateConst, arg="Point"),
            ann="Create point constraint with options below"
        )
        cmds.iconTextButton(
            l="Orient", image="orientConstraint.png",
            h=self.buttonheight01, w=colWidth,
            c=partial(self.CreateConst, arg="Orient"),
            ann="Create orient constraint with options below"
        )
        cmds.iconTextButton(
            l="Scale", image="scaleConstraint.png",
            h=self.buttonheight01, w=colWidth,
            c=partial(self.CreateConst, arg="Scale"),
            ann="Create scale constraint with options below"
        )
        cmds.iconTextButton(
            l="Remove", image="smallTrash.png",
            h=self.buttonheight01, w=colWidth,
            c=partial(self.RemoveConst, arg="FromList"),
            dcc=partial(self.RemoveConst, arg="FromScene"),
            ann=self.helpConstRemove
        )

        # Constraint Options
        Frame1Layout = self.name + "Layout1"
        Frame1Col = self.name + "Layout1Col"
        Frame1Grid = self.name + "Layout1Grid"
        cmds.frameLayout(
            Frame1Layout, parent=ScrollCol, cl=0, cll=1,
            cc=self.UpdateUISize, ec=self.UpdateUISize,
            l="Constraint Options", fn="plainLabelFont"
        )
        cmds.columnLayout(
            Frame1Col, parent=Frame1Layout,
            co=('both', self.rowmargin), rs=self.rowspacing
        )

        axisField = ((self.rowwidth / 3) * 2) / 3
        cmds.rowColumnLayout(
            Frame1Grid, parent=Frame1Col,
            nc=4, cs=((2, 4), (3, 3), (4, 3)),
            cw=((1, self.rowwidth / 3), (2, axisField), (3, axisField), (4, axisField)),
            cal=((1, 'right'), (2, 'left'), (3, 'left'), (4, 'left'))
        )
        #
        cmds.text("Maintain Offset", align='right')
        self.createMaintainOffset = cmds.checkBox(self.name + "OptOffset", l="", value=True)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.text("Offset", align='right')
        self.offsetX = cmds.floatField(self.name + "OffsetX", value=0.0, ebg=True, bgc=self.backgroundColor, pre=4)
        self.offsetY = cmds.floatField(self.name + "OffsetY", value=0.0, ebg=True, bgc=self.backgroundColor, pre=4)
        self.offsetZ = cmds.floatField(self.name + "OffsetZ", value=0.0, ebg=True, bgc=self.backgroundColor, pre=4)
        #
        cmds.text("Translate", align='right')
        self.TAll = cmds.checkBox(self.name + "TAll", l="All", value=True)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.TX = cmds.checkBox(self.name + "TX", l="X", value=False)
        self.TY = cmds.checkBox(self.name + "TY", l="Y", value=False)
        self.TZ = cmds.checkBox(self.name + "TZ", l="Z", value=False)
        #
        cmds.text("Rotate", align='right')
        self.RAll = cmds.checkBox(self.name + "RAll", l="All", value=True)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.RX = cmds.checkBox(self.name + "RX", l="X", value=False)
        self.RY = cmds.checkBox(self.name + "RY", l="Y", value=False)
        self.RZ = cmds.checkBox(self.name + "RZ", l="Z", value=False)
        #
        cmds.text("Scale", align='right')
        self.SAll = cmds.checkBox(self.name + "SAll", l="All", value=True)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.SX = cmds.checkBox(self.name + "SX", l="X", value=False)
        self.SY = cmds.checkBox(self.name + "SY", l="Y", value=False)
        self.SZ = cmds.checkBox(self.name + "SZ", l="Z", value=False)
        #
        cmds.rowColumnLayout(parent=Frame1Col, nc=1)
        self.constWeight = cmds.floatSliderGrp(
            self.name + "WeightSlider", l="Weight", field=True,
            min=0.0, max=1.0, pre=2, value=1.0,
            cw=((1, self.rowwidth / 3), (2, axisField), (3, axisField * 2)),
            cal=((1, 'right'), (2, 'left'), (3, 'center'))
        )

        # Constraint Space Switching
        Frame2Layout = self.name + "Layout2"
        Frame2Col = self.name + "Layout2Col"
        cmds.frameLayout(
            Frame2Layout, parent=ScrollCol,
            cl=0, cll=1,
            cc=self.UpdateUISize, ec=self.UpdateUISize,
            l="Switch", fn="plainLabelFont"
        )
        cmds.columnLayout(
            Frame2Col, parent=Frame2Layout,
            co=('both', self.rowmargin), rs=self.rowspacing
        )
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=2,
            cal=((1, 'left'), (2, 'left')), cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2))
        )
        self.SwitchList = cmds.optionMenu(
            self.name + "SpaceSwitch", parent=Frame2Col,
            w=self.rowwidth + 10, ebg=True, bgc=self.backgroundColor,
            ann=self.helpSwitchList
        )
        #
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=3, h=25,
            cal=((1, 'left'), (2, 'left'), (3, 'left')), cs=((2, 5), (3, 5)),
            cw=((1, self.rowwidth / 3), (2, self.rowwidth / 3), (3, self.rowwidth / 3))
        )
        self.swOff = cmds.iconTextButton(
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="OFF", style='iconAndTextCentered', al='center',
            ann=self.helpSwitchOff,
            c=partial(self.SwitchConst, arg="OFF")
        )
        self.swOn = cmds.iconTextButton(
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="ALL", style='iconAndTextCentered', al='center',
            ann=self.helpSwitchAll,
            c=partial(self.SwitchConst, arg="ALL")
        )
        self.swObj = cmds.iconTextButton(
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="Switch", style='iconAndTextCentered', al='center',
            ann=self.helpSwitchObj,
            c=partial(self.SwitchConst, arg="OBJ")
        )
        #
        self.SwitchVisTrans = cmds.checkBox(
            parent=Frame2Col, l="Maintain Visual Transforms", al='left',
            value=True, h=20, ann=self.helpVisTrans
        )
        #
        self.SwitchKey = cmds.checkBox(
            parent=Frame2Col, l="Key", al='left',
            value=True, h=20, ann=self.helpSwitchKey
        )

        # Help and data management
        HelpRow = self.name + "HelpRow"
        cmds.rowColumnLayout(
            HelpRow, parent=ScrollCol, nc=3,
            cal=((1, 'left'), (2, 'left'), (3, 'left')), cs=((2, 8), (3, 8)),
            cw=((1, self.rowwidth / 3), (2, self.rowwidth / 3), (3, self.rowwidth / 3))
        )
        self.helpButton = cmds.iconTextButton(
            parent=HelpRow,
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="Help", style='iconAndTextCentered', al='center',
            ann=self.helpHelpWindow,
            c=self.HelpUI
        )
        self.cleanData = cmds.iconTextButton(
            parent=HelpRow,
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="Clean Stale", style='iconAndTextCentered', al='center',
            ann=self.helpCleanData,
            c=partial(self.CleanData, arg="Clean")
        )
        self.resetData = cmds.iconTextButton(
            parent=HelpRow,
            ebg=True, bgc=self.backgroundColorBtn, h=25,
            l="Purge", style='iconAndTextCentered', al='center',
            ann=self.helpPurgeData,
            c=partial(self.CleanData, arg="Purge")
        )

        # Recall existing data
        self.CheckPkl(arg="Read")
        self.ListUpdate(None)
        cmds.showWindow(self.window)

        if cmds.textScrollList(self.itemList, q=True, ni=True) > 0:
            cmds.textScrollList(self.itemList, e=True, sii=1)

        self.UpdateUI()
        print("Started constraint manager")

    def DestroyUI(self):
        if cmds.window(self.helpWindow, exists=True):
            cmds.deleteUI(self.helpWindow)
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

    def HelpUI(self):
        helpText = (
            'ConMan: A constraint manager for rigging and animation.\n'
            '\n'
            'Create common constraints (parent, point, orient, scale) with the given options.\n'
            'Remove a constraint from the list with the trash icon; delete from the scene with double click.\n'
            '\n'
            'Switch constraint targets in the second section. Select a constraint, then a target in the dropdown menu.\n'
            '"OFF" turns off all weights and blend attributes.\n'
            '"ON" turns on all weights and blend attributes.\n'
            '"SWITCH" activates a single target and blend attributes and deactivates the rest.\n'
            '\n'
            'Maintain Visual Transforms: Update constraint offsets to maintain the object\'s world-space transforms.\n'
            '\n'
            'Key: Animate the switch across two frames (current and immediately previous).\n'
            '\n'
            'Constraint data is saved in the scene file.\n'
            '\n'
            'Clean Stale: Remove old data of non-existant objects. Any data not shown in the list is removed.\n'
            'Purge: Remove ALL saved constraint data from the scene. WARNING: THIS IS NOT UNDO-ABLE!\n'
            '\n'
            'LIMITATIONS AND KNOWN ISSUES:\n'
            '-- Undo: Undo is supported. If needed, undo and re-run the script. ConMan will recognize the old data exists again and repopulate the tracked list.\n'
            '-- This tool supports only one parent constraint at a time. Maya supports multiple parent constraints and one of any other kind.\n'
            '-- UI does not always update properly when removing constraints. Click a list item or (un)collapse a section to refresh the UI.\n'
            '-- Maintain Visual Transforms: Currently updates offsets in the constraint node. Enable keying to save old offsets during switching.\n'
            '\n'
            '\n'
            '(c) Jeffrey "italic" Hoover\n'
            'italic DOT rendezvous AT gmail DOT com\n'
            '\n'
            'Licensed under the Apache 2.0 license.\n'
            'This script can be used for non-commercial\n'
            'and commercial projects free of charge.\n'
            'For more information, visit:\n'
            'https://www.apache.org/licenses/LICENSE-2.0\n'
        )

        if (cmds.window(self.helpWindow, q=True, exists=True)) is True:
            cmds.showWindow(self.helpWindow)

        else:
            cmds.window(
                self.helpWindow,
                title='ConMan Help',
                widthHeight=[300, 250],
                sizeable=False,
                resizeToFitChildren=True
            )
            cmds.columnLayout(width=300)
            cmds.scrollField(
                wordWrap=True,
                text=helpText,
                editable=False,
                width=300,
                height=250,
                font='smallPlainLabelFont'
            )
            cmds.showWindow(self.helpWindow)

    def UpdateUI(self):
        textList = self.itemList
        listItem = cmds.textScrollList(textList, q=True, sii=True)
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()

        if activeObj is not None and cmds.objExists(activeObj):
            if constUUID is not None and cmds.objExists(constObj):
                pass
            else:
                self.ListUpdate(activeObj)
                try:
                    cmds.textScrollList(textList, e=True, sii=listItem)
                except:
                    pass
        else:
            self.ListUpdate(activeObj)
            try:
                cmds.textScrollList(textList, e=True, sii=listItem)
            except:
                pass

        self.ListSize()
        self.UpdateUISize()
        self.SpaceSwitchMenu()
        self.CheckPkl(arg="Write")

    def UpdateUISize(self):
        resizeHeight = self.windowHeight
        if cmds.frameLayout(self.name + 'Layout1', q=True, cl=True) == 0:
            resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout1', q=True, h=True)) - 20
        if cmds.frameLayout(self.name + 'Layout2', q=True, cl=True) == 0:
            resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout2', q=True, h=True)) - 20
        resizeHeight = (resizeHeight + cmds.textScrollList(self.name + 'ScrollList', q=True, h=True)) - 50
        cmds.window(self.window, e=1, w=self.windowWidth, h=resizeHeight)

    def ListUpdate(self, activeObj):
        textlist = self.itemList
        ListKeys = iter(self.ConstList)
        ConstListOrdered = []
        ConstListTemp = {}
        listIndex = cmds.textScrollList(textlist, q=True, sii=True)
        cmds.textScrollList(textlist, e=True, ra=True)

        for key in ListKeys:
            try:
                obj = cmds.ls(key[0])[0]
                const = cmds.ls(self.ConstList[key][0])
                if cmds.objExists(obj):
                    if cmds.objExists(const[0]):
                        ConstListTemp[key] = self.ConstList[key]
            except:
                pass

        for key in list(self.ConstList):
            if key not in iter(ConstListTemp):
                pass
            else:
                ConstListOrdered.append(key)

        ConstListOrdered.sort()

        for key in ConstListOrdered:
            objName = cmds.ls(key[0])[0]  # Object name from UUID
            constType = key[1]  # Constraint type
            listEntry = "{}  |  {}".format(objName, constType)
            cmds.textScrollList(textlist, e=True, append=listEntry)

        if (activeObj is None or activeObj == "") or (cmds.textScrollList(textlist, q=True, ni=True) == 0):
            pass
        elif activeObj in cmds.textScrollList(textlist, q=True, ai=True):
            cmds.textScrollList(textlist, e=True, si=activeObj)
        elif cmds.textScrollList(textlist, q=True, ni=True) >= listIndex[0]:
            cmds.textScrollList(textlist, e=True, sii=listIndex)
        else:
            listLen = cmds.textScrollList(textlist, q=True, ni=True)
            cmds.textScrollList(textlist, e=True, sii=listLen)

        self.ListSize()

    def ListSize(self):
        amount = cmds.textScrollList(self.itemList, q=True, ni=True)
        heightAll = amount * self.textScrollLayoutLineHeight
        if heightAll < self.textScrollLayoutLineHeightMin:
            heightAll = self.textScrollLayoutLineHeightMin
        elif heightAll > self.textScrollLayoutLineHeightMax:
            heightAll = self.textScrollLayoutLineHeightMax
        cmds.textScrollList(self.itemList, e=True, h=heightAll)

    def ConstSel(self):
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()
        cmds.select(activeObj, r=True)

    def AddConst(self):
        axes = ["x", "y", "z"]
        supported = (
            "constraint",
            "parentConstraint",
            "pointConstraint",
            "orientConstraint",
            "scaleConstraint"
        )

        selNodes = cmds.ls(sl=True)

        if len(selNodes) < 1:
            om.MGlobal.displayError("Select a supported constraint node.")

        for obj in selNodes:
            conns = []
            if cmds.nodeType(obj) not in supported:
                continue
            else:
                pass

            constObj = obj
            constUUID = cmds.ls(constObj, uuid=True)[0]

            # Check constraint type and targets
            if cmds.nodeType(constObj) == "parentConstraint":
                constType = "Parent"
                for ax in axes:
                    activeT = cmds.listConnections(constObj + ".ct{}".format(ax))
                    if activeT is not None:
                        if cmds.nodeType(activeT) == "pairBlend":
                            blendOut = cmds.listConnections(activeT[0] + ".ot{}".format(ax), d=True)
                            conns.append(blendOut[0])
                        else:
                            conns.append(activeT[0])
                    activeR = cmds.listConnections(constObj + ".cr{}".format(ax))
                    if activeR is not None:
                        if cmds.nodeType(activeR) == "pairBlend":
                            blendOut = cmds.listConnections(activeR[0] + ".or{}".format(ax), d=True)
                            conns.append(blendOut[0])
                        else:
                            conns.append(activeR[0])
            elif cmds.nodeType(constObj) == "pointConstraint":
                constType = "Point"
                for ax in axes:
                    activeT = cmds.listConnections(constObj + ".ct{}".format(ax))
                    if activeT is not None:
                        if cmds.nodeType(activeT) == "pairBlend":
                            blendOut = cmds.listConnections(activeT[0] + ".ot{}".format(ax), d=True)
                            conns.append(blendOut[0])
                        else:
                            conns.append(activeT[0])
            elif cmds.nodeType(constObj) == "orientConstraint":
                constType = "Orient"
                for ax in axes:
                    activeR = cmds.listConnections(constObj + ".cr{}".format(ax))
                    if activeR is not None:
                        if cmds.nodeType(activeR) == "pairBlend":
                            blendOut = cmds.listConnections(activeR[0] + ".or{}".format(ax), d=True)
                            conns.append(blendOut[0])
                        else:
                            conns.append(activeR[0])
            elif cmds.nodeType(constObj) == "scaleConstraint":
                constType = "Scale"
                for ax in axes:
                    activeS = cmds.listConnections(constObj + ".cs{}".format(ax))
                    if activeS is not None:
                        if cmds.nodeType(activeS) == "pairBlend":
                            blendOut = cmds.listConnections(activeS[0] + ".os{}".format(ax), d=True)
                            conns.append(blendOut[0])
                        else:
                            conns.append(activeS[0])
            else:
                om.MGlobal.displayError("Only parent, point, orient and scale constraints are supported.")
                sys.exit()

            # Check connections
            activeObj = list(set(conns))[0]
            activeUUID = cmds.ls(activeObj, uuid=True)[0]
            selectedUUID = []
            selObjs = [
                cmds.ls(obj, uuid=True)[0]
                for obj in set(cmds.listConnections(constObj + ".tg"))
                if "constraint" not in cmds.nodeType(obj, i=True)
            ]

            # Sort targets in UUID list
            for ind in range(len(selObjs)):
                activeTG = cmds.listConnections(
                    constObj + ".target[{}].targetParentMatrix".format(ind)
                )
                selectedUUID.append(cmds.ls(activeTG[0], uuid=True)[0])

            # Add to list?
            self.ConstList[(activeUUID, constType)] = constUUID, tuple(selectedUUID)
            newEntry = "{}  |  {}".format(activeObj, constType)
            self.ListUpdate(newEntry)
            self.UpdateUI()

    def CreateConst(self, arg=None):
        # Check for two or more selected objects
        if len(cmds.ls(sl=True)) >= 2:
            # Get selected objects and their UUIDs
            # Use node names for constraining; cannot use UUIDs
            selObj = cmds.ls(sl=True)  # Node names
            selectedObjs = selObj[:-1]
            activeObj = selObj[-1]

            selUUID = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = tuple(selUUID[:-1])
            activeUUID = selUUID[-1]

            # Get constraint creation options
            ConstWeight = cmds.floatSliderGrp(self.constWeight, q=True, v=True)

            MaintainOffset = cmds.checkBox(self.createMaintainOffset, q=True, v=True)
            OffX = cmds.floatField(self.offsetX, q=True, v=True)
            OffY = cmds.floatField(self.offsetY, q=True, v=True)
            OffZ = cmds.floatField(self.offsetZ, q=True, v=True)

            TAll = cmds.checkBox(self.TAll, q=True, v=True)
            TX = cmds.checkBox(self.TX, q=True, v=True)
            TY = cmds.checkBox(self.TY, q=True, v=True)
            TZ = cmds.checkBox(self.TZ, q=True, v=True)

            RAll = cmds.checkBox(self.RAll, q=True, v=True)
            RX = cmds.checkBox(self.RX, q=True, v=True)
            RY = cmds.checkBox(self.RY, q=True, v=True)
            RZ = cmds.checkBox(self.RZ, q=True, v=True)

            SAll = cmds.checkBox(self.SAll, q=True, v=True)
            SX = cmds.checkBox(self.SX, q=True, v=True)
            SY = cmds.checkBox(self.SY, q=True, v=True)
            SZ = cmds.checkBox(self.SZ, q=True, v=True)

            SkipT = []
            SkipR = []
            SkipS = []

            if TX is False:
                SkipT.append("x")
            if TY is False:
                SkipT.append("y")
            if TZ is False:
                SkipT.append("z")
            if TAll is True:
                SkipT = ["none"]

            if RX is False:
                SkipR.append("x")
            if RY is False:
                SkipR.append("y")
            if RZ is False:
                SkipR.append("z")
            if RAll is True:
                SkipR = ["none"]

            if SX is False:
                SkipS.append("x")
            if SY is False:
                SkipS.append("y")
            if SZ is False:
                SkipS.append("z")
            if SAll is True:
                SkipS = ["none"]

            if arg == "Parent":
                newConst = cmds.parentConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    st=SkipT,
                    sr=SkipR,
                    w=ConstWeight
                )
            elif arg == "Point":
                newConst = cmds.pointConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipT,
                    w=ConstWeight
                )
            elif arg == "Orient":
                newConst = cmds.orientConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipR,
                    w=ConstWeight
                )
            elif arg == "Scale":
                newConst = cmds.scaleConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipS,
                    w=ConstWeight
                )
            newConstU = cmds.ls(newConst, uuid=True)[0]

            self.ConstList[(activeUUID, arg)] = newConstU, selectedUUID
            newEntry = "{}  |  {}".format(activeObj, arg)
            self.ListUpdate(newEntry)
            self.UpdateUI()

        # Warning for less than two selected objects
        else:
            om.MGlobal.displayWarning("Must select two or more objects to constrain.")

    def RemoveConst(self, arg=None):
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()

        if arg == "FromScene":
            if cmds.objExists(constObj):
                cmds.delete(constObj)
            else:
                om.MGlobal.displayWarning("Nothing to remove.")

        elif arg == "FromList":
            pass

        try:
            del self.ConstList[(activeObjU, constType)]
        except KeyError:
            om.MGlobal.displayWarning("No item selected. Cannot remove.")

        self.UpdateUI()

    def SpaceSwitchMenu(self):
        textlist = self.itemList
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()
        menuList = cmds.optionMenu(self.SwitchList, q=True, ill=True)

        if menuList:
            cmds.deleteUI(menuList)
        for obj in selObjs:
            objName = cmds.ls(obj)[0]
            cmds.menuItem(p=self.SwitchList, label=objName)

        # Disable switch controls if list is empty
        if cmds.textScrollList(textlist, q=True, ni=True) == 0:
            cmds.disable(self.name + "Layout2Col", v=True)
        else:
            cmds.disable(self.name + "Layout2Col", v=False)
            # Disable target switch if only one item in target list
            if cmds.optionMenu(self.SwitchList, q=True, ni=True) == 1:
                cmds.disable(self.swObj, v=True)
            else:
                cmds.disable(self.swObj, v=False)

    def SwitchConst(self, arg=None):
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()
        currentTime = cmds.currentTime(q=True)
        ws = cmds.xform(activeObj, q=True, matrix=True, worldSpace=True)
        selObjsNames = [cmds.ls(obj)[0] for obj in selObjs]

        wOn = 1.0
        wOff = 0.0

        # Channel keys before
        if constType == "Parent":
            TX, TY, TZ, RX, RY, RZ = self.RetrieveConn()
            if cmds.checkBox(self.SwitchKey, q=True, v=True):
                if TX:
                    oldTime = cmds.getAttr(activeObj + ".tx", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".tx", t=currentTime - 1, v=oldTime)
                if TY:
                    oldTime = cmds.getAttr(activeObj + ".ty", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".ty", t=currentTime - 1, v=oldTime)
                if TZ:
                    oldTime = cmds.getAttr(activeObj + ".tz", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".tz", t=currentTime - 1, v=oldTime)
                if RX:
                    oldTime = cmds.getAttr(activeObj + ".rx", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".rx", t=currentTime - 1, v=oldTime)
                if RY:
                    oldTime = cmds.getAttr(activeObj + ".ry", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".ry", t=currentTime - 1, v=oldTime)
                if RZ:
                    oldTime = cmds.getAttr(activeObj + ".rz", t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".rz", t=currentTime - 1, v=oldTime)

        else:
            ConnX, ConnY, ConnZ = self.RetrieveConn()
            if constType == "Point":
                cType = "t"
            elif constType == "Orient":
                cType = "r"
            elif constType == "Scale":
                cType = "s"
            if cmds.checkBox(self.SwitchKey, q=True, v=True):
                if ConnX:
                    oldTime = cmds.getAttr(activeObj + ".{}x".format(cType), t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".{}x".format(cType), t=currentTime - 1, v=oldTime)
                if ConnY:
                    oldTime = cmds.getAttr(activeObj + ".{}y".format(cType), t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".{}y".format(cType), t=currentTime - 1, v=oldTime)
                if ConnZ:
                    oldTime = cmds.getAttr(activeObj + ".{}z".format(cType), t=currentTime - 1)
                    cmds.setKeyframe(activeObj + ".{}z".format(cType), t=currentTime - 1, v=oldTime)

        # Constraint blend attribute
        try:
            blendAttr = "{}.blend{}1".format(activeObj, constType)
            PrevKey = cmds.findKeyframe(blendAttr, which="previous")
            PrevKeyVal = cmds.getAttr(blendAttr, time=PrevKey)

            if cmds.checkBox(self.SwitchVisTrans, q=True, value=True):
                if cmds.checkBox(self.SwitchKey, q=True, value=True):
                    cmds.setKeyframe(blendAttr, t=currentTime - 1, v=PrevKeyVal)
                    if arg == "OFF":
                        cmds.setKeyframe(blendAttr, t=currentTime, v=wOff)
                        cmds.setAttr(blendAttr, wOff)
                    else:
                        cmds.setKeyframe(blendAttr, t=currentTime, v=wOn)
                        cmds.setAttr(blendAttr, wOn)
                    cmds.xform(activeObj, matrix=ws, worldSpace=True)

                else:
                    if arg == "OFF":
                        cmds.setAttr(blendAttr, wOff)
                    else:
                        cmds.setAttr(blendAttr, wOn)
                    cmds.xform(activeObj, matrix=ws, worldSpace=True)
            else:
                if cmds.checkBox(self.SwitchKey, q=True, value=True):
                    cmds.setKeyframe(blendAttr, t=currentTime - 1, v=PrevKeyVal)
                    if arg == "OFF":
                        cmds.setKeyframe(blendAttr, t=currentTime, v=wOff)
                        cmds.setAttr(blendAttr, wOff)
                    else:
                        cmds.setKeyframe(blendAttr, t=currentTime, v=wOn)
                        cmds.setAttr(blendAttr, wOn)

                else:
                    if arg == "OFF":
                        cmds.setAttr(blendAttr, wOff)
                    else:
                        cmds.setAttr(blendAttr, wOn)

        except:
            pass

        # Weights and offsets
        if constType == "Parent":
            for obj in selObjs:
                selObjsInd = selObjs.index(obj)

                weightAttr = cmds.connectionInfo(
                    '{}.target[{}].targetWeight'.format(constObj, selObjsInd), sfd=True
                )
                PrevWeightKey = cmds.findKeyframe(weightAttr, which="previous")
                PrevWeightVal = cmds.getAttr(weightAttr, time=PrevWeightKey)

                PaT = '{}.target[{}].targetOffsetTranslate'.format(constObj, selObjsInd)
                PaR = '{}.target[{}].targetOffsetRotate'.format(constObj, selObjsInd)

                PT = '{}.target[{}].targetOffsetTranslate{}'
                PR = '{}.target[{}].targetOffsetRotate{}'

                PrevKeyPaT = cmds.findKeyframe(PaT, which="previous")
                PrevKeyPaR = cmds.findKeyframe(PaR, which="previous")

                PrevValPaT = cmds.getAttr(PaT, time=PrevKeyPaT)
                PaTX, PaTY, PaTZ = PrevValPaT[0][0:3]

                PrevValPaR = cmds.getAttr(PaR, time=PrevKeyPaR)
                PaRX, PaRY, PaRZ = PrevValPaR[0][0:3]

                if cmds.checkBox(self.SwitchVisTrans, q=True, v=True):
                    if cmds.checkBox(self.SwitchKey, q=True, v=True):
                        # Set previous offset key
                        cmds.setKeyframe(PT.format(constObj, selObjsInd, "X"), t=currentTime - 1, v=PaTX)
                        cmds.setKeyframe(PT.format(constObj, selObjsInd, "Y"), t=currentTime - 1, v=PaTY)
                        cmds.setKeyframe(PT.format(constObj, selObjsInd, "Z"), t=currentTime - 1, v=PaTZ)

                        cmds.setKeyframe(PR.format(constObj, selObjsInd, "X"), t=currentTime - 1, v=PaRX)
                        cmds.setKeyframe(PR.format(constObj, selObjsInd, "Y"), t=currentTime - 1, v=PaRY)
                        cmds.setKeyframe(PR.format(constObj, selObjsInd, "Z"), t=currentTime - 1, v=PaRZ)

                        # Set previous weight key
                        cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                        # Set current weight key
                        if arg == "OFF":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                                cmds.setAttr(weightAttr, wOff)
                        # Set current transform
                        cmds.xform(activeObj, matrix=ws, worldSpace=True)
                        # Update current offset
                        cmds.parentConstraint(selObjsNames, activeObj, e=True, mo=True)
                        # Set current offset key
                        cmds.setKeyframe(PaT, t=currentTime)
                        cmds.setKeyframe(PaR, t=currentTime)

                    else:
                        if arg == "OFF":
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setAttr(weightAttr, wOff)
                        # after set transforms
                        cmds.xform(activeObj, matrix=ws, worldSpace=True)
                        # after update offset
                        cmds.parentConstraint(selObjsNames, activeObj, e=True, mo=True)

                else:
                    if cmds.checkBox(self.SwitchKey, q=True, v=True):
                        # before key weights
                        cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                        # after key weights
                        if arg == "OFF":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                                cmds.setAttr(weightAttr, wOff)
                        cmds.setAttr(weightAttr, wOff)

                    else:
                        if arg == "OFF":
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setAttr(weightAttr, wOff)

        else:
            for obj in selObjs:
                selObjsInd = selObjs.index(obj)

                weightAttr = cmds.connectionInfo(
                    '{}.target[{}].targetWeight'.format(constObj, selObjsInd), sfd=True
                )
                PrevWeightKey = cmds.findKeyframe(weightAttr, which="previous")
                PrevWeightVal = cmds.getAttr(weightAttr, time=PrevWeightKey)

                OffsetAx = '{}.offset{}'

                PrevKeyOffX = cmds.findKeyframe(OffsetAx.format(constObj, "X"), which="previous")
                PrevKeyOffY = cmds.findKeyframe(OffsetAx.format(constObj, "Y"), which="previous")
                PrevKeyOffZ = cmds.findKeyframe(OffsetAx.format(constObj, "Z"), which="previous")

                PrevValOffX = cmds.getAttr(OffsetAx.format(constObj, "X"), time=PrevKeyOffX)
                PrevValOffY = cmds.getAttr(OffsetAx.format(constObj, "Y"), time=PrevKeyOffY)
                PrevValOffZ = cmds.getAttr(OffsetAx.format(constObj, "Z"), time=PrevKeyOffZ)

                if cmds.checkBox(self.SwitchVisTrans, q=True, v=True):
                    if cmds.checkBox(self.SwitchKey, q=True, v=True):
                        # Set previous offset key
                        cmds.setKeyframe(OffsetAx.format(constObj, "X"), t=currentTime - 1, v=PrevValOffX)
                        cmds.setKeyframe(OffsetAx.format(constObj, "Y"), t=currentTime - 1, v=PrevValOffY)
                        cmds.setKeyframe(OffsetAx.format(constObj, "Z"), t=currentTime - 1, v=PrevValOffZ)

                        # Set previous weight key
                        cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                        # Set current weight key
                        if arg == "OFF":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                # Set previous weight key
                                cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                                # Set current weight key
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                                cmds.setAttr(weightAttr, wOff)
                        # Set current transform
                        cmds.xform(activeObj, matrix=ws, worldSpace=True)
                        # Update current offset
                        if constType == "Point":
                            cmds.pointConstraint(selObjsNames, activeObj, e=True, mo=True)
                        elif constType == "Orient":
                            cmds.orientConstraint(selObjsNames, activeObj, e=True, mo=True)
                        elif constType == "Scale":
                            cmds.scaleConstraint(selObjsNames, activeObj, e=True, mo=True)
                        # Set current offset key
                        cmds.setKeyframe(OffsetAx.format(constObj, "X"), t=currentTime)
                        cmds.setKeyframe(OffsetAx.format(constObj, "Y"), t=currentTime)
                        cmds.setKeyframe(OffsetAx.format(constObj, "Z"), t=currentTime)

                    else:
                        # after set weights
                        if arg == "OFF":
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setAttr(weightAttr, wOff)
                        # after set transforms
                        cmds.xform(activeObj, matrix=ws, worldSpace=True)
                        # after update offset
                        if constType == "Point":
                            cmds.pointConstraint(selObjsNames, activeObj, e=True, mo=True)
                        elif constType == "Orient":
                            cmds.orientConstraint(selObjsNames, activeObj, e=True, mo=True)
                        elif constType == "Scale":
                            cmds.scaleConstraint(selObjsNames, activeObj, e=True, mo=True)

                else:
                    if cmds.checkBox(self.SwitchKey, q=True, value=True):
                        # before key weights
                        cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                        # after key weights
                        if arg == "OFF":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                # Set previous weight key
                                cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                                # Set current weight key
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOn)
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setKeyframe(weightAttr, t=currentTime - 1, v=PrevWeightVal)
                                cmds.setKeyframe(weightAttr, t=currentTime, v=wOff)
                                cmds.setAttr(weightAttr, wOff)

                    else:
                        if arg == "OFF":
                            cmds.setAttr(weightAttr, wOff)
                        elif arg == "ALL":
                            cmds.setAttr(weightAttr, wOn)
                        elif arg == "OBJ":
                            if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                                cmds.setAttr(weightAttr, wOn)
                            else:
                                cmds.setAttr(weightAttr, wOff)

        # Channel keys after
        if constType == "Parent":
            if cmds.checkBox(self.SwitchKey, q=True, v=True):
                if TX:
                    cmds.setKeyframe(activeObj + ".tx", t=currentTime)
                if TY:
                    cmds.setKeyframe(activeObj + ".ty", t=currentTime)
                if TZ:
                    cmds.setKeyframe(activeObj + ".tz", t=currentTime)
                if RX:
                    cmds.setKeyframe(activeObj + ".rx", t=currentTime)
                if RY:
                    cmds.setKeyframe(activeObj + ".ry", t=currentTime)
                if RZ:
                    cmds.setKeyframe(activeObj + ".rz", t=currentTime)

        else:
            ConnX, ConnY, ConnZ = self.RetrieveConn()
            if constType == "Point":
                cType = "t"
            elif constType == "Orient":
                cType = "r"
            elif constType == "Scale":
                cType = "s"
            if cmds.checkBox(self.SwitchKey, q=True, v=True):
                if ConnX:
                    cmds.setKeyframe(activeObj + ".{}x".format(cType), t=currentTime)
                if ConnY:
                    cmds.setKeyframe(activeObj + ".{}y".format(cType), t=currentTime)
                if ConnZ:
                    cmds.setKeyframe(activeObj + ".{}z".format(cType), t=currentTime)

    def RetrieveObj(self):
        textlist = self.itemList
        listItem = cmds.textScrollList(textlist, q=True, si=True)
        RetrievedObj = namedtuple(
            "RetrievedObj",
            ["activeObj", "activeObjU", "constType", "constUUID", "constObj", "selObjs"]
        )

        try:
            activeObj = listItem[0].split("  |  ")[0]
            constType = listItem[0].split("  |  ")[1]
        except:
            activeObj = None
            constType = None

        try:
            activeObjU = cmds.ls(activeObj, uuid=True)[0]
        except:
            activeObjU = None

        try:
            constUUID = self.ConstList.get((activeObjU, constType))[0]
            selObjs = self.ConstList.get((activeObjU, constType))[1]
            constObj = cmds.ls(constUUID)[0]
        except:
            constUUID = None
            constObj = None
            selObjs = []

        RO = RetrievedObj(activeObj, activeObjU, constType, constUUID, constObj, selObjs)
        return RO

    def RetrieveConn(self):
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()

        if constType == "Parent":
            RetrievedConn = namedtuple("RetrievedConn", ["TX", "TY", "TZ", "RX", "RY", "RZ"])

            activeConn = cmds.listConnections(activeObj + ".tx", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    TX = True
            elif nType == "parentConstraint":
                TX = True
            else:
                TX = False

            activeConn = cmds.listConnections(activeObj + ".ty", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    TY = True
            elif nType == "parentConstraint":
                TY = True
            else:
                TY = False

            activeConn = cmds.listConnections(activeObj + ".tz", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    TZ = True
            elif nType == "parentConstraint":
                TZ = True
            else:
                TZ = False

            # ============

            activeConn = cmds.listConnections(activeObj + ".rx", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    RX = True
            elif nType == "parentConstraint":
                RX = True
            else:
                RX = False

            activeConn = cmds.listConnections(activeObj + ".ry", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    RY = True
            elif nType == "parentConstraint":
                RY = True
            else:
                RY = False

            activeConn = cmds.listConnections(activeObj + ".rz", source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "parentConstraint" in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    RZ = True
            elif nType == "parentConstraint":
                RZ = True
            else:
                RZ = False

            return RetrievedConn(TX, TY, TZ, RX, RY, RZ)

        else:
            RetrievedConn = namedtuple("RetrievedConn", ["ConnX", "ConnY", "ConnZ"])

            # Constraint type to determine channels queried
            if constType == "Point":
                chType = "t"
            elif constType == "Orient":
                chType = "r"
            elif constType == "Scale":
                chType = "s"

            activeConn = cmds.listConnections(activeObj + ".{}x".format(chType), source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "{}Constraint".format(constType.lower()) in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    ConnX = True
            elif nType == "{}Constraint".format(constType.lower()):
                ConnX = True
            else:
                ConnX = False

            activeConn = cmds.listConnections(activeObj + ".{}y".format(chType), source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "{}Constraint".format(constType.lower()) in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    ConnY = True
            elif nType == "{}Constraint".format(constType.lower()):
                ConnY = True
            else:
                ConnY = False

            activeConn = cmds.listConnections(activeObj + ".{}z".format(chType), source=True)
            nType = cmds.nodeType(activeConn)
            if nType == "pairBlend":
                blendConn = cmds.listConnections(activeConn, source=True)
                if "{}Constraint".format(constType.lower()) in [cmds.nodeType(nType2) for nType2 in blendConn]:
                    ConnZ = True
            elif nType == "{}Constraint".format(constType.lower()):
                ConnZ = True
            else:
                ConnZ = False

            return RetrievedConn(ConnX, ConnY, ConnZ)

    def CheckPkl(self, arg=None):
        if arg == "Read":
            if cmds.fileInfo("ConMan_data", q=True) != []:
                # Read fileInfo() entry
                binLoad = cmds.fileInfo("ConMan_data", q=True)[0]
                decoded = base64.b64decode(binLoad)
                unPickled = pickle.loads(decoded)
                self.ConstList = unPickled
            else:
                om.MGlobal.displayWarning("No constraint manager data found.")
        elif arg == "Write":
            # Write fileInfo() entry
            binDump = pickle.dumps(self.ConstList, protocol=2)
            encoded = base64.b64encode(binDump)
            cmds.fileInfo("ConMan_data", encoded)

    def CleanData(self, arg=None):
        activeObj, activeObjU, constType, constUUID, constObj, selObjs = self.RetrieveObj()

        if arg == "Purge":
            if cmds.confirmDialog(
                    message="Purge all saved constraint data?", icon="critical", title="Purge Constraint Data",
                    b=("Purge", "Cancel"), defaultButton="Purge", cancelButton="Cancel"
            ) == "Purge":
                self.ConstList = {}
                cmds.fileInfo(rm="ConMan_data")
                om.MGlobal.displayWarning("Constraint data has been purged.")
        else:
            textlist = self.itemList
            ListKeys = iter(self.ConstList)
            ConstListOrdered = []
            ConstListTemp = {}

            listIndex = cmds.textScrollList(textlist, q=True, sii=True)

            cmds.textScrollList(textlist, e=True, ra=True)

            for key in ListKeys:
                try:
                    obj = cmds.ls(key[0])[0]
                    const = cmds.ls(self.ConstList[key][0])
                    if cmds.objExists(obj):
                        if cmds.objExists(const[0]):
                            ConstListTemp[key] = self.ConstList[key]
                except:
                    pass

            for key in list(self.ConstList):
                if key not in iter(ConstListTemp):
                    del self.ConstList[key]
                else:
                    ConstListOrdered.append(key)

            ConstListOrdered.sort()

            for key in ConstListOrdered:
                objName = cmds.ls(key[0])[0]  # Object name from UUID
                constType = key[1]  # Constraint type
                listEntry = "{}  |  {}".format(objName, constType)
                cmds.textScrollList(textlist, e=True, append=listEntry)

            if (activeObj is None or activeObj == "") or (cmds.textScrollList(textlist, q=True, ni=True) == 0):
                pass
            elif activeObj in cmds.textScrollList(textlist, q=True, ai=True):
                cmds.textScrollList(textlist, e=True, si=activeObj)
            elif cmds.textScrollList(textlist, q=True, ni=True) >= listIndex[0]:
                cmds.textScrollList(textlist, e=True, sii=listIndex)
            else:
                listLen = cmds.textScrollList(textlist, q=True, ni=True)
                cmds.textScrollList(textlist, e=True, sii=listLen)

            om.MGlobal.displayWarning("Constraint data has been cleaned.")

        self.UpdateUI()


CMan = ConstraintManager()
