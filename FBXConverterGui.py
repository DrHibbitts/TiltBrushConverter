from PySide import QtGui, QtCore
from glob import glob
import sys, os
import convert_to_fbx
import config
import multiprocessing as mp
import functools
from CustomQtWidgets import QListWidget

class FBXConvertGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FBXConvertGUI, self).__init__(parent)
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
        self.jsonFiles.clear()
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

def main():
    app = QtGui.QApplication(sys.argv)
    FBXGui = FBXConvertGUI()
    FBXGui.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    main()
