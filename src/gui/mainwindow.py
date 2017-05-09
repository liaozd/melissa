import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog

from src.utils.path import get_root_path

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


class XmlDragList(QtWidgets.QListWidget):
    dropped = pyqtSignal(list, name="dropped")

    def __init__(self, type, parent=None):
        super(XmlDragList, self).__init__(parent)
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


class MainWindows(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainWindows, self).__init__()

        # folder tree view on the left
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

        # XML file list view on the right
        self.xml_list_view = XmlDragList(self)
        add_xml_button = QtWidgets.QPushButton("&Add XML File")
        add_xml_button.clicked.connect(self.add_xml)
        remove_xml_button = QtWidgets.QPushButton("&Remove")
        remove_xml_button.clicked.connect(self.remove_xml)
        h_xml_button_box = QtWidgets.QHBoxLayout()
        h_xml_button_box.addWidget(add_xml_button)
        h_xml_button_box.addWidget(remove_xml_button)

        v_xml_box = QtWidgets.QVBoxLayout()
        v_xml_box.addWidget(self.xml_list_view)
        v_xml_box.addLayout(h_xml_button_box)

        v_xml_box.addStretch()

        # input box
        h_input_box = QtWidgets.QHBoxLayout()
        h_input_box.addLayout(v_folder_box)
        h_input_box.addLayout(v_xml_box)

        # main box
        v_main_box = QtWidgets.QVBoxLayout()
        v_main_box.addLayout(h_input_box)
        self.result_list_widget = QtWidgets.QListWidget()
        v_main_box.addWidget(self.result_list_widget)
        self.setLayout(v_main_box)
        self.show()

    def confirm_xml(self):
        movie_files = self.folder_model.export_checked()
        movie_files_on_timeline = self.load_xml_contents()

    def load_xml_contents(self):
        xml_files = []
        for index in range(self.xml_list_view.count()):
            xml_files.append(self.xml_list_view.item(index))
        return xml_files

    def add_xml(self):
        xml_files, _ = QFileDialog.getOpenFileNames(self, "Open File", get_root_path(), "xml Files (*.xml)")
        if xml_files:
            for each_file in xml_files:
                self.xml_list_view.addItem(each_file)

    def remove_xml(self):
        row = self.xml_list_view.currentRow()
        item = self.xml_list_view.item(row)
        if item is None:
            return
        item = self.xml_list_view.takeItem(row)
        del item

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindows()
    window.resize(1000, 600)
    sys.exit(app.exec_())
