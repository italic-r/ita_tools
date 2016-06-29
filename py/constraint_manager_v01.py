"""
    Constraint Manager: create and tracks constraints for rigging and animation

"""

import maya.cmds as cmds
# import maya.OpenMaya as om  # for UUID data

import os
import time
import pickle

from functools import partial


class ConstraintManager(object):
    def __init__(self):
        # Script Properties
        self.name = "ConstraintManager"
        self.window = self.name + "Window"

        # Initial property states

        self.ConstList = {}

        # Constraint Options
        self.createMaintainOffset = True

        self.offsetX = 0.0
        self.offsetY = 0.0
        self.offsetZ = 0.0

        self.TAll = True
        self.TX = False
        self.TY = False
        self.TZ = False

        self.RAll = True
        self.RX = False
        self.RY = False
        self.RZ = False

        self.SAll = True
        self.SX = False
        self.SY = False
        self.SZ = False

        self.constWeight = 1.0

        # Replace Options
        self.constCurrent = ""
        self.constNewType = ""
        self.replaceMaintainVisTrans = True

        # Space Switch
        self.currentObject = ""
        self.switchMaintainVisTrans = True
        self.switchKey = False

        # Dimensions and margins
        self.scrollBarThickness = 15
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

        if (cmds.window(self.window, q=True, exists=True)) is not True:
            self.showUI()
        else:
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
        itemList = cmds.textScrollList(
            self.name + 'ScrollList', parent=ScrollCol,
            h=self.textScrollLayoutLineHeightMin, w=self.buttonwidth,
            bgc=(0.4, 0.4, 0.4), ams=0, sc=self.updateUI
        )
        #
        numButtons = 5
        colWidth = self.buttonwidth / numButtons
        cmds.rowColumnLayout(parent=self.name + "ScrollBox", w=self.buttonwidth, nc=numButtons)
        cmds.iconTextButton(
            l="Parent", image="parentConstraint.png", h=self.buttonheight01, w=colWidth,
            c=partial(
                self.PaConst, self.TAll, self.TX, self.TY, self.TZ,
                self.RAll, self.RX, self.RY, self.RZ,
                self.createMaintainOffset
            )
        )
        cmds.iconTextButton(
            l="Point", image="posConstraint.png", h=self.buttonheight01, w=colWidth,
            c=partial(
                self.PoConst,
                self.createMaintainOffset, self.offsetX, self.offsetY, self.offsetZ,
                self.TAll, self.TX, self.TY, self.TZ,
            )
        )
        cmds.iconTextButton(
            l="Orient", image="orientConstraint.png", h=self.buttonheight01, w=colWidth,
            c=partial(
                self.OrConst,
                self.createMaintainOffset, self.offsetX, self.offsetY, self.offsetZ,
                self.RAll, self.RX, self.RY, self.RZ
            )
        )
        cmds.iconTextButton(
            l="Scale", image="scaleConstraint.png", h=self.buttonheight01, w=colWidth,
            c=partial(
                self.ScConst,
                self.createMaintainOffset, self.offsetX, self.offsetY, self.offsetZ,
                self.SAll, self.SX, self.SY, self.SZ
            )
        )
        cmds.iconTextButton(
            l="Remove", image="smallTrash.png", h=self.buttonheight01, w=colWidth,
            c=self.ConstRemove
        )

        # Constraint Options
        Frame1Layout = self.name + "Layout1"
        Frame1Col = self.name + "Layout1Col"
        Frame1Grid = self.name + "Layout1Grid"
        cmds.frameLayout(Frame1Layout, parent=ScrollCol, cl=0, cll=1, l="Constraint Options", fn="plainLabelFont")
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
        self.createMaintainOffset = cmds.checkBox(self.name + "OptOffset", value=self.createMaintainOffset, l="")
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.text("Offset", align='right')
        self.offsetX = cmds.floatField(self.name + "OffsetX", value=self.offsetX, ebg=True, bgc=self.backgroundColor, pre=4)
        self.offsetY = cmds.floatField(self.name + "OffsetY", value=self.offsetY, ebg=True, bgc=self.backgroundColor, pre=4)
        self.offsetZ = cmds.floatField(self.name + "OffsetZ", value=self.offsetZ, ebg=True, bgc=self.backgroundColor, pre=4)
        #
        cmds.text("Translate", align='right')
        self.TAll = cmds.checkBox(self.name + "TAll", l="All", value=self.TAll)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.TX = cmds.checkBox(self.name + "TX", l="X", value=self.TX)
        self.TY = cmds.checkBox(self.name + "TY", l="Y", value=self.TY)
        self.TZ = cmds.checkBox(self.name + "TZ", l="Z", value=self.TZ)
        #
        cmds.text("Rotate", align='right')
        self.RAll = cmds.checkBox(self.name + "RAll", l="All", value=self.RAll)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.RX = cmds.checkBox(self.name + "RX", l="X", value=self.RX)
        self.RY = cmds.checkBox(self.name + "RY", l="Y", value=self.RY)
        self.RZ = cmds.checkBox(self.name + "RZ", l="Z", value=self.RZ)
        #
        cmds.text("Scale", align='right')
        self.SAll = cmds.checkBox(self.name + "SAll", l="All", value=self.SAll)
        cmds.separator(style='none')
        cmds.separator(style='none')
        #
        cmds.separator(style='none')
        self.SX = cmds.checkBox(self.name + "SX", l="X", value=self.SX)
        self.SY = cmds.checkBox(self.name + "SY", l="Y", value=self.SY)
        self.SZ = cmds.checkBox(self.name + "SZ", l="Z", value=self.SZ)
        #
        cmds.rowColumnLayout(parent=Frame1Col, nc=1)
        cmds.floatSliderGrp(
            self.name + "weightSlider", l="Weight", field=True, min=0.0, max=1.0, pre=2, value=1.0,
            cw=((1, self.rowwidth / 3), (2, axisField), (3, axisField * 2)),
            cal=((1, 'right'), (2, 'left'), (3, 'center'))
        )

        # Replace Constraint
        Frame2Layout = self.name + "Layout2"
        Frame2Col = self.name + "Layout2Col"
        cmds.frameLayout(Frame2Layout, parent=ScrollCol, cl=0, cll=1, l="Replace", fn="plainLabelFont")
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
        cmds.optionMenu(self.name + "targetReplace", ebg=True, bgc=self.backgroundColor, bsp=self.ConstReplaceList)
        #
        cmds.separator(parent=Frame2Col, h=5, style='none')
        #
        cmds.rowColumnLayout(
            parent=Frame2Col, nc=2, h=25, cs=(2, 10),
            cw=((1, self.rowwidth - 60), (2, 60)),
            cal=((1, 'left'), (2, 'right'))
        )
        cmds.checkBox(self.name + "VisTrans", l="Maintain Visual Transforms", al='left', value=True, h=25)
        cmds.iconTextButton(ebg=True, bgc=(0.35, 0.35, 0.35), l="Update", style='iconAndTextCentered', al='center', c=self.updateConst)

        # Constraint Space Switching
        Frame3Layout = self.name + "Layout3"
        Frame3Col = self.name + "Layout3Col"
        cmds.frameLayout(Frame3Layout, parent=ScrollCol, cl=0, cll=1, l="Switch", fn="plainLabelFont")
        cmds.columnLayout(Frame3Col, parent=Frame3Layout, co=('both', self.rowmargin), rs=self.rowspacing)
        cmds.rowColumnLayout(
            nc=2,
            cal=((1, 'left'), (2, 'left')), cs=(2, 10),
            cw=((1, self.rowwidth / 2), (2, self.rowwidth / 2))
        )
        cmds.text("Object:", w=self.rowwidth / 2)
        cmds.text("Type:", w=self.rowwidth / 2)
        #
        cmds.separator(parent=Frame3Col, style=self.separatorstyle, height=self.separatorheight, width=self.rowwidth + 10)
        #
        cmds.optionMenu(self.name + "spaceSwitch", parent=Frame3Col, w=self.rowwidth + 10, ebg=True, bgc=self.backgroundColor, bsp=self.ConstSpaceSwitch)
        # row - maintain visual transforms
        # row - key

        cmds.showWindow(self.window)

    def destroy(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

    def updateUI(self):
        self.ConstList
        print "UpdateUI"

    def checkSel(self):
        if len(cmds.ls(sl=True)) < 2:
            cmds.warning("Must select two or more objects to constrain.")
            return False
        else:
            return True

    def PaConst(self, *args):
        if self.checkSel() is True:
            selection = cmds.ls(sl=True, uuid=True)
            activeObj = selection[-1]
            self.ConstList[(activeObj, "Parent")] = selection[:-1]
            self.ListUpdate(activeObj)

        print "Args:", args
        print self.ConstList
        print "Parent Constraint"
        self.updateUI()

    def PoConst(self, *args):
        if self.checkSel() is True:
            selection = cmds.ls(sl=True, uuid=True)
            activeObj = selection[-1]
            valueList = selection[:-1]
            valueList.insert(0, "Point")
            self.ConstList[activeObj] = valueList

        print "Point Constraint"
        self.updateUI()

    def OrConst(self, *args):
        if self.checkSel() is True:
            selection = cmds.ls(sl=True, uuid=True)
            activeObj = selection[-1]
            valueList = selection[:-1]
            valueList.insert(0, "Orient")
            self.ConstList[activeObj] = valueList

        print "Orient Constraint"
        self.updateUI()

    def ScConst(self, *args):
        if self.checkSel() is True:
            selection = cmds.ls(sl=True, uuid=True)
            activeObj = selection[-1]
            valueList = selection[:-1]
            valueList.insert(0, "Scale")
            self.ConstList[activeObj] = valueList

        print "Scale Constraint"
        self.updateUI()

    def ConstRemove(self):
        print "ConstRemove"

    def ListUpdate(self, activeObj):
        textlist = self.name + 'ScrollList'
        activeName = cmds.ls(activeObj)
        cmds.textScrollList(textlist, e=True, append=activeName)

        self.updateUI()

    def UpdateOptions(self, *args):
        print args
        for arg in args:
            print "Arg:", arg
            self.arg = arg
            print "New Arg:", self.arg

    def ConstReplaceList(*args):
        return "Replace"

    def ConstSpaceSwitch(*args):
        return "Switch"

    def updateConst(self):
        pass

    def checkPkl(self):
        # Existing pickle file
        if cmds.file(query=True, sceneName=True, shortName=True) != "":
            self.projDir = cmds.internalVar(uwd=True)
            self.workFile = cmds.file(query=True, sceneName=True, shortName=True).split('.')
            self.fileStr = '.'.join(self.workFile[:-1])
            self.constraintpkl = os.path.join(self.projDir, 'data', 'ConMan_%s.pkl' % (self.fileStr))
        else:
            self.projDir = cmds.internalVar(utd=True)
            self.fileStr = time.strftime("%Y_%m_%d_%H_%M", time.localtime())
            self.constraintpkl = os.path.join(self.projDir, 'data', 'ConMan_%s.pkl' % (self.fileStr))

        if os.path.exists(self.constraintpkl):
            self.readPkl()
        else:
            pass

    def readPkl(self):
        with open(self.constraintpkl, 'rb') as f:
            self.ConstList = pickle.load(f)

    def writePkl(self):
        with open(self.constraintpkl, 'wb') as f:
            pickle.dump(self.ConstList, f, protocol=0)


CMan = ConstraintManager()
