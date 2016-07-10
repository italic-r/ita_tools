"""
    Constraint Manager: create and track constraints for rigging and animation.

    WARNING: THIS SCRIPT IS PRE-ALPHA. DO NOT USE FOR PRODUCTION YET.

    Create common constraints (parent, point, orient, scale) using the buttons
    above the standard constraint options. Constraints will use data for their
    respective type (ie parent constraints do not use offset values, but allows
    maintaining offset, takes translate and rotate values, but not scale, etc.),
    but no more. Remove a constraint from the list only by single-clicking the
    trash icon; remove a constraint from the scene and list by double-clicking.

    Switch constraint target weights in the lower section of the window. Select
    an item in the list at the top, then from the dropdown menu (each an object
    used to constrain the active object) and press "Switch" to turn weight on
    for that object. Press "OFF" to turn off all weight targets and blend parent
    attributes to allow free animation of the constrained object. Press "ALL"
    to turn on weights for all targets (the state constraints are created in).

    Constraints created through this tool are stored in the item list at the
    top of the window. The tool stores the constraint type, constraint node
    UUID, constrained object UUID, and constraining object UUID(s) in a binary
    pickle file in the current project's data directory ($PROJECT/data/ConMan_%.pkl)
    for retrieval after reopening the scene. Because Maya objects maintain their
    UUIDs across restarts, this data storage is ideal for long-term projects,
    like rigging and animation.

    Limitations and known issues:
    Undo is not well-supported. Remove constraints with the removal button and recreate the constraint.
    Can only store one constraint of a particular type at a time (one parent, one point, etc.) - however it can store many constraints of different types.
    Does not support switching weights to individual targets yet. Switch button has been disabled until ready.
    UI does not update properly when removing constraints. Click a list item or (un)collapse a section to refresh the UI.
    Switch keying sets two keyframes (opposite value on previous frame and indicated value on current frame).
    Maintain visual transforms option has not been fully tested. It will only work when removing weight. It may support keying offset in the future.
    Rerunning the script results in recreation of the window (data is not lost). This is for testing during development.

    (c) Jeffrey "italic" Hoover
    italic DOT rendezvous AT gmail DOT com

    Licensed under the Apache 2.0 license. This script can be used for non-commercial
    and commercial projects free of charge. For more information, visit:
    https://www.apache.org/licenses/LICENSE-2.0
"""
# -*- coding: utf-8 -*-

import maya.cmds as cmds
import os
import time
import pickle
from collections import namedtuple
from functools import partial


