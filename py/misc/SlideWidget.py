#! /usr/autodesk/maya/bin/mayapy
# encoding: utf-8
# From: http://forums.autodesk.com/t5/maya-programming/how-do-i-can-create-those-draggable-slider-like-input-widgets/m-p/6501133#U6501133

from qtshim import QtGui, QtCore, Signal


class QSlideInput(QtGui.QLineEdit):
    """
    own implementation of the maya's slide input widget (2016 channel box)
    # Date: 23.09.2016
    # Author: LifeArtist
    """

    # an public event you can bind to from outside
    # and which notifies if the value has changed or not
    valueChangedEvent = Signal()

    def __init__(self, *args, **kwargs):
        QtGui.QLineEdit.__init__(self, *args, **kwargs)
        self.init()
        self.initUi()

    def init(self):
        self.dragFlipped = False
        # how many pixels you have to move the mouse to increse or decrease
        # the value
        self.incdecSteps = 20
        self._currentStep = 0
        self.lastCoordValueX = 0
        self.dragBeginCount = 9
        self._dragCurrentCount = 0
        # value which will be added or substracted
        self.incdecrementor = 0.1
        self.lastMousePressedPos = QtCore.QPoint()

    def initUi(self):
        self.canSetFocusOnInput = True
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.returnPressed.connect(self.clearFocus)
        self.setCursor(QtCore.Qt.SplitHCursor)
        self.setMouseTracking(0)
        self.setText("1.0")
        self.setValidator(QtGui.QDoubleValidator())

    def mouseMoveEvent(self, event):
        if not self.hasFocus():
            # +---------------------+
            # | enables drag events |
            # +---------------------+
            if self._dragCurrentCount == self.dragBeginCount:
                self.on_dragEnter()

            if self._dragCurrentCount >= self.dragBeginCount:
                self.on_drag()

            self._dragCurrentCount += 1

    def mousePressEvent(self, event):
        self.setMouseTracking(1)
        self.lastMousePressedPos = QtGui.QCursor.pos()
        self.lastCoordValueX = QtGui.QCursor.pos().x()

    def keyPressEvent(self, event):
        return super(QSlideInput, self).keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        function will be called if the mouse was released
        """
        self.setMouseTracking(0)
        self._dragCurrentCount = 0
        self.setCursor(QtCore.Qt.SplitHCursor)
        # if the mouse was released we need to put the mouse to its last pos
        QtGui.QCursor.setPos(self.lastMousePressedPos)

        if self.canSetFocusOnInput:
            self.setFocus()
        else:
            self.canSetFocusOnInput = True

    def on_dragEnter(self):
        """
        function will be called if the mouse was hold down for the amount of dragBeginCount
        """

        self.canSetFocusOnInput = False
        self.setCursor(QtCore.Qt.BlankCursor)

    def on_drag(self):
        """
        function will be called everytime you drag your mouse but first
        after on_dragEnter
        """

        currentX = QtGui.QCursor.pos().x()

        if self.incdecSteps == self._currentStep:
            # +----------------------------------------------+
            # | check whether strg, shift is pressed or none |
            # +----------------------------------------------+
            modifiers = QtGui.QApplication.queryKeyboardModifiers()

            if modifiers == QtCore.Qt.ControlModifier:
                self.incdecrementor = 0.01
            elif modifiers == QtCore.Qt.ShiftModifier:
                self.incdecrementor = 1
            else:
                self.incdecrementor = 0.1

            # +---------------------------------+
            # | addition and substraction logic |
            # +---------------------------------+
            currentValue = float(self.text())
            # determinds if its incremented or decremented
            if self.lastCoordValueX < currentX:
                if currentValue < 1.0:
                    currentValue += self.incdecrementor
            elif self.lastCoordValueX > currentX:
                if currentValue > 0.0:
                    currentValue -= self.incdecrementor
            # sets the new text
            if currentValue > 1.0:
                self.setText(str(1.0))
            elif currentValue < 0.0:
                self.setText(str(0.0))
            else:
                self.setText(str(currentValue))
            # emit event
            self.valueChangedEvent.emit()

            self.lastCoordValueX = currentX
            self._currentStep = 0
        else:
            self._currentStep += 1

        # reset the cursor if it reaches the end of the screen
        desktopWidth = QtGui.QApplication.desktop().availableGeometry().width()

        if currentX == (desktopWidth - 1):
            QtGui.QCursor.setPos(0, QtGui.QCursor.pos().y())
        elif currentX == 0:
            QtGui.QCursor.setPos(desktopWidth - 1, QtGui.QCursor.pos().y())
