"""UI classes for ita_Butter."""

from utils.qtshim import QtCore, QtGui, QtWidgets, logging
Signal = QtCore.Signal

log = logging.getLogger(__name__)


class ButterWindow(QtWidgets.QMainWindow):

    """Main Window."""

    SlidersChangedSig = Signal(int, int, str)

    FilterStartSig = Signal()
    FilterEndSig = Signal()

    def __init__(self, parent=None):
        """:param parent: Window to place Butter under."""
        super(ButterWindow, self).__init__(parent=parent)
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
        self.__set_connections()
        self.__place_ui()
        self.move(self.settings.value("mainwindow/position", QtCore.QPoint(0, 0)))
        self.resize(370, 210)
        self._ButterHelp = None

    def __setup_ui(self):
        self.setObjectName("ButterWindow")
        self.setWindowTitle("Butter")
        self.setMinimumSize(232, 210)
        self.setMaximumSize(1280, 210)
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
        self.FrameMinFreq = QtWidgets.QFrame()
        self.FrameMinFreq.setSizePolicy(self.FrameSizePolicy)
        self.VertLayoutMinFreq = QtWidgets.QVBoxLayout()
        self.FrameMinFreq.setLayout(self.VertLayoutMinFreq)

        self.labelFreqMin = QtWidgets.QLabel(text="Minimum Frequency")
        self.labelFreqMin.setSizePolicy(self.FrameSizePolicy)

        self.sliderRowMin = QtWidgets.QHBoxLayout()

        self.sliderMin = QtWidgets.QSlider()
        self.sliderMin.setRange(1, 1000)
        self.sliderMin.setTickInterval(100)
        self.sliderMin.setSingleStep(1)
        self.sliderMin.setOrientation(QtCore.Qt.Horizontal)
        self.sliderMin.setTracking(True)
        self.sliderMin.setTickPosition(self.sliderMin.TicksBelow)

        self.sliderValMin = QtWidgets.QDoubleSpinBox()
        self.sliderValMin.setRange(0.00001, 1.0)
        self.sliderValMin.setDecimals(5)
        self.sliderValMin.setReadOnly(False)
        self.sliderValMin.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.sliderValMin.setSingleStep(0.00001)

        # Maximum
        self.FrameMaxFreq = QtWidgets.QFrame()
        self.FrameMaxFreq.setSizePolicy(self.FrameSizePolicy)
        self.VertLayoutMaxFreq = QtWidgets.QVBoxLayout()
        self.FrameMaxFreq.setLayout(self.VertLayoutMaxFreq)

        self.labelFreqMax = QtWidgets.QLabel(text="Maximum Frequency")
        self.labelFreqMax.setSizePolicy(self.FrameSizePolicy)

        self.sliderRowMax = QtWidgets.QHBoxLayout()

        self.sliderMax = QtWidgets.QSlider()
        self.sliderMax.setRange(1, 1000)
        self.sliderMax.setTickInterval(100)
        self.sliderMax.setSingleStep(1)
        self.sliderMax.setValue(1000)
        self.sliderMax.setOrientation(QtCore.Qt.Horizontal)
        self.sliderMax.setTracking(True)
        self.sliderMax.setTickPosition(self.sliderMax.TicksBelow)

        self.sliderValMax = QtWidgets.QDoubleSpinBox()
        self.sliderValMax.setRange(0.0, 1.0)
        self.sliderValMax.setDecimals(3)
        self.sliderValMax.setValue(1.0)
        self.sliderValMax.setReadOnly(False)
        self.sliderValMax.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.sliderValMax.setSingleStep(0.001)

        self.start_filter = QtWidgets.QPushButton(text="Start interactive filter")
        self.end_filter = QtWidgets.QPushButton(text="Exit filter")
        self.help_button = QtWidgets.QPushButton(text="Help...")

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

        self.LayoutVert1.addWidget(self.start_filter)
        self.LayoutVert1.addWidget(self.end_filter)
        self.LayoutVert1.addWidget(self.help_button)

        self.setCentralWidget(self.centralwidget)

        # Set default slider enable/disable state
        # Set only after buttons are grouped
        self.radioLowPass.toggle()

        self.end_filter.setEnabled(False)
        self.end_filter.setVisible(False)

    def __set_connections(self):
        self.help_button.clicked.connect(self.show_help_ui)
        self.start_filter.clicked.connect(self.__start_filter)
        self.end_filter.clicked.connect(self.__end_filter)

        self.sliderMin.valueChanged.connect(self.__set_spinbox_value_min)
        self.sliderMax.valueChanged.connect(self.__set_spinbox_value_max)

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
        self.sliderValMin.setValue(value * 0.00001)

    @QtCore.Slot()
    def __set_spinbox_value_max(self, value):
        self.sliderValMax.setValue(value * 0.001)

    @QtCore.Slot()
    def __start_filter(self):
        self.sliderMin.valueChanged.connect(self.__slider_min_send)
        self.sliderMax.valueChanged.connect(self.__slider_max_send)

        self.start_filter.setEnabled(False)
        self.start_filter.setVisible(False)
        self.end_filter.setEnabled(True)
        self.end_filter.setVisible(True)

        self.FilterStartSig.emit()

    @QtCore.Slot()
    def __end_filter(self):
        self.sliderMin.valueChanged.disconnect(self.__slider_min_send)
        self.sliderMax.valueChanged.disconnect(self.__slider_max_send)

        self.end_filter.setEnabled(False)
        self.end_filter.setVisible(False)
        self.start_filter.setEnabled(True)
        self.start_filter.setVisible(True)

        self.FilterEndSig.emit()

    @QtCore.Slot()
    def __slider_min_send(self, low_value):
        # passed in as (low, high, pass_type)
        pass_type = "bandpass" if self.radioBandPass.isChecked() else "highpass"
        self.SlidersChangedSig.emit(low_value, self.sliderMax.value(), pass_type)

    @QtCore.Slot()
    def __slider_max_send(self, high_value):
        # passed in as (low, high, pass_type)
        pass_type = "bandpass" if self.radioBandPass.isChecked() else "lowpass"
        self.SlidersChangedSig.emit(self.sliderMin.value(), high_value, pass_type)

    def closeEvent(self, *args, **kwargs):
        """Custom closeEvent to write settings to files."""
        self.settings.setValue("mainwindow/position", self.pos())
        self.settings.setValue("mainwindow/size", self.size())
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
        super(ButterHelpWindow, self).__init__(parent=parent)
        self.helpText = (
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Butter</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">An animation curve filter for Maya.</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This filter allows you to quickly smooth and denoise high-density animation curves, usually from motion capture. If any curves are selected, the filter will manipulate only selected curves. If no curves are selected, the filter will manipulate all visible curves in the graph editor.</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Quick tip: expand the window sideways for higher precision!</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">How to use:</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Enable the filter by clicking <span style=\" font-weight:600;\">Start interactive filter</span>.</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Select your filter type from [Highpass, Bandpass, Lowpass].</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Use the sliders to start filtering curves.</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Exit the filter by clicking <span style=\" font-weight:600;\">Exit filter</span>.</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Undo or redo as necessary.</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">----</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">(c) Jeffrey &quot;italic&quot; Hoover</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">italic DOT rendezvous AT gmail DOT com</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Licensed under the Apache 2.0 license.</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This script can be used for commercial and non-commercial projects free of charge.</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0057ae;\">https://www.apache.org/licenses/LICENSE-2.0</span></a></p></body></html>"
        )
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
        self.move(self.settings.value("help/position", QtCore.QPoint(0, 0)))
        self.resize(self.settings.value("help/size", QtCore.QSize(0, 0)))
        self.show()

    def __setup_ui(self):
        self.setObjectName("ButterHelpWindow")
        self.setWindowTitle("Butter Help")
        self.setMinimumSize(325, 250)
        self.setMaximumSize(600, 425)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.setFont(font)

        self.centralwidget = QtWidgets.QWidget(self)

        self.vlayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.vlayout.setSpacing(2)
        self.vlayout.setContentsMargins(2, 2, 2, 2)

        self.textwidget = QtWidgets.QTextEdit(self.centralwidget)
        self.textwidget.setReadOnly(True)
        self.textwidget.setHtml(self.helpText)

        self.vlayout.addWidget(self.textwidget)
        self.setCentralWidget(self.centralwidget)

    def closeEvent(self, *args, **kwargs):
        """Custom closeEvent to write settings to file."""
        self.settings.setValue("help/position", self.pos())
        self.settings.setValue("help/size", self.size())
        super(ButterHelpWindow, self).closeEvent(*args, **kwargs)


if __name__ == '__main__':
    try:
        win = QtWidgets.QApplication([])
    except RuntimeError:
        win = QtCore.QCoreApplication.instance()

    _ButterWin = ButterWindow()
    _ButterWin.show()
    win.exec_()
