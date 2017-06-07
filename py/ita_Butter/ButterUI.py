"""UI classes for ita_Butter."""

from utils.qtshim import QtCore, QtGui, QtWidgets, logging
Signal = QtCore.Signal

log = logging.getLogger(__name__)


class ButterWindow(QtWidgets.QMainWindow):

    """Main Window."""

    def __init__(self, parent=None):
        pass

    def __setup_ui(self):
        self.setObjectName("ButterWindow")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.setFont(font)

        self.centralwidget = QtWidgets.QWidget(self)

        self.virticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)

        self.LayoutVert1 = QtWidgets.QVBoxLayout(self.virticalLayoutWidget)


class ButterHelpWindow(QtWidgets.QMainWindow):

    """Help window."""

    def __init__(self, parent=None):
        pass


if __name__ == '__main__':
    try:
        win = QtWidgets.QApplication([])
    except RuntimeError:
        win = QtCore.QCoreApplication.instance()
