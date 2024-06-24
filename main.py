"""
Universal Workflow Language Interface.

Created on Wed Mar  8 10:49:22 2023

adapted from eyllanesc

@author: repps

"""
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QMenu,
                             QMenuBar,
                             QAction,
                             QFileDialog,
                             QMessageBox,
                             QTreeWidget,
                             QToolBar,
                             QLabel,
                             QTreeWidgetItem,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QTextEdit,
                             QTabWidget,
                             QTableWidget,
                             QTableWidgetItem,
                             QGraphicsView,
                             QSizePolicy,
                             QLineEdit,
                             QSpacerItem,
                             QGraphicsScene,
                             QGraphicsRectItem,
                             QGraphicsEllipseItem,
                             QGraphicsItem,
                             QPushButton,
                             QGraphicsSimpleTextItem,
                             QGraphicsLineItem,
                             QCompleter,
                             QCheckBox,
                             QComboBox,
                             QScrollArea
                             )
from PyQt5.QtCore import (Qt,
                          QEventLoop,
                          QSize,
                          QRectF,
                          QPoint,
                          QLineF
                          )
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import (QPen,
                         QFont,
                         QFontMetrics,
                         QPainter,
                         QColor,
                         QPixmap,
                         QIcon,
                         QCursor
                         )
import qdarktheme
import os
import copy
import pandas as pd
import json
import dill as pickle
import sip
import ctypes
import plaintextdictionary


def savejson(entry, filepath):
    """
    Save dictionary as .json file.

    Parameters
    ----------
    entry : dict
    filepath : str

    """
    with open(filepath, 'w') as outfile:
        json.dump(entry, outfile)


def loadjson(filepath):
    """
    Import .json file as dictionary.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict

    """
    with open(filepath) as loadfile:
        data = json.load(loadfile)
        return data


def loadpickle(filepath):
    """
    Import .pkl file as a dictionary.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict

    """
    with open(filepath, 'rb') as loadfile:
        data = pickle.load(loadfile)
        return data


filepath = 'preprocessing//multilingual_dict.pkl'
babelFish = loadpickle(filepath)