class ConstraintManager(object):
    def __init__(self):
        # Script Properties
        self.name = "ConstraintManager"
        self.window = self.name + "Window"

        self.fileTime = time.strftime("%Y_%m_%d_%H_%M", time.localtime())

        # Initial property states

        self.ConstList = {}

        # Dimensions and margins
        self.scrollBarThickness = 10
        self.textScrollLayoutLineHeight = 14
        self.textScrollLayoutLineHeightMin = 50
        self.textScrollLayoutLineHeightMax = 150
        self.separatorheight = 10
        self.separatorstyle = 'in'
        self.buttonwidth = 235
        self.buttonheight01 = 30
        self.buttonheight02 = 20
        self.fieldwidth = 75
        self.rowspacing = 2
        self.rowmargin = 2
        self.rowwidth = self.buttonwidth - (self.rowmargin * 8)

        self.backgroundColor = (0.15, 0.15, 0.15)

        self.windowHeight = 167
        self.windowWidth = 248

        # Help annotations
        self.helpTextList = "Double click to select constrained object"
        self.helpAddConst = "Add existing constraint to the list. \nSelect constraint node, then press button to add"
        self.helpConstRemove = "Remove constraint from list. \nDouble-click to remove from scene."
        self.helpSwitchList = "Select an object to switch to"
        self.helpSwitchOff = "Turn OFF all constraint weights"
        self.helpSwitchAll = "Turn ON all constraint weights"
        self.helpSwitchObj = "Make selected object the sole target of the constraint"
        self.helpVisTrans = "Keep the object in its initial position after switching"
        self.helpSwitchKey = "Keyframe the switch among targets. \nOperation (off, on, object switch) keyed on current frame,\nkeyed opposite on previous frame"

        if (cmds.window(self.window, q=True, exists=True)) is not True:
            self.showUI()

        else:
            # cmds.showWindow(self.window)
            self.destroyUI()
            self.showUI()

    def showUI(self):
        self.window = cmds.window(self.window, title="Constraint Manager", ret=False, rtf=True, s=False)

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
            bgc=(0.4, 0.4, 0.4), ams=0,
            ann=self.helpTextList,
            sc=self.updateUI,
            dcc=self.ConstSel,
        )
        #
        numButtons = 6
        colWidth = self.buttonwidth / numButtons
        cmds.rowColumnLayout(parent=self.name + "ScrollBox", w=self.buttonwidth, nc=numButtons)
        cmds.iconTextButton(l="Add", image="pickHandlesComp.png", h=self.buttonheight01, w=colWidth, c=self.AddConst, ann=self.helpAddConst)
        cmds.iconTextButton(l="Parent", image="parentConstraint.png", h=self.buttonheight01, w=colWidth, c=partial(self.CreateConst, arg="Parent"), ann="Create parent constraint with options below")
        cmds.iconTextButton(l="Point", image="posConstraint.png", h=self.buttonheight01, w=colWidth, c=partial(self.CreateConst, arg="Point"), ann="Create point constraint with options below")
        cmds.iconTextButton(l="Orient", image="orientConstraint.png", h=self.buttonheight01, w=colWidth, c=partial(self.CreateConst, arg="Orient"), ann="Create orient constraint with options below")
        cmds.iconTextButton(l="Scale", image="scaleConstraint.png", h=self.buttonheight01, w=colWidth, c=partial(self.CreateConst, arg="Scale"), ann="Create scale constraint with options below")
        cmds.iconTextButton(l="Remove", image="smallTrash.png", h=self.buttonheight01, w=colWidth, c=partial(self.RemoveConst, arg="FromList"), dcc=partial(self.RemoveConst, arg="FromScene"), ann=self.helpConstRemove)

        # Constraint Options
        Frame1Layout = self.name + "Layout1"
        Frame1Col = self.name + "Layout1Col"
        Frame1Grid = self.name + "Layout1Grid"
        cmds.frameLayout(Frame1Layout, parent=ScrollCol, cl=0, cll=1, cc=self.updateUISize, ec=self.updateUISize, l="Constraint Options", fn="plainLabelFont")
        cmds.columnLayout(Frame1Col, parent=Frame1Layout, co=('both', self.rowmargin), rs=self.rowspacing)

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
            self.name + "WeightSlider", l="Weight", field=True, min=0.0, max=1.0, pre=2, value=1.0,
            cw=((1, self.rowwidth / 3), (2, axisField), (3, axisField * 2)),
            cal=((1, 'right'), (2, 'left'), (3, 'center'))
        )

        # Constraint Space Switching
        Frame2Layout = self.name + "Layout2"
        Frame2Col = self.name + "Layout2Col"
        cmds.frameLayout(Frame2Layout, parent=ScrollCol, cl=0, cll=1, cc=self.updateUISize, ec=self.updateUISize, l="Switch", fn="plainLabelFont")
        cmds.columnLayout(Frame2Col, parent=Frame2Layout, co=('both', self.rowmargin), rs=self.rowspacing)
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=2,
            cal=((1, 'left'), (2, 'left')), cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2))
        )
        self.SwitchList = cmds.optionMenu(self.name + "SpaceSwitch", parent=Frame2Col, w=self.rowwidth + 10, ebg=True, bgc=self.backgroundColor, ann=self.helpSwitchList)
        #
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=3, h=25,
            cal=((1, 'left'), (2, 'left'), (3, 'left')), cs=((2, 5), (3, 5)),
            cw=((1, self.rowwidth / 3), (2, self.rowwidth / 3), (3, self.rowwidth / 3))
        )
        cmds.iconTextButton(
            ebg=True, bgc=(0.35, 0.35, 0.35), l="OFF", style='iconAndTextCentered', al='center', h=25,
            ann=self.helpSwitchOff,
            c=partial(
                self.switchConst, arg="OFF"
            )
        )
        cmds.iconTextButton(
            ebg=True, bgc=(0.35, 0.35, 0.35), l="ALL", style='iconAndTextCentered', al='center', h=25,
            ann=self.helpSwitchAll,
            c=partial(
                self.switchConst, arg="ALL"
            )
        )
        cmds.iconTextButton(
            ebg=True, bgc=(0.35, 0.35, 0.35), l="Switch", style='iconAndTextCentered', al='center', h=25,
            ann=self.helpSwitchObj,
            c=partial(
                self.switchConst, arg=cmds.optionMenu(self.SwitchList, query=True, value=True)
            )
        )
        #
        self.SwitchMaintainVisTrans = cmds.checkBox(parent=Frame2Col, l="Maintain Visual Transforms", al='left', value=True, h=20, ann=self.helpVisTrans)
        #
        self.SwitchKey = cmds.checkBox(parent=Frame2Col, l="Key", al='left', value=True, h=20, ann=self.helpSwitchKey)

        # Recall existing data
        self.checkPkl(arg="Read")
        self.ListUpdate(None)
        cmds.showWindow(self.window)

        if cmds.textScrollList(self.itemList, q=True, ni=True) > 0:
            cmds.textScrollList(self.itemList, e=True, sii=1)

        self.updateUI()

    def destroyUI(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

    def updateUI(self):
        textlist = self.itemList
        activeObj = cmds.textScrollList(textlist, q=True, si=True)

        self.SpaceSwitchMenu()
        self.ListUpdate(activeObj)
        self.ListSize()
        self.updateUISize()
        self.checkPkl(arg="Write")

    def updateUISize(self):
        resizeHeight = self.windowHeight
        if cmds.window(self.window, q=1, exists=1) == 1:
            if cmds.frameLayout(self.name + 'Layout1', q=True, cl=True) == 0:
                resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout1', q=True, h=True)) - 20
            if cmds.frameLayout(self.name + 'Layout2', q=True, cl=True) == 0:
                resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout2', q=True, h=True)) - 20
            resizeHeight = (resizeHeight + cmds.textScrollList(self.name + 'ScrollList', q=True, h=True)) - 80
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
                if cmds.objExists(obj):  # Test if original object still exists
                    if cmds.objExists(const[0]):  # Test if original object still has original constraint
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
            listEntry = "%s  |  %s" % (objName, constType)
            cmds.textScrollList(textlist, e=True, append=listEntry)

        if activeObj is None:
            pass
        elif cmds.textScrollList(textlist, q=True, ni=True) == 0:
            pass
        elif activeObj[0] in cmds.textScrollList(textlist, q=True, ai=True):
            cmds.textScrollList(textlist, e=True, si=activeObj[0])
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
        activeObj, activeObjU, constType, constUUID, selObjs = self.RetrieveObj()
        constName = cmds.ls(constUUID)[0]
        print(constUUID, constName)
        cmds.select(activeObj, r=True)

    def AddConst(self):
        print("Adding constraint to the list")

    def checkSel(self):
        if len(cmds.ls(sl=True)) < 2:
            cmds.warning("Must select two or more objects to constrain.")
            return False
        else:
            return True

    def CreateConst(self, arg=None):
        if self.checkSel():
            print "Creating %s constraint" % (arg)

            # Get selected objects and their UUIDs
            # Use node names for constraining; cannot use UUIDs
            selectionO = cmds.ls(sl=True)  # Node names
            selectedObjs = selectionO[:-1]
            activeObj = selectionO[-1]

            selectionU = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = selectionU[:-1]
            activeUUID = selectionU[-1]

            # Get constraint creation options
            MaintainOffset = cmds.checkBox(self.createMaintainOffset, query=True, value=True)
            OffX = cmds.floatField(self.offsetX, query=True, value=True)
            OffY = cmds.floatField(self.offsetY, query=True, value=True)
            OffZ = cmds.floatField(self.offsetZ, query=True, value=True)

            TAll = cmds.checkBox(self.TAll, query=True, value=True)
            TX = cmds.checkBox(self.TX, query=True, value=True)
            TY = cmds.checkBox(self.TY, query=True, value=True)
            TZ = cmds.checkBox(self.TZ, query=True, value=True)

            RAll = cmds.checkBox(self.RAll, query=True, value=True)
            RX = cmds.checkBox(self.RX, query=True, value=True)
            RY = cmds.checkBox(self.RY, query=True, value=True)
            RZ = cmds.checkBox(self.RZ, query=True, value=True)

            SAll = cmds.checkBox(self.SAll, query=True, value=True)
            SX = cmds.checkBox(self.SX, query=True, value=True)
            SY = cmds.checkBox(self.SY, query=True, value=True)
            SZ = cmds.checkBox(self.SZ, query=True, value=True)

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
                    sr=SkipR
                )
                newConstU = cmds.ls(newConst, uuid=True)
            elif arg == "Point":
                newConst = cmds.pointConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipT,
                )
                newConstU = cmds.ls(newConst, uuid=True)
            elif arg == "Orient":
                newConst = cmds.orientConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipR
                )
                newConstU = cmds.ls(newConst, uuid=True)
            elif arg == "Scale":
                newConst = cmds.scaleConstraint(
                    selectedObjs, activeObj,
                    mo=MaintainOffset,
                    o=[OffX, OffY, OffZ],
                    sk=SkipS,
                )
                newConstU = cmds.ls(newConst, uuid=True)

            self.ConstList[(activeUUID, arg)] = newConstU[0], selectedUUID
            newEntry = "%s  |  %s" % (activeObj, arg)
            self.ListUpdate(newEntry)
            self.updateUI()

    def RemoveConst(self, arg=None):
        textlist = self.itemList
        listItem = cmds.textScrollList(textlist, q=True, si=True)
        activeObj, activeObjU, constType, constUUID, selObjs = self.RetrieveObj()

        if arg == "FromList":
            print("Removing %s from list only" % (listItem))

        elif arg == "FromScene":
            print("Removing %s from scene" % (listItem))
            cmds.delete(cmds.ls(constUUID)[0])

        del self.ConstList[(activeObjU, constType)]

        self.updateUI()

    def SpaceSwitchMenu(self):
        activeObj, activeObjU, constType, constUUID, selObjs = self.RetrieveObj()
        menuList = cmds.optionMenu(self.SwitchList, q=True, ill=True)
        if menuList:
            cmds.deleteUI(menuList)
        for obj in selObjs:
            objName = cmds.ls(obj)[0]
            cmds.menuItem(p=self.SwitchList, label=objName)

    def switchConst(self, arg=None):
        # self.SwitchList
        activeObj, activeObjU, constType, constUUID, selObjs = self.RetrieveObj()
        constName = cmds.ls(constUUID)[0]

        if arg == "OFF":
            ws = cmds.xform(activeObj, q=True, matrix=True, worldSpace=True)

            for obj in selObjs:
                # Get old value properly for setting previous frame
                selObjsInd = selObjs.index(obj)
                weightAttr = cmds.connectionInfo('%s.target[%i].targetWeight' % (constName, selObjsInd), sourceFromDestination=True)
                # If enabled, key previous frame before removing constraint weights
                if cmds.checkBox(self.SwitchKey, q=True, value=True):
                    currentTime = cmds.currentTime(q=True)
                    cmds.setKeyframe(weightAttr, t=currentTime - 1, v=1.0)
                    cmds.setKeyframe(weightAttr, t=currentTime, v=0.0)
                cmds.setAttr(weightAttr, 0.0)
            # blend parent

            # Maintain visual transforms
            if cmds.checkBox(self.SwitchMaintainVisTrans, q=True, value=True):
                cmds.xform(activeObj, matrix=ws, worldSpace=True)

        elif arg == "ALL":
            # Get old value properly for setting previous frame
            for obj in selObjs:
                selObjsInd = selObjs.index(obj)
                weightAttr = cmds.connectionInfo('%s.target[%i].targetWeight' % (constName, selObjsInd), sourceFromDestination=True)
                # If enabled, key previous frame before removing constraint weights
                if cmds.checkBox(self.SwitchKey, q=True, value=True):
                    currentTime = cmds.currentTime(q=True)
                    cmds.setKeyframe(weightAttr, t=currentTime - 1, v=0.0)
                    cmds.setKeyframe(weightAttr, t=currentTime, v=1.0)
                cmds.setAttr(weightAttr, 1.0)
            # blend parent

        else:
            # Get old value properly for setting previous frame
            for obj in selObjs:
                selObjsInd = selObjs.index(obj)
                weightAttr = cmds.connectionInfo('%s.target[%i].targetWeight' % (constName, selObjsInd), sourceFromDestination=True)
                # If enabled, key previous frame before removing constraint weights
                if cmds.ls(obj)[0] == cmds.optionMenu(self.SwitchList, q=True, value=True):
                    if cmds.checkBox(self.SwitchKey, q=True, value=True):
                        currentTime = cmds.currentTime(q=True)
                        cmds.setKeyframe(weightAttr, t=currentTime - 1)
                        cmds.setKeyframe(weightAttr, t=currentTime, v=1.0)
                    cmds.setAttr(weightAttr, 1.0)
                else:
                    if cmds.checkBox(self.SwitchKey, q=True, value=True):
                        currentTime = cmds.currentTime(q=True)
                        cmds.setKeyframe(weightAttr, t=currentTime - 1)
                        cmds.setKeyframe(weightAttr, t=currentTime, v=0.0)
                    cmds.setAttr(weightAttr, 0.0)
            # blend parent
            if cmds.checkBox(self.SwitchMaintainVisTrans, q=True, value=True):
                cmds.parentConstraint([cmds.ls(obj) for obj in selObjs], activeObj[0], edit=True, maintainOffset=True)

    def RetrieveObj(self):
        textlist = self.itemList
        listItem = cmds.textScrollList(textlist, q=True, si=True)
        RetrievedObj = namedtuple("RetrievedObj", ["activeObj", "activeObjU", "constType", "constUUID", "selObjs"])

        try:
            activeObj = listItem[0].split("  |  ")[0]
            activeObjU = cmds.ls(activeObj, uuid=True)[0]
            constType = listItem[0].split("  |  ")[1]
            constUUID = self.ConstList.get((activeObjU, constType))[0]
            selObjs = self.ConstList.get((activeObjU, constType))[1]
        except:
            activeObj = ""
            activeObjU = ""
            constType = ""
            constUUID = ""
            selObjs = []

        RO = RetrievedObj(activeObj, activeObjU, constType, constUUID, selObjs)
        return RO

    def checkPkl(self, arg=None):
        # Initial temp values
        self.projDir = cmds.internalVar(utd=True)
        fileStr = self.fileTime
        self.constraintpkl = os.path.join(self.projDir, 'ConMan_%s.pkl' % (fileStr))

        # Saved scene pickle
        if cmds.file(query=True, sceneName=True, shortName=True) != "":
            # Existing temp pickle file
            if os.path.exists(self.constraintpkl):
                cmds.warning("Temporary pickle found. Saving new pickle into project's data directory.")

            # New pickle
            self.projDir = cmds.workspace(query=True, rd=True)
            self.workFile = cmds.file(query=True, sceneName=True, shortName=True).split('.')
            fileStr = '.'.join(self.workFile[:-1])
            self.constraintpkl = os.path.join(self.projDir, 'data', 'ConMan_%s.pkl' % (fileStr))

        if arg == "Read":
            if os.path.exists(self.constraintpkl):
                self.readPkl()
            else:
                self.writePkl()
                cmds.warning("No constraint manager pickle found; created a new pickle at %s" % (self.constraintpkl))
        elif arg == "Write":
            self.writePkl()

    def readPkl(self):
        with open(self.constraintpkl, 'rb') as f:
            self.ConstList = pickle.load(f)

    def writePkl(self):
        with open(self.constraintpkl, 'w+b') as f:
            pickle.dump(self.ConstList, f, protocol=2)


CMan = ConstraintManager()
