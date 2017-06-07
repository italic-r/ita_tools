"""UI classes for ita_Butter."""

from utils.qtshim import QtCore, QtGui, QtWidgets, logging
Signal = QtCore.Signal

log = logging.getLogger(__name__)


class LogSlider(QtWidgets.QSlider):

    def __init__(self, parent=None):
        super(LogSlider, self).__init__(parent=parent)
        self.setMinimum(1)
        self.setMaximum(240)
        self.setTickInterval(20)
        self.setSingleStep(1)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setTracking(True)
        self.setTickPosition(self.TicksBelow)


class ButterWindow(QtWidgets.QMainWindow):

    """Main Window."""

    SliderChanged = Signal(int)
    SpinBoxChanged = Signal(int)

    def __init__(self, parent=None):
        """:param parent: Window to place Butter under."""
        super(ButterWindow, self).__init__(parent=parent)
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
        self.__place_ui()
        self.__set_connections()
        self.move(self.settings.value("mainwindowposition", QtCore.QPoint(0, 0)))
        self._ButterHelp = None

    def __setup_ui(self):
        self.setObjectName("ButterWindow")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.setFont(font)

        self.centralwidget = QtWidgets.QWidget(self)
        self.virticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.LayoutVert1 = QtWidgets.QVBoxLayout(self.virticalLayoutWidget)

        self.radioRow = QtWidgets.QHBoxLayout()
        self.radioLowPass = QtWidgets.QRadioButton(text="Lowpass")
        self.radioBandPass = QtWidgets.QRadioButton(text="Bandpass")
        self.radioHighPass = QtWidgets.QRadioButton(text="Highpass")

        self.sliderRow = QtWidgets.QHBoxLayout()
        self.slider = LogSlider()
        self.sliderVal = QtWidgets.QSpinBox()
        self.sliderVal.setRange(1, 240)


    def __place_ui(self):
        self.radioRow.addWidget(self.radioHighPass)
        self.radioRow.addWidget(self.radioBandPass)
        self.radioRow.addWidget(self.radioLowPass)

        self.sliderRow.addWidget(self.slider)
        self.sliderRow.addWidget(self.sliderVal)

        self.LayoutVert1.addLayout(self.radioRow)
        self.LayoutVert1.addLayout(self.sliderRow)

        self.setCentralWidget(self.centralwidget)

    def __set_connections(self):
        self.slider.valueChanged.connect(self.__set_spinbox_value)
        self.SliderChanged.connect(self.slider.valueChanged)

        self.sliderVal.valueChanged.connect(self.__set_slider_value)
        self.SpinBoxChanged.connect(self.sliderVal.valueChanged)

    @QtCore.Slot()
    def __set_spinbox_value(self, value):
        self.sliderVal.setValue(value)

    @QtCore.Slot()
    def __set_slider_value(self, value):
        self.slider.setValue(value)

    def closeEvent(self, *args, **kwargs):
        """Custom closeEvent to write settings to files."""
        self.settings.setValue("mainwindowposition", self.pos())
        super(ButterWindow, self).closeEvent(*args, **kwargs)

    def show_help_ui(self):
        """Show help window."""
        if self._ButterHelp is None:
            self._ButterHelp = ButterHelpWindow()
        self._ButterHelp.show()


class ButterHelpWindow(QtWidgets.QMainWindow):

    """Help window."""

    def __init__(self, parent=None):
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
