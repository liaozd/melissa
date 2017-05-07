import sys

from PyQt5 import QtCore, QtWidgets


class CheckableDirModel(QtWidgets.QDirModel):
    def __init__(self, parent=None):
        QtWidgets.QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.CheckStateRole:
            return QtWidgets.QDirModel.data(self, index, role)
        else:
            if index.column() == 0:
                return self.checkState(index)

    def flags(self, index):
        return QtWidgets.QDirModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable

    def checkState(self, index):
        if index in self.checks:
            return self.checks[index]
        else:
            return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.checks[index] = value
            self.dataChanged.emit(index, index)
            return True
        return QtWidgets.QDirModel.setData(self, index, value, role)


class MainWindows(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MainWindows, self).__init__()

        folder_model = CheckableDirModel()
        folder_tree_view = QtWidgets.QTreeView()
        folder_tree_view.setModel(folder_model)
        folder_tree_view.setAnimated(False)
        folder_tree_view.setSortingEnabled(True)

        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(folder_tree_view)
        h_box.addStretch()

        self.setLayout(h_box)
        self.show()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindows()
    sys.exit(app.exec_())
