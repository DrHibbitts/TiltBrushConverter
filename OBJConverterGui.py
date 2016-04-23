from PySide import QtGui, QtCore
import multiprocessing as mp
import functools
import sys, os
from glob import glob
import config
import convert_to_obj
from CustomQtWidgets import QListWidget

class OBJConvertGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OBJConvertGUI, self).__init__(parent)
        self.setWindowTitle('Tilt Brush OBJ Conversion')
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

        optionsFLayout = QtGui.QFormLayout()

        self.cooked = QtGui.QCheckBox(self)
        self.cooked.setChecked(True)
        optionsFLayout.addRow("Cook meshes: ", self.cooked)

        mainVLayout.addLayout(optionsFLayout)

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
        outFiles = [os.path.join(outPath, file[0] + '.obj') for file in files]
        progressBar = QtGui.QProgressDialog("Converting Files...", "Cancel", 0, len(outFiles), self)
        progressBar.setWindowModality(QtCore.Qt.WindowModal)
        progressBar.show()
        for i, _ in enumerate(parPool.imap_unordered(functools.partial(convert_to_obj.convertFile,
                                                                       cooked=self.cooked.isChecked()),
                                                     zip(inFiles, outFiles))):
            progressBar.setValue(i)
        progressBar.setValue(len(outFiles))

def main():
    app = QtGui.QApplication(sys.argv)
    OBJGui = OBJConvertGUI()
    OBJGui.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    main()