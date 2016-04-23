from PySide import QtGui, QtCore
from glob import glob
import sys, os
import convert_to_fbx
import config
import multiprocessing as mp
import functools

class QListWidget(QtGui.QListView):
    item_checked = QtCore.Signal(str, bool)

    def __init__(self, items=[], parent=None):
        super(QListWidget, self).__init__(parent)
        self.item_count = 0
        self.renameEnabled = False
        self.item_list_model = None
        self.item_selection_model = None
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.createWidgets()
        for item in items:
            self.addItem(item)

    def createWidgets(self):
        self.item_list_model = QtGui.QStandardItemModel(self)
        self.item_list_model.setSortRole(QtCore.Qt.DisplayRole)
        self.item_list_model.dataChanged.connect(self.handleDataChange)
        self.setModel(self.item_list_model)
        self.item_selection_model = self.selectionModel()
        self.setMinimumHeight(60)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred))

    def handleDataChange(self, *args):
        item = self.item_list_model.item(args[0].row())
        self.item_checked.emit(item.data(QtCore.Qt.DisplayRole), True if item.checkState() == QtCore.Qt.Checked else False)


    def getSelection(self):
        try:
            selection = self.item_selection_model.selection().indexes()[0].row()
        except IndexError:
            selection = -1
        return selection

    def removeItem(self, index):
        self.item_list_model.takeRow(index)
        self.item_count -= 1

    def clear(self):
        while self.item_count:
            self.removeItem(0)

    def addItem(self, mitem, data=None, checked=False):
        item = QtGui.QStandardItem()
        item.setData(mitem, QtCore.Qt.DisplayRole)
        if data is not None:
            item.setData(data, QtCore.Qt.UserRole)
        item.setEditable(self.renameEnabled)
        item.setDropEnabled(False)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.Unchecked if not checked else QtCore.Qt.Checked)
        # Can be used to store data linked to the name
        # item.setData(customData, QtCore.Qt.UserRole)
        self.item_list_model.appendRow(item)
        self.item_count += 1

    def addItems(self, items, data=None, checked=None):
        if checked is None:
            checked = [False] * len(items)
        if data is None:
            data = [None] * len(items)
        for item, check in zip(items, checked):
            self.addItem(item, data, checked=check)

    def setUserSelection(self, index):
        if self.item_count > 0:
            self.setCurrentIndex(self.item_list_model.item(index).index())
            self.selectedItem = self.getItem(index)

    def getItems(self):
        return [self.getItem(i) for i in xrange(0, self.item_count)]

    def getItem(self, index):
        item = self.item_list_model.item(index)
        return (str(item.data(QtCore.Qt.DisplayRole)),
                str(item.data(QtCore.Qt.UserRole)[0]),
                True if item.checkState() == QtCore.Qt.Checked else False)


class FBXConvertGUI(QtGui.QWidget):
    def __init__(self):
        super(FBXConvertGUI, self).__init__()
        self.setWindowTitle('Tilt Brush FBX Conversion')
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(450, 400)
        self.createWidgets()
        self.createConenctions()
        self.updateList()

    def createWidgets(self):
        mainVLayout = QtGui.QVBoxLayout()

        fileFLayout = QtGui.QFormLayout()

        self.exportPath = QtGui.QLineEdit(self)
        self.exportPath.setText(config.tiltBrushExportDir)
        fileFLayout.addRow('Exported Files path: ', self.exportPath)
        self.outputPath = QtGui.QLineEdit(self)
        self.outputPath.setText(config.tiltBrushExportDir)
        fileFLayout.addRow('Output path: ', self.outputPath)

        mainVLayout.addLayout(fileFLayout)

        self.updateListButton = QtGui.QPushButton(self)
        self.updateListButton.setText("Update List")

        mainVLayout.addWidget(self.updateListButton)

        optionsHLayout = QtGui.QHBoxLayout()

        optionsFLayout1 = QtGui.QFormLayout()
        self.add_backface = QtGui.QCheckBox(self)
        optionsFLayout1.addRow("Add Backface: ", self.add_backface)
        self.weld_verts = QtGui.QCheckBox(self)
        optionsFLayout1.addRow("Weld Vertices: ", self.weld_verts)

        optionsFLayout2 = QtGui.QFormLayout()
        self.merge_stroke = QtGui.QCheckBox(self)
        optionsFLayout2.addRow("Merge Strokes: ", self.merge_stroke)
        self.merge_brush = QtGui.QCheckBox(self)
        self.merge_brush.setChecked(True)
        optionsFLayout2.addRow("Merge Brushes: ", self.merge_brush)

        optionsHLayout.addLayout(optionsFLayout1)
        optionsHLayout.addLayout(optionsFLayout2)

        mainVLayout.addLayout(optionsHLayout)

        listVLayout = QtGui.QVBoxLayout()

        listVLayout.addWidget(QtGui.QLabel('Exported Files:'))

        self.jsonFiles = QListWidget(parent=self)

        listVLayout.addWidget(self.jsonFiles)

        mainVLayout.addLayout(listVLayout)

        self.convertButton = QtGui.QPushButton(self)
        self.convertButton.setText('Convert')
    
        mainVLayout.addWidget(self.convertButton)

        self.setLayout(mainVLayout)

    def createConenctions(self):
        self.updateListButton.pressed.connect(self.updateList)
        self.convertButton.pressed.connect(self.convertFiles)

    def updateList(self):
        paths = map(str, glob(os.path.join(self.exportPath.text().strip(), '*.json')))
        fileNames = [x.rsplit('\\', 1)[-1][:-5] for x in paths]
        self.jsonFiles.addItems(fileNames, paths, checked=[False] * len(fileNames))

    def convertFiles(self):
        files = [x for x in self.jsonFiles.getItems() if x[2] is True]
        outPath = self.exportPath.text().strip() if not len(self.outputPath.text().strip()) else self.outputPath.text().strip()
        if not os.path.exists(outPath):
            os.mkdir(outPath)
        parPool = mp.Pool(mp.cpu_count() - 1)
        inFiles = [file[1] for file in files]
        outFiles = [os.path.join(outPath, file[0] + '.fbx') for file in files]
        parPool.map_async(functools.partial(convert_to_fbx.convertFile,
                                            add_backface=self.add_backface.isChecked(),
                                            merge_stroke=self.merge_stroke.isChecked(),
                                            merge_brush=self.merge_brush.isChecked(),
                                            weld_verts=self.weld_verts.isChecked()), zip(inFiles, outFiles))

def run(type):
    app = QtGui.QApplication(sys.argv)
    if type == 'FBX':
        FBXGui = FBXConvertGUI()
        FBXGui.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    run('FBX')
