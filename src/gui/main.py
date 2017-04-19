import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets


def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False


class CheckableDirModel(QtWidgets.QDirModel):
    def __init__(self, parent=None):
        QtWidgets.QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return QtWidgets.QDirModel.data(self, index, role)

    def flags(self, index):
        return QtWidgets.QDirModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable

    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i, v in self.checks.items():
                if are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QtWidgets.QDirModel.setData(self, index, value, role)

    def exportChecked(self, acceptedSuffix=['jpg', 'png', 'bmp']):
        selection=set()
        for index in self.checks.keys():
            if self.checks[index] == QtCore.Qt.Checked:
                for path, dirs, files in os.walk(self.filePath(index)):
                    for filename in files:
                        if QtCore.QFileInfo(filename).completeSuffix().toLower() in acceptedSuffix:
                            if self.checkState(self.index(os.path.join(path, filename))) == QtCore.Qt.Checked:
                                try:
                                    selection.add(os.path.join(path, filename))
                                except:
                                    pass
        return selection


# class MainWindows(QtWidgets.QWidget):
#
#     def __init__(self, parent=None):
#         super(MainWindows, self).__init__()
#         self.init_ui()
#
#     def init_ui(self):
#         self.b = CheckableDirModel()
#
#         h_box = QtWidgets.QHBoxLayout()
#         h_box.addStretch()
#         h_box.addWidget(self.b)
#
#         self.setLayout(h_box)
#         self.show()

app = QtWidgets.QApplication(sys.argv)

model = CheckableDirModel()
tree = QtWidgets.QTreeView()
tree.setModel(model)

tree.setAnimated(False)
tree.setIndentation(20)
tree.setSortingEnabled(True)

tree.setWindowTitle("Dir View")
tree.resize(640, 480)
tree.show()

sys.exit(app.exec_())
