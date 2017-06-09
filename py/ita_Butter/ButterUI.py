"""UI classes for ita_Butter."""

from utils.qtshim import QtCore, QtGui, QtWidgets, logging
Signal = QtCore.Signal

log = logging.getLogger(__name__)


class ButterWindow(QtWidgets.QMainWindow):

    """Main Window."""

    SliderMinChangedSig = Signal(int, int, str)
    SliderMaxChangedSig = Signal(int, int, str)

    SliderClickSig = Signal()
    SliderReleaseSig = Signal()

    def __init__(self, parent=None):
        """:param parent: Window to place Butter under."""
        super(ButterWindow, self).__init__(parent=parent)
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
        self.__set_connections()
        self.__place_ui()
        self.move(self.settings.value("mainwindow/position", QtCore.QPoint(0, 0)))
        self.resize(370, 162)
        self._ButterHelp = None

    def __setup_ui(self):
        self.setObjectName("ButterWindow")
        self.setMinimumSize(232, 162)
        self.setMaximumSize(1280, 162)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.setFont(font)

        # Size policy
        self.FrameSizePolicy = QtWidgets.QSizePolicy()
        self.FrameSizePolicy.setVerticalPolicy(self.FrameSizePolicy.Fixed)
        self.FrameSizePolicy.setHorizontalPolicy(self.FrameSizePolicy.Expanding)

        # Main layout and central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.LayoutVert1 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.LayoutVert1.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.LayoutVert1.setSpacing(1)

        # Radio buttons
        self.radioRow = QtWidgets.QHBoxLayout()
        self.radioLowPass = QtWidgets.QRadioButton(text="Lowpass")
        self.radioBandPass = QtWidgets.QRadioButton(text="Bandpass")
        self.radioHighPass = QtWidgets.QRadioButton(text="Highpass")

        # Minimum
        # Range set to (1, 240) - subject to change
        self.FrameMinFreq = QtWidgets.QFrame()
        self.FrameMinFreq.setSizePolicy(self.FrameSizePolicy)
        self.VertLayoutMinFreq = QtWidgets.QVBoxLayout()
        self.FrameMinFreq.setLayout(self.VertLayoutMinFreq)

        self.labelFreqMin = QtWidgets.QLabel(text="Minimum Frequency")
        self.labelFreqMin.setSizePolicy(self.FrameSizePolicy)

        self.sliderRowMin = QtWidgets.QHBoxLayout()

        self.sliderMin = QtWidgets.QSlider()
        self.sliderMin.setRange(1, 240)
        self.sliderMin.setTickInterval(20)
        self.sliderMin.setSingleStep(1)
        self.sliderMin.setOrientation(QtCore.Qt.Horizontal)
        self.sliderMin.setTracking(True)
        self.sliderMin.setTickPosition(self.sliderMin.TicksBelow)

        self.sliderValMin = QtWidgets.QSpinBox()
        self.sliderValMin.setRange(1, 240)
        self.sliderValMin.setSuffix(" Hz")
        self.sliderValMin.setReadOnly(True)
        self.sliderValMin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        # Maximum
        # Range set to (1, 240) - subject to change
        self.FrameMaxFreq = QtWidgets.QFrame()
        self.FrameMaxFreq.setSizePolicy(self.FrameSizePolicy)
        self.VertLayoutMaxFreq = QtWidgets.QVBoxLayout()
        self.FrameMaxFreq.setLayout(self.VertLayoutMaxFreq)

        self.labelFreqMax = QtWidgets.QLabel(text="Maximum Frequency")
        self.labelFreqMax.setSizePolicy(self.FrameSizePolicy)

        self.sliderRowMax = QtWidgets.QHBoxLayout()

        self.sliderMax = QtWidgets.QSlider()
        self.sliderMax.setRange(1, 240)
        self.sliderMax.setTickInterval(20)
        self.sliderMax.setSingleStep(1)
        self.sliderMax.setOrientation(QtCore.Qt.Horizontal)
        self.sliderMax.setTracking(True)
        self.sliderMax.setTickPosition(self.sliderMax.TicksBelow)

        self.sliderValMax = QtWidgets.QSpinBox()
        self.sliderValMax.setRange(1, 240)
        self.sliderValMax.setSuffix(" Hz")
        self.sliderValMax.setReadOnly(True)
        self.sliderValMax.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

    def __place_ui(self):
        self.radioRow.addWidget(self.radioHighPass)
        self.radioRow.addWidget(self.radioBandPass)
        self.radioRow.addWidget(self.radioLowPass)

        self.sliderRowMin.addWidget(self.sliderMin)
        self.sliderRowMin.addWidget(self.sliderValMin)

        self.VertLayoutMinFreq.addWidget(self.labelFreqMin)
        self.VertLayoutMinFreq.addLayout(self.sliderRowMin)

        self.sliderRowMax.addWidget(self.sliderMax)
        self.sliderRowMax.addWidget(self.sliderValMax)

        self.VertLayoutMaxFreq.addWidget(self.labelFreqMax)
        self.VertLayoutMaxFreq.addLayout(self.sliderRowMax)

        self.LayoutVert1.addLayout(self.radioRow)
        self.LayoutVert1.addWidget(self.FrameMinFreq)
        self.LayoutVert1.addWidget(self.FrameMaxFreq)

        self.setCentralWidget(self.centralwidget)

        # Set default slider enable/disable state
        # Set only after buttons are grouped
        self.radioLowPass.toggle()

    def __set_connections(self):
        self.sliderMin.valueChanged.connect(self.__set_spinbox_value_min)
        self.sliderMax.valueChanged.connect(self.__set_spinbox_value_max)
        self.sliderMin.valueChanged.connect(self.__slider_min_send)
        self.sliderMax.valueChanged.connect(self.__slider_max_send)

        self.sliderMin.sliderPressed.connect(self.__undo_queue_start)
        self.sliderMin.sliderReleased.connect(self.__undo_queue_end)
        self.sliderMax.sliderPressed.connect(self.__undo_queue_start)
        self.sliderMax.sliderReleased.connect(self.__undo_queue_end)

        self.radioLowPass.toggled.connect(self.__slider_config)
        self.radioBandPass.toggled.connect(self.__slider_config)
        self.radioHighPass.toggled.connect(self.__slider_config)

    def __slider_config(self, checked):
        if self.radioLowPass.isChecked():
            self.FrameMinFreq.setEnabled(False)
            self.FrameMaxFreq.setEnabled(True)

        elif self.radioBandPass.isChecked():
            self.FrameMinFreq.setEnabled(True)
            self.FrameMaxFreq.setEnabled(True)

        elif self.radioHighPass.isChecked():
            self.FrameMinFreq.setEnabled(True)
            self.FrameMaxFreq.setEnabled(False)

    @QtCore.Slot()
    def __set_spinbox_value_min(self, value):
        self.sliderValMin.setValue(value)

    @QtCore.Slot()
    def __set_slider_value_min(self, value):
        self.sliderMin.setValue(value)

    @QtCore.Slot()
    def __set_spinbox_value_max(self, value):
        self.sliderValMax.setValue(value)

    @QtCore.Slot()
    def __set_slider_value_max(self, value):
        self.sliderMax.setValue(value)

    @QtCore.Slot()
    def __undo_queue_start(self):
        self.SliderClickSig.emit()

    @QtCore.Slot()
    def __undo_queue_end(self):
        self.SliderReleaseSig.emit()

    @QtCore.Slot()
    def __slider_min_send(self, low_value):
        pass_type = "bandpass" if self.radioBandPass.isChecked() else "highpass"
        self.SliderMinChangedSig.emit(low_value, self.sliderMax.value(), pass_type)

    @QtCore.Slot()
    def __slider_max_send(self, high_value):
        pass_type = "bandpass" if self.radioBandPass.isChecked() else "lowpass"
        self.SliderMinChangedSig.emit(self.sliderMin.value(), high_value, pass_type)

    def closeEvent(self, *args, **kwargs):
        """Custom closeEvent to write settings to files."""
        self.settings.setValue("mainwindow/position", self.pos())
        super(ButterWindow, self).closeEvent(*args, **kwargs)

    def show_help_ui(self):
        """Show help window."""
        if self._ButterHelp is None:
            self._ButterHelp = ButterHelpWindow()
        self._ButterHelp.show()


class ButterHelpWindow(QtWidgets.QMainWindow):

    """Help window."""

    def __init__(self, parent=None):
        """:param parent: Window to place Butter Help under."""
        self.helpText = (
            ""
        )
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
        self.move(self.settings.value("helpwindowposition", QtCore.QPoint(0, 0)))

    def __setup_ui(self):
        pass

    def closeEvent(self, *args, **kwargs):
        """Custom closeEvent to write settings to file."""
        self.settings.setValue("helpwindowposition", self.pos())
        super(ButterHelpWindow, self).closeEvent(*args, **kwargs)


if __name__ == '__main__':
    try:
        win = QtWidgets.QApplication([])
    except RuntimeError:
        win = QtCore.QCoreApplication.instance()

    _ButterWin = ButterWindow()
    _ButterWin.show()
    win.exec_()
