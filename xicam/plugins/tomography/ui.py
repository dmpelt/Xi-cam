from PySide import QtCore, QtGui
from PySide.QtUiTools import QUiLoader
import pyqtgraph as pg
from pyqtgraph import parametertree as pt
import toolbar as ttoolbar
import fdata
import fmanager

blankform = None
propertytable = None
configparams = None
paramformstack = None
functionwidget = None
centerwidget = None


class funcAction(QtGui.QAction):
    def __init__(self, func, subfunc, *args,**kwargs):
        super(funcAction, self).__init__(*args,**kwargs)
        self.func=func
        self.subfunc=subfunc
        self.triggered.connect(self.addFunction)
    def addFunction(self):
        fmanager.add_action(self.func, self.subfunc)


def loadUi():
    global blankform, propertytable, configparams, functionwidget, paramformstack, centerwidget

    toolbar = ttoolbar.tomotoolbar()

    centerwidget = QtGui.QTabWidget()

    centerwidget.setDocumentMode(True)
    centerwidget.setTabsClosable(True)

    bottomwidget = None

    # Load the gui from file
    functionwidget = QUiLoader().load('gui/tomographyleft.ui')

    functionwidget.clearButton.clicked.connect(fmanager.clear_action)
    functionwidget.moveUpButton.clicked.connect(
        lambda: fmanager.swap_functions(fmanager.currentindex,
                                        fmanager.currentindex - 1))
    functionwidget.moveDownButton.clicked.connect(
        lambda: fmanager.swap_functions(fmanager.currentindex,
                                        fmanager.currentindex + 1))

    addfunctionmenu = QtGui.QMenu()
    for func,subfuncs in fdata.funcs.iteritems():
        if len(subfuncs)>1 or func != subfuncs[0]:
            funcmenu = QtGui.QMenu(func)
            addfunctionmenu.addMenu(funcmenu)
            for subfunc in subfuncs:
                if isinstance(subfuncs, dict) and len(subfuncs[subfunc]) > 0:
                    optsmenu = QtGui.QMenu(subfunc)
                    funcmenu.addMenu(optsmenu)
                    for opt in subfuncs[subfunc]:
                        funcaction = funcAction(func, opt, opt, funcmenu)
                        optsmenu.addAction(funcaction)
                else:
                    funcaction=funcAction(func,subfunc,subfunc,funcmenu)
                    funcmenu.addAction(funcaction)
        elif len(subfuncs)==1:
            funcaction=funcAction(func,func,func,addfunctionmenu)
            addfunctionmenu.addAction(funcaction)

    functionwidget.addFunctionButton.setMenu(addfunctionmenu)
    functionwidget.addFunctionButton.setPopupMode(QtGui.QToolButton.ToolButtonPopupMode.InstantPopup)
    functionwidget.addFunctionButton.setArrowType(QtCore.Qt.NoArrow)

    filefuncmenu = QtGui.QMenu()
    openaction = QtGui.QAction(filefuncmenu)
    openaction.triggered.connect(fmanager.open_pipeline_file)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("gui/open_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    openaction.setIcon(icon)
    saveaction = QtGui.QAction(filefuncmenu)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("gui/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    saveaction.setIcon(icon)
    refreshaction = QtGui.QAction(filefuncmenu)
    refreshaction.triggered.connect(lambda: fmanager.load_function_pipeline(
                                                           'xicam/plugins/tomography/yaml/functionstack.yml'))
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("gui/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    refreshaction.setIcon(icon)
    filefuncmenu.addActions([openaction, saveaction, refreshaction])

    functionwidget.fileButton.setMenu(filefuncmenu)
    functionwidget.fileButton.setPopupMode(QtGui.QToolButton.ToolButtonPopupMode.InstantPopup)
    functionwidget.fileButton.setArrowType(QtCore.Qt.NoArrow)

    leftwidget = QtGui.QWidget()

    l = QtGui.QVBoxLayout()
    l.setContentsMargins(0, 0, 0, 0)

    paramtree = pt.ParameterTree()
    paramformstack = QtGui.QStackedWidget()
    paramformstack.addWidget(paramtree)
    paramformstack.setFixedHeight(160)
    l.addWidget(paramformstack)
    l.addWidget(functionwidget)

    leftwidget.setLayout(l)

    rightwidget = QtGui.QSplitter(QtCore.Qt.Vertical)

    configtree = pt.ParameterTree()
    configtree.setMinimumHeight(230)
    params = [{'name': 'Rotation Center', 'type': 'float', 'value': 0, 'default': 0, 'suffix':'px'},
              {'name': 'Rotation Angle', 'type': 'float', 'value':0, 'default': 0, 'suffix':u'\u00b0'},
              {'name': 'Recon Rotation', 'type': 'float', 'value': 0, 'default': 0, 'suffix': u'\u00b0'},
              {'name': 'Notes', 'type': 'text', 'value': ''}]
    configparams = pt.Parameter.create(name='Configuration', type='group', children=params)
    configtree.setParameters(configparams, showTop=False)
    rightwidget.addWidget(configtree)

    propertytable = pg.TableWidget() #QtGui.QTableView()
    propertytable.verticalHeader().hide()
    propertytable.horizontalHeader().setStretchLastSection(True)
    propertytable.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)

    rightwidget.addWidget(propertytable)
    # rightwidget.setLayout(l)
    propertytable.hide()


    blankform = QtGui.QLabel('Select a function from\n below to set parameters...')
    blankform.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
    blankform.setAlignment(QtCore.Qt.AlignCenter)
    showform(blankform)

    return leftwidget, centerwidget, rightwidget, bottomwidget, toolbar


def showform(widget):
    paramformstack.addWidget(widget)
    paramformstack.setCurrentWidget(widget)