class WindowClass(QMainWindow):
    """Primary interface widget and root parent for all widgets."""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.dict = plaintextdictionary.loadDictionary()
        self.setWindowTitle(
            'Universal Workflow Language Interface - ver. 0.0.0')
        self.baseFeatures = []
        self.clipboard = {'ID': 'root',
                          'Links': [],
                          'position': [0, 0],
                          'Objects': {},
                          'language': 'en'}
        self.lankey = 'en'
        self.tabCtrl = TabViewController(
            parent=self, rootwindow=self, lankey=self.lankey)
        self.setCentralWidget(self.tabCtrl)
        self.setAcceptDrops(True)
        self._createMenuBar()
        self._createToolBars()
        self.filename = -1

    def dragEnterEvent(self, event):
        """
        Intercept dragEnterEvent and evaluate if a valid file is selected.

        Event is used for drag and drop file open functionality.

        Parameters
        ----------
        event : QEvent
            dragEnterEvent caught from MainWindow

        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Intercept dropEvent and open file if .json.

        Event is used for drag and drop file open functionality.

        Parameters
        ----------
        event : QEvent

        """
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        filenames = []
        for f in files:
            if os.path.splitext(f)[-1] == '.json':
                filenames.append(f)
        if filenames != []:
            self.onOpen(filenames)

    def _createMenuBar(self):
        """Build tool menus for File, Edit, Insert, Language, and Help."""
        self.menubar = QMenuBar(self)

        self.buildFileMenu()
        self.buildEditMenu()
        self.buildInsertMenu()
        self.buildLanguageMenu()
        self.buildHelpMenu()

        self.menubar.addMenu(self.filemenu)
        self.menubar.addMenu(self.editmenu)
        self.menubar.addMenu(self.insertmenu)
        self.menubar.addMenu(self.langmenu)
        self.menubar.addMenu(self.helpmenu)
        self.setMenuBar(self.menubar)

    def buildHelpMenu(self):
        """Build feedback, tutorial, and controls actions in help menu."""
        self.helpmenu = QMenu('Help', self)

        self.feedbackMenu = QMenu('Feedback', self)

        feedbacktxt = "Provide feedback, report bugs, or get involved with the"
        feedbacktxt += " project, at https://github.com/NREL/"
        feedbacktxt += "Universal-Workflow-Language-Interface"
        self.feedbackAction = QAction(feedbacktxt)
        self.feedbackMenu.addAction(self.feedbackAction)

        self.buildControlsAction()
        self.buildTutorialAction()

        self.helpmenu.addAction(self.tutorialAction)
        self.helpmenu.addAction(self.controlsAction)
        self.helpmenu.addMenu(self.feedbackMenu)

    def buildControlsAction(self):
        """Build controls option widget to launch controls window."""
        self.controlsAction = QAction('Controls', self)
        self.controlsAction.triggered.connect(self.openControlsWindow)

    def openControlsWindow(self):
        """Create and launch window displaying controls information."""
        self.controlsprompt = QScrollArea()
        self.controlsprompt.setWindowTitle('Interface Controls')
        # TODO: Add multilingual support.
        controlstxt = """
        Workflow View Navigation
            Pan Up - < Up Arrow > or < Scroll Down .
            Pan Down - < Down Arrow > or < Scroll Up >
            Pan Left - < Left Arrow > or < Alt + Scroll Down >
            Pan Right - < Right Arrow > or < Alt + Scroll Up >
            Faster Pan - < Shift + Command >
            Zoom In - < Ctrl + Scroll Down >
            Zoom Out - < Ctrl + Scroll Up >

        File Management
            New File - File >> New or < Ctrl + N >
            Open File - File >> Open or < Ctrl + O >
            Save File - File >> Save or < Ctrl + S >
            Save File as - File >> Save as or < Ctrl + Shift + S >

        Block Placing
            Place Action Block - Right click and select or < Shift + D >
            Place Item Block - Right click and select or < Shift + F >
            Place Section Block - Right click and select or < Shift + G >
            Insert Blocks from File - Right click and select or < Ctrl + I >
            Insert Blocks from File as Section - Right click and select or < Ctrl + Shift + I >

        Block Connection (For all highlighted blocks)
            Add A-Type Connections - Right click and select or < Shift + 1 >
            Add B-Type Connections - Right click and select or < Shift + 2 >
            Add C-Type Connections - Right click and select or < Shift + 3 >

        Workflow Editing
            Copy - Edit >> Copy, Right click and select, or < Ctrl + C >
            Paste - Edit >> Paste, Right click and select, or < Ctrl + V >
            Select All - Edit >> Copy, Right click and select, or < Ctrl + A >
            Delete - Edit >> Delete, Right click and select, or < Delete >
            Move Blocks - Click and drag
            Highlight Blocks - Click and drag box or < Ctrl + Click >
        """

        font = QFont('Arial')
        font.setPointSize(10)

        textWidget = QLabel(controlstxt)
        textWidget.setFont(font)
        self.controlsprompt.setWidget(textWidget)
        self.controlsprompt.show()

    def buildTutorialAction(self):
        """Create tutorial window launch action on help menu."""
        self.tutorialAction = QAction('Tutorial', self)
        self.tutorialAction.triggered.connect(self.openTutorialWindow)

    def openTutorialWindow(self):
        """Open new window with TutorialWindow class."""
        self.tutorialWindow = TutorialWindow()
        self.tutorialWindow.show()

    def buildLanguageMenu(self):
        """Get translator method and create language menu."""
        self.langmenu = QMenu('Language', self)
        self.getLanguages()
        self.buildLangList()

    def getLanguages(self):
        """Generate list of supported languages and keys."""
        self.langmenucurrind = 7
        self.trimlangKeys = [key for key in babelFish['languages'].keys()]
        self.languagelistall = [
            babelFish['languages'][key]['Menu label']
            for key in self.trimlangKeys]

    def buildLangList(self):
        """Add supported languages to Language menu bar."""
        self.langActions = []
        for ii, lang in enumerate(self.languagelistall):
            self.langActions.append(QAction(lang, self))
            self.langActions[ii].triggered.connect(self.updateLanguage)
            self.langmenu.addAction(self.langActions[ii])
        self.setSelectedLanguageMenu()

    def updateLanguage(self):
        """Update interface and UWLs with language clicked in menu bar."""
        clickedlanguage = self.sender().text()
        self.langmenucurrind = self.languagelistall.index(clickedlanguage)
        self.oldlankey = self.lankey
        self.lankey = self.trimlangKeys[self.langmenucurrind]
        self.updateLankeyThroughInterface()

        self.setSelectedLanguageMenu()
        self.applySelectedLanguageInterface()

        self.applySelectedLanguagetoWorkflows()

    def applySelectedLanguagetoWorkflows(self):
        """Change language in all workflows and update graphics displays."""
        c = 0
        while self.tabCtrl.workflowTab.widget(c) is not None:
            workflow = self.tabCtrl.workflowTab.widget(c).scene().mainEntry
            workflow['language'] = self.lankey
            self.tabCtrl.workflowTab.widget(c).scene().addBlocksEdgesFromData()
            c += 1

    def updateLankeyThroughInterface(self):
        """Update lankey attribute throughout child widgets."""
        self.tabCtrl.lankey = self.lankey

        self.tabCtrl.workflowTab.lankey = self.lankey
        for ind in range(self.tabCtrl.workflowTab.count()):
            self.tabCtrl.workflowTab.widget(ind).lankey = self.lankey
            self.tabCtrl.workflowTab.widget(ind).scene().lankey = self.lankey
            self.tabCtrl.workflowTab.widget(
                ind).scene().mainEntry['language'] = self.lankey

        self.tabCtrl.tableTab.lankey = self.lankey

        self.tabCtrl.plainTextTab.lankey = self.lankey

        self.tabCtrl.rawTextTab.laneky = self.lankey

    def setSelectedLanguageMenu(self):
        """Remove check from all menu languages. Add check for selected."""
        for action in self.langActions:
            action.setCheckable(False)
            action.setChecked(False)

        self.langActions[self.langmenucurrind].setCheckable(True)
        self.langActions[self.langmenucurrind].setChecked(True)

    def applySelectedLanguageInterface(self):
        """Get all interface text and translate to selected language."""
        self.getInterfaceWidgetsText()
        translatedInterfaceText = babelFish['ui'][self.lankey]['widgets']
        self.changeInterfaceWidgetsText(translatedInterfaceText)
        self.updateBase()

    def getInterfaceWidgetsText(self):
        """
        Build lists of all interface text and widgets.

        Method called in language preprocessing script.

        """
        self.allwidgets, self.allwidgetstext = [], []
        self.getInterfaceWidgetsMenus()
        self.getInterfaceWidgetsTabs()
        self.getInterfaceWidgetsTools()

    def getInterfaceWidgetsMenus(self):
        """Append all widgets and text in menu bar to full translate list."""
        langmenucounter = 0
        for child in self.menubar.actions():
            if str(type(child)) == "<class 'PyQt5.QtWidgets.QAction'>":
                langmenucounter += 1
                self.allwidgets.append(child)
                self.allwidgetstext.append(child.text())

                if langmenucounter == 4:
                    continue
                for subchild in child.menu().actions():
                    if str(type(child)) == "<class 'PyQt5.QtWidgets.QAction'>":
                        self.allwidgets.append(subchild)
                        self.allwidgetstext.append(subchild.text())
                        if subchild.menu() is not None:
                            subsubchild = subchild.menu().actions()[0]
                            self.allwidgets.append(subsubchild)
                            self.allwidgetstext.append(subsubchild.text())

    def getInterfaceWidgetsTabs(self):
        """Append all widgets and text in main tab view to full widget list."""
        tabcount = self.centralWidget().count()
        for tab_ii in range(tabcount):
            child = self.centralWidget().widget(tab_ii)
            self.allwidgets.append(child)
            self.allwidgetstext.append(child.parent.tabText(tab_ii))

    def getInterfaceWidgetsTools(self):
        """Append all widgets and text in tool bars to full widget list."""
        for childlayout in self.layout.children():
            for ii in range(childlayout.count()):
                child = childlayout.itemAt(ii).widget()
                if str(type(child)) == "<class 'PyQt5.QtWidgets.QLabel'>":
                    self.allwidgets.append(child)
                    self.allwidgetstext.append(child.text())

        for child in self.children():
            if str(type(child)) == "<class 'PyQt5.QtWidgets.QToolBar'>":
                self.allwidgets.append(child)
                self.allwidgetstext.append(child.windowTitle())

    def changeInterfaceWidgetsText(self, textlist):
        """Translate all widget text in full widget list to new language."""
        tab_widget_strs = ["<class '__main__.TabWorkflowController'>",
                           "<class '__main__.TabTableController'>",
                           "<class '__main__.TabPlaintextController'>",
                           "<class '__main__.TabRawController'>"]

        type1_widget_strs = ["<class 'PyQt5.QtWidgets.QAction'>",
                             "<class 'PyQt5.QtWidgets.QLabel'>"]

        for ii, widget in enumerate(self.allwidgets):
            widget_str = str(type(widget))
            if widget_str in type1_widget_strs:
                widget.setText(textlist[ii])
            elif widget_str in tab_widget_strs:
                widget.parent.setTabText(widget.tabind, textlist[ii])
            elif widget_str == "<class 'PyQt5.QtWidgets.QToolBar'>":
                widget.setWindowTitle(textlist[ii])

    def buildFileMenu(self):
        """Add all file menu actions to menu and connect to functions."""
        self.filemenu = QMenu('File', self)

        self.newAction = QAction('New', self)
        self.newAction.setShortcut('Ctrl+N')
        self.newAction.triggered.connect(self.onNew)
        self.filemenu.addAction(self.newAction)

        self.openAction = QAction('Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.onOpen)
        self.filemenu.addAction(self.openAction)

        self.saveAction = QAction('Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.onSave)
        self.filemenu.addAction(self.saveAction)

        self.saveAsAction = QAction('Save As', self)
        self.saveAsAction.setShortcut('Ctrl+Shift+S')
        self.saveAsAction.triggered.connect(self.onSaveAs)
        self.filemenu.addAction(self.saveAsAction)

        self.testAction = QAction('Test Button', self)
        self.testAction.triggered.connect(self.testPrint)
        self.filemenu.addAction(self.testAction)

    def testPrint(self):
        """Print currently selected workflow for troubleshooting."""
        ii = self.centralWidget().widget(0).currentIndex()
        print(self.centralWidget().widget(0).widget(ii).scene().mainEntry)

    def onSaveAs(self):
        """
        Save current workflow as a copy through file dialog.

        Operation is connected to Ctrl+Shift+S hot key.

        """
        filename = QFileDialog.getSaveFileName(
            self, 'Save File', filter='*.json')
        if filename == ('', ''):  # Leave function if cancel button selected.
            return
        else:
            tabsWorkflows = self.centralWidget().widget(0)
            for ii in range(tabsWorkflows.count()):
                tabfile = self.centralWidget().widget(0).widget(
                    ii).scene().mainEntry['File']
                if filename[0] == tabfile:
                    self.centralWidget().widget(0).setCurrentIndex(ii)
                    self.errorFilepathAreadyOpen()
                    return
            self.filename = filename

        self.filename = self.filename[0]

        currTabInd = self.centralWidget().widget(0).currentIndex()
        copyEntry = copy.deepcopy(self.centralWidget().widget(0).widget(
            currTabInd).scene().mainEntry)  # Create copy of current workflow.

        self.createTab()

        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(
            currTabInd).scene().mainEntry = copyEntry  # Write to new workflow.

        self.centralWidget().widget(0).tabNameUpdate(self.filename,
                                                     currTabInd)
        self.centralWidget().widget(0).widget(
            currTabInd).scene().onSaveAs(self.filename)

        self.updateToolBars()
        self.centralWidget().updateCurrentTab()

        self.centralWidget().widget(0).setCurrentIndex(currTabInd)

    def onSave(self):
        """
        Save current workflow.

        Operation is connected to Ctrl+S hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        tabname = self.centralWidget().widget(0).tabText(currTabInd)
        if tabname == 'Untitled':
            filename = QFileDialog.getSaveFileName(
                self, 'Save File', filter='*.json')

            if filename == ('', ''):
                return
            else:
                tabsWorkflows = self.centralWidget().widget(0)
                for ii in range(tabsWorkflows.count()):
                    tabfile = self.centralWidget().widget(0).widget(
                        ii).scene().mainEntry['File']
                    if filename[0] == tabfile:
                        self.centralWidget().widget(0).setCurrentIndex(ii)
                        self.errorFilepathAreadyOpen()
                        return
                self.filename = filename

            self.filename = self.filename[0]
        else:
            self.filename = self.centralWidget().widget(0).widget(
                currTabInd).scene().mainEntry['File']

        currTabInd = self.centralWidget().widget(0).currentIndex()

        self.centralWidget().widget(0).widget(
            currTabInd).scene().onSave(self.filename)
        self.centralWidget().widget(0).tabNameUpdate(self.filename,
                                                     currTabInd)

        self.updateToolBars()
        self.centralWidget().updateCurrentTab()

    def onOpen(self, filenames=[]):
        """
        Open .jsons in filenames as workflow tabs.

        Operation supports multiple files at once and is connected to Ctrl+O
        hot key.

        Parameters
        ----------
        filenames : str, optional
            List of .json file name strings. The default is [].

        """
        if filenames is False:
            filenames = QFileDialog.getOpenFileNames(
                self, 'Open File', filter='*.json')
            filenames = filenames[0]
        if filenames == []:
            return
        else:
            for filename in filenames:
                self.filename = filename

                tabsWorkflows = self.centralWidget().widget(0)
                for ii in range(tabsWorkflows.count()):
                    tabfile = self.centralWidget().widget(0).widget(
                        ii).scene().mainEntry['File']

                    if tabfile == '':
                        fileAlreadyOpen = False
                    else:
                        print(filename, tabfile)
                        fileAlreadyOpen = os.path.samefile(filename, tabfile)

                    if fileAlreadyOpen:
                        self.centralWidget().widget(0).setCurrentIndex(ii)
                        return

                self.createTab()

                currTabInd = self.centralWidget().widget(0).currentIndex()

                self.centralWidget().widget(0).widget(
                    currTabInd).scene().onOpen(self.filename)
                self.centralWidget().widget(0).tabNameUpdate(
                    self.filename, currTabInd)

                self.updateToolBars()
            self.centralWidget().updateCurrentTab()

    def createTab(self):
        """Create a new, 'Untitled' tab next to the currently selected tab."""
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).addNewTab(currTabInd)
        self.updateToolBars()

    def onNew(self):
        """
        Create a new tab, set as selected, and update other data view tabs.

        Operation is connected to the Ctrl+N hot key.

        """
        self.createTab()
        self.centralWidget().subTabInd = self.centralWidget(
        ).widget(0).currentIndex()
        self.centralWidget().updateEntries()
        self.centralWidget().updateCurrentTab()

    def errorFilepathAreadyOpen(self):
        """Display error message if an already open file is selected."""
        # TODO: Message is currently intercepted by inbuilt error handling.
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(
            """
            The selected file path is already open. Select a different path or
            close the open tab before proceeding.
            """)
        msg.setWindowTitle("Error")
        msg.exec_()

    def buildEditMenu(self):
        """Add all edit menu actions to menu and connect to functions."""
        self.editmenu = QMenu('Edit', self)

        self.copyAction = QAction('Copy', self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.triggered.connect(self.onCopy)
        self.editmenu.addAction(self.copyAction)

        self.pasteAction = QAction('Paste', self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.triggered.connect(self.onPaste)
        self.editmenu.addAction(self.pasteAction)

        self.selectAllAction = QAction('Select All', self)
        self.selectAllAction.setShortcut('Ctrl+A')
        self.selectAllAction.triggered.connect(self.onSelectAll)
        self.editmenu.addAction(self.selectAllAction)

        self.delAction = QAction('Delete', self)
        self.delAction.triggered.connect(self.onDelete)
        self.editmenu.addAction(self.delAction)

    def onDelete(self):
        """Connect delete action to scene element delete function."""
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
            ).widget(0).widget(currTabInd).scene().runElementDelete()

    def onCopy(self):
        """
        Create a copy of the selected workflow segment in clipboard.

        Current copy operations are handled by scene method. Operations is
        connected to the Ctrl+C hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onCopyBlock()

    def onPaste(self):
        """
        Paste the clipboard workflow segment into the current workflow.

        Paste occurs at last recorded mouse location in the workflow. Current
        paste operations are handled by scene method. Operation is connected to
        the Ctrl+V hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
        ).widget(0).widget(currTabInd).scene().onPasteBlock()

    def onSelectAll(self):
        """
        Select all objects in the current workflow.

        Select all operations are handled by the scene method. Operation is
        connected to the Ctrl+A hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onSelectAll()

    def buildInsertMenu(self):
        """Add all insert menu actions to menu and connect to functions."""
        self.insertmenu = QMenu('Insert', self)

        self.actionAction = QAction('Create Action Block', self)
        self.actionAction.setShortcut('Shift+D')
        self.actionAction.triggered.connect(self.onAddAction)
        self.insertmenu.addAction(self.actionAction)

        self.itemAction = QAction('Create Item Block', self)
        self.itemAction.setShortcut('Shift+F')
        self.itemAction.triggered.connect(self.onAddItem)
        self.insertmenu.addAction(self.itemAction)

        self.sectionAction = QAction('Create Section Block', self)
        self.sectionAction.setShortcut('Shift+G')
        self.sectionAction.triggered.connect(self.onSection)
        self.insertmenu.addAction(self.sectionAction)

        self.insertAction = QAction('Insert from File', self)
        self.insertAction.setShortcut('Ctrl+I')
        self.insertAction.triggered.connect(self.onLoad)
        self.insertmenu.addAction(self.insertAction)

        self.insertSectAction = QAction('Insert from File as Section', self)
        self.insertSectAction.setShortcut('Ctrl+Shift+I')
        self.insertSectAction.triggered.connect(self.onLoadasSection)
        self.insertmenu.addAction(self.insertSectAction)

        self.addAAction = QAction('Add A-Type Connections', self)
        self.addAAction.setShortcut('Shift+1')
        self.addAAction.triggered.connect(self.onAddAType)
        self.insertmenu.addAction(self.addAAction)

        self.addBAction = QAction('Add B-Type Connections', self)
        self.addBAction.setShortcut('Shift+2')
        self.addBAction.triggered.connect(self.onAddBType)
        self.insertmenu.addAction(self.addBAction)

        self.addCAction = QAction('Add C-Type Connections', self)
        self.addCAction.setShortcut('Shift+3')
        self.addCAction.triggered.connect(self.onAddCType)
        self.insertmenu.addAction(self.addCAction)

    def onAddAction(self, event):
        """
        Add action block to workflow at last mouse position.

        Operations are handled by scene method and are bound to Shift+D
        hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
        ).widget(0).widget(currTabInd).scene().onNewActionBlock()

    def onAddItem(self, event):
        """
        Add item block to workflow at last mouse position.

        Operations are handled by scene method and are bound to Shift+F
        hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
        ).widget(0).widget(currTabInd).scene().onNewItemBlock()

    def onSection(self, event):
        """
        Add section block to workflow at last mouse position.

        Operations are handled by scene method and are bound to Shift+G
        hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
        ).widget(0).widget(currTabInd).scene().onNewSection()

    def onAddAType(self):
        """
        Add an A type connection between all selected action and item blocks.

        Connections do not overwrite existing connections and can only be made
        between action and item blocks. Operations are handled by scene method
        and are bound to the Shift+1 hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onAddAType()

    def onAddBType(self):
        """
        Add an B type connection between all selected action and item blocks.

        Connections do not overwrite existing connections and can only be made
        between action and item blocks. Operations are handled by scene method
        and are bound to the Shift+2 hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onAddBType()

    def onAddCType(self):
        """
        Add an C type connection between all selected action and item blocks.

        Connections do not overwrite existing connections and can only be made
        between action and item blocks. Operations are handled by scene method
        and are bound to the Shift+3 hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onAddCType()

    def onLoad(self):
        """
        Load workflow from file and insert to workflow at mouse location.

        Launches file selection prompt and inserts file into workflow at last
        recorded mouse location. Operations are handled by scene methods and
        are bound to the Ctrl+I hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene().onLoadBlock()

    def onLoadasSection(self):
        """
        Load workflow and insert to workflow at mouse location as a section.

        Launches file selection prompt and inserts file into workflow at last
        recorded mouse location as a new section, title with the selected file
        name. Operations are handled by scene methods and are bound to the
        Ctrl+Shift+I hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget(
        ).widget(0).widget(currTabInd).scene().onLoadBlockasSection()

    def _createToolBars(self):
        """Build all movable tool bars on MainWindow."""
        filedirToolBar = QToolBar('File Directory', self)
        filedirToolBar.setFloatable(True)
        self.addToolBar(Qt.RightToolBarArea, filedirToolBar)
        self.dirTree = QTreeWidget()
        self.dirTree.itemDoubleClicked.connect(self.onTreeOpen)
        self.dirTree.setHeaderHidden(True)
        self.dirTree.clear()
        self.updateDirTree(os.getcwd(), self.dirTree)
        filedirToolBar.addWidget(self.dirTree)

        self.baseToolBar = QToolBar('Base Entry Features', self)
        self.baseToolBar.setFloatable(True)
        self.addToolBar(Qt.RightToolBarArea, self.baseToolBar)
        self.updateBase()

        self.actionContextToolBar = QToolBar('Action Context', self)
        self.actionContextToolBar.setFloatable(True)
        self.addToolBar(Qt.RightToolBarArea, self.actionContextToolBar)
        self.buildActionContext()

    def buildActionContext(self):
        """Construct blank label widget and add placeholder context."""
        self.contextLbl = QLabel(self.actionContextToolBar)
        self.updateContextText()

    def updateContextText(self, action=None):
        """
        Update context workflow tool with new action label.

        Action name and step statement text are generated then written on a
        blank workflow. Label widget is cleared before each text update.
        Function is called in block hover over event.

        Parameters
        ----------
        action : string, optional
            Action name to be added to context workflow. If None then
            placeholder values are used. The default is None.

        """
        self.contextLbl.clear()

        pixmap = QPixmap('Context//Blank_v1.png')
        
        try:
            if action is None:
                action = 'Action'
                step = 'Hover over a workflow action for context'
            else:
                if action in self.dict['Action']['Modify']:
                    func_ver = '02'
                else:
                    func_ver = '01'
                    
                func = babelFish['Action'][action][self.lankey]['Func'][func_ver]
                action = babelFish['Action'][action][self.lankey]['Name']
                step = func('A', 'B', 'C')
        except Exception as e:
            print(e)
            step = f"{action} is not listed."
            

        pen = QPen(QColor(255, 255, 255))
        font = QFont('Arial')
        font.setBold(True)
        font.setPointSize(10)

        fontMetric = QFontMetrics(font)
        actionTextWidth = fontMetric.width(action)
        stepTextWidth = fontMetric.width(step)

        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(136 - actionTextWidth // 2, 50, action)

        if stepTextWidth > 200:
            splitInd = step.index(' ', 20, len(step))
            step1 = step[:splitInd]
            step2 = step[splitInd+1:]
            stepTextWidth1 = fontMetric.width(step1)
            stepTextWidth2 = fontMetric.width(step2)
            painter.drawText(136 - stepTextWidth1 // 2, 240, step1)
            painter.drawText(136 - stepTextWidth2 // 2, 260, step2)
        else:
            painter.drawText(136 - stepTextWidth // 2, 250, step)
        painter.end()

        self.contextLbl.setPixmap(pixmap.scaled(
            QSize(270, 270), Qt.KeepAspectRatio))
        self.actionContextToolBar.addWidget(self.contextLbl)

    def updateDirTree(self, directory, parentTree):
        """Update directory tree tool with full file directory."""
        # TODO: Currently runs on main.py cwd. Add main directory navigation.
        for item in os.listdir(directory):
            tempPath = directory + '\\' + item
            if os.path.isdir(tempPath):
                parentItem = QTreeWidgetItem(
                    parentTree, [os.path.basename(item)])
                self.updateDirTree(tempPath, parentItem)
            elif os.path.splitext(tempPath)[-1] == '.json':
                parentItem = QTreeWidgetItem(
                    parentTree, [os.path.basename(item)])
                parentItem.filepath = tempPath

    def onTreeOpen(self, item):
        """
        Open file selected from tree directory tool.

        Method is connected to double click event on all tree directory items.

        """
        if item.childCount() == 0:
            self.onOpen([item.filepath])

    def updateBase(self):
        """Rebuild base information tool bar widgets from workflow."""
        if self.baseFeatures != []:
            self.baseToolBar.clear()
            sip.delete(self.baseFeatures)
            self.baseFeatures = None
        self.baseFeatures = QWidget()

        currTabInd = self.centralWidget().widget(0).currentIndex()
        if self.centralWidget().widget(0).widget(
                currTabInd) is None:
            return

        baseEntry = self.centralWidget().widget(0).widget(
            currTabInd).scene().mainEntry

        self.layout = QVBoxLayout()

        layoutName = QHBoxLayout()
        listind = babelFish['ui']['en']['widgets'].index('Entry Name: ')
        nameStr = babelFish['ui'][self.lankey]['widgets'][listind] + \
            baseEntry['Name']
        nameLabel = QLabel(nameStr)
        nameLabel.setWordWrap(True)
        layoutName.addWidget(nameLabel)
        self.layout.addLayout(layoutName)

        layoutFile = QHBoxLayout()
        listind = babelFish['ui']['en']['widgets'].index('File Path: ')
        fileStr = babelFish['ui'][self.lankey]['widgets'][listind] + \
            baseEntry['File']
        fileLabel = QLabel(fileStr)
        fileLabel.setWordWrap(True)
        layoutFile.addWidget(fileLabel)
        self.layout.addLayout(layoutFile)

        layoutDesc = QVBoxLayout()
        listind = babelFish['ui']['en']['widgets'].index(
            'Experiment Description:')
        descStr = babelFish['ui'][self.lankey]['widgets'][listind]
        descLabel = QLabel(descStr)
        layoutDesc.addWidget(descLabel)
        self.descWidget = QTextEdit()
        self.descWidget.setText(baseEntry['Description'])
        self.descWidget.textChanged.connect(self.updateEntryBase)
        layoutDesc.addWidget(self.descWidget)
        self.layout.addLayout(layoutDesc)

        self.baseFeatures.setLayout(self.layout)
        self.baseToolBar.addWidget(self.baseFeatures)

    def updateEntryBase(self):
        """Update workflow data from base information tool bar widget."""
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().widget(0).widget(currTabInd).scene(
        ).mainEntry['Description'] = self.descWidget.toPlainText()
        self.centralWidget().updateEntries()

    def updateToolBars(self):
        """Rebuild tool bars from current work flow data."""
        self.dirTree.clear()
        self.updateDirTree(os.getcwd(), self.dirTree)
        self.updateBase()
        self.updateEntryBase()


class TutorialWindow(QTabWidget):
    """Manage tutorial popup window."""

    def __init__(self):
        QTabWidget.__init__(self)

        self.filepath = 'tutorial'

        self.setWindowTitle('Tutorial')
        self.setTabPosition(QTabWidget.TabPosition.West)

        self.addQuickstart()

    def addQuickstart(self):
        """Build tab for quick start tutorial."""
        self.filepath_quickstart = self.filepath + '//quickstart'
        self.quickstartTab = QTabWidget()
        self.addQuickstartTabs()

        self.addTab(self.quickstartTab, 'Quick Start')

    def addQuickstartTabs(self):
        """Add step tabs to quick start tutorial."""
        for file in os.listdir(self.filepath_quickstart):
            if file.endswith('.png'):
                fullpath = os.path.join(self.filepath_quickstart, file)
                name = file[:-4]

                textpath = fullpath[:-4] + '.txt'

                with open(textpath, 'r') as file:
                    importedtext = file.read()

                layout = QVBoxLayout()

                font = QFont('Arial')
                font.setBold(True)
                font.setPointSize(10)
                lblwidget = QLabel(importedtext)
                lblwidget.setWordWrap(True)
                lblwidget.setFont(font)
                layout.addWidget(lblwidget)

                pixmap = QPixmap(fullpath)
                pixwidget = QLabel()
                pixwidget.setPixmap(pixmap)
                layout.addWidget(pixwidget)

                btnlayout = QHBoxLayout()

                btnleft = QPushButton(' < ')
                btnleft.clicked.connect(self.quickstartLeft)
                btnlayout.addWidget(btnleft)

                btnright = QPushButton(' > ')
                btnright.clicked.connect(self.quickstartRight)
                btnlayout.addWidget(btnright)

                layout.addLayout(btnlayout)

                widget = QWidget()
                widget.setLayout(layout)

                self.quickstartTab.addTab(widget, name)

    def quickstartLeft(self):
        """Move quick start tab position to the left."""
        currInd = self.quickstartTab.currentIndex()
        self.quickstartTab.setCurrentIndex(currInd - 1)

    def quickstartRight(self):
        """Move quick start tab position to the right."""
        currInd = self.quickstartTab.currentIndex()
        self.quickstartTab.setCurrentIndex(currInd + 1)


class TabViewController(QTabWidget):
    """Tab control widget for management of all four data view tabs."""

    def __init__(self, parent=None, rootwindow=None, lankey='en'):
        QTabWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        self.setTabPosition(QTabWidget.TabPosition.West)

        self.workflowTab = TabWorkflowController(
            parent=self, rootwindow=rootwindow, lankey=self.lankey)
        self.workflowTab.tabind = 0
        self.addTab(self.workflowTab, 'Workflows')

        self.tableTab = TabTableController(parent=self, lankey=self.lankey)
        self.tableTab.tabind = 1
        self.addTab(self.tableTab, 'Table')

        self.plainTextTab = TabPlaintextController(
            parent=self, lankey=self.lankey)
        self.plainTextTab.tabind = 2
        self.addTab(self.plainTextTab, 'Protocol')

        self.rawTextTab = TabRawController(parent=self, lankey=self.lankey)
        self.rawTextTab.tabind = 3
        self.addTab(self.rawTextTab, 'Raw')

        self.entries = []

        self.currentChanged.connect(self.onCurrentChanged)

        self.subTabInd = 0

    def onCurrentChanged(self):
        """Update all workflow data when a cell value is changed."""
        self.updateEntries()
        self.updateCurrentTab()

    def updateEntries(self):
        """Rebuild workflow data from workflows and distribute to all tabs."""
        self.entriesWorkflow = {}
        c = 0
        while self.workflowTab.widget(c) is not None:
            entryName = self.workflowTab.widget(c).scene(
            ).mainEntry['Name']

            self.entriesWorkflow[entryName] = self.workflowTab.widget(
                c).scene().mainEntry

            c = c + 1

        self.updateEntryTable()
        self.updateEntryText()

    def updateEntryText(self):
        """Update display data for plain text and raw data tabs."""
        self.plainTextTab.updateFromWorkflows(self.entriesWorkflow)
        self.rawTextTab.updateFromWorkflows(self.entriesWorkflow)

    def updateEntryTable(self):
        """Empty and rebuild all data in table controller."""
        self.tableTab.clear()
        self.buildTableNames()
        self.entriesTable = pd.DataFrame([], index=self.tableNames)
        self.addDatatoTable()
        self.tableTab.updateTable(self.entriesTable)
        self.tableTab.tabletoWorkflowIndex = self.tabletoWorkflowIndex

    def updateCurrentTab(self):
        """Set tabs to match current tab across data views."""
        self.workflowTab.setCurrentIndex(self.subTabInd)
        self.plainTextTab.setCurrentIndex(self.subTabInd)
        self.rawTextTab.setCurrentIndex(self.subTabInd)

    def buildTableNames(self):
        """Iterate through all work flows and add unique parameter names."""
        self.tableNames = []
        for entryID in self.entriesWorkflow.keys():
            self.entrynames = []
            entry = self.entriesWorkflow[entryID]
            self.addSectionTableNames(section=entry)

    def addSectionTableNames(self, section, prevSectName=''):
        """
        Add unique table names to tableNames class attribute.

        Iterate through all parameters within the action and item blocks of the
        current section or workflow and add the parameter with associated
        relationship branching to the tableNames class attribute if it does not
        already exist. If a section within the current section is found,
        recursively iterate through this function with the nested section.

        Parameters
        ----------
        section : dict
            Work flow or section object containing action and / or item blocks.
        prevSectName : str, optional
            Name of previous section within section nesting. Section name
            branches are labeled as [First Level] > [Second Level] > ... >
            [Previous Level]. The default is ''.

        """
        if section['Type'] == 'root':
            sectName = ''
        else:
            sectName = prevSectName + section['Name'] + ' > '

        for objKey in section['Objects'].keys():
            block = section['Objects'][objKey]
            if block['Type'] in ['Action', 'Item']:
                try:
                    blockName = babelFish[block['Type']
                                          ][block['Name']][self.lankey]['Name']
                except Exception as e:
                    print(e)
                    blockName = block['Name']
                blockName = blockName + ' > '
                if block['Type'] == 'Action':
                    actionMod = self.getActionModifier(section, block)
                else:
                    actionMod = ''

                for param in block['Parameters']:
                    try:
                        param_type = babelFish[block['Type'] + ' Parameter']
                        param = param_type[param][self.lankey]['Name']
                    except Exception as e:
                        print(e)
                        param = param

                    entryName = sectName + blockName + param + actionMod
                    entryName = self.fixEntryNameDuplicates(entryName)
                    if entryName not in self.tableNames:
                        self.tableNames.append(entryName)
            elif block['Type'] == 'Section':
                self.addSectionTableNames(section=block, prevSectName=sectName)

    def getActionModifier(self, section, block):
        """
        Return descriptive text for an action block.

        Action block modifier text is used to add context to an action block
        parameter. In most cases, action block names are not unique, so the
        modifier text will display next to the name to add specificity. For
        example:
            Add > Mass [Potassium chloride to beaker]

        Parameters
        ----------
        section : dict
            Work flow or section dictionary data.
        block : dict
            Dictionary data for an action block object.

        Returns
        -------
        actionMod : str
            Descriptive text to add context to action block parameters.

        """
        try:
            actionMod = ''
            if block['Subtype'] == 'Add':
                ABlockName = self.getConnectionBlockName(section, block, 'A')
                BBlockName = self.getConnectionBlockName(section, block, 'B')
                try:
                    ABlockName = babelFish[
                        'Item'][ABlockName][self.lankey]['Name']
                    BBlockName = babelFish[
                        'Item'][BBlockName][self.lankey]['Name']
                except Exception as e:
                    print(e)
                    pass
                actionMod = ' [' + BBlockName + ' to ' + ABlockName + '] '
            elif block['Subtype'] == 'Remove':
                ABlockName = self.getConnectionBlockName(section, block, 'A')
                BBlockName = self.getConnectionBlockName(section, block, 'B')
                try:
                    ABlockName = babelFish[
                        'Item'][ABlockName][self.lankey]['Name']
                    BBlockName = babelFish[
                        'Item'][BBlockName][self.lankey]['Name']
                except Exception as e:
                    print(e)
                    pass
                actionMod = ' [' + BBlockName + ' from ' + ABlockName + '] '
            elif block['Subtype'] == 'Modify':
                ABlockName = self.getConnectionBlockName(section, block, 'A')
                try:
                    ABlockName = babelFish[
                        'Item'][ABlockName][self.lankey]['Name']
                except Exception as e:
                    print(e)
                    pass
                actionMod = ' [' + ABlockName + '] '
        except Exception as e:
            print(e)
            actionMod = ''

        return actionMod

    def getConnectionBlockName(self, section, block, connectionType):
        """
        Return name of item block(s) connected to an action block.

        Parameters
        ----------
        section : dict
            Work flow or section dictionary data.
        block : dict
            Action block used to search for connections.
        connectionType : {'A','B','C'}
            Connection type to search from.

        Returns
        -------
        blockName : str
            Name(s) of item blocks connected to the action block through the
            specified type. Multiple items are separated in the string through
            the delimiter '/'.

        """
        inLabel = connectionType + ' In'
        inKeys = block[inLabel]
        blockName = ''
        for inKey in inKeys:
            blockName += section['Objects'][inKey]['Name'] + '/'
        if blockName != '':
            blockName = blockName[:-1]
        return blockName

    def addDatatoTable(self):
        """Add parameter values to table view column by column."""
        self.c = 0
        self.tabletoWorkflowIndex = []
        for entryID in self.entriesWorkflow.keys():
            self.entryID = entryID
            entry = self.entriesWorkflow[entryID]

            self.entrynames = []
            self.tempCol = []
            for ii in range(len(self.tableNames)):
                self.tempCol.append(None)

            self.addSectionDatatoCol(section=entry)

            self.entriesTable.insert(self.c, entryID, self.tempCol)
            self.c += 1

    def addSectionDatatoCol(self, section, prevSectName='', prevSectPath=[]):
        """
        Fill in table column data for the specified entry.

        Iterate through sections in the workflow and fill in data into the
        tempCol class attribute. Parameter names are constructed to mimic the
        format specified in addSectionTableNames method.

        Parameters
        ----------
        section : dict
            Work flow or section object containing action and / or item blocks.
        prevSectName : str, optional
            Name of previous section within section nesting. Section name
            branches are labeled as [First Level] > [Second Level] > ... >
            [Previous Level]. The default is ''.
        prevSectPath : list, optional
            List of previous section name strings within the current section
            branch path. The default is [].

        """
        if section['Type'] == 'root':
            sectName = ''
        else:
            sectName = prevSectName + section['Name'] + ' > '

        for objKey in section['Objects'].keys():
            block = section['Objects'][objKey]
            blockName = block['Name'] + ' > '
            if block['Type'] in ['Action', 'Item']:
                try:
                    blockName = babelFish[block['Type']
                                          ][block['Name']][self.lankey]['Name']
                except Exception as e:
                    print(e)
                    blockName = block['Name']
                blockName = blockName + ' > '

                for ii, param in enumerate(block['Parameters']):
                    val = block['Values'][ii]

                    try:
                        param_type = babelFish[block['Type'] + ' Parameter']
                        param = param_type[param][self.lankey]['Name']
                    except Exception as e:
                        print(e)
                        param = param

                    if block['Type'] == 'Action':
                        actionMod = self.getActionModifier(section, block)
                    else:
                        actionMod = ''

                    entryName = sectName + blockName + param + actionMod
                    entryName = self.fixEntryNameDuplicates(entryName)

                    iTab = self.entriesTable.index.get_loc(entryName)
                    self.tempCol[iTab] = val

                    self.tabletoWorkflowIndex.append(
                        [self.c, iTab, self.entryID, prevSectPath, objKey, ii])

            elif block['Type'] == 'Section':
                sectPath = prevSectPath.copy()
                sectPath.append(block['ID'])
                self.addSectionDatatoCol(
                    section=block, prevSectName=sectName,
                    prevSectPath=sectPath)

    def fixEntryNameDuplicates(self, tempname):
        """
        Modify parameter name to ensure it has not been duplicated.

        Compare the entered parameter name with all the names in the table view
        parameters column, and if a duplicate exists, add a modifier text
        string with the format (1), (2), ... ([N]) corresponding to duplicate
        1, duplicate 2, to duplicate [N] respectively.

        Parameters
        ----------
        tempname : str
            Original parameter name.

        Returns
        -------
        tempname : str
            Modified unique parameter name.

        """
        d = 1
        while tempname in self.entrynames:
            nameMod = ' (' + str(d) + ')'
            if tempname + nameMod in self.entrynames:
                d = d + 1
            else:
                tempname = tempname + nameMod

        self.entrynames.append(tempname)
        return tempname


class TabTableController(QTableWidget):
    """Table widget class used to control the 'Table' tab."""

    def __init__(self, parent=None, lankey='en'):
        QTableWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        self.tabletoWorkflowIndex = []

        data = pd.DataFrame([''], index=['Untitled'], columns=['Untitled'])
        self.updateTable(data)
        self.cellChanged.connect(self.onCellChange)

    def updateTable(self, data):
        """
        Fill table values and refit cell dimensions.

        Parameters
        ----------
        data : DataFrame
            Data frame containing all table values.

        """
        cols = data.columns
        rows = data.index

        self.setColumnCount(len(cols))
        self.setRowCount(len(rows))

        self.setVerticalHeaderLabels(rows)
        self.setHorizontalHeaderLabels(cols)

        for n, key in enumerate(sorted(data.keys())):
            for m, item in enumerate(data[key]):
                newitem = QTableWidgetItem(item)
                if item is None:  # Gray out cells without existing data.
                    newitem.setBackground(QColor(31, 32, 33))
                self.setItem(m, n, newitem)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def onCellChange(self):
        """
        Update work flow data if valid cell is changed.

        Method connected to onChanged event.

        """
        col = self.currentColumn()
        if col != -1:
            self.pushDatatoWorkflows()

    def pushDatatoWorkflows(self):
        """Update work flow data with table view data values."""
        if self.tabletoWorkflowIndex == []:
            return

        for [ii, jj, entry, sectionPath, item, ii_param
             ] in self.tabletoWorkflowIndex:
            workflow = self.parent.workflowTab.widget(ii).scene().mainEntry
            self.assignValThroughSections(
                workflow, ii, jj, entry, sectionPath, item, ii_param)

    def assignValThroughSections(self, section, ii, jj, entry, sectionPath,
                                 item, ii_param):
        """
        Update work flow data through sections with table data.

        Parameters
        ----------
        section : dict
            Section or work flow dictionary.
        ii : int
            Table row index.
        jj : int
            Table column index.
        entry : int
            Work flow entry index.
        sectionPath : list
            List of section branch path object identifiers.
        item : str
            Object identifier.
        ii_param : int
            Parameter index within the selected object.

        """
        if sectionPath == []:
            section['Objects'][item]['Values'][ii_param] = self.item(
                jj, ii).text()
        else:
            section = section['Objects'][sectionPath[0]]
            sectionPath = sectionPath[1:].copy()
            self.assignValThroughSections(
                section, ii, jj, entry, sectionPath, item, ii_param)

    def getPriorityList(self, workflow):
        """
        Generate a list of block IDs ordered in positional priority.

        Object positional priority is based on object feature 'postion':(x, y).
        Priority is first given by horizontal position from left to right, then
        by vertical postion, from top to bottom.

        Parameters
        ----------
        workflow : dict
            Work flow or section object dictionary.

        """
        x = []
        y = []
        ID = []
        for key in workflow['Objects'].keys():
            ID.append(workflow['Objects'][key]['ID'])
            x.append(workflow['Objects'][key]['position'][0])
            y.append(workflow['Objects'][key]['position'][1])

        tempdict = {'ID': ID, 'X': x, 'Y': y}
        df = pd.DataFrame(tempdict)
        df = df.sort_values(by=['X', 'Y'])
        priority = df.loc[:, 'ID'].tolist()

        return priority


class TabPlaintextController(QTabWidget):
    """Manage plain written text protocol data view tab."""

    def __init__(self, parent=None, lankey='en'):
        QTabWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        try:
            self.textconstlist = babelFish[
                'ui'][self.lankey]['plain text const']
        except Exception as e:
            print(e)
            self.textconstlist = ['' for ii in range(30)]

        self.actionDict = babelFish['Action']
        self.itemDict = babelFish['Item']

        self.setTabsClosable(True)
        self.setMovable(True)

        plainTextTab = PlainTextClass(parent=self)
        self.addTab(plainTextTab, 'Untitled')

        self.tabCloseRequested.connect(self.onClose)
        self.tabBarClicked.connect(self.onTabChange)

    def onTabChange(self, index):
        """
        Update work flow tab in remaining data views to current index.

        Method is connected to tabBarClicked event.

        Parameters
        ----------
        index : int
            Current work flow tab index.

        """
        self.parent.subTabInd = index
        self.parent.updateCurrentTab()
        self.parent.parent.updateToolBars()

    def onClose(self, ind):
        """
        Close work flow tab specified by index and update data views.

        Parameters
        ----------
        ind : int
            Index of closed work flow tab.

        """
        self.parent.workflowTab.onClose(ind)
        self.removeTab(ind)
        self.parent.updateEntries()

    def updateFromWorkflows(self, entriesWorkflow):
        """
        Update plain text tabs from all open workflows.

        Parameters
        ----------
        entriesWorkflow : dict
            Dictionary of all workflow entry data.

        """
        self.clear()

        for entryKey in entriesWorkflow.keys():
            entryText = self.textFromWorkflow(entriesWorkflow[entryKey])
            entryWidget = PlainTextClass(parent=self, text='')
            entryWidget.textWidget.setPlainText(entryText)
            self.addTab(entryWidget, entryKey)

    def textFromWorkflow(self, workflow):
        """
        Generate full protocol text for a given workflow entry.

        Parameters
        ----------
        workflow : dict
            Workflow data dictionary.

        Returns
        -------
        text : str
            Full protocol text for a given work flow.

        """
        try:
            self.textconstlist = babelFish[
                'ui'][self.lankey]['plain text const']
            self.itemDict = babelFish['Item']
            text = ''

            # Base features
            text = self.generateBaseText(text, workflow)

            # Additional list
            text = self.generateAbstractText(text, workflow)
            text += '\n'

            # Materials list
            text = self.generateMaterialsText(text, workflow)
            text += '\n'

            # Equipment list
            text = self.generateEquipmentText(text, workflow)
            text += '\n'

            # Protocol steps
            text = self.generateProtocolText(text, workflow)

        except Exception as e:
            self.textconstlist = [' ' for ii in range(30)]
            print(e)
            text = '** ' + self.textconstlist[0] + ' **'

        return text

    def generateBaseText(self, text, workflow):
        """
        Add basic information and description text to full protocol.

        Parameters
        ----------
        text : str
            Current protocol text.
        workflow : dict
            Workflow entry data dictionary.

        Returns
        -------
        text : str
            Protocol text with base information appended.

        """
        try:
            text += self.textconstlist[1] + ' ' + str(workflow['Name']) + '\n'
            text += self.textconstlist[2] + ' ' + \
                str(workflow['Description']) + '\n'
        except Exception as e:
            print(e)
            text = text + '** ' + self.textconstlist[3] + ' **'
        text = text + '\n'
        return text

    def generateAbstractText(self, text, workflow, sectName=''):
        """
        Add abstract item block data to protocol text.

        Iterate through sections within the current workflow or section.

        Parameters
        ----------
        text : str
            Current protocol text.
        workflow : dict
            Workflow entry or section data dictionary.
        sectName : str, optional
            Current section branch path. Section levels are separated by ' > '.
            The default is ''.

        Returns
        -------
        text : str
            Protocol text with abstract information appended.

        """
        try:
            _tab = '   '
            if sectName == '':
                text = text + self.textconstlist[4] + ' \n'
            itemNames = []
            for key in workflow['Objects'].keys():
                if workflow['Objects'][key]['Type'] == 'Section':
                    newSectName = sectName + \
                        workflow['Objects'][key]['Name'] + ' > '
                    text = self.generateAbstractText(
                        text, workflow['Objects'][key], newSectName)

                elif workflow['Objects'][key]['Type'] != 'Item':
                    continue

                elif workflow['Objects'][key]['Subtype'] == 'Abstract':
                    connected = self.checkItemForConnections(workflow, key)
                    if connected:
                        continue

                    text = text + _tab + sectName
                    itemName, itemNames = self.getUniqueItemName(
                        workflow, key, itemNames)
                    text = text + itemName
                    text = self.addParamsList(workflow, text, key)
                    text = self.addNoteText(workflow, text, key)
                    text = text + '\n'

        except Exception as e:
            print(e)
            text = text + '** ' + self.textconstlist[5] + ' **'
        return text

    def generateMaterialsText(self, text, workflow, sectName=''):
        """
        Add source item block data to protocol text.

        Iterate through sections within the current workflow or section.

        Parameters
        ----------
        text : str
            Current protocol text.
        workflow : dict
            Workflow entry or section data dictionary.
        sectName : str, optional
            Current section branch path. Section levels are separated by ' > '.
            The default is ''.

        Returns
        -------
        text : str
            Protocol text with materials information appended.

        """
        try:
            _tab = '   '
            if sectName == '':
                text = text + self.textconstlist[6] + ' \n'
            itemNames = []
            for key in workflow['Objects'].keys():
                if workflow['Objects'][key]['Type'] == 'Section':
                    newSectName = sectName + \
                        workflow['Objects'][key]['Name'] + ' > '
                    text = self.generateMaterialsText(
                        text, workflow['Objects'][key], newSectName)
                elif workflow['Objects'][key]['Type'] != 'Item':
                    continue

                elif workflow['Objects'][key]['Subtype'] in ['Source']:
                    text = text + _tab + sectName
                    itemName, itemNames = self.getUniqueItemName(
                        workflow, key, itemNames)
                    text = text + itemName
                    text = self.addParamsList(workflow, text, key)
                    text = self.addNoteText(workflow, text, key)
                    text = text + '\n'
        except Exception as e:
            print(e)
            text = text + '** ' + self.textconstlist[7] + ' **'
        return text

    def checkItemForConnections(self, workflow, checkkey):
        """
        Check if action block is connected to any item.

        Parameters
        ----------
        workflow : dict
            Workflow or section entry data dictionary.
        checkkey : str
            Identifier for the action block to check within workflow.

        Returns
        -------
        bool
            True if any item connection type is listed in the action block
            data. False if no item connections are found.

        """
        for key in workflow['Objects'].keys():
            testobject = workflow['Objects'][key]
            if testobject['Type'] != 'Action':
                continue
            if checkkey in testobject['A In']:
                return True
            if checkkey in testobject['B In']:
                return True
            if checkkey in testobject['C In']:
                return True
        return False

    def generateEquipmentText(self, text, workflow, sectName=''):
        """
        Add tool and container item block data to protocol text.

        Iterate through sections within the current workflow or section.

        Parameters
        ----------
        text : str
            Current protocol text.
        workflow : dict
            Workflow entry or section data dictionary.
        sectName : str, optional
            Current section branch path. Section levels are separated by ' > '.
            The default is ''.

        Returns
        -------
        text : str
            Protocol text with equipment information appended.

        """
        try:
            _tab = '   '
            if sectName == '':
                text = text + self.textconstlist[8] + ' \n'
            itemNames = []
            for key in workflow['Objects'].keys():
                if workflow['Objects'][key]['Type'] == 'Section':
                    newSectName = sectName + \
                        workflow['Objects'][key]['Name'] + ' > '
                    text = self.generateEquipmentText(
                        text, workflow['Objects'][key], newSectName)
                elif workflow['Objects'][key]['Type'] != 'Item':
                    continue

                elif workflow['Objects'][key]['Subtype'] in ['Tool',
                                                             'Container']:
                    text = text + _tab + sectName
                    itemName, itemNames = self.getUniqueItemName(
                        workflow, key, itemNames)
                    text = text + itemName
                    text = self.addParamsList(workflow, text, key)
                    text = self.addNoteText(workflow, text, key)
                    text = text + '\n'
        except Exception as e:
            print(e)
            text = text + '** ' + self.textconstlist[9] + ' **'
        return text

    def getUniqueItemName(self, workflow, key, itemNames):
        """
        Add unique modifier to current item.

        Check if the item name identified through key is a unique name in
        itemNames list. If it is not unique, add a modifier with the format
        <Duplicate 1>, <Duplicate 2>, ... <Duplicate N> is represented by (1),
        (2), ... (N), respectively.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.
        key : str
            Identifier for named block in workflow.
        itemNames : list
            List of all previously checked item names.

        Returns
        -------
        itemName : str
            Unique item name.
        itemNames : list
            List of all item names with unique name added.

        """
        try:
            rootItemName_en = workflow['Objects'][key]['Name']
            rootItemName = self.itemDict[rootItemName_en][self.lankey]['Name']
        except Exception as e:
            print(e)
            rootItemName = workflow['Objects'][key]['Name']
        itemName = rootItemName

        d = 0
        while itemName in itemNames:
            d = d + 1
            modName = ' (' + str(d) + ')'
            itemName = rootItemName + modName

        itemNames.append(itemName)
        return itemName, itemNames

    def generateProtocolText(self, text, workflow, level=1):
        """
        Add protocol steps data to protocol text.

        Iterate through sections within the current workflow or section.

        Parameters
        ----------
        text : str
            Current protocol text.
        workflow : dict
            Workflow entry or section data dictionary.
        level : int, optional
            Current section level. The default is 1.

        Returns
        -------
        text : str
            Protocol text with protocol steps appended.

        """
        try:
            if level == 1:
                text = text + self.textconstlist[10] + ' \n'

            itemPriority, actionPriority = self.getPriorityList(workflow)
            _tab = '   '
            c = 0
            for key in actionPriority:
                c = c + 1
                try:
                    if workflow['Objects'][key]['Type'] == 'Section':
                        sectName = workflow['Objects'][key]['Name']
                        text += _tab*level + str(c) + '. ' + sectName + '\n'
                        sectLevel = level + 1
                        text = self.generateProtocolText(
                            text, workflow['Objects'][key], sectLevel)
                        text += '\n'
                    else:
                        textline = self.generateTextLine(
                            workflow, key, itemPriority)
                        textline = self.addParamsList(workflow, textline, key)
                        textline = self.addNoteText(workflow, textline, key)
                        text = text + _tab*level + \
                            str(c) + '. ' + textline + '.\n'
                        text = self.addAbstractText(workflow, text, key)

                except Exception as e:
                    print(e)
                    textline = '** ' + self.textconstlist[11] + ' **'

        except Exception as e:
            print(e)
            text = text + '** ' + self.textconstlist[12] + ' **'
        return text

    def addAbstractText(self, workflow, text, key):
        """
        Add modifier text to current protocol step for abstract blocks.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.
        text : str
            Current protocol text.
        key : str
            Action block identifier.

        Returns
        -------
        text : str
            Protocol text with abstract modifier appended.

        """
        _tab = '   '
        keyList = []
        for mkey in workflow['Objects'][key]['A In']:
            if workflow['Objects'][mkey]['Subtype'] == 'Abstract':
                keyList.append(mkey)
        for mkey in workflow['Objects'][key]['B In']:
            if workflow['Objects'][mkey]['Subtype'] == 'Abstract':
                keyList.append(mkey)
        for mkey in workflow['Objects'][key]['C In']:
            if workflow['Objects'][mkey]['Subtype'] == 'Abstract':
                keyList.append(mkey)

        for inKey in keyList:
            if workflow['Objects'][inKey]['Parameters'] == []:
                continue

            text += _tab + _tab
            text += '- ' + workflow['Objects'][inKey]['Name']
            text = self.addParamsList(workflow, text, inKey)
            text += '\n'

        return text

    def addNoteText(self, workflow, text, key):
        """
        Add note text to current protocol step for abstract blocks.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.
        text : str
            Current protocol text.
        key : str
            Action block identifier.

        Returns
        -------
        text : str
            Protocol text with note data appended.

        """
        if workflow['Objects'][key]['Notes'] != '':
            text = text + ' (Note: ' + workflow['Objects'][key]['Notes'] + ')'
        return text

    def addParamsList(self, workflow, text, key):
        """
        Add action parameter text to current protocol step.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.
        text : str
            Current protocol text.
        key : str
            Action block identifier.

        Returns
        -------
        text : str
            Protocol text with action parameter data appended.

        """
        typeKey = workflow['Objects'][key]['Type'] + ' Parameter'
        text = text + ': ['
        for ii in range(len(workflow['Objects'][key]['Parameters'])):
            param_en = str(workflow['Objects'][key]['Parameters'][ii])
            try:
                param = babelFish[typeKey][param_en][self.lankey]['Name']
            except Exception as e:
                print(e)
                param = param_en
            val = str(workflow['Objects'][key]['Values'][ii])
            if val == '':
                val = '###'
            text = text + param + ' - ' + val + '; '
        if text[-1] != '[':
            text = text[:-2]
        text = text + ']'
        if text[-4:] == ': []':
            text = text[:-4]
        return text

    def getPriorityList(self, workflow):
        """
        Generate action and item priority lists based on block positions.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.

        Returns
        -------
        itemPriority : list
            List of item block identifiers sorted by positional priority.
        actionPriority : list
            List of action block identifiers sorted by positional priority.

        """
        x = []
        y = []
        ID = []
        for key in workflow['Objects'].keys():
            ID.append(workflow['Objects'][key]['ID'])
            x.append(workflow['Objects'][key]['position'][0])
            y.append(workflow['Objects'][key]['position'][1])

        tempdict = {'ID': ID, 'X': x, 'Y': y}
        df = pd.DataFrame(tempdict)
        df = df.sort_values(by=['X', 'Y'])
        priority = df.loc[:, 'ID'].tolist()

        actionPriority = priority.copy()
        itemPriority = priority.copy()
        for key in priority:
            if workflow['Objects'][key]['Type'] not in ['Action', 'Section']:
                actionPriority.remove(key)
            if workflow['Objects'][key]['Type'] != 'Item':
                itemPriority.remove(key)

        return itemPriority, actionPriority

    def getItemNouns(self, keys, workflow):
        """
        Generate grammatical series string for all item names from keys.

        Returns noun string which follows english grammatical rules for
        listing multiple items together (e.g. A, B, and C).

        Parameters
        ----------
        keys : list
            List of item block identifiers to convert to string.
        workflow : dict
            Workflow entry or section data dictionary.

        Returns
        -------
        nounStr : str
            Series string for all listed objects.

        """
        #  TODO: Make multilingual
        if len(keys) == 0:
            nounStr = ''
        elif len(keys) == 1:
            nounStr = self.getTranslatedNoun(
                workflow['Objects'][keys[0]]['Name'])
        elif len(keys) == 2:
            nounStr = self.getTranslatedNoun(
                workflow['Objects'][keys[0]]['Name'])
            nounStr += ' ' + self.textconstlist[14] + ' '
            nounStr += self.getTranslatedNoun(
                workflow['Objects'][keys[1]]['Name'])
        elif len(keys) > 2:
            nounStr = ''
            for key in keys[:-1]:
                nounStr += self.getTranslatedNoun(
                    workflow['Objects'][key]['Name'])
                nounStr += ', '
            nounStr += self.textconstlist[14] + ' '
            nounStr += self.getTranslatedNoun(
                workflow['Objects'][keys[-1]]['Name'])
        return nounStr

    def getTranslatedNoun(self, noun):
        """Return translated noun with bypass error handling."""
        try:
            noun_nat = self.itemDict[noun][self.lankey]['Name']
        except Exception as e:
            print(e)
            noun_nat = noun
        return noun_nat

    def generateTextLine(self, workflow, key, priority):
        """
        Generate protocol step line for a given action item.

        Parameters
        ----------
        workflow : dict
            Workflow entry or section data dictionary.
        key : str
            Action block identifier.
        priority : list
            Item block priority list sorted by position.

        Returns
        -------
        textline : str
            Text line for a protocol step.

        """
        self.actionDict = babelFish['Action']

        actionName = workflow['Objects'][key]['Name']
        actionParent = workflow['Objects'][key]['Subtype']

        aKeys = [aKey for aKey in workflow['Objects'][key]['A In']]
        bKeys = [bKey for bKey in workflow['Objects'][key]['B In']]
        cKeys = [cKey for cKey in workflow['Objects'][key]['C In']]

        numAIns = len(aKeys)
        numBIns = len(bKeys)
        numCIns = len(cKeys)

        aKeys = self.sortListbyPriority(aKeys, priority)
        bKeys = self.sortListbyPriority(bKeys, priority)
        cKeys = self.sortListbyPriority(cKeys, priority)

        itemA = self.getItemNouns(aKeys, workflow)
        itemB = self.getItemNouns(bKeys, workflow)
        itemC = self.getItemNouns(cKeys, workflow)

        errorMsg = '**' + self.textconstlist[13] + '**'
        def errorFunc(a, b, c): return errorMsg

        if actionParent == 'Add':
            if numBIns == 0 or numAIns == 0:
                tempfunc = errorFunc
            elif numBIns > 0 and numCIns == 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['00']
            elif numBIns > 0 and numCIns > 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['01']

        if actionParent == 'Remove':
            if numBIns == 0 or numAIns == 0:
                tempfunc = errorFunc
            elif numBIns > 0 and numCIns == 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['00']
            elif numBIns > 0 and numCIns > 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['01']

        if actionParent == 'Modify':
            try:
                if numBIns == 0 and numCIns == 0:
                    tempfunc = self.actionDict[
                        actionName][self.lankey]['Func']['00']
                elif numBIns > 0 and numCIns == 0:
                    tempfunc = self.actionDict[
                        actionName][self.lankey]['Func']['01']
                elif numBIns > 0 and numCIns > 0:
                    tempfunc = self.actionDict[
                        actionName][self.lankey]['Func']['02']
                elif numBIns == 0 and numCIns > 0:
                    tempfunc = self.actionDict[
                        actionName][self.lankey]['Func']['03']
                else:  # Special case function handling
                    tempfunc = self.actionDict[
                        actionName][self.lankey]['Func']['S']
            except Exception as e:
                print(e)
                tempfunc = errorFunc

        textline = tempfunc(itemA, itemB, itemC)
        return textline

    def sortListbyPriority(self, keys, priority):
        """Sort item keys by positional priority."""
        newKeys = []
        for key in priority:
            if key in keys:
                newKeys.append(key)
        return newKeys


class TabRawController(QTabWidget):
    """Manage raw workflow data display widgets."""

    def __init__(self, parent=None, lankey='en'):
        QTabWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        self.setTabsClosable(True)
        self.setMovable(True)

        rawTextTab = PlainTextClass(parent=self)
        self.addTab(rawTextTab, 'Untitled')

        self.tabCloseRequested.connect(self.onClose)
        self.tabBarClicked.connect(self.onTabChange)

    def onTabChange(self, index):
        """Update all data view tabs to current."""
        self.parent.subTabInd = index
        self.parent.updateCurrentTab()
        self.parent.parent.updateToolBars()

    def onClose(self, ind):
        """Remove closed tab from all data views."""
        self.parent.workflowTab.onClose(ind)
        self.removeTab(ind)
        self.parent.updateEntries()

    def updateFromWorkflows(self, entriesWorkflow):
        """Update display data from all workflows."""
        self.clear()
        for entryKey in entriesWorkflow.keys():
            entryText = self.formatEntry(entriesWorkflow[entryKey])
            entryWidget = PlainTextClass(parent=self, text='')
            entryWidget.textWidget.setPlainText(entryText)
            self.addTab(entryWidget, entryKey)

    def formatEntry(self, entry):
        """
        Return formatted display string for a workflow.

        Parameters
        ----------
        entry : dict
            Workflow data entry dictionary.

        Returns
        -------
        text : str
            Entry reformatted as a string for display.

        """
        text = json.dumps(entry, indent=4)
        return text


class PlainTextClass(QWidget):
    """Display plain text with custom formatting."""

    def __init__(self, parent=None, text=''):
        QWidget.__init__(self, parent)

        self.text = text
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.textWidget = QTextEdit(self.text)
        self.textWidget.setReadOnly(True)
        self.layout.addWidget(self.textWidget)
        self.setLayout(self.layout)


class TabWorkflowController(QTabWidget):
    """Manage workflow dispaly widgets."""

    def __init__(self, parent=None, rootwindow=None, lankey='en'):
        QTabWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        self.setTabsClosable(True)
        self.setMovable(True)
        self.rootwindow = rootwindow

        workflowTab = ViewClass(
            parent=self, rootwindow=self.rootwindow, lankey=self.lankey)
        self.addTab(workflowTab, 'Untitled')

        self.tabCloseRequested.connect(self.onClose)

        self.tabBarClicked.connect(self.onTabChange)

    def onTabChange(self, index):
        """Update other data view tab indices with current tab index."""
        self.parent.subTabInd = index
        self.parent.updateCurrentTab()
        self.parent.parent.updateToolBars()

    def tabNameUpdate(self, filename, tabInd):
        """
        Update tab display name with file name.

        Parameters
        ----------
        filename : str
            File path for saved .json.
        tabInd : int
            Current tab index.

        """
        tabname = os.path.basename(filename)
        tabname = os.path.splitext(tabname)[0]
        self.setTabText(tabInd, tabname)

    def addNewTab(self, tabInd):
        """Open a new tab after current tab and update other data views."""
        for ii in range(self.count()):
            # Do not open if current tab is empty and unnamed.
            cond1 = (self.widget(ii).scene().mainEntry['File'] == '')
            cond2 = (self.widget(ii).scene().mainEntry['Objects'] == {})
            if cond1 and cond2:
                self.setCurrentIndex(ii)
                return

        tabName = self.getNewTabName()
        workflowTab = ViewClass(
            parent=self, rootwindow=self.rootwindow, lankey=self.lankey)
        self.insertTab(tabInd+1, workflowTab, tabName)
        self.setCurrentIndex(tabInd+1)

    def getNewTabName(self):
        """Return unique new tab name with duplicate modifier."""
        tabNames = []
        for ii in range(self.count()):
            cond1 = (self.widget(ii).scene().mainEntry['File'] == '')
            cond2 = (self.widget(ii).scene().mainEntry['Objects'] == {})
            if cond1 and cond2:
                continue
            tabNames.append(self.tabText(ii))
        tempName = 'Untitled'
        newName = tempName
        c = 0
        while newName in tabNames:
            c += 1
            nameMod = ' (' + str(c) + ')'
            newName = tempName + nameMod
        return newName

    def onClose(self, ind):
        """Close workflow tab across all data views."""
        self.removeTab(ind)
        if self.widget(0) is None:  # Add 'Untitled' tab if none remain.
            workflowTab = ViewClass(
                parent=self, rootwindow=self.rootwindow, lankey=self.lankey)
            self.addTab(workflowTab, 'Untitled')
        self.parent.updateEntries()


class ViewClass(QGraphicsView):
    """Manages graphics scene for individual workflows."""

    def __init__(self, parent=None, rootwindow=None, lankey='en'):
        QGraphicsView.__init__(self, parent)

        self.parent = parent
        self.lankey = lankey

        self.rootwindow = rootwindow

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

        self.setMouseTracking(True)

        self.s = SceneClass(
            parent=self, rootwindow=self.rootwindow, lankey=self.lankey)
        self.setScene(self.s)
        self.setRenderHint(QPainter.Antialiasing)

        self.zoom_times = 10
        self.center = [0, 0]

        self.setSceneRect(self.center[0], self.center[1], 1000, 500)

    def wheelEvent(self, event):
        """
        Pan or zoom graphics view for individual workflow with mouse wheel.

        Pan up and down on mouse scroll. Pan left and right on Alt + mouse
        scroll. Accelerate pan on Shift+command. Zoom in and out with Ctrl +
        mouse scroll.

        """
        mods = QApplication.keyboardModifiers()
        if mods == Qt.ControlModifier:
            self.zoomEvt(event)

        elif mods == (Qt.AltModifier | Qt.ShiftModifier):
            self.panXEvt(event, 'fast')

        elif mods == Qt.AltModifier:
            self.panXEvt(event, 'slow')

        elif mods == Qt.ShiftModifier:
            self.panYEvt(event, 'fast')

        else:
            self.panYEvt(event, 'slow')

    def keyPressEvent(self, event):
        """
        Pan graphics view for individual workflow with keyboard arrows.

        Pan in the direction of the arrow keys. Accelerate pan with Shift +
        arrow key.

        """
        mods = QApplication.keyboardModifiers()
        if mods == Qt.ShiftModifier:
            rate = 'fast'
        else:
            rate = 'slow'

        if event.key() == Qt.Key_Left:
            self.panstepEvt(event, 'left', rate)

        elif event.key() == Qt.Key_Right:
            self.panstepEvt(event, 'right', rate)

        elif event.key() == Qt.Key_Up:
            self.panstepEvt(event, 'up', rate)

        elif event.key() == Qt.Key_Down:
            self.panstepEvt(event, 'down', rate)

        return QGraphicsView.keyPressEvent(self, event)

    def zoomEvt(self, event):
        """Zoom graphics view in or out."""
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            if self.zoom_times == 15:
                return
            zoom_factor = zoom_in_factor
            self.zoom_times += 1
        else:
            if self.zoom_times == -20:
                return
            zoom_factor = zoom_out_factor
            self.zoom_times -= 1
        self.scale(zoom_factor, zoom_factor)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

    def panstepEvt(self, event, direction, rate='slow'):
        """Pan graphics view at specified direction and step."""
        if rate == 'slow':
            stepsize = 125/((self.zoom_times + 20.5)**0.5)
        elif rate == 'fast':
            stepsize = 1000/((self.zoom_times + 20.5)**0.5)

        if direction == 'left':
            self.center[0] = self.center[0] - stepsize

        elif direction == 'right':
            self.center[0] = self.center[0] + stepsize

        elif direction == 'up':
            self.center[1] = self.center[1] - stepsize

        elif direction == 'down':
            self.center[1] = self.center[1] + stepsize

        self.setSceneRect(self.center[0], self.center[1], 1000, 500)
        event.accept()

    def panYEvt(self, event, rate):
        """Pan graphics view horizontally at specified direction and rate."""
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

        if rate == 'slow':
            panRate = 250/((self.zoom_times + 20.5)**0.5)
        elif rate == 'fast':
            panRate = 1000/((self.zoom_times + 20.5)**0.5)

        if event.angleDelta().y() > 0:
            self.center[1] = self.center[1] - panRate
            self.setSceneRect(self.center[0], self.center[1], 1000, 500)
        else:
            self.center[1] = self.center[1] + panRate
            self.setSceneRect(self.center[0], self.center[1], 1000, 500)
        event.accept()

    def panXEvt(self, event, rate):
        """Pan graphics view vertically at specified direction and rate."""
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

        if rate == 'slow':
            panRate = 250/((self.zoom_times + 20.5)**0.5)
        elif rate == 'fast':
            panRate = 1000/((self.zoom_times + 20.5)**0.5)

        if event.angleDelta().x() > 0:
            self.center[0] = self.center[0] - panRate
            self.setSceneRect(self.center[0], self.center[1], 1000, 500)
        else:
            self.center[0] = self.center[0] + panRate
            self.setSceneRect(self.center[0], self.center[1], 1000, 500)
        event.accept()


class SectionWindow(QWidget):
    """Manage pop-up workflow for opened sections."""

    windowSignal = Signal(object)

    def __init__(self, rootwindow, item, lankey):
        super().__init__()

        self.item = item
        self.data = item.data
        self.lankey = lankey
        self.rootwindow = rootwindow
        self.buildWidgets()
        self.prefillData()

    def buildWidgets(self):
        """Add data entry widgets and graphics scene to section window."""
        windowTitle = self.data['Name']
        if windowTitle == '':
            windowTitle = '(Untitled)'
        self.setWindowTitle(windowTitle)
        self.mainLayout = QHBoxLayout()
        self.graphicView = ViewClass(
            rootwindow=self.rootwindow, lankey=self.lankey)
        self.mainLayout.addWidget(self.graphicView, QSizePolicy().Expanding)
        self.addInfoWidget()
        self.setLayout(self.mainLayout)

    def addInfoWidget(self):
        """Add name and description entry widgets."""
        self.infoLayout = QGridLayout()

        namelabel = babelFish['ui'][self.lankey]['section'][0]
        self.nameLabel = QLabel(namelabel)
        self.infoLayout.addWidget(self.nameLabel, 0, 0)

        self.nameWidget = QLineEdit()
        self.nameWidget.setFixedWidth(200)
        self.nameWidget.textChanged.connect(self.updateData)
        self.infoLayout.addWidget(self.nameWidget, 1, 0)

        desclabel = babelFish['ui'][self.lankey]['section'][1]
        self.descriptionLabel = QLabel(desclabel)
        self.infoLayout.addWidget(self.descriptionLabel, 2, 0)

        self.descriptionWidget = QTextEdit()
        self.descriptionWidget.setFixedWidth(200)
        self.descriptionWidget.textChanged.connect(self.updateData)
        self.infoLayout.addWidget(self.descriptionWidget, 3, 0)

        self.infoLayout.addItem(QSpacerItem(
            4, 0, QSizePolicy().Expanding, QSizePolicy().Expanding))

        self.mainLayout.addLayout(self.infoLayout, stretch=0)

    def prefillData(self):
        """Fill data from parent workflow into section widget."""
        self.nameWidget.setText(self.data['Name'])
        self.descriptionWidget.setText(self.data['Description'])

        self.graphicView.scene().mainEntry = self.data
        self.graphicView.scene().addBlocksEdgesFromData()

    def closeEvent(self, event):
        """Push section data to parent workflow and close current window."""
        self.updateData()
        self.close()

    def updateData(self):
        """Push section data to parent workflow."""
        self.data['Name'] = self.nameWidget.text()
        self.data['Description'] = self.descriptionWidget.toPlainText()
        windowTitle = self.data['Name']
        if windowTitle == '':
            windowTitle = '(Untitled)'
        self.setWindowTitle(windowTitle)

        self.item.textItem.changeText(self.data['Name'])
        self.item.parent.updateEntryEdges()
        self.item.parent.addBlocksEdgesFromData()

        self.windowSignal.emit(self.data)


class SceneClass(QGraphicsScene):
    """Graphics display widget for individual workflows."""

    grid = 30

    def __init__(self, parent=None, rootwindow=None, lankey='en'):
        QGraphicsScene.__init__(self, QRectF(0, 0, 1000, 500), parent)

        self.rootwindow = rootwindow
        self.parent = parent
        self.lankey = lankey
        self.selectMemory = []
        self.temppos = []
        self.mainEntry = {'Name': '',
                          'language': self.lankey,
                          'Type': 'root',
                          'File': '',
                          'Description': '',
                          'Objects': {}
                          }

        self.objectKeys = []

    def mouseMoveEvent(self, event):
        """Update saved mouse position and pass event forward."""
        self.temppos = event.scenePos()
        QGraphicsScene.mouseMoveEvent(self, event)

    def drawBackground(self, painter, rect):
        """Overwrite drawBackground operation for custom color."""
        painter.fillRect(rect, QColor(96, 98, 97))

    def contextMenuEvent(self, event):
        """Build and display context menu on right click."""
        lankey = self.rootwindow.lankey
        labels = babelFish['ui'][lankey]['scene context']

        self.temppos = event.scenePos()
        menu = QMenu()

        createActionBtn = menu.addAction(labels[0])
        createActionBtn.setShortcut('Shift+D')
        createActionBtn.triggered.connect(self.onNewActionBlock)

        createItemBtn = menu.addAction(labels[1])
        createItemBtn.setShortcut('Shift+F')
        createItemBtn.triggered.connect(self.onNewItemBlock)

        createSectionBtn = menu.addAction(labels[2])
        createSectionBtn.setShortcut('Shift+G')
        createSectionBtn.triggered.connect(self.onNewSection)

        loadBtn = menu.addAction(labels[3])
        loadBtn.setShortcut('Ctrl+I')
        loadBtn.triggered.connect(self.onLoadBlock)

        loadBtn = menu.addAction(labels[4])
        loadBtn.setShortcut('Ctrl+Shift+I')
        loadBtn.triggered.connect(self.onLoadBlockasSection)

        addAActionBtn = menu.addAction(labels[5])
        addAActionBtn.setShortcut('Shift+1')
        addAActionBtn.triggered.connect(self.onAddAType)

        addBActionBtn = menu.addAction(labels[6])
        addBActionBtn.setShortcut('Shift+2')
        addBActionBtn.triggered.connect(self.onAddBType)

        addCActionBtn = menu.addAction(labels[7])
        addCActionBtn.setShortcut('Shift+3')
        addCActionBtn.triggered.connect(self.onAddCType)

        copyBtn = menu.addAction(labels[8])
        copyBtn.setShortcut('Ctrl+C')
        copyBtn.triggered.connect(self.onCopyBlock)

        pasteBtn = menu.addAction(labels[9])
        pasteBtn.setShortcut('Ctrl+V')
        pasteBtn.triggered.connect(self.onPasteBlock)

        selectBtn = menu.addAction(labels[10])
        selectBtn.setShortcut('Ctrl+A')
        selectBtn.triggered.connect(self.onSelectAll)

        delBtn = menu.addAction(labels[11])
        delBtn.triggered.connect(self.runElementDelete)

        emptyclipboard = {'ID': 'root',
                          'Links': [],
                          'Objects': {}}
        currentclipboard = self.rootwindow.clipboard
        if emptyclipboard == currentclipboard:
            pasteBtn.setEnabled(False)

        isConnectable = self.checkIfBlocksConnectable()
        if not isConnectable:
            addAActionBtn.setEnabled(False)
            addBActionBtn.setEnabled(False)
            addCActionBtn.setEnabled(False)

        menu.exec_(event.screenPos())

    def keyPressEvent(self, event):
        """Intercept key press events and pass to shortcut functions."""
        mods = QApplication.keyboardModifiers()

        if event.key() == Qt.Key_Delete:
            self.runElementDelete()
            self.updateEntryEdges()

        elif event.key() == Qt.Key_Return:
            if len(self.selectedItems()) == 1:
                Item = self.selectedItems()[0]
                blocktypestr = "<class '__main__.Block.<locals>.BlockBase'>"
                if str(type(Item)) == blocktypestr:
                    self.blockUpdate(Item)

        elif event.key() == Qt.Key_D and mods == Qt.ShiftModifier:
            self.onNewActionBlock()

        elif event.key() == Qt.Key_F and mods == Qt.ShiftModifier:
            self.onNewItemBlock()

        elif event.key() == Qt.Key_G and mods == Qt.ShiftModifier:
            self.onNewSection()

        elif event.key() == Qt.Key_I and mods == Qt.ControlModifier:
            self.onLoadBlock()

        elif event.key() == Qt.Key_I and mods == (
                Qt.ShiftModifier | Qt.ControlModifier):
            self.onLoadBlockasSection()

        elif event.key() in [
                Qt.Key_1, Qt.Key_Exclam] and mods == Qt.ShiftModifier:
            self.onAddAType()

        elif event.key() in [Qt.Key_2, Qt.Key_At] and mods == Qt.ShiftModifier:
            self.onAddBType()

        elif event.key() in [
                Qt.Key_2, Qt.Key_NumberSign] and mods == Qt.ShiftModifier:
            self.onAddCType()

        elif event.key() == Qt.Key_C and mods == Qt.ControlModifier:
            self.onCopyBlock()

        elif event.key() == Qt.Key_V and mods == Qt.ControlModifier:
            self.onPasteBlock()

        elif event.key() == Qt.Key_A and mods == Qt.ControlModifier:
            self.onSelectAll()

    def checkIfBlocksConnectable(self):
        """
        Return whether selected blocks are connectable.

        Return True if both an action and item block are selected. Otherwise
        return False.

        """
        itemList = []
        for item in self.selectedItems():
            blockstrtype = "<class '__main__.Block.<locals>.BlockBase'>"
            if str(type(item)) == blockstrtype:
                itemList.append(item.data['Type'])
        if 'Action' in itemList and 'Item' in itemList:
            return True
        else:
            return False

    def onAddAType(self):
        """Add A-Type edge connection between valid selected blocks."""
        self.addEdgestoScene('A')

    def onAddBType(self):
        """Add B-Type edge connection between valid selected blocks."""
        self.addEdgestoScene('B')

    def onAddCType(self):
        """Add C-Type edge connection between valid selected blocks."""
        self.addEdgestoScene('C')

    def onNewActionBlock(self):
        """Launch empty action block data entry window."""
        self.onNewBlock('Action')

    def onNewItemBlock(self):
        """Launch empty item block data entry window."""
        self.onNewBlock('Item')

    def onNewBlock(self, blockType):
        """Launch empty block data entry window specified by blockType."""
        self.generateBlockData(blockType=blockType)
        if self.newdata == []:
            return

    def onNewSection(self):
        """Launch empty section data entry window."""
        self.getBlockKeys()

        self.prompt = NewSectionWindow(self, objectKeys=self.objectKeys,
                                       pos=self.temppos, lankey=self.lankey)
        self.prompt.windowSignal.connect(self.transferWindowData)
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.show()

        loop = QEventLoop()
        self.prompt.destroyed.connect(loop.quit)
        loop.exec_()

        if self.newdata == []:
            return

    def onSelectAll(self):
        """Select all items in graphics scene."""
        for item in self.items():
            item.setSelected(True)

    def generateBlockData(self, data=[], blockType='', item=[]):
        """Launch block data entry window with prefilled data if available."""
        self.getBlockKeys()

        if data != []:
            blockType = data['Type']
        self.prompt = NewBlockWindow(self, data=data,
                                     objectKeys=self.objectKeys,
                                     blockType=blockType, item=item,
                                     pos=self.temppos)
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.windowSignal.connect(self.transferWindowData)
        self.prompt.show()

        loop = QEventLoop()
        self.prompt.destroyed.connect(loop.quit)
        loop.exec_()

        self.writeLinkedData()

    def writeLinkedData(self):
        """Check if data is linked then distribute to corresponding links."""
        if self.newdata == []:
            return
        if self.newdata['Type'] != 'Item':
            return
        if self.newdata['Link']:
            linkID = self.newdata['Link ID']
            currInd = self.rootwindow.centralWidget().widget(0).currentIndex()
            entry = self.rootwindow.centralWidget().widget(
                0).widget(currInd).scene().mainEntry
            entry = self.writeLinkedDatabySection(
                entry, linkID)
            self.rootwindow.centralWidget().widget(
                0).widget(currInd).scene().mainEntry = entry

    def writeLinkedDatabySection(self, section, linkID):
        """
        Check all blocks in workflow for current link and update linked data.

        If current workflow or section contains another section, iterate method
        through section.

        Parameters
        ----------
        section : dict
            Workflow or section data entry dictionary.
        linkID : str
            Link indentifier string.

        Returns
        -------
        section : dict
            Updated section or workflow data dictionary.

        """
        for key in section['Objects']:
            if section['Objects'][key]['Type'] != 'Item':
                continue
            if not section['Objects'][key]['Link']:
                continue
            if section['Objects'][key]['Link ID'] == linkID:
                oldpos = section['Objects'][key]['position'].copy()
                section['Objects'][key] = self.newdata.copy()
                section['Objects'][key]['position'] = oldpos
                section['Objects'][key]['ID'] = key

        for key in section['Objects']:
            if section['Objects'][key]['Type'] == 'Section':
                section['Objects'][key] = self.writeLinkedDatabySection(
                    section['Objects'][key], linkID)
        return section

    def updateEdgeData(self):
        """Iterate through scene objects and add edge data to workflow."""
        for ii in [*self.mainEntry['Objects']]:
            if self.mainEntry['Objects'][ii]['Type'] == 'Action':
                self.mainEntry['Objects'][ii]['A In'] = []
                self.mainEntry['Objects'][ii]['B In'] = []
                self.mainEntry['Objects'][ii]['C In'] = []

        for item in self.items():
            if str(type(item)) == "<class '__main__.Edge'>":
                if item.edgeType == 'L':
                    continue
                A_list = self.mainEntry['Objects'][item.destID]['A In']
                B_list = self.mainEntry['Objects'][item.destID]['B In']
                C_list = self.mainEntry['Objects'][item.destID]['C In']
                if item.edgeType == 'A' and item.sourceID not in A_list:
                    self.mainEntry['Objects'][item.destID]['A In'].append(
                        item.sourceID)
                elif item.edgeType == 'B' and item.sourceID not in B_list:
                    self.mainEntry['Objects'][item.destID]['B In'].append(
                        item.sourceID)
                elif item.edgeType == 'C' and item.sourceID not in C_list:
                    self.mainEntry['Objects'][item.destID]['C In'].append(
                        item.sourceID)

    def getBlockKeys(self):
        """Get identifiers for all objects in current workflow or scene."""
        if self.mainEntry['Objects'] != {}:
            self.objectKeys = [key for key in self.mainEntry['Objects'].keys()]

    def mousePressEvent(self, event):
        """Update old data and position on mouse press then forward event."""
        if event.button() == Qt.LeftButton:
            self.temppos = event.scenePos()
            self.olddata = copy.deepcopy(self.mainEntry)
        QGraphicsScene.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Forward mouse release then update graphics data if changed."""
        QGraphicsScene.mouseReleaseEvent(self, event)
        if event.button() == Qt.LeftButton:
            if self.olddata != self.mainEntry:
                self.addBlocksEdgesFromData()

    def mouseDoubleClickEvent(self, event):
        """Start object modification if graphic item selected."""
        if event.button() == Qt.LeftButton:
            items = self.selectedItems()
            if len(items) == 1:
                item = items[0]
                itemStr = str(type(item))
                if itemStr == "<class '__main__.Block.<locals>.BlockBase'>":
                    self.blockUpdate(item)
                elif itemStr == "<class '__main__.Edge'>":
                    if item.edgeType != 'L':
                        self.edgeUpdateMenu(event, item)
                elif itemStr == "<class '__main__.Section'>":
                    self.openSectionWindow(item)

    def blockUpdate(self, item):
        """Launch block modification window and update workflow."""
        self.generateBlockData(item.data, item=item)
        if self.newdata == []:
            return
        item.data = self.blockdata
        item.setBrush(item.colorMain)

        children = item.childItems()
        for child in children:
            if str(type(child)) == "<class '__main__.Text'>":
                text = str(self.blockdata['Name'])
                child.changeText(text)

        self.addBlocksEdgesFromData()

    def openSectionWindow(self, item):
        """Open workflow work space for selected section block."""
        self.prompt = SectionWindow(rootwindow=self.rootwindow, item=item,
                                    lankey=self.rootwindow.lankey)
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.windowSignal.connect(self.transferWindowData)
        self.prompt.show()

    def edgeUpdateMenu(self, event, edge):
        """Open custom edge modification context menu."""
        menu = QMenu()

        typeA = menu.addAction('Set A-Type')
        typeA.triggered.connect(
            lambda: self.onChangeEdgetoType(event, edge, 'A'))

        typeB = menu.addAction('Set B-Type')
        typeB.triggered.connect(
            lambda: self.onChangeEdgetoType(event, edge, 'B'))

        typeC = menu.addAction('Set C-Type')
        typeC.triggered.connect(
            lambda: self.onChangeEdgetoType(event, edge, 'C'))

        menu.exec_(event.screenPos())

    def onChangeEdgetoType(self, event, edge, edgeType):
        """Apply selected edge type change."""
        edge.edgeType = edgeType
        self.updateEntryEdges()
        for item in self.selectedItems():
            item.setSelected(False)

    def addEdgestoScene(self, edgeType):
        """
        Add all valid edges of specified type to selected blocks.

        Parameters
        ----------
        edgeType : {'A','B','C'}
            Edge type to add to selected blocks.

        """
        actionList = []
        itemList = []
        for item in self.selectedItems():
            blocktypestr = "<class '__main__.Block.<locals>.BlockBase'>"
            if str(type(item)) == blocktypestr:
                if item.data['Type'] == 'Item':
                    itemList.append(item)
                elif item.data['Type'] == 'Action':
                    actionList.append(item)

        for item_in in actionList:
            for item_out in itemList:
                itemID = item_out.data['ID']
                actionID = item_in.data['ID']
                connectIDs = []
                for ID in self.mainEntry['Objects'][actionID]['A In']:
                    connectIDs.append(ID)
                for ID in self.mainEntry['Objects'][actionID]['B In']:
                    connectIDs.append(ID)
                for ID in self.mainEntry['Objects'][actionID]['C In']:
                    connectIDs.append(ID)

                edgeExists = (itemID in connectIDs)
                if not edgeExists:
                    edge = Edge(item_out, item_in, edgeType, self)
                    self.addItem(edge)

        self.clearSelection()
        self.updateEntryEdges()

        self.updateBlockPositionData()

    def sceneEvent(self, event):
        """Pass graphics scene event to graphics scene."""
        # TODO: Why is this here?
        QGraphicsScene.sceneEvent(self, event)

    def runElementDelete(self):
        """Delete all selected graphics items."""
        if len(self.selectedItems()) > 0:
            itemlist = self.selectedItems()
            for item in itemlist:
                blocktypestr = "<class '__main__.Block.<locals>.BlockBase'>"
                if str(type(item)) == blocktypestr:
                    for edge in item.edges:
                        self.removeItem(edge)
                    del self.mainEntry['Objects'][str(item.data['ID'])]
                    self.removeItem(item)
                elif str(type(item)) == "<class '__main__.Section'>":
                    del self.mainEntry['Objects'][str(item.data['ID'])]
                    self.removeItem(item)

            itemlist = self.selectedItems()
            for item in itemlist:
                if str(type(item)) == "<class '__main__.Edge'>":
                    self.deleteEdgeData(item)
                self.removeItem(item)
            self.addBlocksEdgesFromData()

    def deleteEdgeData(self, item):
        """Delete data of selected edge from workflow data."""
        outID = item.source.data['ID']
        inID = item.dest.data['ID']

        if outID in self.mainEntry['Objects'][inID]['A In']:
            self.mainEntry['Objects'][inID]['A In'].remove(outID)
        elif outID in self.mainEntry['Objects'][inID]['B In']:
            self.mainEntry['Objects'][inID]['B In'].remove(outID)
        elif outID in self.mainEntry['Objects'][inID]['C In']:
            self.mainEntry['Objects'][inID]['C In'].remove(outID)

    def transferWindowData(self, data):
        """Update block data in workflow on window close."""
        # TODO: Double check function.
        self.newdata = data
        if self.newdata == []:
            return

        self.blockdata = self.newdata
        entryID = self.blockdata['ID']

        tempdata = self.blockdata.copy()
        self.mainEntry['Objects'][entryID] = tempdata
        self.addBlocksEdgesFromData()
        self.updateEdgeData()
        self.updateEntryEdges()

    def updateEntryEdges(self):
        """Update display edges from workflow data."""
        self.updateEdgeData()
        self.updateBlockPositionData()

    def updateBlockPositionData(self):
        """Update workflow block positions from graphics scene."""
        for item in self.items():
            if str(type(item)) in [
                    "<class '__main__.Block.<locals>.BlockBase'>",
                    "<class '__main__.Section'>"]:
                ID = item.data['ID']
                self.mainEntry['Objects'][ID]['position'] = [
                    int(item.pos().x()), int(item.pos().y())]
                item.data['position'] = [
                    int(item.pos().x()), int(item.pos().y())]

                if item.data['Type'] == 'Action':
                    workflow = copy.deepcopy(self.mainEntry)
                    key = item.data['ID']
                    tooltiptext = self.getTooltipLine(key, workflow)
                    item.setToolTipText(tooltiptext)

    def getTooltipLine(self, key, workflow):
        """
        Return tooltip text for the current protocol step.

        Parameters
        ----------
        key : str
            Action block identifier.
        workflow : dict
            Workflow or section entry data dictionary.

        Returns
        -------
        textline : str
            Protocol step for the specified action.

        """
        itemPriority, actionPriority = TabPlaintextController(
            lankey=self.lankey).getPriorityList(workflow)
        textline = TabPlaintextController(
            lankey=self.lankey).generateTextLine(workflow, key, itemPriority)
        block = workflow['Objects'][key]
        if block['A In'] == [] and block['B In'] == [] and block['C In'] == []:
            speciallist = ['Wait']
            if workflow['Objects'][key]['Name'] not in speciallist:
                textline = ''
        return textline

    def normalizeBlockPositions(self):
        """Shift all blocks so that the top left is at position (100,100)."""
        minX = 99999999
        minY = 99999999
        for item in self.items():
            isBlock = str(
                type(item)) == "<class '__main__.Block.<locals>.BlockBase'>"
            isSection = str(type(item)) == "<class '__main__.Section'>"
            if isBlock or isSection:
                if item.pos().x() < minX:
                    minX = item.pos().x()
                if item.pos().y() < minY:
                    minY = item.pos().y()
        for item in self.items():
            isBlock = str(
                type(item)) == "<class '__main__.Block.<locals>.BlockBase'>"
            isSection = str(type(item)) == "<class '__main__.Section'>"
            if isBlock or isSection:
                ID = item.data['ID']
                self.mainEntry['Objects'][ID]['position'] = [
                    int(item.pos().x() - minX + 100),
                    int(item.pos().y() - minY + 100)]

    def onSave(self, filename):
        """
        Update workflow data to match graphic scene and save to filepath.

        Parameters
        ----------
        filename : str
            .json file path for saved workflow.

        """
        self.updateBlockPositionData()
        self.normalizeBlockPositions()

        tabname = os.path.basename(filename)
        tabname = os.path.splitext(tabname)[0]
        self.mainEntry['Name'] = tabname
        self.mainEntry['File'] = filename
        self.parent.parent.parent.updateEntries()
        savejson(self.mainEntry, filename)
        self.lastSaveEntry = copy.deepcopy(self.mainEntry)

    def onSaveAs(self, filename):
        """
        Update workflow data to match graphic scene and save to filepath.

        Parameters
        ----------
        filename : str
            .json file path for saved workflow.

        """
        # TODO: How does this work differently from onSave?
        self.updateBlockPositionData()
        self.normalizeBlockPositions()

        tabname = os.path.basename(filename)
        tabname = os.path.splitext(tabname)[0]
        self.mainEntry['Name'] = tabname
        self.mainEntry['File'] = filename
        self.parent.parent.parent.updateEntries()

        savejson(self.mainEntry, filename)
        self.lastSaveEntry = copy.deepcopy(self.mainEntry)
        self.addBlocksEdgesFromData()

    def onLoadBlockasSection(self):
        """Launch prompt to import file as a new section block."""
        self.onLoadBlock(asSection=True)

    def onLoadBlock(self, asSection=False):
        """
        Launch prompt to import workflow from file.

        Parameters
        ----------
        asSection : bool, optional
            If True import the selected workflow as a new section block with.
            If False import the selected workflow as loose blocks. The default
            is False.

        """
        filename = QFileDialog.getOpenFileName(
            None, 'Import File', filter='*.json')

        if filename[0] == '':
            return

        importData = loadjson(filename[0])

        if asSection:
            self.insertBlockAsSection(importData)
        else:
            self.insertBlock(importData)

    def onCopyBlock(self):
        """Copy selected blocks to clipboard."""
        clipboard = {'ID': 'root',
                     'Objects': {}}

        for item in self.items():
            isBlock = (str(type(item)) ==
                       "<class '__main__.Block.<locals>.BlockBase'>")
            isSection = (str(type(item)) == "<class '__main__.Section'>")
            if isBlock or isSection:
                if item.isSelected():
                    clipboard['Objects'][item.data['ID']] = item.data
        print(clipboard)
        clipboard = self.normalizeClipboard(clipboard)
        print(clipboard)
        self.rootwindow.clipboard = copy.deepcopy(clipboard)

    def normalizeClipboard(self, clipboard):
        """Shift clipboard blocks so that top left is in postion (100, 100)."""
        minX = 99999999
        minY = 99999999
        for key in clipboard['Objects'].keys():
            tempX = clipboard['Objects'][key]['position'][0]
            tempY = clipboard['Objects'][key]['position'][1]
            if tempX < minX:
                minX = tempX
            if tempY < minY:
                minY = tempY

        for key in clipboard['Objects'].keys():
            tempX = clipboard['Objects'][key]['position'][0]
            tempY = clipboard['Objects'][key]['position'][1]
            clipboard['Objects'][key]['position'] = [
                tempX - minX + 100, tempY - minY + 100]
        return clipboard

    def onPasteBlock(self):
        """Insert clipboard data at last mouse position."""
        importData = copy.deepcopy(self.rootwindow.clipboard)
        self.insertBlock(importData)

    def insertBlockAsSection(self, importData):
        """
        Insert workflow data as a new section block.

        Parameters
        ----------
        importData : dict
            Workflow data to be inserted as a section block.

        """
        sectionData = {'Type': 'Section',
                       'ID': '0',
                       'Name': importData['Name'],
                       'Description': importData['Description'],
                       'Objects': importData['Objects'],
                       'position': [75, 50]}

        nestedData = {'Objects': {'0': sectionData}}
        self.insertBlock(nestedData)

    def insertBlock(self, importData):
        """
        Insert workflow data as loose blocks.

        Parameters
        ----------
        importData : dict
            Workflow data to be inserted as loose blocks.

        """
        self.updateBlockPositionData()
        importData = self.updatePosFromMouse(importData)


        if self.mainEntry['Objects'] == {}:
            self.mainEntry['Objects'] = importData['Objects']
            newKeys = [k for k in importData['Objects'].keys()]
        else:
            importData = self.removeDislocatedEdges(importData)
            importData, newKeys = self.replaceImportDataKeys(importData)
            self.appendImportData(importData)

        self.addBlocksEdgesFromData()

        # TODO: Highlight on import broken. Keys get shuffled with new blocks.
        # keys = importData['Objects'].keys()
        # for item in self.items():
        #     blocktypestr = "<class '__main__.Block.<locals>.BlockBase'>"
        #     if str(type(item)) == blocktypestr:
        #         if item.data['ID'] in keys:
        #             item.setSelected(True)
        #         else:
        #             item.setSelected(False)

    def updatePosFromMouse(self, data):
        """
        Shift workflow data to start at current mouse position.

        Parameters
        ----------
        data : dict
            Workflow data to shift.

        """
        if self.temppos != []:
            xStart = self.temppos.x() - 60
            yStart = self.temppos.y() - 60
        else:
            xStart = 0
            yStart = 0

        for key in data['Objects'].keys():
            data['Objects'][key]['position'][0] = data[
                'Objects'][key]['position'][0] + int(xStart)
            data['Objects'][key]['position'][1] = data[
                'Objects'][key]['position'][1] + int(yStart)

        return data

    def removeDislocatedEdges(self, importData):
        """Delete all edges with missing source or destination block."""
        keys = [k for k in importData['Objects'].keys()]
        for key in keys:
            if importData['Objects'][key]['Type'] != 'Action':
                continue
            for cKey in importData['Objects'][key]['C In']:
                if cKey not in keys:
                    importData['Objects'][key]['C In'].remove(cKey)
            for bKey in importData['Objects'][key]['B In']:
                if bKey not in keys:
                    importData['Objects'][key]['B In'].remove(bKey)
            for aKey in importData['Objects'][key]['A In']:
                if aKey not in keys:
                    importData['Objects'][key]['A In'].remove(aKey)
        return importData

    def replaceImportDataKeys(self, importData):
        """Update import block keys to ensure unique values."""
        mainData = self.mainEntry
        mainKeys = [k for k in mainData['Objects'].keys()]
        mainKeysint = [int(k) for k in mainKeys]

        importKeys = [k for k in importData['Objects'].keys()]
        for importKey in importKeys:
            importData = self.replaceAllKeyInstances(
                importData, importKey, importKey + 'n')

        importKeys = [k for k in importData['Objects'].keys()]
        importKeys_new = []
        for importKey in importKeys:
            newImportKey = str(max(mainKeysint)+1)
            mainKeysint.append(int(newImportKey))
            importData = self.replaceAllKeyInstances(
                importData, importKey, newImportKey)
            importKeys_new.append(newImportKey)

        return importData, importKeys_new

    def replaceAllKeyInstances(self, data, oldKey, newKey):
        """Replace old block key values with new key values."""
        newData = copy.deepcopy(data)

        # Replace all instances of keys within object dictionary items
        for dataKey in data['Objects'].keys():
            if data['Objects'][dataKey]['ID'] == oldKey:
                newData['Objects'][dataKey]['ID'] = newKey

            if data['Objects'][dataKey]['Type'] != 'Action':
                continue

            for ii in range(len(data['Objects'][dataKey]['A In'])):
                if data['Objects'][dataKey]['A In'][ii] == oldKey:
                    newData['Objects'][dataKey]['A In'][ii] = newKey

            for ii in range(len(data['Objects'][dataKey]['B In'])):
                if data['Objects'][dataKey]['B In'][ii] == oldKey:
                    newData['Objects'][dataKey]['B In'][ii] = newKey

            for ii in range(len(data['Objects'][dataKey]['C In'])):
                if data['Objects'][dataKey]['C In'][ii] == oldKey:
                    newData['Objects'][dataKey]['C In'][ii] = newKey

        # Replace keys in object dictionary
        mainKeys = [k for k in data['Objects'].keys()]
        for dataKey in mainKeys:
            if dataKey == oldKey:
                newData['Objects'][newKey] = newData['Objects'][oldKey]
                del newData['Objects'][oldKey]

        return newData

    def appendImportData(self, importData):
        """Add imported data to full workflow data."""
        importKeys = [k for k in importData['Objects'].keys()]
        for importKey in importKeys:
            self.mainEntry[
                'Objects'][importKey] = importData['Objects'][importKey]

    def onOpen(self, filename):
        """Open .json file as new workflow entry."""
        openEntry = loadjson(filename)
        openEntry['language'] = self.lankey
        openEntry['File'] = filename
        openEntry['Name'] = os.path.basename(filename)[:-4]
        self.mainEntry = openEntry

        self.lastSaveEntry = copy.deepcopy(self.mainEntry)
        self.addBlocksEdgesFromData()

    def addBlocksEdgesFromData(self):
        """Rebuild all blocks and edges in workflow."""
        self.clearScene()
        self.forceUniqueBlockIDs()

        newdata = self.mainEntry
        self.getBlockKeys()

        self.buildBlockGridIndex(newdata)
        self.setBlockPosfromGridIndex(newdata)

        for ii in newdata['Objects'].keys():
            if newdata['Objects'][ii]['Type'] != 'Action':
                continue
            item_in = self.getBlockItemFromKey(ii)
            for outlet in newdata['Objects'][ii]['A In']:
                for blockKey in self.objectKeys:
                    if outlet == blockKey:
                        item_out = self.getBlockItemFromKey(outlet)
                        edge = Edge(item_out, item_in, 'A', self)
                        self.addItem(edge)

            for outlet in newdata['Objects'][ii]['B In']:
                for blockKey in self.objectKeys:
                    if outlet == blockKey:
                        item_out = self.getBlockItemFromKey(outlet)
                        edge = Edge(item_out, item_in, 'B', self)
                        self.addItem(edge)

            for outlet in newdata['Objects'][ii]['C In']:
                for blockKey in self.objectKeys:
                    if outlet == blockKey:
                        item_out = self.getBlockItemFromKey(outlet)
                        edge = Edge(item_out, item_in, 'C', self)
                        self.addItem(edge)

        self.updateBlockPositionData()
        self.updateSequenceEdges(newdata)

    def clearScene(self):
        """Remove all graphics items in scene."""
        for item in self.items():
            self.removeItem(item)

    def forceUniqueBlockIDs(self):
        """Force all blocks to have unique IDs throughout workflow."""
        if self.mainEntry['Type'] != 'root':
            return
        data = copy.deepcopy(self.mainEntry)
        newdata, nBlocks = self.forceUniqueBlockIDsbySection(data)
        self.mainEntry = newdata

    def forceUniqueBlockIDsbySection(self, section, indx=-1):
        """
        Rewrite block identifiers to always be unique.

        Parameters
        ----------
        section : dict
            Workflow or section data entry.
        indx : int, optional
            Most recent block identifier index. The default is -1.

        Returns
        -------
        newsection : dict
            Updated workflow or section entry.
        indx : int
            Updated most recent block identifier index.

        """
        newsection = copy.deepcopy(section)
        prioritylist = self.getPriorityList(newsection)
        keypairs = []
        for key in prioritylist:
            indx += 1
            keypairs.append([key, str(indx)])
        newsection = self.swapKeyPairsinSection(newsection, keypairs)

        for key in newsection['Objects'].keys():
            if newsection['Objects'][key]['Type'] == 'Section':
                newsection[
                    'Objects'][key], indx = self.forceUniqueBlockIDsbySection(
                        newsection['Objects'][key], indx)

        return newsection, indx

    def getPriorityList(self, workflow):
        """
        Return list of all block identifiers in position order.

        Parameters
        ----------
        workflow : dict
            Workflow or section data entry.

        Returns
        -------
        priority : list
            List of block identifiers in position order.

        """
        x = []
        y = []
        ID = []
        for key in workflow['Objects'].keys():
            ID.append(workflow['Objects'][key]['ID'])
            x.append(workflow['Objects'][key]['position'][0])
            y.append(workflow['Objects'][key]['position'][1])

        tempdict = {'ID': ID, 'X': x, 'Y': y}
        df = pd.DataFrame(tempdict)
        df = df.sort_values(by=['X', 'Y'])
        priority = df.loc[:, 'ID'].tolist()

        return priority

    def swapKeyPairsinSection(self, section, keypairs):
        """
        Update section block keys with new keys.

        Parameters
        ----------
        section : dict
            Workflow entry data dictionary.
        keypairs : list
            List of block key pairs to replace in workflow. Key pairs are in
            the format [<old_key>, <new_key>].

        Returns
        -------
        newsection : dict
            Updated workflow entry data dictionary.

        """
        tempsection = copy.deepcopy(section)
        linkTypes = ['A In', 'B In', 'C In']
        for keypair in keypairs:
            for key in section['Objects'].keys():
                if section['Objects'][key]['Type'] != 'Action':
                    continue
                for linkType in linkTypes:
                    for ii, link in enumerate(
                            section['Objects'][key][linkType]):
                        if link == keypair[0]:
                            tempsection[
                                'Objects'][key][linkType][ii] = keypair[1]+'n'

        for keypair in keypairs:
            tempsection['Objects'][keypair[1] + 'n'
                                   ] = tempsection['Objects'].pop(keypair[0])

        newsection = copy.deepcopy(tempsection)
        for key in tempsection['Objects'].keys():
            if tempsection['Objects'][key]['Type'] != 'Action':
                continue
            for linkType in linkTypes:
                for ii, link in enumerate(
                        tempsection['Objects'][key][linkType]):
                    newsection['Objects'][key][linkType][ii] = tempsection[
                        'Objects'][key][linkType][ii][:-1]

        for key in tempsection['Objects'].keys():
            newsection['Objects'][key[:-1]] = newsection['Objects'].pop(key)
            newsection['Objects'][key[:-1]]['ID'] = key[:-1]

        return newsection

    def buildBlockGridIndex(self, data):
        """
        Build key table to provide position for all blocks in workflow.

        Key table is listed under class attribute gridIndices under the format
        [[<key>, <x-postion>, <y-postion>],...].

        Parameters
        ----------
        data : dict
            Workflow or section data entry dictionary.

        """
        objdata = data['Objects']
        self.gridIndices = []
        for key in objdata.keys():
            self.gridIndices.append([int(key), objdata[key]['position'][0],
                                     objdata[key]['position'][1]])

    def setBlockPosfromGridIndex(self, data):
        """Add and position all blocks in workflow data."""
        for gridIndex in self.gridIndices:
            tempdata = data['Objects'][str(gridIndex[0])]
            blockType = tempdata['Type']

            if blockType in ['Action', 'Item']:
                block = Block(blockType=blockType, data=tempdata,
                              parent=self, lankey=self.lankey)
            elif blockType == 'Section':
                block = Section(parent=self, data=tempdata)
            self.addItem(block)
            block.setPos(QPoint(gridIndex[1], gridIndex[2]))

    def updateSequenceEdges(self, data):
        """Add guideline edges between action blocks to indicate sequence."""
        itemPriority, actionPriority = TabPlaintextController(
            lankey=self.lankey).getPriorityList(data)
        if len(actionPriority) < 2:
            return
        for ii, key in enumerate(actionPriority[1:]):
            item_in = self.getBlockItemFromKey(actionPriority[ii])
            item_out = self.getBlockItemFromKey(key)
            edge = Edge(item_in, item_out, 'L', self)
            self.addItem(edge)

    def getBlockItemFromKey(self, key):
        """
        Return graphics item associated with block key.

        Parameters
        ----------
        key : str
            Block identifier for desired graphics item.

        Returns
        -------
        item : QGraphicsItem
            Graphics item associated with the selected key.

        """
        for item in self.items():
            cond1 = (str(type(item)) ==
                     "<class '__main__.Block.<locals>.BlockBase'>")
            cond2 = (str(type(item)) == "<class '__main__.Section'>")
            if cond1 or cond2:
                if key == item.data['ID']:
                    return item


def Block(blockType='Action', rect=QRectF(-50, -50, 100, 100), parent=None,
          data=[], lankey='en'):
    """Manage block graphics objects with action or item selection."""
    if blockType == 'Item':
        shapeClass = QGraphicsRectItem
    elif blockType == 'Action':
        shapeClass = QGraphicsEllipseItem

    class BlockBase(shapeClass):
        """Action and item block graphics object."""

        def __init__(self, rect=rect, parent=parent, data=data,
                     blockType=blockType, lankey=lankey):

            shapeClass.__init__(self, rect, None)

            self.setAcceptHoverEvents(True)

            self.lankey = lankey

            if blockType == 'Item':
                self.setRect(-40, -40, 80, 80)
            self.setRotation(-45)

            if blockType == 'Action':
                self.setToolTipText('')

            self.colorSelected = QColor(182, 227, 250)
            self.colorMain = QColor(11, 121, 191)
            self.colorText = QColor(255, 255, 255)

            self.parent = parent
            self.blockType = blockType
            self.data = data
            self.data['position'] = [self.pos().x(), self.pos().y()]
            self.text = self.convertBlockDatatoText(data)

            self.edges = []
            self.setZValue(2)
            self.setBrush(Qt.darkGray)
            self.setFlags(QGraphicsItem.ItemIsMovable |
                          QGraphicsItem.ItemSendsGeometryChanges |
                          QGraphicsItem.ItemIsSelectable)

            Text(parent=self, text=self.text)

            self.pen = QPen(QColor(255, 255, 255))
            self.pen.setWidthF(3.5)
            if blockType == 'Item':
                if self.data['Link']:
                    self.pen.setDashPattern([0.5, 3.25])
                else:
                    self.pen.setStyle(Qt.NoPen)
            else:
                self.pen.setStyle(Qt.NoPen)
            self.setPen(self.pen)

            self.setBrush(self.colorMain)

        def setToolTipText(self, text):
            """Set block tooltip to input text."""
            if text == '':  # Set tooltip to placeholder method if empty.
                text = 'Connect Item Blocks to view step transcript.'
            self.setToolTip("<font color=black>%s</font>" % text)

        def itemChange(self, change, value):
            """Manage graphics item selection color and snap movement."""
            if change == QGraphicsItem.ItemSelectedChange:
                if value:
                    self.setBrush(self.colorSelected)
                else:
                    self.setBrush(self.colorMain)

                for child in self.childItems():
                    child.setSelected(value)

            if change == QGraphicsItem.ItemPositionHasChanged:
                snapsize = 30
                snapX = round(self.scenePos().x()/snapsize)*snapsize
                snapY = round(self.scenePos().y()/snapsize)*snapsize
                self.setPos(snapX, snapY)
                self.data['position'] = [snapX, snapY]
                for edge in self.edges:
                    edge.adjust()

            return QGraphicsItem.itemChange(self, change, value)

        def convertBlockDatatoText(self, data):
            """
            Return text for translated block name if available.

            Parameters
            ----------
            data : dict
                Block data dictionary.

            Returns
            -------
            text : str
                Translated block name text.

            """
            try:
                text = babelFish[self.blockType][data['Name']
                                                 ][self.lankey]['Name']
            except Exception as e:
                print(e)
                text = str(data['Name'])
            return text

        def addEdge(self, edge):
            """
            Add edge item to current block.

            Parameters
            ----------
            edge : QGraphicsLineItem
                Graphics item to connect to block.

            """
            self.edges.append(edge)

        def hoverEnterEvent(self, event):
            """Update context workflow on hover over if action block."""
            if self.blockType == 'Action':
                self.parent.rootwindow.updateContextText(data['Name'])

    return BlockBase(rect=rect, parent=parent, data=data)


class Section(QGraphicsRectItem):
    """Section block graphics object."""

    def __init__(self, rect=QRectF(-75, -50, 150, 100), parent=None, data=[],
                 color=[]):
        QGraphicsRectItem.__init__(self, rect)

        self.parent = parent
        self.data = data

        self.data['position'] = [self.pos().x(), self.pos().y()]
        self.edges = []

        self.setZValue(3)

        self.pen = QPen(QColor(255, 255, 255))
        self.pen.setWidthF(1)
        self.pen.setStyle(Qt.NoPen)
        self.setPen(self.pen)

        self.colorSelected = QColor(182, 227, 250)
        self.colorMain = QColor(11, 121, 191)
        self.colorText = QColor(255, 255, 255)

        self.setBrush(self.colorMain)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemIsSelectable)

        self.text = self.data['Name']
        self.textItem = Text(parent=self, text=self.text)

    def itemChange(self, change, value):
        """Manage graphics item selection color and snap movement."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setBrush(self.colorSelected)
            else:
                self.setBrush(self.colorMain)

            for child in self.childItems():
                child.setSelected(value)

        if change == QGraphicsItem.ItemPositionHasChanged:
            snapsize = 30
            snapX = round(self.scenePos().x()/snapsize)*snapsize
            snapY = round(self.scenePos().y()/snapsize)*snapsize
            self.setPos(snapX, snapY)
            self.data['position'] = [snapX, snapY]
            for edge in self.edges:
                edge.adjust()

        return QGraphicsItem.itemChange(self, change, value)

    def addEdge(self, edge):
        """
        Add edge graphics object to section block.

        Method is used for time series sequence guideline.

        """
        self.edges.append(edge)


class Text(QGraphicsSimpleTextItem):
    """Custom text style graphics item."""

    def __init__(self, parent, text=''):
        QGraphicsSimpleTextItem.__init__(self, text, parent)
        self.parent = parent

        if str(type(self.parent)) != "<class '__main__.Section'>":
            self.setRotation(45)

        self.color = parent.colorText
        self.setBrush(self.color)
        self.font = QFont('Arial', 12)
        self.font.setWeight(80)
        self.pen = QPen(QColor(0, 0, 0))
        self.pen.setWidthF(0.5)
        self.setPen(self.pen)
        self.setFont(self.font)

        self.positionText()

    def changeText(self, newtext):
        """Change displayed text to newtext string value."""
        self.setText(newtext)
        self.positionText()

    def positionText(self):
        """Postion text relative to parent with rotation adjustment."""
        itemRect = self.sceneBoundingRect()
        if str(type(self.parent)) == "<class '__main__.Section'>":
            xAdj = -itemRect.width() // 2
            yAdj = -itemRect.height() // 2
            self.setPos(int(xAdj), int(yAdj))

        else:
            xAdj = 1 + itemRect.width() // 4
            yAdj = -3 + itemRect.height() // 4
            # 45 degree xy correction
            xAdjRot = (2**0.5) * (2*yAdj - xAdj)
            yAdjRot = -(2**0.5) * (2*yAdj + xAdj)

            self.setPos(int(xAdjRot), int(yAdjRot))


class Edge(QGraphicsLineItem):
    """Edge connection graphic object for all edge types."""

    def __init__(self, source, dest, edgeType, parent=None):
        QGraphicsLineItem.__init__(self, None)

        self.parent = parent

        self.edgeType = edgeType

        self.source = source
        self.dest = dest
        self.source.addEdge(self)
        self.dest.addEdge(self)

        self.AColor = Qt.white
        self.BColor = QColor(107, 192, 236)
        self.CColor = Qt.black
        self.LColor = QColor(7, 0, 150)

        # TODO: Add colorblind support.
        if self.edgeType == 'A':
            self.setPen(QPen(self.AColor, 10))
        elif self.edgeType == 'B':
            self.setPen(QPen(self.BColor, 10))
        elif self.edgeType == 'C':
            self.setPen(QPen(self.CColor, 10))
        elif self.edgeType == 'L':
            pen = QPen(self.LColor, 10)
            # pen.setStyle(Qt.DotLine)
            pen.setDashPattern([0.01, 1.5])
            pen.setCapStyle(Qt.RoundCap)
            self.setPen(pen)

        self.adjust()

        self.setFlags(QGraphicsItem.ItemIsSelectable)

        self.sourceID = self.source.data['ID']
        self.destID = self.dest.data['ID']
        self.setZValue(1)

    def itemChange(self, change, value):
        """Change edge color when selected or deselected."""
        if change == QGraphicsItem.ItemSelectedChange:
            if self.edgeType == 'A':
                self.setPen(QPen(QColor(175, 214, 255)
                            if value else self.AColor, 10))
            elif self.edgeType == 'B':
                self.setPen(QPen(QColor(175, 214, 255)
                            if value else self.BColor, 10))
            elif self.edgeType == 'C':
                self.setPen(QPen(QColor(175, 214, 255)
                            if value else self.CColor, 10))

        return QGraphicsItem.itemChange(self, change, value)

    def adjust(self):
        """Reposition and reshape edge to fit connected block positions."""
        self.prepareGeometryChange()
        self.setLine(QLineF(self.dest.pos(), self.source.pos()))


class NewSectionWindow(QWidget):
    """Prompt window for creating a new section object."""

    windowSignal = Signal(object)

    def __init__(self, parent, data=[], objectKeys=[], pos=[], lankey='en'):
        super().__init__()

        self.setWindowTitle('New Section Info')

        self.parent = parent
        self.pos = pos

        self.lankey = parent.rootwindow.lankey

        self.olddata = data

        self.objectKeys = objectKeys

        self.confirmed = False

        self.setWindowModality(Qt.ApplicationModal)
        self.move(QCursor.pos().x()-100, QCursor.pos().y()-50)

        self.layout = QGridLayout()
        namelabel = babelFish['ui'][self.lankey]['section'][0]
        self.layout.addWidget(QLabel(namelabel), 0, 0)
        self.nameWidget = QLineEdit()
        self.nameWidget.setMinimumWidth(200)
        self.layout.addWidget(self.nameWidget, 0, 1)

        desclabel = babelFish['ui'][self.lankey]['section'][1]
        self.layout.addWidget(QLabel(desclabel), 1, 0)
        self.descriptionWidget = QTextEdit()
        self.descriptionWidget.setMinimumWidth(200)
        self.layout.addWidget(self.descriptionWidget, 1, 1)

        addlabel = babelFish['ui'][self.lankey]['section'][2]
        addBtn = QPushButton(addlabel)
        addBtn.setFixedWidth(120)
        addBtn.clicked.connect(self.onConfirm)
        self.layout.addWidget(addBtn, 2, 0)

        cancellabel = babelFish['ui'][self.lankey]['section'][3]
        cancelBtn = QPushButton(cancellabel)
        cancelBtn.setFixedWidth(120)
        cancelBtn.clicked.connect(self.closeEvent)
        self.layout.addWidget(cancelBtn, 2, 1)

        self.setLayout(self.layout)

    def onConfirm(self):
        """Close window and emit entered data on confirm button click."""
        self.confirmed = True

        self.objectKeys = [round(float(ii)) for ii in self.objectKeys]

        self.data = {'Type': 'Section',
                     'Name': self.nameWidget.text(),
                     'Description': self.descriptionWidget.toPlainText(),
                     'Objects': {},
                     'position': [int(self.pos.x()), int(self.pos.y())]}

        if self.olddata == []:
            links = []
            if self.objectKeys == []:
                ID = str(0)
            else:
                ID = str(max(self.objectKeys) + 1)
        else:
            ID = self.olddata['ID']
            links = self.olddata['Links']
        self.data['ID'] = ID
        self.data['Links'] = links

        self.windowSignal.emit(self.data)
        self.close()

    def closeEvent(self, event):
        """Close window."""
        if not self.confirmed:
            self.windowSignal.emit([])
        self.close()


class NewBlockWindow(QWidget):
    """Prompt window for modifying or creating action or item block data."""

    windowSignal = Signal(object)

    def __init__(self, parent, data=[], objectKeys=[], blockType='', item=[],
                 pos=[]):
        super().__init__()

        self.lankey = parent.rootwindow.lankey
        labellist = babelFish['ui'][self.lankey]['new block']

        self.confirmed = False

        self.msgOpen = False

        self.dict = plaintextdictionary.loadDictionary()
        self.item = item
        self.pos = pos

        self.rootwindow = parent.rootwindow
        currInd = self.rootwindow.centralWidget().widget(0).currentIndex()
        self.alldata = self.rootwindow.centralWidget().widget(
            0).widget(currInd).scene().mainEntry
        self.getLinkIDList()

        self.olddata = data
        self.objectKeys = objectKeys
        self.blockType = blockType

        self.setWindowModality(Qt.ApplicationModal)
        self.move(QCursor.pos().x() - 200, QCursor.pos().y() - 100)

        self.layout = QGridLayout()

        if blockType == 'Action':
            self.blockLabel = labellist[0]
        elif blockType == 'Item':
            self.blockLabel = labellist[1]

        self.setWindowTitle(self.blockLabel)

        self.layout.addWidget(QLabel(labellist[2]), 1, 0)
        if blockType == 'Action':
            self.typeWidget = QLabel(labellist[18])
        elif blockType == 'Item':
            self.typeWidget = QLabel(labellist[19])

        self.layout.addWidget(self.typeWidget, 1, 1)

        self.layout.addWidget(QLabel(labellist[3]), 2, 0)
        self.subtypeWidget = QComboBox()
        self.subtypeWidget.addItems(self.subtypeChoices(blockType))
        self.subtypeWidget.currentIndexChanged.connect(self.onSubtypeChange)
        self.layout.addWidget(self.subtypeWidget, 2, 1)

        self.layout.addWidget(QLabel(labellist[4]), 3, 0)
        self.nameWidget = autocompleteLineEdit()
        self.nameWidget.clicked.connect(self.onNameClick)
        if self.nameWidget.text() == '':
            self.nameWidget.setPlaceholderText(
                self.subtypeWidget.currentText())
        self.layout.addWidget(self.nameWidget, 3, 1)
        self.setNameCompleter()

        self.linkLabel = QLabel(labellist[5])
        self.layout.addWidget(self.linkLabel, 4, 0)
        self.linkWidget = QCheckBox()
        self.linkWidget.stateChanged.connect(self.onLinkBoxClick)
        self.layout.addWidget(self.linkWidget, 4, 1)
        if blockType == 'Action':
            self.linkLabel.hide()
            self.linkWidget.hide()

        self.linkIDLabel = QLabel(labellist[6])
        self.layout.addWidget(self.linkIDLabel, 5, 0)
        self.linkIDWidget = autocompleteLineEdit()
        self.linkIDWidget.clicked.connect(self.onLinkClick)
        self.linkIDWidget.editingFinished.connect(self.onLinkIDEditFinish)
        self.layout.addWidget(self.linkIDWidget, 5, 1)
        if blockType == 'Action':
            self.linkIDLabel.hide()
            self.linkIDWidget.hide()
        elif not self.linkWidget.isChecked():
            self.linkIDLabel.hide()
            self.linkIDWidget.hide()
        self.setLinkCompleter()

        self.layout.addWidget(QLabel(labellist[7]), 6, 0)
        self.layout.addWidget(QLabel(labellist[8]), 6, 1)

        self.paramWidgets = []
        self.paramWidgets.append(autocompleteLineEdit())
        self.paramWidgets[0].clicked.connect(self.onParamClick)
        self.paramlayout = QVBoxLayout()
        self.paramlayout.addWidget(self.paramWidgets[0])

        self.layout.addLayout(self.paramlayout, 7, 0)

        self.valueWidgets = []
        self.valueWidgets.append(QLineEdit())
        self.valuelayout = QVBoxLayout()
        self.valuelayout.addWidget(self.valueWidgets[0])

        self.layout.addLayout(self.valuelayout, 7, 1)

        addParamBtn = QPushButton(labellist[9])
        addParamBtn.setFixedWidth(150)
        addParamBtn.clicked.connect(self.onParamAdd)

        self.layout.addWidget(addParamBtn, 8, 0)

        self.layout.addWidget(QLabel(labellist[10]), 9, 0)
        self.notes = QTextEdit()
        self.layout.addWidget(self.notes, 9, 1)

        addBtn = QPushButton(labellist[11])
        addBtn.setFixedWidth(120)
        addBtn.clicked.connect(self.onConfirm)
        self.layout.addWidget(addBtn, 10, 0)

        cancelBtn = QPushButton(labellist[12])
        cancelBtn.setFixedWidth(120)
        cancelBtn.clicked.connect(self.closeEvent)
        self.layout.addWidget(cancelBtn, 10, 1)

        self.setLayout(self.layout)

        self.prefillData(data)

        self.setNameCompleter()
        self.setParamCompleter()

    def onNameClick(self):
        """Display dropdown list for block names on click."""
        self.nameCompleter.complete()

    def onParamClick(self):
        """Display dropdown list for block parameters on click."""
        self.paramCompleter.complete()

    def onLinkClick(self):
        """Display dropdown list for link identifiers on click."""
        self.linkCompleter.complete()

    def setNameCompleter(self):
        """Generate name complete list and link to name completer."""
        parentType = self.blockType

        parentClasses = [parclass for parclass in self.dict[parentType].keys()]
        parentClass = parentClasses[self.subtypeWidget.currentIndex()]

        self.nameCompleteList = self.getNameCompleteList(
            parentType, parentClass)
        self.nameCompleter = QCompleter(self.nameCompleteList)
        self.nameCompleter.setModelSorting(QCompleter.UnsortedModel)
        self.nameWidget.setCompleter(self.nameCompleter)

    def setParamCompleter(self):
        """Generate parameter complete list and link to param completer."""
        typeKey = self.blockType + ' Parameter'

        parentClasses = [parclass for parclass in self.dict[typeKey].copy()]
        parentClass = parentClasses[self.subtypeWidget.currentIndex()]

        self.paramCompleteList = self.getParamCompleteList(
            self.blockType, parentClass)
        self.paramCompleter = QCompleter(self.paramCompleteList)
        self.paramCompleter.setModelSorting(QCompleter.UnsortedModel)
        for widget in self.paramWidgets:
            widget.setCompleter(self.paramCompleter)

    def setLinkCompleter(self):
        """Generate link ID completer list and link to link completer."""
        self.linkCompleter = QCompleter(self.linkIDs)
        self.linkCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.linkCompleter.setModelSorting(
            QCompleter.CaseInsensitivelySortedModel)
        self.linkIDWidget.setCompleter(self.linkCompleter)

    def getNameCompleteList(self, parentType, parentClass):
        """Generate name complete list."""
        if self.blockType == 'Action':
            self.completeList_en = self.dict[parentType][parentClass].keys()
        elif self.blockType == 'Item':
            self.completeList_en = self.dict[parentType][parentClass]

        self.completeList_en = [c for c in self.completeList_en]
        self.completeList_en.sort()
        self.completeList = [
            babelFish[self.blockType][c]
            [self.lankey]['Name'] for c in self.completeList_en]

        return self.completeList

    def getParamCompleteList(self, parentType, parentClass):
        """Generate parameter complete list."""
        self.paramCompleteList_en = self.dict[self.blockType +
                                              ' Parameter'].copy()
        self.paramCompleteList_en = [c for c in self.paramCompleteList_en]
        self.paramCompleteList_en.sort()
        self.paramCompleteList = [
            babelFish[self.blockType + ' Parameter'][c]
            [self.lankey]['Name'] for c in self.paramCompleteList_en]

        return self.paramCompleteList

    def onLinkIDEditFinish(self):
        """Prompt to insert data if selected link ID exists."""
        self.getLinkIDList()
        currLinkID = self.linkIDWidget.text()
        self.setLinkCompleter()
        if currLinkID not in self.linkIDs:
            return

        if self.olddata == []:
            pass
        elif 'Link ID' not in self.olddata.keys():
            pass
        elif currLinkID == self.olddata['Link ID']:
            return

        if self.msgOpen:
            return

        self.launchLinkOverwriteMsg()

    def launchLinkOverwriteMsg(self):
        """Prompt warning message for overwriting current with link data."""
        labellist = babelFish['ui'][self.lankey]['new block']

        self.msgOpen = True
        self.msg = QMessageBox()
        msgtxt = labellist[13] + ' '
        msgtxt += labellist[14] + '\n'
        msgtxt += labellist[15]
        self.msg.setText(msgtxt)
        yesBtn = self.msg.addButton(labellist[16], QMessageBox.YesRole)
        yesBtn.clicked.connect(self.onMsgYes)
        noBtn = self.msg.addButton(labellist[17], QMessageBox.NoRole)
        noBtn.clicked.connect(self.onMsgNo)
        self.msg.exec()
        self.msgOpen = False

    def onMsgYes(self):
        """Overwrite current data with link data."""
        currLinkID = self.linkIDWidget.text()
        self.getLinkData(currLinkID)

    def getLinkData(self, linkID):
        """Write link data in workflow from current link identifier."""
        self.olddata = self.findLinkDatainSection(
            copy.deepcopy(self.alldata), linkID)

        if self.item != []:
            self.olddata['position'] = self.item.data['position']
        else:
            self.olddata['position'] = [self.pos.x(), self.pos.y()]

        self.prefillData(self.olddata)

    def findLinkDatainSection(self, section, linkID):
        """Get link data in workflow from current link identifier."""
        for key in section['Objects'].keys():
            if section['Objects'][key]['Type'] != 'Item':
                continue
            if not section['Objects'][key]['Link']:
                continue
            if section['Objects'][key]['Link ID'] == linkID:
                return copy.deepcopy(section['Objects'][key])

        for key in section['Objects'].keys():
            if section['Objects'][key]['Type'] == 'Section':
                linkData = self.findLinkDatainSection(
                    section['Objects'][key], linkID)
                if linkData is not None:
                    return linkData

    def onMsgNo(self):
        """Cancel data overwrite and revert link identifier value."""
        if self.olddata == []:
            revertLinkTxt = ''
        elif 'Link ID' not in self.olddata.keys():
            revertLinkTxt = ''
        else:
            revertLinkTxt = self.olddata['Link ID']

        self.linkIDWidget.setText(revertLinkTxt)

    def getLinkIDList(self):
        """Get list of all link identifiers in workflow."""
        linkIDs = self.getNestedLinkIDs(self.alldata)
        if linkIDs != []:
            self.linkIDs = [c for c in linkIDs]
            self.linkIDs.sort()
        else:
            self.linkIDs = []

    def getNestedLinkIDs(self, data, linkIDs=[]):
        """Iterate through nested sections and return link identifier list."""
        for key in data['Objects'].keys():
            if data['Objects'][key]['Type'] != 'Item':
                continue
            if not data['Objects'][key]['Link']:
                continue
            if data['Objects'][key]['Link ID'] == '':
                continue
            linkID = data['Objects'][key]['Link ID']
            if linkID not in linkIDs:
                linkIDs.append(linkID)

        for key in data['Objects'].keys():
            if data['Objects'][key]['Type'] == 'Section':
                linkIDs = self.getNestedLinkIDs(
                    data['Objects'][key], linkIDs=linkIDs)

        return linkIDs

    def onSubtypeChange(self):
        """Update name completer when subtype selection changes."""
        subtype = self.subtypeWidget.currentText()
        self.nameWidget.setPlaceholderText(subtype)
        self.setNameCompleter()

    def subtypeChoices(self, blocktype):
        """Build translated list of subtype completer choices."""
        actions = ['Add', 'Remove', 'Modify']
        items = ['Container', 'Source', 'Tool', 'Abstract']
        dictionary = {
            'Action': [babelFish['Action'][
                action][self.lankey]['Name'] for action in actions],
            'Item': [babelFish['Item'][
                item][self.lankey]['Name'] for item in items]}
        return dictionary[blocktype]

    def onLinkBoxClick(self):
        """Add or remove link identifier box on link checkbox click."""
        linkChecked = self.linkWidget.isChecked()
        if linkChecked:
            self.linkIDLabel.show()
            self.linkIDWidget.show()
        elif not linkChecked:
            self.linkIDLabel.hide()
            self.linkIDWidget.hide()
        self.setLinkCompleter()

    def onParamAdd(self):
        """Add new parameter and value row line edit on parameter add click."""
        self.paramWidgets.append(autocompleteLineEdit())
        self.paramWidgets[-1].clicked.connect(self.onParamClick)
        self.paramlayout.addWidget(self.paramWidgets[-1])
        self.setParamCompleter()

        self.valueWidgets.append(QLineEdit())
        self.valuelayout.addWidget(self.valueWidgets[-1])

    def onConfirm(self):
        """Update block data, emit to workflow scene, and close prompt."""
        self.confirmed = True
        self.buildEntryData(self.olddata, self.objectKeys)
        self.windowSignal.emit(self.data)
        self.close()

    def closeEvent(self, event):
        """Emit blank data if not confirmed and close window."""
        if not self.confirmed:
            self.windowSignal.emit([])
        self.close()

    def buildEntryData(self, data, objectKeys):
        """
        Update data attribute with values entered in prompt.

        Parameters
        ----------
        data : dict or []
            Block data dictionary values at the time the block window prompt
            was opened. If window was created for a new block, the value is set
            to [].
        objectKeys : list
            List of all block keys in current work flow.

        """
        block = {}

        objectKeys = [round(float(ii)) for ii in objectKeys]

        if data == []:
            if objectKeys == []:
                block['ID'] = str(0)
            else:
                block['ID'] = str(max(objectKeys) + 1)
        else:
            block['ID'] = data['ID']

        block['Type'] = self.blockType
        subtypes = [key for key in self.dict[self.blockType].keys()]
        block['Subtype'] = subtypes[self.subtypeWidget.currentIndex()]

        if self.nameWidget.text() == '':
            placeholdText = self.nameWidget.placeholderText()
            ind_en = self.completeList.index(placeholdText)
            block['Name'] = self.completeList_en[ind_en]
        else:
            try:
                # https://stackoverflow.com/questions/15421363/find-the-index-of-a-string-ignoring-cases
                ind_en = next(ii for ii, item in enumerate(
                            self.completeList) if item.lower(
                                ) == self.nameWidget.text())
                block['Name'] = self.completeList_en[ind_en]
            except Exception as e:
                print(e)
                block['Name'] = self.nameWidget.text()

        block['Notes'] = self.notes.toPlainText()

        if self.blockType == 'Item':
            pass
        elif self.olddata == []:
            block['A In'] = []
            block['B In'] = []
            block['C In'] = []
        else:
            block['A In'] = self.olddata['A In']
            block['B In'] = self.olddata['B In']
            block['C In'] = self.olddata['C In']

        block['Parameters'] = []
        block['Values'] = []

        typeName = self.blockType + ' Parameter'
        paramList_en = [name for name in babelFish[typeName].keys()]
        paramList_en.sort()
        paramList = [babelFish[typeName][name][self.lankey]['Name']
                     for name in paramList_en]

        for ii in range(len(self.paramWidgets)):
            if '' != self.paramWidgets[ii].text():
                try:
                    param_ind = paramList.index(self.paramWidgets[ii].text())
                    param_en = paramList_en[param_ind]
                except Exception as e:
                    print(e)
                    param_en = self.paramWidgets[ii].text()
                block['Parameters'].append(param_en)
                block['Values'].append(self.valueWidgets[ii].text())

        if self.item != []:
            block['position'] = self.item.data['position']
        else:
            block['position'] = [int(self.pos.x()), int(self.pos.y())]

        if self.blockType == 'Item':
            block['Link'] = self.linkWidget.isChecked()
            if self.linkWidget.isChecked():
                block['Link ID'] = self.linkIDWidget.text()

        self.data = block

    def prefillData(self, data):
        """Fill prompt window fields with data if modifiying existing block."""
        labellist = babelFish['ui'][self.lankey]['new block']
        if data != []:
            if self.blockType == 'Action':
                self.typeWidget.setText(labellist[18])
            elif self.blockType == 'Item':
                self.typeWidget.setText(labellist[19])

            subtypeLbl = babelFish[self.blockType][data['Subtype']
                                                   ][self.lankey]['Name']
            self.subtypeWidget.setCurrentText(subtypeLbl)

            try:
                nameLbl = babelFish[self.blockType][data['Name']
                                                    ][self.lankey]['Name']
            except Exception as e:
                print(e)
                nameLbl = data['Name']

            self.nameWidget.setText(nameLbl)
            self.notes.insertPlainText(data['Notes'])
            if self.blockType == 'Item':
                if data['Link']:
                    linkState = Qt.Checked
                    self.linkIDWidget.setText(data['Link ID'])
                elif not data['Link']:
                    linkState = Qt.Unchecked
                self.linkWidget.setCheckState(linkState)

            for ii in range(len(data['Parameters'])):
                try:
                    typeKey = self.blockType + ' Parameter'
                    paramName_en = data['Parameters'][ii]
                    paramName = babelFish[
                        typeKey][paramName_en][self.lankey]['Name']
                    self.paramWidgets[ii].insert(paramName)
                except Exception as e:
                    print(e)
                    self.paramWidgets[ii].insert(data['Parameters'][ii])

                self.valueWidgets[ii].insert(data['Values'][ii])
                self.onParamAdd()


class autocompleteLineEdit(QLineEdit):
    """Modified QLineEdit that emits a mouse release event."""

    clicked = Signal(object)

    def mouseReleaseEvent(self, event):
        """Emit mouse release event when line edit box is clicked."""
        self.clicked.emit(event)


if __name__ == "__main__":
    myappid = 'NREL.UWLI.0.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    # app.setStyle("Breeze")
    qdarktheme.setup_theme('auto')
    window = WindowClass()
    window.setWindowIcon(QIcon('Logo//Logo_v1f.png'))
    window.show()
    app.exec_()
