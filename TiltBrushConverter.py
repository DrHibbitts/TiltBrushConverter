from PySide import QtGui, QtCore
import sys

class ConversionTypeSelection(QtGui.QWidget):
    def __init__(self):
        super(ConversionTypeSelection, self).__init__()
        self.setWindowTitle('Tilt Brush Converter')
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(450, 400)
        self.createWidgets()
        self.createConnections()

    def createWidgets(self):
        mainVLayout = QtGui.QVBoxLayout()
        self.objButton = QtGui.QPushButton(self)
        self.objButton.setText("Convert to OBJ")
        self.fbxButton = QtGui.QPushButton(self)
        self.fbxButton.setText("Convert to FBX")
        mainVLayout.addWidget(self.objButton)
        mainVLayout.addWidget(self.fbxButton)
        self.setLayout(mainVLayout)

    def createConnections(self):
        self.objButton.pressed.connect(self.convertOBJs)
        self.fbxButton.pressed.connect(self.convertFBXs)

    def convertOBJs(self):
        import OBJConverterGui
        objGUI = OBJConverterGui.OBJConvertGUI(self)
        objGUI.show()

    def convertFBXs(self):
        import FBXConverterGui
        fbxGUI = FBXConverterGui.FBXConvertGUI(self)
        fbxGUI.show()


def main():
    app = QtGui.QApplication(sys.argv)
    OBJGui = ConversionTypeSelection()
    OBJGui.show()
    app.exec_()
    sys.exit()


if __name__ == '__main__':
    main()