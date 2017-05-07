import sys, os

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

CLIP_FILTER = ['mov']


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

    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i in list(self.checks):
                if self.are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True
        return QtWidgets.QDirModel.setData(self, index, value, role)

    def export_checked(self, accepted_suffix=CLIP_FILTER):
        selection = set()
        for index in self.checks.keys():
            if self.checks[index] == QtCore.Qt.Checked:
                for path, dirs, files in os.walk(self.filePath(index)):
                    for filename in files:
                        if QtCore.QFileInfo(filename).completeSuffix().lower() in accepted_suffix:
                            if self.checkState(self.index(os.path.join(path, filename))) == QtCore.Qt.Checked:
                                try:
                                    selection.add(os.path.join(path, filename))
                                except:
                                    pass
        return selection

    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked

    @staticmethod
    def are_parent_and_child(parent, child):
        while child.isValid():
            if child == parent:
                return True
            child = child.parent()
        return False


class XmlDragListView(QtWidgets.QListWidget):
    dropped = pyqtSignal(list, name="dropped")

    def __init__(self, type, parent=None):
        super(XmlDragListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(72, 72))
        self.dropped.connect(self.pictureDropped)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            event.ignore()

    def pictureDropped(self, l):
        for url in l:
            if os.path.exists(url):
                print(url)
                icon = QtGui.QIcon(url)
                pixmap = icon.pixmap(72, 72)
                icon = QtGui.QIcon(pixmap)
                item = QtWidgets.QListWidgetItem(url, self)
                item.setIcon(icon)
                item.setStatusTip(url)


class MainWindows(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindows, self).__init__()

        # Folder view on left
        self.folder_model = CheckableDirModel()
        self.folder_view = QtWidgets.QTreeView()
        self.folder_view.setModel(self.folder_model)
        self.folder_view.setAnimated(False)
        self.folder_view.setIndentation(20)
        self.folder_view.setSortingEnabled(True)
        self.folder_view.setColumnWidth(0, 500)
        self.folder_view.setColumnHidden(2, True)

        self.scan_button = QtWidgets.QPushButton("Scan Folders")
        self.scan_button.clicked.connect(self.confirm_xml)

        v_folder_box = QtWidgets.QVBoxLayout()
        v_folder_box.addWidget(self.folder_view)
        v_folder_box.addWidget(self.scan_button)

        # XML file list view on right
        self.xml_list_view = XmlDragListView(self)
        v_xml_box = QtWidgets.QVBoxLayout()
        v_xml_box.addWidget(self.xml_list_view)
        v_xml_box.addStretch()

        # Main box
        h_box = QtWidgets.QHBoxLayout()
        h_box.addLayout(v_folder_box)
        h_box.addLayout(v_xml_box)
        self.setLayout(h_box)
        self.show()

    def confirm_xml(self):
        print(self.folder_model.export_checked())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindows()
    window.resize(800, 600)
    sys.exit(app.exec_())
