"""
    Constraint Manager: create and track constraints for rigging and animation

"""

import maya.cmds as cmds

import os
import time
import pickle

from functools import partial


class ConstraintManager(object):
    def __init__(self):
        # Script Properties
        self.name = "ConstraintManager"
        self.window = self.name + "Window"

        self.fileTime = time.strftime("%Y_%m_%d_%H_%M", time.localtime())

        # Initial property states

        self.ConstList = {}

        # Constraint Options

        # Replace Options
        self.constCurrent = ""
        self.constNewType = ""

        # Space Switch
        self.currentObject = ""
        self.switchKey = False

        # Dimensions and margins
        self.scrollBarThickness = 10
        self.textScrollLayoutLineHeight = 14
        self.textScrollLayoutLineHeightMin = 50
        self.textScrollLayoutLineHeightMax = 100
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

        if (cmds.window(self.window, q=True, exists=True)) is not True:
            self.showUI()

        else:
            # cmds.showWindow(self.window)
            self.destroy()
            self.showUI()

    def showUI(self):
        self.window = cmds.window(self.window, title="Constraint Manager", ret=True, rtf=1, s=1)

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
            bgc=(0.4, 0.4, 0.4), ams=0, sc=self.updateUI
        )
        #
        numButtons = 5
        colWidth = self.buttonwidth / numButtons
        cmds.rowColumnLayout(parent=self.name + "ScrollBox", w=self.buttonwidth, nc=numButtons)
        cmds.iconTextButton(l="Parent", image="parentConstraint.png", h=self.buttonheight01, w=colWidth, c=self.PaConst)
        cmds.iconTextButton(l="Point", image="posConstraint.png", h=self.buttonheight01, w=colWidth, c=self.PoConst)
        cmds.iconTextButton(l="Orient", image="orientConstraint.png", h=self.buttonheight01, w=colWidth, c=self.OrConst)
        cmds.iconTextButton(l="Scale", image="scaleConstraint.png", h=self.buttonheight01, w=colWidth, c=self.ScConst)
        cmds.iconTextButton(l="Remove", image="smallTrash.png", h=self.buttonheight01, w=colWidth, c=self.ConstRemove)

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

        # Replace Constraint
        Frame2Layout = self.name + "Layout2"
        Frame2Col = self.name + "Layout2Col"
        cmds.frameLayout(Frame2Layout, parent=ScrollCol, cl=0, cll=1, cc=self.updateUISize, ec=self.updateUISize, l="Replace", fn="plainLabelFont")
        cmds.columnLayout(Frame2Col, parent=Frame2Layout, co=('both', self.rowmargin), rs=self.rowspacing)
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=2, cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2)),
            cal=((1, 'left'), (2, 'left')),
        )
        cmds.text("Current Constraint")
        cmds.text("Target Constraint")
        #
        cmds.separator(style=self.separatorstyle, height=self.separatorheight, width=self.rowwidth / 2)
        cmds.separator(style=self.separatorstyle, height=self.separatorheight, width=self.rowwidth / 2)
        #
        cmds.text("  " + "Point", h=16, bgc=self.backgroundColor)
        self.replaceTarget = cmds.optionMenu(self.name + "TargetReplace", ebg=True, bgc=self.backgroundColor, bsp=self.ConstReplaceList)
        #
        cmds.separator(parent=Frame2Col, h=5, style='none')
        #
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=2, h=25, cs=(2, 10),
            cw=((1, self.rowwidth - 60), (2, 60)),
            cal=((1, 'left'), (2, 'right'))
        )
        self.replaceMaintainVisTrans = cmds.checkBox(l="Maintain Visual Transforms", al='left', value=True, h=25)
        cmds.iconTextButton(ebg=True, bgc=(0.35, 0.35, 0.35), l="Update", style='iconAndTextCentered', al='center', c=self.updateConst)

        # Constraint Space Switching
        Frame3Layout = self.name + "Layout3"
        Frame3Col = self.name + "Layout3Col"
        cmds.frameLayout(Frame3Layout, parent=ScrollCol, cl=0, cll=1, cc=self.updateUISize, ec=self.updateUISize, l="Switch", fn="plainLabelFont")
        cmds.columnLayout(Frame3Col, parent=Frame3Layout, co=('both', self.rowmargin), rs=self.rowspacing)
        cmds.rowColumnLayout(
            parent=Frame3Col, nc=2,
            cal=((1, 'left'), (2, 'left')), cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2))
        )
        cmds.text("Object:", w=self.rowwidth / 2)
        cmds.text("Type:", w=self.rowwidth / 2)
        #
        cmds.separator(parent=Frame3Col, style=self.separatorstyle, height=self.separatorheight, width=self.rowwidth + 10)
        #
        self.SwitchList = cmds.optionMenu(self.name + "SpaceSwitch", parent=Frame3Col, w=self.rowwidth + 10, ebg=True, bgc=self.backgroundColor, bsp=self.ConstSpaceSwitch)
        #
        cmds.rowColumnLayout(
            parent=Frame3Col, nc=2, h=25,
            cal=((1, 'left'), (2, 'left')), cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2))
        )
        cmds.iconTextButton(
            ebg=True, bgc=(0.35, 0.35, 0.35), l="OFF", style='iconAndTextCentered', al='center', h=25,
            c=partial(
                self.switchConst, arg="OFF"
            )
        )
        cmds.iconTextButton(
            ebg=True, bgc=(0.35, 0.35, 0.35), l="Switch", style='iconAndTextCentered', al='center', h=25,
            c=partial(
                self.switchConst, arg=cmds.optionMenu(self.SwitchList, query=True, value=True)
            )
        )
        #
        self.SwitchMaintainVisTrans = cmds.checkBox(parent=Frame3Col, l="Maintain Visual Transforms", al='left', value=True, h=20)
        #
        self.SwitchKey = cmds.checkBox(parent=Frame3Col, l="Key", al='left', value=True, h=20)

        self.checkPkl(arg="Read")
        cmds.showWindow(self.window)
        self.updateUI()

        if cmds.textScrollList(self.itemList, q=True, sii=1):
            cmds.textScrollList(self.itemList, e=True, sii=1)

    def destroy(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

    def updateUI(self):
        # fill replace and switch options
        #
        self.checkPkl(arg="Write")
        self.updateUISize()

    def updateUISize(self):
        resizeHeight = self.windowHeight
        if cmds.window(self.window, q=1, exists=1) == 1:
            if cmds.frameLayout(self.name + 'Layout1', q=True, cl=True) == 0:
                resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout1', q=True, h=True)) - 20
            if cmds.frameLayout(self.name + 'Layout2', q=True, cl=True) == 0:
                resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout2', q=True, h=True)) - 20
            if cmds.frameLayout(self.name + 'Layout3', q=True, cl=True) == 0:
                resizeHeight = (resizeHeight + cmds.frameLayout(self.name + 'Layout3', q=True, h=True)) - 20
            resizeHeight = (resizeHeight + cmds.textScrollList(self.name + 'ScrollList', q=True, h=True)) - 50
            cmds.window(self.window, e=1, w=self.windowWidth, h=resizeHeight)

    def ListUpdate(self, activeObj):
        textlist = self.itemList
        cmds.textScrollList(textlist, e=True, ra=True)

        ConstListOrdered = []
        ConstListTemp = {}
        for key in self.ConstList.iterkeys():
            try:
                if cmds.objExists(cmds.ls(key[0])[0]):
                    ConstListTemp[key] = self.ConstList[key]
            except:
                pass

        for key in ConstListTemp.iterkeys():
            if key not in self.ConstList.iterkeys():
                del self.ConstList[key]
        for key in ConstListTemp.iterkeys():
            ConstListOrdered.append(key)

        ConstListOrdered.sort()

        for key in ConstListOrdered:
            cmds.textScrollList(
                textlist, e=True,
                append=cmds.ls(key[0])[0] + "  |  " + key[1]
            )
        if activeObj == "":
            pass
        else:
            cmds.textScrollList(textlist, e=True, si=activeObj)

        self.ListSize()

    def ListSize(self):
        amount = cmds.textScrollList(self.itemList, q=True, ni=True)
        heightAll = amount * self.textScrollLayoutLineHeight
        if heightAll < self.textScrollLayoutLineHeightMin:
            heightAll = self.textScrollLayoutLineHeightMin
        elif heightAll > self.textScrollLayoutLineHeightMax:
            heightAll = self.textScrollLayoutLineHeightMax
        cmds.textScrollList(self.itemList, e=True, h=heightAll)

        self.updateUI()

    def PaConst(self):
        if self.checkSel():
            # Get selected objects and their UUIDs
            selectionO = cmds.ls(sl=True)  # Node names
            selectedObjs = selectionO[:-1]
            activeObj = selectionO[-1]

            selectionU = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = selectionU[:-1]
            activeUUID = selectionU[-1]

            # Test option values
            MaintainOffset = cmds.checkBox(self.createMaintainOffset, query=True, value=True)
            TAll = cmds.checkBox(self.TAll, query=True, value=True)
            TX = cmds.checkBox(self.TX, query=True, value=True)
            TY = cmds.checkBox(self.TY, query=True, value=True)
            TZ = cmds.checkBox(self.TZ, query=True, value=True)
            RAll = cmds.checkBox(self.RAll, query=True, value=True)
            RX = cmds.checkBox(self.RX, query=True, value=True)
            RY = cmds.checkBox(self.RY, query=True, value=True)
            RZ = cmds.checkBox(self.RZ, query=True, value=True)
            SkipT = []
            SkipR = []

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

            cmds.parentConstraint(
                selectedObjs, activeObj,  # Use node names; cannot use UUIDs
                mo=MaintainOffset,
                st=SkipT,
                sr=SkipR
            )

            self.ConstList[(activeUUID, "Parent")] = selectedUUID
            updatetemp = (cmds.ls(activeUUID)[0] + "  |  " + "Parent")
            self.ListUpdate(updatetemp)

    def PoConst(self):
        if self.checkSel():
            # Get selected objects and their UUIDs
            selectionO = cmds.ls(sl=True)  # Node names
            selectedObjs = selectionO[:-1]
            activeObj = selectionO[-1]

            selectionU = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = selectionU[:-1]
            activeUUID = selectionU[-1]

            # Test option values
            MaintainOffset = cmds.checkBox(self.createMaintainOffset, query=True, value=True)
            OffX = cmds.floatField(self.offsetX, query=True, value=True)
            OffY = cmds.floatField(self.offsetY, query=True, value=True)
            OffZ = cmds.floatField(self.offsetZ, query=True, value=True)
            TAll = cmds.checkBox(self.TAll, query=True, value=True)
            TX = cmds.checkBox(self.TX, query=True, value=True)
            TY = cmds.checkBox(self.TY, query=True, value=True)
            TZ = cmds.checkBox(self.TZ, query=True, value=True)
            SkipT = []

            if TX is False:
                SkipT.append("x")
            if TY is False:
                SkipT.append("y")
            if TZ is False:
                SkipT.append("z")
            if TAll is True:
                SkipT = ["none"]

            cmds.pointConstraint(
                selectedObjs, activeObj,  # Use node names; cannot use UUIDs
                mo=MaintainOffset,
                o=[OffX, OffY, OffZ],
                sk=SkipT,
            )

            self.ConstList[(activeUUID, "Point")] = selectedUUID
            updatetemp = (cmds.ls(activeUUID)[0] + "  |  " + "Point")
            self.ListUpdate(updatetemp)

    def OrConst(self):
        if self.checkSel():
            # Get selected objects and their UUIDs
            selectionO = cmds.ls(sl=True)  # Node names
            selectedObjs = selectionO[:-1]
            activeObj = selectionO[-1]

            selectionU = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = selectionU[:-1]
            activeUUID = selectionU[-1]

            # Test option values
            MaintainOffset = cmds.checkBox(self.createMaintainOffset, query=True, value=True)
            OffX = cmds.floatField(self.offsetX, query=True, value=True)
            OffY = cmds.floatField(self.offsetY, query=True, value=True)
            OffZ = cmds.floatField(self.offsetZ, query=True, value=True)
            RAll = cmds.checkBox(self.RAll, query=True, value=True)
            RX = cmds.checkBox(self.RX, query=True, value=True)
            RY = cmds.checkBox(self.RY, query=True, value=True)
            RZ = cmds.checkBox(self.RZ, query=True, value=True)
            SkipR = []

            if RX is False:
                SkipR.append("x")
            if RY is False:
                SkipR.append("y")
            if RZ is False:
                SkipR.append("z")
            if RAll is True:
                SkipR = ["none"]

            cmds.orientConstraint(
                selectedObjs, activeObj,  # Use node names; cannot use UUIDs
                mo=MaintainOffset,
                o=[OffX, OffY, OffZ],
                sk=SkipR
            )

            self.ConstList[(activeUUID, "Orient")] = selectedUUID
            updatetemp = (cmds.ls(activeUUID)[0] + "  |  " + "Orient")
            self.ListUpdate(updatetemp)

    def ScConst(self):
        if self.checkSel():
            # Get selected objects and their UUIDs
            selectionO = cmds.ls(sl=True)  # Node names
            selectedObjs = selectionO[:-1]
            activeObj = selectionO[-1]

            selectionU = cmds.ls(sl=True, uuid=True)  # Node UUIDs
            selectedUUID = selectionU[:-1]
            activeUUID = selectionU[-1]

            # Test option values
            MaintainOffset = cmds.checkBox(self.createMaintainOffset, query=True, value=True)
            OffX = cmds.floatField(self.offsetX, query=True, value=True)
            OffY = cmds.floatField(self.offsetY, query=True, value=True)
            OffZ = cmds.floatField(self.offsetZ, query=True, value=True)
            SAll = cmds.checkBox(self.SAll, query=True, value=True)
            SX = cmds.checkBox(self.SX, query=True, value=True)
            SY = cmds.checkBox(self.SY, query=True, value=True)
            SZ = cmds.checkBox(self.SZ, query=True, value=True)
            SkipS = []

            if SX is False:
                SkipS.append("x")
            if SY is False:
                SkipS.append("y")
            if SZ is False:
                SkipS.append("z")
            if SAll is True:
                SkipS = ["none"]

            cmds.scaleConstraint(
                selectedObjs, activeObj,  # Use node names; cannot use UUIDs
                mo=MaintainOffset,
                o=[OffX, OffY, OffZ],
                sk=SkipS,
            )

            self.ConstList[(activeUUID, "Scale")] = selectedUUID
            updatetemp = (cmds.ls(activeUUID)[0] + "  |  " + "Scale")
            self.ListUpdate(updatetemp)

    def checkSel(self):
        if len(cmds.ls(sl=True)) < 2:
            cmds.warning("Must select two or more objects to constrain.")
            return False
        else:
            return True

    def ConstRemove(self):
        print "ConstRemove"

    def ConstReplaceList(*args):
        print "Replace"

    def ConstSpaceSwitch(*args):
        print "Switch"

    def updateConst(self):
        pass

    def switchConst(self, arg=None):
        pass

    def checkPkl(self, arg=None):
        # Existing pickle file
        if cmds.file(query=True, sceneName=True, shortName=True) != "":
            self.projDir = cmds.workspace(query=True, rd=True)
            self.workFile = cmds.file(query=True, sceneName=True, shortName=True).split('.')
            self.fileStr = '.'.join(self.workFile[:-1])
            self.constraintpkl = os.path.join(self.projDir, 'data', 'ConMan_%s.pkl' % (self.fileStr))
        else:
            self.projDir = cmds.internalVar(utd=True)
            self.fileStr = self.fileTime
            self.constraintpkl = os.path.join(self.projDir, 'data', 'ConMan_%s.pkl' % (self.fileStr))

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
        self.ListUpdate("")

    def writePkl(self):
        with open(self.constraintpkl, 'w+b') as f:
            pickle.dump(self.ConstList, f, protocol=2)


CMan = ConstraintManager()
