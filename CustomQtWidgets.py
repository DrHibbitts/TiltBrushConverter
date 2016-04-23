from PySide import QtCore, QtGui

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
