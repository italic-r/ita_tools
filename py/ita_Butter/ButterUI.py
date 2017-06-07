"""UI classes for ita_Butter."""

from utils.qtshim import QtCore, QtGui, QtWidgets, logging
Signal = QtCore.Signal

log = logging.getLogger(__name__)


class ButterWindow(QtWidgets.QMainWindow):

    """Main Window."""

    def __init__(self, parent=None):
        """:param parent: Window to place Butter under."""
        super(ButterWindow, self).__init__(parent=parent)
        self.settings = QtCore.QSettings("italic", "Butter")
        self.__setup_ui()
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
