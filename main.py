"""
Universal Workflow Language Interface.

@author: repps

"""
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QMenu,
                             QMenuBar,
                             QAction,
                             QFileDialog,
                             QMessageBox,
                             QToolBar,
                             QLabel,
                             QWidget,
                             QLayout,
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
                             QScrollArea,
                             QToolButton,
                             QInputDialog,
                             QShortcut,
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
                         QCursor,
                         QDoubleValidator,
                         QIntValidator,
                         QKeySequence
                         )
import qdarktheme
import os
import copy
import random
import math
import pandas as pd
from scipy.stats import qmc
from scipy.spatial import distance_matrix
from scipy.optimize import minimize
import json
import dill as pickle
import sip
import itertools
import ctypes
import numpy as np
import plaintextdictionary
from datetime import datetime
from openpyxl import load_workbook
import ast
import re


UWL_VERSION = '1.1.0'

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


def get_translation(babelFish, lankey, category, english_key, fallback=None):
    """
    Get translation by English key instead of index.
    
    Parameters
    ----------
    babelFish : dict
        The translation dictionary
    lankey : str
        Language key (e.g., 'en', 'es', 'zh-Hans')
    category : str
        Translation category (e.g., 'section', 'new block', 'scene context', 'plain text const', 'widgets')
    english_key : str
        The English text key to look up
    fallback : str, optional
        Fallback text if translation not found
        
    Returns
    -------
    str
        Translated text or fallback
    """
    try:
        # Try to get translation from the new dictionary structure
        if category in babelFish['ui'][lankey] and english_key in babelFish['ui'][lankey][category]:
            return babelFish['ui'][lankey][category][english_key]
        
        # Try the actual structure: babelFish[lankey]['text list ui']
        if lankey in babelFish and 'text list ui' in babelFish[lankey]:
            ui_list = babelFish[lankey]['text list ui']
            # Get the English list to find the index
            if 'en' in babelFish and 'text list ui' in babelFish['en']:
                en_list = babelFish['en']['text list ui']
                try:
                    # Find the index of the english_key in the English list
                    index = en_list.index(english_key)
                    # Return the translation at the same index
                    if index < len(ui_list):
                        return ui_list[index]
                except ValueError:
                    pass
        
        # Fallback to English if translation not found
        if fallback is not None:
            return fallback
        return english_key
    except (KeyError, TypeError):
        # If the new structure doesn't exist, fallback to English
        if fallback is not None:
            return fallback
        return english_key


filepath = 'preprocessing//multilingual_dict.pkl'
babelFish = loadpickle(filepath)


class WindowClass(QMainWindow):
    """Primary interface widget and root parent for all widgets."""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.dict = plaintextdictionary.loadDictionary()
        self.setWindowTitle(
            f'Universal Workflow Language Interface - ver. {UWL_VERSION}')
        self.baseFeatures = []
        self.clipboard = {'ID': 'root',
                          'Links': [],
                          'position': [0, 0],
                          'Objects': {},
                          'language': 'en'}
        self.lankey = 'en'
        self.tableCellViewMode = "show_all"

        self.tabCtrl = TabViewController(
            parent=self, rootwindow=self, lankey=self.lankey)
        self.setCentralWidget(self.tabCtrl)
        self.setAcceptDrops(True)
        self._createMenuBar()
        self._createToolBars()
        self.filename = -1
        
        # Initialize save actions state
        self.updateSaveActionsState()

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
            if os.path.splitext(f)[-1] in ['.json', '.uwl', 'uwlt']:
                filenames.append(f)
        if filenames != []:
            self.onOpen(filenames)

    def _createMenuBar(self):
        """Build tool menus for File, Edit, Insert, Language, and Help."""
        self.menubar = QMenuBar(self)

        self.buildFileMenu()
        self.buildEditMenu()
        self.buildInsertMenu()
        self.buildViewMenu()
        self.buildDesignMenu()
        self.buildLanguageMenu()
        self.buildHelpMenu()

        self.menubar.addMenu(self.filemenu)
        self.menubar.addMenu(self.editmenu)
        self.menubar.addMenu(self.insertmenu)
        self.menubar.addMenu(self.viewmenu)
        self.menubar.addMenu(self.designmenu)
        self.menubar.addMenu(self.langmenu)
        self.menubar.addMenu(self.helpmenu)
        self.setMenuBar(self.menubar)

    def buildViewMenu(self):
        """Build view menu and add actions."""
        self.viewmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'View'), self)

        self.tableViewMenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Table View'), self)
        self.showAllCellsAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Show all cells'), self)
        self.showAllCellsAction.setCheckable(True)
        self.showAllCellsAction.setChecked(True)
        self.showAllCellsAction.triggered.connect(self.onShowAllCells)

        self.showEmptyCellsAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Show empty cells'), self)
        self.showEmptyCellsAction.setCheckable(True)
        self.showEmptyCellsAction.triggered.connect(self.onShowEmptyCells)

        self.showUniqueCellsAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Show unique cells'), self)
        self.showUniqueCellsAction.setCheckable(True)
        self.showUniqueCellsAction.triggered.connect(self.onShowUniqueCells)

        self.tableViewMenu.addAction(self.showAllCellsAction)
        self.tableViewMenu.addAction(self.showEmptyCellsAction)
        self.tableViewMenu.addAction(self.showUniqueCellsAction)

        self.viewmenu.addMenu(self.tableViewMenu)

    def onShowAllCells(self):
        self.tableCellViewMode = "show_all"
        self.showAllCellsAction.setChecked(True)
        self.showEmptyCellsAction.setChecked(False)
        self.showUniqueCellsAction.setChecked(False)
        self.tabCtrl.updateEntryTable()

    def onShowEmptyCells(self):
        self.tableCellViewMode = "show_empty"
        self.showAllCellsAction.setChecked(False)
        self.showEmptyCellsAction.setChecked(True)
        self.showUniqueCellsAction.setChecked(False)
        self.tabCtrl.updateEntryTable()

    def onShowUniqueCells(self):
        self.tableCellViewMode = "show_unique"
        self.showAllCellsAction.setChecked(False)
        self.showEmptyCellsAction.setChecked(False)
        self.showUniqueCellsAction.setChecked(True)
        self.tabCtrl.updateEntryTable()

    def buildHelpMenu(self):
        """Build feedback, tutorial, and controls actions in help menu."""
        self.helpmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Help'), self)

        self.feedbackMenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Feedback'), self)

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
        self.controlsAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Controls'), self)
        self.controlsAction.triggered.connect(self.openControlsWindow)

    def openControlsWindow(self):
        """Create and launch window displaying controls information."""
        self.controlsprompt = QScrollArea()
        self.controlsprompt.setWindowTitle(get_translation(babelFish, self.lankey, 'widgets', 'Interface Controls'))
        # TODO: Add multilingual support for the controlstxt content.
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
        self.tutorialAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Tutorial'), self)
        self.tutorialAction.triggered.connect(self.openTutorialWindow)

    def openTutorialWindow(self):
        """Open new window with TutorialWindow class."""
        self.tutorialWindow = TutorialWindow(lankey=self.lankey)
        self.tutorialWindow.show()

    def buildLanguageMenu(self):
        """Get translator method and create language menu."""
        self.langmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Language'), self)
        # self.langmenu.setDisabled(True)
        self.getLanguages()
        self.buildLangList()

    def getLanguages(self):
        """Generate list of supported languages and keys."""
        # self.langmenucurrind = 7
        self.langmenucurrind = 7  # Set English as default (index 0)
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
        self.changeInterfaceWidgetsText(babelFish, self.lankey)
        self.updateBase()

    def getInterfaceWidgetsText(self):
        """
        Build lists of all interface text and widgets.

        Method called in language preprocessing script.
        This method is now deprecated as we use key-based translation.

        """
        pass

    def changeInterfaceWidgetsText(self, babelFish, lankey):
        """Translate all widget text using key-based translation system."""
        # Update menu actions
        self.updateMenuActions(babelFish, lankey)
        
        # Update tab texts
        self.updateTabTexts(babelFish, lankey)
        
        # Update toolbar texts
        self.updateToolbarTexts(babelFish, lankey)
        
        # Update label texts
        self.updateLabelTexts(babelFish, lankey)

    def updateMenuActions(self, babelFish, lankey):
        """Update all menu action texts using key-based translation."""
        # File menu actions
        self.newAction.setText(get_translation(babelFish, lankey, 'widgets', 'New'))
        self.openAction.setText(get_translation(babelFish, lankey, 'widgets', 'Open'))
        self.saveAction.setText(get_translation(babelFish, lankey, 'widgets', 'Save'))
        self.saveAsAction.setText(get_translation(babelFish, lankey, 'widgets', 'Save As'))
        self.saveAllAction.setText(get_translation(babelFish, lankey, 'widgets', 'Save All'))
        self.testAction.setText(get_translation(babelFish, lankey, 'widgets', 'Test Button'))
        
        # Edit menu actions
        self.copyAction.setText(get_translation(babelFish, lankey, 'widgets', 'Copy'))
        self.pasteAction.setText(get_translation(babelFish, lankey, 'widgets', 'Paste'))
        self.selectAllAction.setText(get_translation(babelFish, lankey, 'widgets', 'Select All'))
        self.delAction.setText(get_translation(babelFish, lankey, 'widgets', 'Delete'))
        
        # Insert menu actions
        self.actionAction.setText(get_translation(babelFish, lankey, 'widgets', 'Create Action Block'))
        self.itemAction.setText(get_translation(babelFish, lankey, 'widgets', 'Create Item Block'))
        self.sectionAction.setText(get_translation(babelFish, lankey, 'widgets', 'Create Section Block'))
        self.insertAction.setText(get_translation(babelFish, lankey, 'widgets', 'Insert from File'))
        self.insertSectAction.setText(get_translation(babelFish, lankey, 'widgets', 'Insert from File as Section'))
        self.addAAction.setText(get_translation(babelFish, lankey, 'widgets', 'Add A-Type Connections'))
        self.addBAction.setText(get_translation(babelFish, lankey, 'widgets', 'Add B-Type Connections'))
        self.addCAction.setText(get_translation(babelFish, lankey, 'widgets', 'Add C-Type Connections'))

        
        # View menu actions
        self.showAllCellsAction.setText(get_translation(babelFish, lankey, 'widgets', 'Show all cells'))
        self.showEmptyCellsAction.setText(get_translation(babelFish, lankey, 'widgets', 'Show empty cells'))
        self.showUniqueCellsAction.setText(get_translation(babelFish, lankey, 'widgets', 'Show unique cells'))
        
        # Design menu actions
        self.expselectAction.setText(get_translation(babelFish, lankey, 'widgets', 'Design Experiment Set'))
        self.buildtablemapAction.setText(get_translation(babelFish, lankey, 'widgets', 'Build Table Map'))
        self.importtableAction.setText(get_translation(babelFish, lankey, 'widgets', 'Import Table'))
        
        # Help menu actions
        self.tutorialAction.setText(get_translation(babelFish, lankey, 'widgets', 'Tutorial'))
        self.controlsAction.setText(get_translation(babelFish, lankey, 'widgets', 'Controls'))
        
        # Menu titles
        self.filemenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'File'))
        self.editmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Edit'))
        self.insertmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Insert'))
        self.viewmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'View'))
        self.designmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Batch'))
        self.helpmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Help'))
        self.langmenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Language'))
        
        # Submenu titles
        self.tableViewMenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Table View'))
        self.feedbackMenu.setTitle(get_translation(babelFish, lankey, 'widgets', 'Feedback'))

    def updateTabTexts(self, babelFish, lankey):
        """Update tab texts using key-based translation."""
        # Update the main TabViewController tabs
        if hasattr(self, 'tabCtrl') and self.tabCtrl is not None:
            self.tabCtrl.updateTabTexts(babelFish, lankey)

    def updateToolbarTexts(self, babelFish, lankey):
        """Update toolbar texts using key-based translation."""
        for child in self.children():
            if str(type(child)) == "<class 'PyQt5.QtWidgets.QToolBar'>":
                original_title = child.windowTitle()
                translated_title = get_translation(babelFish, lankey, 'widgets', original_title)
                child.setWindowTitle(translated_title)

    def updateLabelTexts(self, babelFish, lankey):
        """Update label texts using key-based translation."""
        for childlayout in self.layout.children():
            for ii in range(childlayout.count()):
                child = childlayout.itemAt(ii).widget()
                if str(type(child)) == "<class 'PyQt5.QtWidgets.QLabel'>":
                    original_text = child.text()
                    translated_text = get_translation(babelFish, lankey, 'widgets', original_text)
                    child.setText(translated_text)

    def buildFileMenu(self):
        """Add all file menu actions to menu and connect to functions."""
        self.filemenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'File'), self)

        self.newAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'New'), self)
        self.newAction.setShortcut('Ctrl+N')
        self.newAction.triggered.connect(self.onNew)
        self.filemenu.addAction(self.newAction)

        self.openAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Open'), self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.onOpen)
        self.filemenu.addAction(self.openAction)

        self.saveAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Save'), self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.onSave)
        self.filemenu.addAction(self.saveAction)

        self.saveAsAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Save As'), self)
        self.saveAsAction.setShortcut('Ctrl+Shift+S')
        self.saveAsAction.triggered.connect(self.onSaveAs)
        self.filemenu.addAction(self.saveAsAction)

        self.saveAllAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Save All'), self)
        self.saveAllAction.setShortcut('Ctrl+Shift+A')
        self.saveAllAction.triggered.connect(self.onSaveAll)
        self.filemenu.addAction(self.saveAllAction)

        self.testAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Test Button'), self)
        self.testAction.triggered.connect(self.testPrint)
        self.filemenu.addAction(self.testAction)

    def updateSaveActionsState(self):
        """Enable or disable save actions based on current tab selection."""
        if hasattr(self, 'tabCtrl') and self.tabCtrl is not None:
            currentTabIndex = self.tabCtrl.currentIndex()
            # Disable save actions when table tab (index 1) is selected
            isTableTabSelected = (currentTabIndex == 1)
            self.saveAction.setEnabled(not isTableTabSelected)
            self.saveAsAction.setEnabled(not isTableTabSelected)

    def testPrint(self):
        """Print currently selected workflow for troubleshooting."""
        ii = self.centralWidget().widget(0).currentIndex()
        print(self.centralWidget().widget(0).widget(ii).scene().mainEntry)

    def onSaveAs(self):
        """
        Save current workflow as a copy through file dialog.

        Operation is connected to Ctrl+Shift+S hot key.

        """
        filter_string = "UWL Entry (*.uwl);;UWL Template (*.uwlt)"
        filename = QFileDialog.getSaveFileName(
            self, 'Save File', filter=filter_string)
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

    def onTableExport(self):
        self.tabCtrl.tableTab.onTableExport()

    def onSave(self):
        """
        Save current workflow.

        Operation is connected to Ctrl+S hot key.

        """
        currTabInd = self.centralWidget().widget(0).currentIndex()
        tabname = self.centralWidget().widget(0).tabText(currTabInd)
        if tabname == 'Untitled':
            
            filter_string = "UWL Entry (*.uwl);;UWL Template (*.uwlt)"
            filename = QFileDialog.getSaveFileName(
                self, 'Save File', filter=filter_string)

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

    def onSaveAll(self):
        """
        Save all open workflows.

        Operation is connected to Ctrl+Shift+A hot key.
        For untitled workflows, prompts user for save location.
        """
        tabsWorkflows = self.centralWidget().widget(0)
        untitledTabs = []
        savedCount = 0
        errorCount = 0
        
        # First pass: identify untitled tabs and save titled ones
        for ii in range(tabsWorkflows.count()):
            tabname = tabsWorkflows.tabText(ii)
            filename = tabsWorkflows.widget(ii).scene().mainEntry['File']
            
            if tabname == 'Untitled' or filename == '':
                # Add to untitled tabs if tab name is 'Untitled' or filename is empty
                untitledTabs.append(ii)
            else:
                # Save titled tabs directly (only if they have a valid filename)
                try:
                    tabsWorkflows.widget(ii).scene().onSave(filename)
                    savedCount += 1
                except Exception as e:
                    errorCount += 1
                    print(f"Error saving tab {ii}: {e}")
                    # Show error message to user
                    QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'Save Error'), 
                                       f"{get_translation(babelFish, self.lankey, 'widgets', 'Failed to save tab')} {ii + 1}: {str(e)}")
        
        # Second pass: handle untitled tabs
        if untitledTabs:
            filter_string = "UWL Entry (*.uwl);;UWL Template (*.uwlt)"
            
            # Remove any duplicate tab indices
            untitledTabs = list(set(untitledTabs))
            
            for tabIndex in untitledTabs:
                # Switch to the untitled tab
                tabsWorkflows.setCurrentIndex(tabIndex)
                
                # Prompt user for save location
                filename = QFileDialog.getSaveFileName(
                    self, f'Save File for Tab {tabIndex + 1}', filter=filter_string)
                
                if filename == ('', ''):
                    # User cancelled, skip this tab
                    continue
                
                # Check if filename is already in use
                filename = filename[0]
                fileAlreadyOpen = False
                
                # Check against all other tabs (excluding current untitled tab)
                for jj in range(tabsWorkflows.count()):
                    if jj != tabIndex:  # Don't check against self
                        tabfile = tabsWorkflows.widget(jj).scene().mainEntry['File']
                        # Only check against tabs that have actual filenames (not empty strings)
                        if tabfile != '' and filename == tabfile:
                            fileAlreadyOpen = True
                            break
                
                if fileAlreadyOpen:
                    self.errorFilepathAreadyOpen()
                    continue
                
                # Save the file
                try:
                    tabsWorkflows.widget(tabIndex).scene().onSave(filename)
                    tabsWorkflows.tabNameUpdate(filename, tabIndex)
                    savedCount += 1
                except Exception as e:
                    errorCount += 1
                    print(f"Error saving untitled tab {tabIndex}: {e}")
                    # Show error message to user
                    QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'Save Error'), 
                                       f"{get_translation(babelFish, self.lankey, 'widgets', 'Failed to save tab')} {tabIndex + 1}: {str(e)}")
        
        # Update UI
        self.updateToolBars()
        self.centralWidget().updateCurrentTab()
        
        # Show summary message
        if savedCount > 0:
            message = f"Successfully saved {savedCount} file(s)"
            if errorCount > 0:
                message += f". {errorCount} file(s) had errors."
            QMessageBox.information(self, get_translation(babelFish, self.lankey, 'widgets', 'Save All Complete'), message)
        elif errorCount > 0:
            QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'Save All Failed'), f"{get_translation(babelFish, self.lankey, 'widgets', 'Failed to save')} {errorCount} {get_translation(babelFish, self.lankey, 'widgets', 'file(s)')}.")

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
            filter_string = "UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)"
            filenames = QFileDialog.getOpenFileNames(
                self, 'Open File', filter=filter_string)
            filenames = filenames[0]
        if filenames == []:
            return
        else:
            for filename in filenames:
                self.filename = filename

                tabsWorkflows = self.centralWidget().widget(0)
                fileAlreadyOpen = False
                existingTabIndex = -1
                
                for ii in range(tabsWorkflows.count()):
                    tabfile = self.centralWidget().widget(0).widget(
                        ii).scene().mainEntry['File']

                    if tabfile != '':
                        try:
                            if os.path.samefile(filename, tabfile):
                                fileAlreadyOpen = True
                                existingTabIndex = ii
                                break
                        except (OSError, FileNotFoundError):
                            # Handle case where files don't exist or can't be compared
                            pass

                if fileAlreadyOpen:
                    # Ensure the existing tab is selected
                    self.centralWidget().widget(0).setCurrentIndex(existingTabIndex)
                    # Update the interface to reflect the selected tab
                    self.centralWidget().updateCurrentTab()
                    continue  # Skip to next file instead of returning

                self.createTab()

                currTabInd = self.centralWidget().widget(0).currentIndex()

                self.centralWidget().widget(0).widget(
                    currTabInd).scene().onOpen(self.filename)
                self.centralWidget().widget(0).tabNameUpdate(
                    self.filename, currTabInd)

                # Update the interface to reflect the selected tab
                self.updateToolBars()
                self.centralWidget().updateCurrentTab()
                
                # Ensure all tabs are properly synchronized
                self.centralWidget().updateEntries()

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
        # Get the current tab index after creation and update the interface
        currTabInd = self.centralWidget().widget(0).currentIndex()
        self.centralWidget().subTabInd = currTabInd
        self.centralWidget().updateEntries()
        self.centralWidget().updateCurrentTab()

    def errorFilepathAreadyOpen(self):
        """Display error message if an already open file is selected."""
        # TODO: Message is currently intercepted by inbuilt error handling.
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(get_translation(babelFish, self.lankey, 'widgets', 'Error'))
        msg.setInformativeText(
            get_translation(babelFish, self.lankey, 'widgets', 
            """
            The selected file path is already open. Select a different path or
            close the open tab before proceeding.
            """))
        msg.setWindowTitle(get_translation(babelFish, self.lankey, 'widgets', 'Error'))
        msg.exec_()

    def buildEditMenu(self):
        """Add all edit menu actions to menu and connect to functions."""
        self.editmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Edit'), self)

        self.copyAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Copy'), self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.triggered.connect(self.onCopy)
        self.editmenu.addAction(self.copyAction)

        self.pasteAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Paste'), self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.triggered.connect(self.onPaste)
        self.editmenu.addAction(self.pasteAction)

        self.selectAllAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Select All'), self)
        self.selectAllAction.setShortcut('Ctrl+A')
        self.selectAllAction.triggered.connect(self.onSelectAll)
        self.editmenu.addAction(self.selectAllAction)

        self.delAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Delete'), self)
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
        self.insertmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Insert'), self)

        self.actionAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Create Action Block'), self)
        self.actionAction.setShortcut('Shift+D')
        self.actionAction.triggered.connect(self.onAddAction)
        self.insertmenu.addAction(self.actionAction)

        self.itemAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Create Item Block'), self)
        self.itemAction.setShortcut('Shift+F')
        self.itemAction.triggered.connect(self.onAddItem)
        self.insertmenu.addAction(self.itemAction)

        self.sectionAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Create Section Block'), self)
        self.sectionAction.setShortcut('Shift+G')
        self.sectionAction.triggered.connect(self.onSection)
        self.insertmenu.addAction(self.sectionAction)

        self.insertAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Insert from File'), self)
        self.insertAction.setShortcut('Ctrl+I')
        self.insertAction.triggered.connect(self.onLoad)
        self.insertmenu.addAction(self.insertAction)

        self.insertSectAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Insert from File as Section'), self)
        self.insertSectAction.setShortcut('Ctrl+Shift+I')
        self.insertSectAction.triggered.connect(self.onLoadasSection)
        self.insertmenu.addAction(self.insertSectAction)

        self.addAAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Add A-Type Connections'), self)
        self.addAAction.setShortcut('Shift+1')
        self.addAAction.triggered.connect(self.onAddAType)
        self.insertmenu.addAction(self.addAAction)

        self.addBAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Add B-Type Connections'), self)
        self.addBAction.setShortcut('Shift+2')
        self.addBAction.triggered.connect(self.onAddBType)
        self.insertmenu.addAction(self.addBAction)

        self.addCAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Add C-Type Connections'), self)
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
        self.baseToolBar = QToolBar('Base Entry Features', self)
        self.baseToolBar.setFloatable(True)
        self.addToolBar(Qt.RightToolBarArea, self.baseToolBar)
        self.updateBase()

        self.actionContextToolBar = QToolBar('Action Context', self)
        self.actionContextToolBar.setFloatable(True)
        self.addToolBar(Qt.RightToolBarArea, self.actionContextToolBar)
        self.buildActionContext()

    def buildDesignMenu(self):
        """Build feedback, tutorial, and controls actions in help menu."""
        self.designmenu = QMenu(get_translation(babelFish, self.lankey, 'widgets', 'Batch'), self)

        self.expselectAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Design Experiment Set'), self)
        self.expselectAction.triggered.connect(self.openExperimentDesignWindow)
        self.designmenu.addAction(self.expselectAction)

        self.buildtablemapAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Build Table Map'), self)
        self.buildtablemapAction.triggered.connect(self.tablemapBuildWindow)
        self.designmenu.addAction(self.buildtablemapAction)

        self.importtableAction = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Import Table'), self)
        self.importtableAction.triggered.connect(self.openTableImportWindow)
        self.designmenu.addAction(self.importtableAction)
    
    def openExperimentDesignWindow(self):
        self.prompt = ExperimentDesignWindow(lankey=self.lankey)
        self.prompt.setWindowTitle("Design of Experiments Tool")
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.windowSignal.connect(self.transferDesignWindowData)
        self.prompt.show()
        
    def transferDesignWindowData(self, data):
            # print(data)
            pass
    
    def tablemapBuildWindow(self):
        self.prompt = BuildTableMapWindow(lankey=self.lankey)
        self.prompt.setWindowTitle("Excel Table Export Tool")
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.windowSignal.connect(self.transferBuildTableMapWindowData)
        self.prompt.show()

    def transferBuildTableMapWindowData(self, data):
        pass

    def openTableImportWindow(self):
        self.prompt = TableMapImportWindow(lankey=self.lankey)
        self.prompt.setWindowTitle("Excel Table Import Tool")
        self.prompt.setAttribute(Qt.WA_DeleteOnClose)
        self.prompt.windowSignal.connect(self.transferTableMapImportWindowData)
        self.prompt.show()

    def transferTableMapImportWindowData(self, data):
        if data != []:
            self.onOpen(data)

    

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
                func = babelFish['Action'][
                    action][self.lankey]['Func'][func_ver]
                action = babelFish['Action'][action][self.lankey]['Name']
                step = func('A', 'B', 'C')
        except Exception as e:
            #print(e)
            # # print(e)
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

    def updateBase(self):
        """Rebuild base information tool bar widgets from workflow."""
        if self.baseFeatures != []:
            self.baseToolBar.clear()
            sip.delete(self.baseFeatures)
            self.baseFeatures = None
        self.baseFeatures = QWidget()

        # Check if we're currently on the Table tab
        if hasattr(self, 'centralWidget') and self.centralWidget() is not None:
            currentMainTab = self.centralWidget().currentIndex()
            if currentMainTab == 1:  # Table tab
                # Create disabled base information tool for Table tab
                self._createDisabledBaseInfoTool()
                return

        currTabInd = self.centralWidget().widget(0).currentIndex()
        if self.centralWidget().widget(0).widget(
                currTabInd) is None:
            # Handle case when no tabs exist - create empty description box
            self._createEmptyBaseInfoTool()
            return

        baseEntry = self.centralWidget().widget(0).widget(
            currTabInd).scene().mainEntry

        self.layout = QVBoxLayout()

        layoutName = QHBoxLayout()
        nameStr = get_translation(babelFish, self.lankey, 'widgets', 'Entry Name: ') + \
            baseEntry['Name']
        nameLabel = QLabel(nameStr)
        nameLabel.setWordWrap(True)
        layoutName.addWidget(nameLabel)
        self.layout.addLayout(layoutName)

        layoutFile = QHBoxLayout()
        fileStr = get_translation(babelFish, self.lankey, 'widgets', 'File Path: ') + \
            baseEntry['File']
        fileLabel = QLabel(fileStr)
        fileLabel.setWordWrap(True)
        layoutFile.addWidget(fileLabel)
        self.layout.addLayout(layoutFile)

        layoutDesc = QVBoxLayout()
        descStr = get_translation(babelFish, self.lankey, 'widgets', 'Experiment Description:')
        descLabel = QLabel(descStr)
        layoutDesc.addWidget(descLabel)
        self.descWidget = QTextEdit()
        self.descWidget.setText(baseEntry['Description'])
        self.descWidget.textChanged.connect(self.updateEntryBase)
        layoutDesc.addWidget(self.descWidget)
        self.layout.addLayout(layoutDesc)

        self.baseFeatures.setLayout(self.layout)
        self.baseToolBar.addWidget(self.baseFeatures)

    def _createDisabledBaseInfoTool(self):
        """Create a disabled base information tool for the Table tab."""
        self.layout = QVBoxLayout()

        layoutName = QHBoxLayout()
        nameStr = get_translation(babelFish, self.lankey, 'widgets', 'Entry Name: ') + 'N/A (Table View)'
        nameLabel = QLabel(nameStr)
        nameLabel.setWordWrap(True)
        nameLabel.setEnabled(False)
        layoutName.addWidget(nameLabel)
        self.layout.addLayout(layoutName)

        layoutFile = QHBoxLayout()
        fileStr = get_translation(babelFish, self.lankey, 'widgets', 'File Path: ') + 'N/A'
        fileLabel = QLabel(fileStr)
        fileLabel.setWordWrap(True)
        fileLabel.setEnabled(False)
        layoutFile.addWidget(fileLabel)
        self.layout.addLayout(layoutFile)

        layoutDesc = QVBoxLayout()
        descStr = get_translation(babelFish, self.lankey, 'widgets', 'Experiment Description:')
        descLabel = QLabel(descStr)
        descLabel.setEnabled(False)
        layoutDesc.addWidget(descLabel)
        self.descWidget = QTextEdit()
        self.descWidget.setText('Base information tool is disabled in Table view.')
        self.descWidget.setEnabled(False)
        layoutDesc.addWidget(self.descWidget)
        self.layout.addLayout(layoutDesc)

        self.baseFeatures.setLayout(self.layout)
        self.baseToolBar.addWidget(self.baseFeatures)

    def _createEmptyBaseInfoTool(self):
        """Create an empty base information tool when no tabs exist."""
        self.layout = QVBoxLayout()

        layoutName = QHBoxLayout()
        nameStr = get_translation(babelFish, self.lankey, 'widgets', 'Entry Name: ') + 'Untitled'
        nameLabel = QLabel(nameStr)
        nameLabel.setWordWrap(True)
        layoutName.addWidget(nameLabel)
        self.layout.addLayout(layoutName)

        layoutFile = QHBoxLayout()
        fileStr = get_translation(babelFish, self.lankey, 'widgets', 'File Path: ') + ''
        fileLabel = QLabel(fileStr)
        fileLabel.setWordWrap(True)
        layoutFile.addWidget(fileLabel)
        self.layout.addLayout(layoutFile)

        layoutDesc = QVBoxLayout()
        descStr = get_translation(babelFish, self.lankey, 'widgets', 'Experiment Description:')
        descLabel = QLabel(descStr)
        layoutDesc.addWidget(descLabel)
        self.descWidget = QTextEdit()
        self.descWidget.setText('')
        self.descWidget.textChanged.connect(self.updateEntryBase)
        layoutDesc.addWidget(self.descWidget)
        self.layout.addLayout(layoutDesc)

        self.baseFeatures.setLayout(self.layout)
        self.baseToolBar.addWidget(self.baseFeatures)

    def updateEntryBase(self):
        """Update workflow data from base information tool bar widget."""
        # Don't update if we're on the Table tab
        if hasattr(self, 'centralWidget') and self.centralWidget() is not None:
            currentMainTab = self.centralWidget().currentIndex()
            if currentMainTab == 1:  # Table tab
                return
        
        currTabInd = self.centralWidget().widget(0).currentIndex()
        if self.centralWidget().widget(0).widget(currTabInd) is not None:
            self.centralWidget().widget(0).widget(currTabInd).scene(
            ).mainEntry['Description'] = self.descWidget.toPlainText()
            self.centralWidget().updateEntries()

    def updateToolBars(self):
        """Rebuild tool bars from current work flow data."""
        self.updateBase()
        self.updateEntryBase()


class TutorialWindow(QTabWidget):
    """Manage tutorial popup window."""

    def __init__(self, lankey='en'):
        QTabWidget.__init__(self)
        
        self.lankey = lankey
        self.filepath = 'tutorial'

        self.setWindowTitle(get_translation(babelFish, self.lankey, 'widgets', 'Tutorial'))
        self.setTabPosition(QTabWidget.TabPosition.West)

        self.addQuickstart()

    def addQuickstart(self):
        """Build tab for quick start tutorial."""
        self.filepath_quickstart = self.filepath + '//quickstart'
        self.quickstartTab = QTabWidget()
        self.addQuickstartTabs()

        self.addTab(self.quickstartTab, get_translation(babelFish, self.lankey, 'widgets', 'Quick Start'))

    def addQuickstartTabs(self):
        """Add step tabs to quick start tutorial."""
        files = os.listdir(self.filepath_quickstart)
        files.sort()
        for file in files:
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

                btnleft = QPushButton(get_translation(babelFish, self.lankey, 'widgets', ' < '))
                btnleft.clicked.connect(self.quickstartLeft)
                btnlayout.addWidget(btnleft)

                btnright = QPushButton(get_translation(babelFish, self.lankey, 'widgets', ' > '))
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
        self.rootwindow = rootwindow
        
        if self.rootwindow is not None:
            self.tableCellViewMode = self.rootwindow.tableCellViewMode

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
        self._lastActiveTab = 0  # Track the last active main tab

    def onCurrentChanged(self):
        """Update all workflow data when a cell value is changed."""
        currentIndex = self.currentIndex()
        
        # Check if we're switching to the Table tab
        if currentIndex == 1:  # Table tab
            self._disableBaseInformationTool()
        else:
            self._enableBaseInformationTool()
            # Only update entries if we're not on the table tab
            self.updateEntries()
            self.updateCurrentTab()
            # Ensure file tabs are synchronized
            self.syncFileTabs()
        
        # Update save actions state in main window
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            self.rootwindow.updateSaveActionsState()
            # Update toolbars to refresh experiment description box
            self.rootwindow.updateToolBars()
        
        self._lastActiveTab = currentIndex

    def _disableBaseInformationTool(self):
        """Disable the base information tool when on Table tab."""
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            if hasattr(self.rootwindow, 'baseFeatures') and self.rootwindow.baseFeatures is not None:
                self.rootwindow.baseFeatures.setEnabled(False)
                # Grey out the description widget
                if hasattr(self.rootwindow, 'descWidget'):
                    self.rootwindow.descWidget.setEnabled(False)

    def _enableBaseInformationTool(self):
        """Enable the base information tool when not on Table tab."""
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            if hasattr(self.rootwindow, 'baseFeatures') and self.rootwindow.baseFeatures is not None:
                self.rootwindow.baseFeatures.setEnabled(True)
                # Enable the description widget
                if hasattr(self.rootwindow, 'descWidget'):
                    self.rootwindow.descWidget.setEnabled(True)

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
        if not hasattr(self, "entriesWorkflow") or self.entriesWorkflow is None:
            return
        self.tableTab.clear()
        self.buildTableNames()
        self.entriesTable = pd.DataFrame([], index=self.tableNames)
        self.addDatatoTable()
        self.tableTab.updateTable(self.entriesTable)
        # self.updateTableViewMode()
        self.tableTab.tabletoWorkflowIndex = self.tabletoWorkflowIndex

    def updateTableViewMode(self):
        self.tableCellViewMode = self.rootwindow.tableCellViewMode
        if self.tableCellViewMode == "show_all":
            self.showAllTableRows()
        elif self.tableCellViewMode == "show_empty":
            self.hideNonEmptyTableRows()
        elif self.tableCellViewMode == "show_unique":
            self.hideNonUniqueTableRows()

    def showAllTableRows(self):
        for row_index in range(self.entriesTable.shape[0]):
            self.tableTab.showRow(row_index)

    def hideNonEmptyTableRows(self):
        self.showAllTableRows()
        for row_index in range(self.entriesTable.shape[0]):
            if all(self.entriesTable.iloc[row_index].apply(lambda x: x != "" and x is not None)):
                self.tableTab.hideRow(row_index)

    def hideNonUniqueTableRows(self):
        self.showAllTableRows()
        for row_index in range(self.entriesTable.shape[0]):
            if len(self.entriesTable.iloc[row_index].unique()) == 1:
                self.tableTab.hideRow(row_index)

    def updateCurrentTab(self):
        """Set tabs to match current tab across data views."""
        # Only update if we're not on the table tab
        if self.currentIndex() != 1:
            self.workflowTab.setCurrentIndex(self.subTabInd)
            self.plainTextTab.setCurrentIndex(self.subTabInd)
            self.rawTextTab.setCurrentIndex(self.subTabInd)
            
            # Update the base information tool with the current file's information
            self._updateBaseInformationTool()

    def _updateBaseInformationTool(self):
        """Update the base information tool with the current file's information."""
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            self.rootwindow.updateToolBars()
    
    def syncFileTabs(self):
        """Ensure all file tabs are synchronized across all main tabs."""
        if self.currentIndex() != 1:  # Not on Table tab
            currentFileIndex = self.workflowTab.currentIndex()
            self.subTabInd = currentFileIndex
            self.plainTextTab.setCurrentIndex(currentFileIndex)
            self.rawTextTab.setCurrentIndex(currentFileIndex)

    def updateTabTexts(self, babelFish, lankey):
        """Update the main tab texts when language changes."""
        # Update the four main tabs: Workflows, Table, Protocol, Raw
        tab_texts = ['Workflows', 'Table', 'Protocol', 'Raw']
        for i, text in enumerate(tab_texts):
            translated_text = get_translation(babelFish, lankey, 'widgets', text)
            self.setTabText(i, translated_text)

    def buildTableNames(self):
        """Iterate through all work flows and add unique parameter names."""
        self.tableNames = []
        
        for entryID in self.entriesWorkflow.keys():
            self.entrynames = []
            entry = self.entriesWorkflow[entryID]
            self.linkIDs = []
            self.addSectionTableNames(section=entry)

    def addSectionTableNames(self, section, prevSectName='', keyPath=[]):
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
        if not hasattr(self, "linkIDs"):
            self.linkIDs = []

        keyPath = copy.deepcopy(keyPath)
        if section['Type'] == 'root':
            sectName = ''
            self.keyPathLists = []
        else:
            sectName = prevSectName + section['Name'] + ' > '
            keyPath.append(section['ID'])
        for objKey in section['Objects'].keys():
            block = section['Objects'][objKey]
            if block['Type'] in ['Action', 'Item']:
                if block['Type'] == "Item" and block["Link"]:
                    if block['Link ID'] not in self.linkIDs:
                        self.linkIDs.append(block['Link ID'])
                    else:
                        continue
                try:
                    blockName = babelFish[block['Type']
                                          ][block['Name']][self.lankey]['Name']
                except Exception as e:
                    # print(e)
                    ##print(e)
                    blockName = block['Name']
                blockName = blockName + ' > '
                if block['Type'] == 'Action':
                    actionMod = self.getActionModifier(section, block)
                else:
                    actionMod = ''

                for ii_param, param in enumerate(block['Parameters']):
                    try:
                        param_type = babelFish[block['Type'] + ' Parameter']
                        param = param_type[param][self.lankey]['Name']
                    except Exception as e:
                        # print(e)
                        #print(e)
                        param = param

                    entryName = sectName + blockName + param + actionMod
                    entryName = self.fixEntryNameDuplicates(entryName)
                    if entryName not in self.tableNames:
                        self.tableNames.append(entryName)
                        tempKeyPath = keyPath.copy()
                        tempKeyPath.append(block['ID'])
                        tempKeyPath.append(ii_param)
                        self.keyPathLists.append(tempKeyPath.copy())
            elif block['Type'] == 'Section':
                self.addSectionTableNames(section=block, prevSectName=sectName,
                                          keyPath=keyPath)

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
                    # print(e)
                    #print(e)
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
                    # print(e)
                    #print(e)
                    pass
                actionMod = ' [' + BBlockName + ' from ' + ABlockName + '] '
            elif block['Subtype'] == 'Modify':
                ABlockName = self.getConnectionBlockName(section, block, 'A')
                try:
                    ABlockName = babelFish[
                        'Item'][ABlockName][self.lankey]['Name']
                except Exception as e:
                    # print(e)
                    #print(e)
                    pass
                actionMod = ' [' + ABlockName + '] '
        except Exception as e:
            # print(e)
            #print(e)
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
            self.linkIDs = []
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
                if block['Type'] == "Item" and block["Link"]:
                    if block['Link ID'] not in self.linkIDs:
                        self.linkIDs.append(block['Link ID'])
                    else:
                        continue
                try:
                    blockName = babelFish[block['Type']
                                          ][block['Name']][self.lankey]['Name']
                except Exception as e:
                    # print(e)
                    #print(e)
                    blockName = block['Name']
                blockName = blockName + ' > '

                for ii, param in enumerate(block['Parameters']):
                    val = block['Values'][ii]

                    try:
                        param_type = babelFish[block['Type'] + ' Parameter']
                        param = param_type[param][self.lankey]['Name']
                    except Exception as e:
                        # print(e)
                        #print(e)
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
        self.data_df = data

        cols = data.columns
        rows = data.index

        self.setColumnCount(len(cols))
        self.setRowCount(len(rows))

        self.setVerticalHeaderLabels(rows)
        self.setHorizontalHeaderLabels(cols)

        for n, key in enumerate(data.keys()):
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
                workflow, ii, jj, entry, sectionPath, item, ii_param, rootworkflow=workflow)

    def assignValThroughSections(self, section, ii, jj, entry, sectionPath,
                                 item, ii_param, rootworkflow):
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
            value = self.item(jj, ii).text()

            if section['Objects'][item]['Type'] == "Item" and section['Objects'][item]['Link'] is True:
                linkID = section['Objects'][item]['Link ID']
                self.applyValtoLinkedItems(linkID, value, rootworkflow)
            else:
                section['Objects'][item]['Values'][ii_param] = value
        else:
            section = section['Objects'][sectionPath[0]]
            sectionPath = sectionPath[1:].copy()
            self.assignValThroughSections(
                section, ii, jj, entry, sectionPath, item, ii_param, rootworkflow)

    def applyValtoLinkedItems(self, linkID, value, section):
        for key in section['Objects'].keys():
            if section['Objects'][key]['Type'] == 'Item' and \
               section['Objects'][key]['Link'] is True and \
               section['Objects'][key]['Link ID'] == linkID:
                for ii_param in range(len(section['Objects'][key]['Values'])):
                    section['Objects'][key]['Values'][ii_param] = value
            elif section['Objects'][key]['Type'] == 'Section':
                self.applyValtoLinkedItems(linkID, value, section['Objects'][key])

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

    def onTableExport(self):
        # try:
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, get_translation(babelFish, self.lankey, 'widgets', 'Save to Excel'), "", get_translation(babelFish, self.lankey, 'widgets', 'Excel Files (*.xlsx);;All Files (*)'), options=options)
        # df = self.get_dataframe()
        self.data_df.to_excel(file_path, index=True, header=True)


class TabPlaintextController(QTabWidget):
    """Manage plain written text protocol data view tab."""

    def __init__(self, parent=None, lankey='en'):
        QTabWidget.__init__(self, parent)
        self.parent = parent
        self.lankey = lankey

        try:
            # Initialize with empty list, will be populated as needed
            self.textconstlist = []
        except Exception as e:
            # print(e)
            #print(e)
            self.textconstlist = []

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
        # Ensure all file tabs are synchronized
        self.parent.syncFileTabs()
        # Update the base information tool with the current file's information
        if hasattr(self.parent, 'rootwindow') and self.parent.rootwindow is not None:
            self.parent.rootwindow.updateToolBars()

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
            # print(e)
            #print(e)
            text = '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Protocol Generation Error') + ' **'

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
            text += get_translation(babelFish, self.lankey, 'plain text const', 'Experiment Name:') + ' ' + str(workflow['Name']) + '\n'
            text += get_translation(babelFish, self.lankey, 'plain text const', 'Experiment Description:') + ' ' + \
                    str(workflow['Description']) + '\n'
        except Exception as e:
            # print(e)
            #print(e)
            text = text + '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Base Information Transcription Error') + ' **'
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
                text = text + get_translation(babelFish, self.lankey, 'plain text const', 'Additional Information') + ' \n'
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
            # print(e)
            #print(e)
            text = text + '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Additional Information List Transcription Error') + ' **'
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
                text = text + get_translation(babelFish, self.lankey, 'plain text const', 'Materials') + ' \n'
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
            # print(e)
            #print(e)
            text = text + '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Materials List Transcription Error') + ' **'
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
                text = text + get_translation(babelFish, self.lankey, 'plain text const', 'Equipment') + ' \n'
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
            # print(e)
            #print(e)
            text = text + '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Equipment List Transcription Error') + ' **'
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
            # print(e)
            #print(e)
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
                text = text + get_translation(babelFish, self.lankey, 'plain text const', 'Procedure') + ' \n'

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
                    # print(e)
                    #print(e)
                    textline = '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Action Transcription Error') + ' **'

        except Exception as e:
            # print(e)
            #print(e)
            text = text + '** ' + get_translation(babelFish, self.lankey, 'plain text const', 'Protocol List Transcription Error') + ' **'
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
                # print(e)
                #print(e)
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
            nounStr += ' ' + get_translation(babelFish, self.lankey, 'plain text const', 'and') + ' '
            nounStr += self.getTranslatedNoun(
                workflow['Objects'][keys[1]]['Name'])
        elif len(keys) > 2:
            nounStr = ''
            for key in keys[:-1]:
                nounStr += self.getTranslatedNoun(
                    workflow['Objects'][key]['Name'])
                nounStr += ', '
            nounStr += get_translation(babelFish, self.lankey, 'plain text const', 'and') + ' '
            nounStr += self.getTranslatedNoun(
                workflow['Objects'][keys[-1]]['Name'])
        return nounStr

    def getTranslatedNoun(self, noun):
        """Return translated noun with bypass error handling."""
        try:
            noun_nat = self.itemDict[noun][self.lankey]['Name']
        except Exception as e:
            # print(e)
            #print(e)
            noun_nat = noun
        return noun_nat

    def errorFunc(self, a, b, c, type="Modify", error=False):
        errorMsg = '**' + get_translation(babelFish, self.lankey, 'plain text const', 'Error') + '**'
        return errorMsg

    def defaultModFunc(self, a, b, c,):
        steptext = self.tempActionName + " "
        steptext += a
        
        if b != "":
            steptext += " with "
            steptext += b

        if c != "":
            steptext += " using "
            steptext += c

        return steptext

    def defaultAddFunc(self, a, b, c):
        steptext = self.tempActionName + " "
        
        if b == "":
            steptext += "[Missing]"
        else:
            steptext += b
        
        steptext += " to "
        if a == "":
            steptext += "[Missing]"
        else:
            steptext += a

        if c != "":
            steptext += " using "
            steptext += c

        return steptext
    
    def defaultRemFunc(self, a, b, c):
        steptext = self.tempActionName + " "
        
        if b == "":
            steptext += "[Missing]"
        else:
            steptext += b
            
        if a == "":
            steptext += "[Missing]"
        else:
            steptext += " from "
            steptext += a
            
        if c != "":
            steptext += " using "
            steptext += c

        return steptext

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

        if actionParent == 'Add':
            if actionName not in self.actionDict.keys():
                self.tempActionName = actionName
                tempfunc = self.defaultAddFunc
            elif numBIns == 0 or numAIns == 0:
                tempfunc = self.errorFunc
            elif numBIns > 0 and numCIns == 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['00']
            elif numBIns > 0 and numCIns > 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['01']

        if actionParent == 'Remove':
            if actionName not in self.actionDict.keys():
                self.tempActionName = actionName
                tempfunc = self.defaultRemFunc
            elif numBIns == 0 or numAIns == 0:
                tempfunc = self.errorFunc
            elif numBIns > 0 and numCIns == 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['00']
            elif numBIns > 0 and numCIns > 0:
                tempfunc = self.actionDict[
                    actionName][self.lankey]['Func']['01']

        if actionParent == 'Modify':
            try:
                if actionName not in self.actionDict.keys():
                    self.tempActionName = actionName
                    tempfunc = self.defaultModFunc
                elif numBIns == 0 and numCIns == 0:
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
                # # print(e)
                # tempfunc = errorFunc
                #print(e)
                tempfunc = self.errorFunc

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
        # Ensure all file tabs are synchronized
        self.parent.syncFileTabs()
        # Update the base information tool with the current file's information
        if hasattr(self.parent, 'rootwindow') and self.parent.rootwindow is not None:
            self.parent.rootwindow.updateToolBars()

    def onClose(self, ind):
        """Remove closed tab from all data views."""
        self.parent.workflowTab.onClose(ind)
        self.removeTab(ind)
        self.parent.updateEntries()
        # Ensure all tabs are synchronized after closing
        # Ensure all tabs are synchronized after closing
        if hasattr(self, 'parent') and self.parent is not None:
            self.parent.syncFileTabs()

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
        # Ensure all file tabs are synchronized
        self.parent.syncFileTabs()
        # Update the base information tool with the current file's information
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            self.rootwindow.updateToolBars()

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
        """Open a new tab at the specified position and update other data views."""
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
        self.insertTab(tabInd, workflowTab, tabName)
        # Ensure the newly created tab is selected
        self.setCurrentIndex(tabInd)
        # Update toolbars to refresh experiment description box
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            self.rootwindow.updateToolBars()
        # Ensure all tabs are synchronized
        if hasattr(self, 'parent') and self.parent is not None:
            self.parent.syncFileTabs()

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
        # Update toolbars to refresh experiment description box
        if hasattr(self, 'rootwindow') and self.rootwindow is not None:
            self.rootwindow.updateToolBars()
        # Ensure all tabs are synchronized after closing
        if hasattr(self, 'parent') and self.parent is not None:
            self.parent.syncFileTabs()

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

        self.addNavLayout()

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
            self.zoomIn()
        else:
            self.zoomOut()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

    def zoomIn(self):
        zoom_in_factor = 1.1
        if self.zoom_times == 15:
                return
        zoom_factor = zoom_in_factor
        self.zoom_times += 1
        self.scale(zoom_factor, zoom_factor)

    def zoomOut(self):
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor
        if self.zoom_times == -20:
                return
        zoom_factor = zoom_out_factor
        self.zoom_times -= 1
        self.scale(zoom_factor, zoom_factor)

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
        if not isinstance(event, bool):
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

    def zoomFit(self):
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        window_size = self.size()
        window_dims = [window_size.width(), window_size.height()]
        
        positions = []
        for key in self.s.mainEntry['Objects']:
            positions.append(self.s.mainEntry['Objects'][key]['position'])
        positions = np.array(positions)
        if len(positions) == 0:
            self.center = [0, 0]
        elif len(positions) == 1:
            self.center = [positions[0][0] - 500, positions[0][1] - 250]
        else:
            x_min = min(positions[:,0])
            x_max = max(positions[:,0])
            y_min = min(positions[:,1])
            y_max = max(positions[:,1])
            width = x_max - x_min
            height = y_max - y_min
            self.center = [x_min + 0.5 * width - 500, y_min + 0.5 * height - 250]
        self.setSceneRect(self.center[0], self.center[1], 1000, 500)


        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()

    def addNavLayout(self):
        """Build the layout containing the workflow navigation buttons."""
        self.navLayout = QHBoxLayout()
        self.navLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy().Expanding, QSizePolicy().Minimum))

        self.pan_up = QToolButton()
        self.pan_up.setArrowType(Qt.UpArrow)
        self.pan_up.clicked.connect(self.onPanUp)
        self.navLayout.addWidget(self.pan_up)

        self.pan_down = QToolButton()
        self.pan_down.setArrowType(Qt.DownArrow)
        self.pan_down.clicked.connect(self.onPanDown)
        self.navLayout.addWidget(self.pan_down)
        
        self.pan_left = QToolButton()
        self.pan_left.setArrowType(Qt.LeftArrow)
        self.pan_left.clicked.connect(self.onPanLeft)
        self.navLayout.addWidget(self.pan_left)
        
        self.pan_right = QToolButton()
        self.pan_right.setArrowType(Qt.RightArrow)
        self.pan_right.clicked.connect(self.onPanRight)
        self.navLayout.addWidget(self.pan_right)

        # TODO: Ugly!
        self.zoom_in = QPushButton("+")
        self.zoom_in.clicked.connect(self.onZoomIn)
        self.navLayout.addWidget(self.zoom_in)
        
        # TODO: Ugly!
        self.zoom_out = QPushButton("-")
        self.zoom_out.clicked.connect(self.onZoomOut)
        self.navLayout.addWidget(self.zoom_out)
        
        # TODO: Ugly!
        self.zoom_fit = QPushButton("Center")
        self.zoom_fit.clicked.connect(self.onZoomFit)
        self.navLayout.addWidget(self.zoom_fit)

        self.navVerLayout = QVBoxLayout()
        self.navVerLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy().Minimum, QSizePolicy().Expanding))
        self.navVerLayout.addLayout(self.navLayout)
        self.setLayout(self.navVerLayout)

    def onZoomIn(self, event):
        self.onZoom(event, direction="in")

    def onZoomOut(self, event):
        self.onZoom(event, direction="out")

    def onZoom(self, event, direction):
        if direction == "in":
            self.zoomIn()
        elif direction == "out":
            self.zoomOut()

    def onZoomFit(self, event):
        self.zoomFit()

    def onPanUp(self, event):
        self.onPan(event, direction="up")

    def onPanDown(self, event):
        self.onPan(event, direction="down")

    def onPanLeft(self, event):
        self.onPan(event, direction="left")

    def onPanRight(self, event):
        self.onPan(event, direction="right")

    def onPan(self, event, direction):
        self.panstepEvt(event=event, direction=direction, rate='slow')

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
        
        # Add Ctrl+S shortcut to save the workflow
        self.saveShortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        self.saveShortcut.activated.connect(self.onSaveWorkflow)

    def buildWidgets(self):
        """Add data entry widgets and graphics scene to section window."""
        windowTitle = self.data['Name']
        if windowTitle == '':
            windowTitle = get_translation(babelFish, self.lankey, 'widgets', '(Untitled)')
        self.setWindowTitle(windowTitle)
        self.mainLayout = QHBoxLayout()
        self.addWorkflowWidget()
        self.addInfoWidget()
        self.setLayout(self.mainLayout)

    def addWorkflowWidget(self):
        """Add widget containing workflow and navigation tools."""
        self.graphicView = ViewClass(
            parent=self, rootwindow=self.rootwindow, lankey=self.lankey)
        self.mainLayout.addWidget(self.graphicView, QSizePolicy().Expanding)

    def addInfoWidget(self):
        """Add name and description entry widgets."""
        self.infoLayout = QGridLayout()

        namelabel = get_translation(babelFish, self.lankey, 'section', 'Section Name:')
        self.nameLabel = QLabel(namelabel)
        self.infoLayout.addWidget(self.nameLabel, 0, 0)

        self.nameWidget = QLineEdit()
        self.nameWidget.setFixedWidth(200)
        # Don't connect textChanged to updateData to avoid overwriting data during typing
        # self.nameWidget.textChanged.connect(self.updateData)
        self.infoLayout.addWidget(self.nameWidget, 1, 0)

        desclabel = get_translation(babelFish, self.lankey, 'section', 'Section Description:')
        self.descriptionLabel = QLabel(desclabel)
        self.infoLayout.addWidget(self.descriptionLabel, 2, 0)

        self.descriptionWidget = QTextEdit()
        self.descriptionWidget.setFixedWidth(200)
        # Don't connect textChanged to updateData to avoid overwriting data during typing
        # self.descriptionWidget.textChanged.connect(self.updateData)
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
            windowTitle = get_translation(babelFish, self.lankey, 'widgets', '(Untitled)')
        self.setWindowTitle(windowTitle)

        self.item.textItem.changeText(self.data['Name'])
        self.item.parent.updateEntryEdges()
        self.item.parent.addBlocksEdgesFromData()

        self.windowSignal.emit(self.data)
        
    def onSaveWorkflow(self):
        """Handle Ctrl+S shortcut to save the main workflow."""
        # First update the section data
        self.updateData()
        # Then trigger the main window's save functionality
        if hasattr(self.rootwindow, 'onSave'):
            self.rootwindow.onSave()


class SceneClass(QGraphicsScene):
    """Graphics display widget for individual workflows."""

    grid = 120

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
                          'Objects': {},
                          'Format': 'uwl'
                          }

        self.objectKeys = []

    def mouseMoveEvent(self, event):
        """Update saved mouse position and pass event forward."""
        self.temppos = event.scenePos()
        QGraphicsScene.mouseMoveEvent(self, event)

    def drawBackground(self, painter, rect):
        """Overwrite drawBackground operation for custom color."""
        painter.fillRect(rect, QColor(96, 98, 97))
        lines = []
        left = int(rect.left()) - int((rect.left()) % self.grid)
        top = int(rect.top()) - int((rect.top()) % self.grid)
        right = int(rect.right())
        bottom = int(rect.bottom())
        for x in range(left, right, self.grid):
            lines.append(QLineF(x, top, x, bottom))
        for y in range(top, bottom, self.grid):
            lines.append(QLineF(left, y, right, y))
        painter.setPen(QPen(QColor(130, 130, 130)))
        painter.drawLines(lines)

    def contextMenuEvent(self, event):
        """Build and display context menu on right click."""
        lankey = self.rootwindow.lankey

        self.temppos = event.scenePos()
        menu = QMenu()

        createActionBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Create Action Block'))
        createActionBtn.setShortcut('Shift+D')
        createActionBtn.triggered.connect(self.onNewActionBlock)

        createItemBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Create Item Block'))
        createItemBtn.setShortcut('Shift+F')
        createItemBtn.triggered.connect(self.onNewItemBlock)

        createSectionBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Create Section Block'))
        createSectionBtn.setShortcut('Shift+G')
        createSectionBtn.triggered.connect(self.onNewSection)

        loadBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Insert from File'))
        loadBtn.setShortcut('Ctrl+I')
        loadBtn.triggered.connect(self.onLoadBlock)

        loadBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Insert from File as Section'))
        loadBtn.setShortcut('Ctrl+Shift+I')
        loadBtn.triggered.connect(self.onLoadBlockasSection)

        addAActionBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Add A-Type Connections'))
        addAActionBtn.setShortcut('Shift+1')
        addAActionBtn.triggered.connect(self.onAddAType)

        addBActionBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Add B-Type Connections'))
        addBActionBtn.setShortcut('Shift+2')
        addBActionBtn.triggered.connect(self.onAddBType)

        addCActionBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Add C-Type Connections'))
        addCActionBtn.setShortcut('Shift+3')
        addCActionBtn.triggered.connect(self.onAddCType)

        copyBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Copy'))
        copyBtn.setShortcut('Ctrl+C')
        copyBtn.triggered.connect(self.onCopyBlock)

        pasteBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Paste'))
        pasteBtn.setShortcut('Ctrl+V')
        pasteBtn.triggered.connect(self.onPasteBlock)

        replaceBtn = menu.addAction("Replace block from file")
        replaceBtn.triggered.connect(self.onReplaceBlock)

        selectBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Select All'))
        selectBtn.setShortcut('Ctrl+A')
        selectBtn.triggered.connect(self.onSelectAll)

        delBtn = menu.addAction(get_translation(babelFish, lankey, 'scene context', 'Delete'))
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

        isOneBlock = self.checkIfOneBlockSelected()
        if not isOneBlock:
            replaceBtn.setEnabled(False)

        menu.exec_(event.screenPos())

    def keyPressEvent(self, event):
        """Intercept key press events and pass to shortcut functions."""
        mods = QApplication.keyboardModifiers()

        if event.key() == Qt.Key_Delete:
            self.runElementDelete()
            self.updateEntryEdges()
            self.addBlocksEdgesFromData()

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

    def checkIfOneBlockSelected(self):
        """Return whether only one block is selected."""
        if len(self.selectedItems()) == 1:
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
        self.newdata = data
        if self.newdata == []:
            return

        self.blockdata = self.newdata
        entryID = self.blockdata['ID']

        tempdata = copy.deepcopy(self.blockdata)
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
                # Only update position, preserve other data fields
                if 'position' not in item.data:
                    item.data['position'] = [0, 0]
                item.data['position'][0] = int(item.pos().x())
                item.data['position'][1] = int(item.pos().y())

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
        if not filename or filename.strip() == '':
            raise ValueError("Cannot save with empty filename")
            
        self.updateBlockPositionData()
        self.normalizeBlockPositions()

        tabname = os.path.basename(filename)
        tabname = os.path.splitext(tabname)[0]
        self.mainEntry['Name'] = tabname
        self.mainEntry['File'] = filename
        self.mainEntry['UWL Version'] = UWL_VERSION
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
        if not filename or filename.strip() == '':
            raise ValueError("Cannot save with empty filename")
            
        # TODO: How does this work differently from onSave?
        self.updateBlockPositionData()
        self.normalizeBlockPositions()

        tabname = os.path.basename(filename)
        tabname = os.path.splitext(tabname)[0]
        self.mainEntry['Name'] = tabname
        self.mainEntry['File'] = filename
        self.mainEntry['UWL Version'] = UWL_VERSION
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
        filter_string = "UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)"
        filename = QFileDialog.getOpenFileName(
            None, 'Import File', filter=filter_string)

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
        clipboard = self.normalizeClipboard(clipboard)
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

    def onReplaceBlock(self):
        """Replace selected block with block from file."""
        selected = {'ID': 'root',
                     'Objects': {}}
        for item in self.items():
            isBlock = (str(type(item)) ==
                       "<class '__main__.Block.<locals>.BlockBase'>")
            isSection = (str(type(item)) == "<class '__main__.Section'>")
            if isBlock or isSection:
                if item.isSelected():
                    selected['Objects'][item.data['ID']] = item.data
                    selected_item = item
                    selected_item_ID = item.data['ID']

        if len(selected['Objects']) > 1 or len(selected['Objects']) < 1:
            print('Select only one block to replace.')
            return
        
        selected_block = selected['Objects'][list(selected['Objects'].keys())[0]]

        filter_string = "UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)"
        filename = QFileDialog.getOpenFileName(
            None, 'Import File', filter=filter_string)

        if filename[0] == '':
            return
        
        importData = loadjson(filename[0])
        if len(importData['Objects']) != 1 or selected_block["Type"] == "Section":
            print('Select a file with only one block to replace.')
            return

        import_block = importData['Objects'][list(importData['Objects'].keys())[0]]
        
        if import_block['Type'] != selected_block['Type']:
            print('Block types do not match.')
            return
        
        replace_keys = ["Subtype", "Name", "Notes", "Parameters", "Values"]
        for key in replace_keys:
            selected_item.data[key] = import_block[key]
            self.mainEntry['Objects'][selected_item_ID][key] = import_block[key]

        self.addBlocksEdgesFromData()

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

    def insertBlock(self, importData, del_existing=False):
        """
        Insert workflow data as loose blocks.

        Parameters
        ----------
        importData : dict
            Workflow data to be inserted as loose blocks.

        del_existing : bool
            If true, delete all items in importData that share a name with an
            existing block in self.mainEntry and create an edge connected to
            the existing block.

        """
        self.updateBlockPositionData()
        importData = self.updatePosFromMouse(importData)

        importData = self.caseSwapDataObjectNames(importData)

        if self.mainEntry['Objects'] == {}:
            self.mainEntry['Objects'] = importData['Objects']
            newKeys = [k for k in importData['Objects'].keys()]
        else:
            importData = self.removeDislocatedEdges(importData)
            importData, newKeys = self.replaceImportDataKeys(importData)
            if del_existing:
                importData = self.delwireExistingBlocks(importData)

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

    def delwireExistingBlocks(self, importData):
        """
        Delete and rewire all overlapping item blocks.
        If an item block in import data shares a name with an item in
        self.mainEntry, then delete that item from importData and rewire the
        edge between the import action items and the item in self.mainEntry.

        Parameters
        ----------
        importData : dict
            Workflow data being imported into the main workflow.

        Returns
        -------
        importData : dict
            Workflow data with rewired action blocks and deleted item blocks.

        """
        action_keys = []
        for key in importData['Objects'].keys():
            if importData['Objects'][key]['Type'] == 'Action':
                action_keys.append(key)
        
        temp_import = copy.deepcopy(importData)
        for key in temp_import['Objects'].keys():
            if temp_import['Objects'][key]['Type'] == 'Item':
                import_name = temp_import['Objects'][key]['Name']
                for main_key in self.mainEntry['Objects'].keys():
                    main_name = self.mainEntry['Objects'][main_key]['Name']
                    if import_name == main_name:
                        del importData['Objects'][key]
                        for edge_type in ['A In', 'B In', 'C In']:
                            for action_key in action_keys:
                                if key in importData[
                                        'Objects'][action_key][edge_type]:
                                    importData['Objects'][
                                        action_key][edge_type].remove(key)
                                    importData['Objects'][
                                        action_key][edge_type].append(main_key)
                        break
        return copy.deepcopy(importData)

    def caseSwapDataObjectNames(self, data):
        """
        Fix the capitolization for every object in a workflow if in dictionary.

        Parameters
        ----------
        data : dict
            Workflow data to case adjust.

        Returns
        -------
        new_data : dict
            Workflow with case adjusted data.

        """
        new_data = copy.deepcopy(data)
        new_data = self.caseSwapDataObjectNamesbySection(data)
        return new_data

    def caseSwapDataObjectNamesbySection(self, section):
        """
        Fix object case for all objects in section.

        Parameters
        ----------
        section : dict
            Section workflow to case adjust.

        Returns
        -------
        section : dict
            Case adjust updated workflow.

        """
        for key in section['Objects'].keys():
            block = section['Objects'][key]
            if block['Type'] == 'Section':
                block = self.caseSwapDataObjectNamesbySection(block)
            else:
                textfound = False
                for name in babelFish[block['Type']].keys():
                    if block['Name'].casefold() == name.casefold():
                        textkey = name
                        block['Name'] = babelFish[
                            block['Type']][textkey][self.lankey]['Name']
                        textfound = True
                        break
                if not textfound:
                    continue
        return section

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
        openEntry['Name'] = os.path.splitext(os.path.basename(filename))[0]
        extension = os.path.splitext(filename)[-1]
        if extension in [".json", ".uwl"]:
            openEntry['Format'] = "uwl"
        elif extension in [".uwlt"]:
            openEntry['Format'] = "uwl_template"
        openEntry['Name'] = os.path.basename(filename)[:-4]

        openEntry = self.caseSwapDataObjectNames(openEntry)
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
                textfound = False
                for name in babelFish[self.blockType].keys():
                    if data['Name'].casefold() == name.casefold():
                        textkey = name
                        text = babelFish[
                            self.blockType][textkey][self.lankey]['Name']
                        textfound = True
                        break
                if not textfound:
                    #print(e)
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

        self.setWindowTitle(get_translation(babelFish, parent.rootwindow.lankey, 'widgets', 'New Section Info'))

        self.parent = parent
        self.pos = pos

        self.lankey = parent.rootwindow.lankey

        self.olddata = data

        self.objectKeys = objectKeys

        self.confirmed = False

        self.setWindowModality(Qt.ApplicationModal)
        self.move(QCursor.pos().x()-100, QCursor.pos().y()-50)

        self.layout = QGridLayout()
        namelabel = get_translation(babelFish, self.lankey, 'section', 'Section Name:')
        self.layout.addWidget(QLabel(namelabel), 0, 0)
        self.nameWidget = QLineEdit()
        self.nameWidget.setMinimumWidth(200)
        self.layout.addWidget(self.nameWidget, 0, 1)

        desclabel = get_translation(babelFish, self.lankey, 'section', 'Section Description:')
        self.layout.addWidget(QLabel(desclabel), 1, 0)
        self.descriptionWidget = QTextEdit()
        self.descriptionWidget.setMinimumWidth(200)
        self.layout.addWidget(self.descriptionWidget, 1, 1)

        addlabel = get_translation(babelFish, self.lankey, 'section', 'Confirm')
        addBtn = QPushButton(addlabel)
        addBtn.setFixedWidth(120)
        addBtn.clicked.connect(self.onConfirm)
        self.layout.addWidget(addBtn, 2, 0)

        cancellabel = get_translation(babelFish, self.lankey, 'section', 'Cancel')
        cancelBtn = QPushButton(cancellabel)
        cancelBtn.setFixedWidth(120)
        cancelBtn.clicked.connect(self.closeEvent)
        self.layout.addWidget(cancelBtn, 2, 1)

        self.setLayout(self.layout)

    def onConfirm(self):
        """Close window and emit entered data on confirm button click."""
        self.confirmed = True

        self.objectKeys = [round(float(ii)) for ii in self.objectKeys]

        # Handle position - if pos is empty list, use default position
        if isinstance(self.pos, list) and len(self.pos) == 0:
            position = [0, 0]  # Default position when no mouse position available
        else:
            position = [int(self.pos.x()), int(self.pos.y())]

        self.data = {'Type': 'Section',
                     'Name': self.nameWidget.text(),
                     'Description': self.descriptionWidget.toPlainText(),
                     'Objects': {},
                     'position': position}

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
            self.blockLabel = get_translation(babelFish, self.lankey, 'widgets', 'New Action Block Entry')
        elif blockType == 'Item':
            self.blockLabel = get_translation(babelFish, self.lankey, 'widgets', 'New Item Block Entry')

        self.setWindowTitle(self.blockLabel)

        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Block Class:')), 1, 0)
        if blockType == 'Action':
            self.typeWidget = QLabel(get_translation(babelFish, self.lankey, 'new block', 'Action'))
        elif blockType == 'Item':
            self.typeWidget = QLabel(get_translation(babelFish, self.lankey, 'new block', 'Item'))

        self.layout.addWidget(self.typeWidget, 1, 1)

        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Block Sub-Class:')), 2, 0)
        self.subtypeWidget = QComboBox()
        self.subtypeWidget.addItems(self.subtypeChoices(blockType))
        self.subtypeWidget.currentIndexChanged.connect(self.onSubtypeChange)
        self.layout.addWidget(self.subtypeWidget, 2, 1)

        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Name:')), 3, 0)
        self.nameWidget = autocompleteLineEdit()
        self.nameWidget.clicked.connect(self.onNameClick)
        if self.nameWidget.text() == '':
            self.nameWidget.setPlaceholderText(
                self.subtypeWidget.currentText())
        self.layout.addWidget(self.nameWidget, 3, 1)
        self.setNameCompleter()

        self.linkLabel = QLabel(get_translation(babelFish, self.lankey, 'new block', 'Linked Item:'))
        self.layout.addWidget(self.linkLabel, 4, 0)
        self.linkWidget = QCheckBox()
        self.linkWidget.stateChanged.connect(self.onLinkBoxClick)
        self.layout.addWidget(self.linkWidget, 4, 1)
        if blockType == 'Action':
            self.linkLabel.hide()
            self.linkWidget.hide()

        self.linkIDLabel = QLabel(get_translation(babelFish, self.lankey, 'new block', 'Link ID:'))
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

        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Parameters')), 6, 0)
        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Values')), 6, 1)

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

        addParamBtn = QPushButton(get_translation(babelFish, self.lankey, 'new block', '+ Add Parameter'))
        addParamBtn.setFixedWidth(150)
        addParamBtn.clicked.connect(self.onParamAdd)

        self.layout.addWidget(addParamBtn, 8, 0)

        self.layout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'new block', 'Notes:')), 9, 0)
        self.notes = QTextEdit()
        self.layout.addWidget(self.notes, 9, 1)

        addBtn = QPushButton(get_translation(babelFish, self.lankey, 'new block', 'Confirm'))
        addBtn.setFixedWidth(120)
        addBtn.clicked.connect(self.onConfirm)
        self.layout.addWidget(addBtn, 10, 0)

        cancelBtn = QPushButton(get_translation(babelFish, self.lankey, 'new block', 'Cancel'))
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
        self.nameCompleter.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive)
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
        self.paramCompleter.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive)
        self.paramCompleter.setModelSorting(QCompleter.UnsortedModel)
        for widget in self.paramWidgets:
            widget.setCompleter(self.paramCompleter)

    def setLinkCompleter(self):
        """Generate link ID completer list and link to link completer."""
        self.linkCompleter = QCompleter(self.linkIDs)
        self.linkCompleter.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive)
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
        self.msgOpen = True
        self.msg = QMessageBox()
        msgtxt = get_translation(babelFish, self.lankey, 'new block', 'The data in this block will be linked to the selected link ID.') + ' '
        msgtxt += get_translation(babelFish, self.lankey, 'new block', 'All other data in this block will be overwritten.\n') + '\n'
        msgtxt += get_translation(babelFish, self.lankey, 'new block', 'Would you like to continue?')
        self.msg.setText(msgtxt)
        yesBtn = self.msg.addButton(get_translation(babelFish, self.lankey, 'new block', 'Yes'), QMessageBox.YesRole)
        yesBtn.clicked.connect(self.onMsgYes)
        noBtn = self.msg.addButton(get_translation(babelFish, self.lankey, 'new block', 'No'), QMessageBox.NoRole)
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
                ind_en = next(ii for ii, item in enumerate(
                            self.completeList) if item.lower(
                                ) == self.nameWidget.text())
                ind_en = next(ii for ii, item in enumerate(
                            self.completeList) if item.lower(
                                ) == self.nameWidget.text())
                block['Name'] = self.completeList_en[ind_en]
            except Exception as e:
                # print(e)
                #print(e)
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
                    # print(e)
                    #print(e)
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
        if data != []:
            if self.blockType == 'Action':
                self.typeWidget.setText(get_translation(babelFish, self.lankey, 'new block', 'Action'))
            elif self.blockType == 'Item':
                self.typeWidget.setText(get_translation(babelFish, self.lankey, 'new block', 'Item'))

            subtypeLbl = babelFish[self.blockType][data['Subtype']
                                                   ][self.lankey]['Name']
            self.subtypeWidget.setCurrentText(subtypeLbl)

            try:
                nameLbl = babelFish[self.blockType][data['Name']
                                                    ][self.lankey]['Name']
            except Exception as e:
                # print(e)
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
                    # print(e)
                    self.paramWidgets[ii].insert(data['Parameters'][ii])

                self.valueWidgets[ii].insert(data['Values'][ii])
                self.onParamAdd()

class ExperimentDesignWindow(QWidget):
    windowSignal = Signal(object)
    def __init__(self, lankey='en'):
        super().__init__()
        
        self.lankey = lankey
        self.layout = QVBoxLayout()
        
        self.setWindowModality(Qt.ApplicationModal)
        self.file_path = ""
        self.confirmed = False
        self.paramList = []
        
        self.addDesignTypeWidgets()
        self.addRootFileWidgets()
        self.addRootNameWidgets()
        self.addParametersWidgets()
        self.addConfirmWidgets()
        
        self.layout.addItem(QSpacerItem(0, 0,
                                        QSizePolicy.Minimum,
                                        QSizePolicy.Expanding))
        self.setLayout(self.layout)

    def spacer(self, method="min"):
        if method == "min":
            spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        elif method == "hor-exp":
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        return spacer

    def addDesignTypeWidgets(self):
        self.layoutDesignType = QHBoxLayout()
        self.layoutDesignType.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Design Method:')))
        
        self.designTypeWidget = QComboBox()
        design_methods = [
            get_translation(babelFish, self.lankey, 'widgets', 'Random'),
            get_translation(babelFish, self.lankey, 'widgets', 'Grid'),
            get_translation(babelFish, self.lankey, 'widgets', 'Latin Hypercube'),
            get_translation(babelFish, self.lankey, 'widgets', 'Minimax')
        ]
        self.designTypeWidget.addItems(design_methods)
        self.layoutDesignType.addWidget(self.designTypeWidget)
        self.designTypeWidget.currentIndexChanged.connect(
            self.updateParamWidgets)
        
        self.layoutDesignType.addItem(self.spacer("hor-exp"))
        
        self.layout.addLayout(self.layoutDesignType)
        
        
    def addRootFileWidgets(self):
        self.layoutRootFile = QHBoxLayout()
        self.layoutRootFile.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Root UWL:')))

        self.filepathIndicatorWidget = QLabel(get_translation(babelFish, self.lankey, 'widgets', '** Select File to View Parameters **'))
        self.layoutRootFile.addWidget(self.filepathIndicatorWidget)
        
        self.browseRootFileWidget = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Browse'))
        self.browseRootFileWidget.clicked.connect(self.open_file_browser)
        self.layoutRootFile.addWidget(self.browseRootFileWidget)
        
        self.layoutRootFile.addItem(self.spacer("hor-exp"))
        
        self.layout.addLayout(self.layoutRootFile)

    def addRootNameWidgets(self):
        self.layoutRootName = QHBoxLayout()
        self.layoutRootName.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Root File Name:')))
        
        self.rootNameWidget = QLineEdit()
        self.rootNameWidget.editingFinished.connect(self.updateParamWidgets)
        self.updateRootNameWidget()
            
        self.layoutRootName.addWidget(self.rootNameWidget)
        self.layoutRootFile.addItem(self.spacer("hor-exp"))

        self.layoutRootName.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Number of New Experiments:')))

        self.numExpWidget = QLineEdit()
        self.numExpWidget.setValidator(QIntValidator(0, 999999))
        self.numExpWidget.editingFinished.connect(self.updateParamWidgets)
        self.numExpWidget.setMaximumWidth(100)
        self.layoutRootName.addWidget(self.numExpWidget)
        self.layoutRootFile.addItem(self.spacer("hor-exp"))

        self.layout.addLayout(self.layoutRootName)
    
    def updateRootNameWidget(self):
        if self.file_path == "":
            self.rootNameWidget.setText(get_translation(babelFish, self.lankey, 'widgets', 'Experiment_#'))
        else:
            fname = os.path.basename(self.file_path)
            self.rootNameWidget.setText(f"{os.path.splitext(fname)[0]}_#")
    
    def open_file_browser(self):
        # Open a file dialog and get the selected file path
        filter_string = get_translation(babelFish, self.lankey, 'widgets', 'UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)')
        temp_file_path, _ = QFileDialog.getOpenFileName(self, get_translation(babelFish, self.lankey, 'widgets', 'Open File'), "", filter_string)
        
        if temp_file_path != "" and temp_file_path != self.file_path:
            self.file_path = temp_file_path
            self.filepathIndicatorWidget.setText(self.file_path)
            self.updateRootNameWidget()
            self.getParameterList()
            self.updateParamWidgets()
            self.updateDesignData()

    def getParameterList(self):
        workflow = loadjson(self.file_path)
        
        paramListObj = TabViewController()
        paramListObj.entrynames, paramListObj.tableNames = [], []
        paramListObj.addSectionTableNames(workflow, keyPath=[])
        
        self.keyPathLists = paramListObj.keyPathLists
        self.paramList = paramListObj.tableNames
       
    def addParametersWidgets(self):
        self.init_param_dict = {"parameter": "",
                                "dtype": "Numerical-Continuous",
                                "units": "",
                                "disc_levels": 3,
                                "min_bnd": -100,
                                "max_bnd": 100,
                                "categories": ["", ""],
                                "scale": "Linear",
                                "levels": 5
                                }
        self.designData = [self.init_param_dict.copy()]
        
        self.designType = "Random"
        
        self.paramLayout = QGridLayout()
        self.updateParamWidgets()
        self.layout.addLayout(self.paramLayout)
        
    def updateParamWidgets(self):
        self.clear_grid_layout()
        self.init_designWidgets()
        
        self.designType = self.designTypeWidget.currentText()
        self.designNumExp = self.numExpWidget.text()
        self.designRootName = self.rootNameWidget.text()

        self.updateNumberExperiments()
        self.updateBounds()

        max_row = 0
        self.paramLayouts = []
        for row_ind, paramDataRow in enumerate(self.designData):
            self.addParamRowWidget(row_ind, paramDataRow)
            max_row = row_ind
        
        if not max_row >= (len(self.paramList) -1):
            self.addRowBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', '+ Add Parameter'))
            self.addRowBtn.setFixedWidth(400)
            self.addRowBtn.clicked.connect(self.onAddRow)
            self.paramLayout.addWidget(self.addRowBtn, max_row + 1, 1)
            self.paramLayout.addItem(self.spacer("hor-exp"), max_row + 1, 2)

    def updateNumberExperiments(self):
        if self.numExpWidget.text() == "":
            self.numExpWidget.setText("1")
            numExp = 1
        else:
            numExp = int(self.numExpWidget.text())

        if self.designType in ["Random"]:
            if numExp < 1:
                numExp = 1
        elif self.designType in ["Grid"]:
            numExp = self.getNumExp_Grid()
        elif self.designType in ["Latin Hypercube", "Minimax"]:
            numExp = self.getNumExp_LatinHypercube()

        self.numExpWidget.setText(str(numExp))
        self.numExp = numExp

    def updateBounds(self):
        for row_ind, paramDataRow in enumerate(self.designData):
            if paramDataRow["dtype"] in ["Numerical-Integer",
                                         "Numerical-Continuous",
                                         "Numerical-Discrete"]:
                if paramDataRow["scale"] == "Log":
                    for key in ["min_bnd", "max_bnd"]:
                        if float(paramDataRow[key]) < 0:
                            self.designData[row_ind][key] = 0.1
                
                if float(paramDataRow["min_bnd"]) > float(paramDataRow["max_bnd"]):
                     min_val = str(float(paramDataRow["min_bnd"]))
                     max_val = str(float(paramDataRow["max_bnd"]))
                     self.designData[row_ind]["min_bnd"] = max_val
                     self.designData[row_ind]["max_bnd"] = min_val

                if float(paramDataRow["min_bnd"]) == float(paramDataRow["max_bnd"]):
                     self.designData[row_ind]["max_bnd"] = str(float(paramDataRow["min_bnd"]) + 1)

    def getNumExp_Grid(self):
        numExp = 1
        for param in self.designData:
            if param["dtype"] in ["Numerical-Integer", "Numerical-Continuous"]:
                numExp = numExp * int(param["levels"])
            elif param["dtype"] in ["Numerical-Discrete"]:
                numExp = numExp * int(param["disc_levels"])
            elif param["dtype"] in ["Categorical"]:
                numExp = numExp * len(param["categories"])
        return numExp

    def getNumExp_LatinHypercube(self):
        numExp = 1
        for param in self.designData:
            if param["dtype"] in ["Numerical-Integer", "Numerical-Continuous"]:
                numExp = max([numExp, 2])
            elif param["dtype"] in ["Numerical-Discrete"]:
                numExp = max([numExp, int(param["disc_levels"])])
            elif param["dtype"] in ["Categorical"]:
                numExp = max([numExp, len(param["categories"])])
        numExp = max([numExp, int(self.numExpWidget.text())])
        return numExp

    def init_designWidgets(self):
        self.designWidgets = []
        for row in self.designData:
            self.designWidgets.append({})
            
    def addParamRowWidget(self, row_ind, paramRow):
        delRowBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'x'))
        delRowBtn.setMaximumWidth(30)
        delRowBtn.clicked.connect(self.onRowDelete)
        self.paramLayout.addWidget(delRowBtn, row_ind, 0)
        self.addParamWidget(row_ind, paramRow)
        
    def addParamWidget(self, row_ind, paramRow):
        self.paramLayouts.append(QHBoxLayout())
        self.addParam_parameter(row_ind, paramRow)
        
        self.addParam_dtype(row_ind, paramRow)
        self.addParam_units(row_ind, paramRow)
        
        if paramRow["dtype"] in ["Numerical-Continuous",
                                 "Numerical-Discrete",
                                 "Numerical-Integer"]:
            self.addParam_scale(row_ind, paramRow)
            self.addParam_minmax(row_ind, paramRow)
        
        if paramRow['dtype'] == "Numerical-Discrete":
            self.addParam_discLevels(row_ind, paramRow)
            
        if self.designType in ["Grid"]:
            if paramRow['dtype'] in ["Numerical-Continuous",
                                     "Numerical-Integer"]:
                self.addParam_levels(row_ind, paramRow)
            
        if paramRow["dtype"] == "Categorical":
            self.addParam_categories(row_ind, paramRow)
        
        self.paramLayouts[row_ind].addItem(self.spacer("hor-exp"))
        self.connectParamLayoutWidgets_updateDesignonChange()
        self.paramLayout.addLayout(self.paramLayouts[row_ind], row_ind, 1)
    
    def connectParamLayoutWidgets_updateDesignonChange(self):
        for ii in range(len(self.designWidgets)):
            for key in self.designWidgets[ii].keys():
                if isinstance(self.designWidgets[ii][key], QComboBox):
                    self.designWidgets[ii][key].currentIndexChanged.connect(
                        self.onWidgetChange)
                elif isinstance(self.designWidgets[ii][key], QLineEdit):
                    self.designWidgets[ii][key].editingFinished.connect(
                        self.onWidgetChange)
                elif key == "categories":
                    for jj in range(self.designWidgets[ii][key].count()):
                        widget = self.designWidgets[ii][key].itemAt(
                            jj).widget()
                        if isinstance(widget, QLineEdit):
                            widget.editingFinished.connect(self.onWidgetChange)
        
    def onWidgetChange(self):
        self.updateDesignData()                    
        self.updateParamWidgets()
    
    def updateDesignData(self):
        for ii in range(len(self.designWidgets)):
            for key in self.designWidgets[ii].keys():
                if isinstance(self.designWidgets[ii][key], QComboBox):
                    self.designData[ii][key] = self.designWidgets[
                        ii][key].currentText()
                elif isinstance(self.designWidgets[ii][key], QLineEdit):
                    self.designData[ii][key] = self.designWidgets[
                        ii][key].text()
                elif key == "categories":
                    cat_list = []
                    for jj in range(self.designWidgets[ii][key].count()):
                        widget = self.designWidgets[ii][key].itemAt(
                            jj).widget()
                        if isinstance(widget, QLineEdit):
                            cat_list.append(widget.text())
                    self.designData[ii][key] = cat_list

    def addParam_parameter(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Parameter:')))
        self.designWidgets[row_ind]["parameter"] = QComboBox()
        
        self.designWidgets[row_ind]["parameter"].addItems(self.paramList)
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["parameter"])

        used_params = [self.designData[ii]["parameter"] for ii in range(len(self.designData))]

        if used_params[0] != "" and self.designData[row_ind]["parameter"] == "":
            param_ind = 0
            while self.paramList[param_ind] in used_params:
                param_ind += 1
            
            self.designData[row_ind]["parameter"] = self.paramList[param_ind]

        self.designWidgets[row_ind]["parameter"].setCurrentText(
            self.designData[row_ind]["parameter"])
        self.paramLayouts[row_ind].addItem(self.spacer())
        
    def addParam_dtype(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Data Type:')))
        self.designWidgets[row_ind]["dtype"] = QComboBox()
        self.designWidgets[row_ind]["dtype"].addItems([get_translation(babelFish, self.lankey, 'widgets', 'Numerical-Continuous'),
                                                       get_translation(babelFish, self.lankey, 'widgets', 'Numerical-Integer'),
                                                       get_translation(babelFish, self.lankey, 'widgets', 'Numerical-Discrete'),
                                                       get_translation(babelFish, self.lankey, 'widgets', 'Categorical')])
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["dtype"])
        self.designWidgets[row_ind]["dtype"].setCurrentText(
            self.designData[row_ind]["dtype"])
        
        self.paramLayouts[row_ind].addItem(self.spacer())
    
    def addParam_scale(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Scale:')))
        self.designWidgets[row_ind]["scale"] = QComboBox()
        self.designWidgets[row_ind]["scale"].addItems([get_translation(babelFish, self.lankey, 'widgets', 'Linear'), get_translation(babelFish, self.lankey, 'widgets', 'Log')])
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["scale"])
        self.designWidgets[row_ind]["scale"].setCurrentText(
            self.designData[row_ind]["scale"])
        self.paramLayouts[row_ind].addItem(self.spacer())

    def addParam_units(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Units (optional):')))
        self.designWidgets[row_ind]["units"] = QLineEdit()
        self.paramLayouts[row_ind].addWidget(self.designWidgets[row_ind]["units"])
        self.designWidgets[row_ind]["units"].setText(
            str(self.designData[row_ind]["units"]))
        
        self.paramLayouts[row_ind].addItem(self.spacer())

    def addParam_minmax(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Min Bound:')))
        self.designWidgets[row_ind]["min_bnd"] = QLineEdit()
        if self.designData[row_ind]["dtype"] in ["Numerical-Continuous",
                                                 "Numerical-Discrete"]:
            self.designWidgets[row_ind]["min_bnd"].setValidator(
                QDoubleValidator(-float('inf'), float('inf'), 99)) 
        elif self.designData[row_ind]["dtype"] == "Numerical-Integer":
            self.designWidgets[row_ind]["min_bnd"].setValidator(
                QIntValidator())
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["min_bnd"])
        self.designWidgets[row_ind]["min_bnd"].setText(
            str(self.designData[row_ind]["min_bnd"]))
        
        self.paramLayouts[row_ind].addItem(self.spacer())
        
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Max Bound:')))
        self.designWidgets[row_ind]["max_bnd"] = QLineEdit()
        if self.designData[row_ind]["dtype"] in ["Numerical-Continuous",
                                                 "Numerical-Discrete"]:
            self.designWidgets[row_ind]["max_bnd"].setValidator(
                QDoubleValidator(-float('inf'), float('inf'), 99)) 
        elif self.designData[row_ind]["dtype"] == "Numerical-Integer":
            self.designWidgets[row_ind]["max_bnd"].setValidator(
                QIntValidator())  
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["max_bnd"])
        self.designWidgets[row_ind]["max_bnd"].setText(
            str(self.designData[row_ind]["max_bnd"]))
        
        self.paramLayouts[row_ind].addItem(self.spacer())
        
    def addParam_discLevels(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Discrete Levels:')))
        self.designWidgets[row_ind]["disc_levels"] = QLineEdit()
        self.designWidgets[row_ind]["disc_levels"].setValidator(
            QIntValidator(0, 999999)) 
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["disc_levels"])
        self.designWidgets[row_ind]["disc_levels"].setText(
            str(self.designData[row_ind]["disc_levels"]))
        
        self.paramLayouts[row_ind].addItem(self.spacer())

    def addParam_levels(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Levels:')))
        self.designWidgets[row_ind]["levels"] = QLineEdit()
        self.designWidgets[row_ind]["levels"].setValidator(
            QIntValidator(0, 999999)) 
        self.paramLayouts[row_ind].addWidget(
            self.designWidgets[row_ind]["levels"])
        self.designWidgets[row_ind]["levels"].setText(
            str(self.designData[row_ind]["levels"]))
        
        self.paramLayouts[row_ind].addItem(self.spacer())
        
    def addParam_categories(self, row_ind, paramRow):
        self.paramLayouts[row_ind].addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Categories:')))
        self.designWidgets[row_ind]["categories"] = QHBoxLayout()
        for cat in self.designData[row_ind]["categories"]:
            lineedit = QLineEdit(cat)
            self.designWidgets[row_ind]["categories"].addWidget(lineedit)
            
        self.paramLayouts[row_ind].addLayout(
            self.designWidgets[row_ind]["categories"])
        
        self.addCategoryBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', '+ Add Category'))
        self.addCategoryBtn.row_ind = row_ind
        self.addCategoryBtn.clicked.connect(self.onAddCategory)
        self.paramLayouts[row_ind].addWidget(self.addCategoryBtn)
        
        self.paramLayouts[row_ind].addItem(self.spacer())

    def onAddCategory(self, event):
        clicked_button = self.sender()
        cat_row_ind = clicked_button.row_ind

        self.designData[cat_row_ind]['categories'].append("")
        self.updateParamWidgets()

    def onAddRow(self, event):
        self.designData.append(self.init_param_dict.copy())
        self.updateParamWidgets()

    def onRowDelete(self, event):
        clicked_button = self.sender()
        for row in range(len(self.designData)):
            widget = self.paramLayout.itemAtPosition(row, 0).widget()
            if widget == clicked_button:
                del_row_ind = row
                
        self.designData.pop(del_row_ind)
        if self.designData == []:
            self.designData = [self.init_param_dict.copy()]
        self.updateParamWidgets()
    
    def addConfirmWidgets(self):
        self.confirmLayout = QHBoxLayout()
        self.confirmBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Generate Batch'))
        self.confirmBtn.clicked.connect(self.onConfirm)
        self.confirmLayout.addWidget(self.confirmBtn)
        
        self.cancelBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Cancel'))
        self.cancelBtn.clicked.connect(self.onCancel)
        self.confirmLayout.addWidget(self.cancelBtn)
    
        self.confirmLayout.addItem(self.spacer("hor-exp"))
    
        self.layout.addLayout(self.confirmLayout)

    def onConfirm(self, event):
        if self.file_path == "":
            QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'No File Selected'),
                                get_translation(babelFish, self.lankey, 'widgets', 'Please select a root UWL file to generate experiments.'))
            return
        
        self.confirmed = True
        parent_directory = QFileDialog.getExistingDirectory(self, get_translation(babelFish, self.lankey, 'widgets', 'Select Directory'))
        if parent_directory:
            self.createDateTimeDir(parent_directory)
            self.generateExperiments()
            self.saveExperiments()
            self.closeEvent(event)

    def onCancel(self, event):
        self.closeEvent(event)
    
    def closeEvent(self, event):
        """Emit blank data if not confirmed and close window."""
        if not self.confirmed:
            self.windowSignal.emit([])
        else:
            self.windowSignal.emit(self.designData)
        self.close()

    def clear_grid_layout(self):
        # Loop through all the items in the grid layout and remove them
        while self.paramLayout.count():
            item = self.paramLayout.takeAt(0)  # Remove the first item from the layout

            # If the item is a widget, delete it
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            # If the item is a layout, clear it recursively
            layout = item.layout()
            if layout is not None:
                self.clear_layout(layout)  # Call recursive function to clear nested layout

            # Finally, remove the layout item itself
            self.paramLayout.removeItem(item)

    def clear_layout(self, layout):
        """Recursively clear all widgets and nested layouts from a layout."""
        while layout.count():
            item = layout.takeAt(0)

            # If the item is a widget, delete it
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            # If the item is another layout, clear it recursively
            nested_layout = item.layout()
            if nested_layout is not None:
                self.clear_layout(nested_layout)

            # Remove the item
            layout.removeItem(item)

    def createDateTimeDir(self, parent_dir):
        dt_str = datetime.now().strftime("Generated_%Y-%m-%d_%H-%M-%S")
        self.dirpath = os.path.join(parent_dir, dt_str)
        os.makedirs(self.dirpath)

    def saveExperiments(self):
        root_UWL = loadjson(self.file_path)
        for ii, experiment in enumerate(self.experimentSet):
            temp_UWL = copy.deepcopy(root_UWL)
            for jj, experiment_val in enumerate(experiment):
                self.temp_units = self.designData[jj]["units"]
                if self.temp_units != "":
                    self.temp_units = " " + self.temp_units
                keypath = self.keyPathLists[self.paramList.index(self.designData[jj]["parameter"])]
                self.assignValuetoWorkflowThroughSection(temp_UWL, keypath, experiment_val)
            filename = self.rootNameWidget.text().replace("#", str(ii+1).zfill(3))
            filename += ".uwl"
            filepath = os.path.join(self.dirpath, filename)
            savejson(temp_UWL, filepath)

    def assignValuetoWorkflowThroughSection(self, section, keypath, value):
        if len(keypath) > 2:
            self.assignValuetoWorkflowThroughSection(section['Objects'][keypath[0]], keypath[1:], value)
        else:
            section['Objects'][keypath[0]]['Values'][keypath[1]] = str(value) + self.temp_units

    def generateExperiments(self):
        self.clearEmptyCategories()
        if self.designType == "Random":
            self.generateExperiments_Random()
        elif self.designType == "Grid":
            self.generateExperiments_Grid()
        elif self.designType == "Latin Hypercube":
            self.generateExperiments_LatinHypercube()
        elif self.designType == "Minimax":
            self.generateExperiments_Minimax()

    def clearEmptyCategories(self):
        for row_ind, param in enumerate(self.designData):
            if param["dtype"] == "Categorical":
                cat_list = self.designData[row_ind]["categories"]
                self.designData[row_ind]["categories"] = [value for value in cat_list if value != ""]

    def generateExperiments_Random(self):
        self.experimentSet = []
        for exp_num in range(self.numExp):
            experiment = []
            for param in self.designData:
                if param["dtype"] == "Numerical-Continuous":
                    min_bnd = float(param["min_bnd"])
                    max_bnd = float(param["max_bnd"])
                    if param["scale"] == "Linear":
                        param_val = random.uniform(min_bnd, max_bnd)
                    elif param["scale"] == "Log":
                        log_min_bnd = math.log10(min_bnd)
                        log_max_bnd = math.log10(max_bnd)
                        log_param_val = random.uniform(log_min_bnd, log_max_bnd)
                        param_val = 10 ** log_param_val

                elif param["dtype"] == "Numerical-Integer":
                    min_bnd = float(param["min_bnd"])
                    max_bnd = float(param["max_bnd"])
                    if param["scale"] == "Linear":
                        param_val = random.randint(min_bnd, max_bnd)
                    elif param["scale"] == "Log":
                        log_min_bnd = math.log10(min_bnd)
                        log_max_bnd = math.log10(max_bnd)
                        log_param_val = random.uniform(log_min_bnd, log_max_bnd)
                        param_val = round(10 ** log_param_val)
                
                elif param["dtype"] == "Numerical-Discrete":
                    min_bnd = float(param["min_bnd"])
                    max_bnd = float(param["max_bnd"])
                    levels = int(param["disc_levels"])
                    if param["scale"] == "Linear":
                        disc_list = np.linspace(min_bnd, max_bnd, levels).tolist()
                    elif param["scale"] == "Log":
                        log_min_bnd = math.log10(min_bnd)
                        log_max_bnd = math.log10(max_bnd)
                        disc_list = np.logspace(log_min_bnd, log_max_bnd, levels).tolist()
                    param_val = random.choice(disc_list)

                elif param["dtype"] == "Categorical":
                    param_val = random.choice(param["categories"])

                experiment.append(param_val)

            self.experimentSet.append(experiment)

    def generateExperiments_Grid(self):
        param_lists = []
        for param in self.designData:
            if param["dtype"] == "Numerical-Continuous":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                levels = int(param["levels"])
                if param["scale"] == "Linear":
                    param_list = np.linspace(min_bnd, max_bnd, levels).tolist()
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    param_list = np.logspace(log_min_bnd, log_max_bnd, levels).tolist()

            elif param["dtype"] == "Numerical-Integer":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                levels = int(param["levels"])
                if param["scale"] == "Linear":
                    param_list = np.linspace(min_bnd, max_bnd, levels, dtype=int).tolist()
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    param_list = np.logspace(log_min_bnd, log_max_bnd, levels, dtype=int).tolist()
            
            elif param["dtype"] == "Numerical-Discrete":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                levels = int(param["disc_levels"])
                if param["scale"] == "Linear":
                    param_list = np.linspace(min_bnd, max_bnd, levels).tolist()
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    param_list = np.logspace(log_min_bnd, log_max_bnd, levels).tolist()

            elif param["dtype"] == "Categorical":
                param_list = param["categories"]

            param_lists.append(param_list)

        self.experimentSet = [list(item) for item in itertools.product(*param_lists)]  
        random.shuffle(self.experimentSet)

    def generateExperiments_LatinHypercube(self):
        sampler = qmc.LatinHypercube(d=1)
        param_lists = []
        for param in self.designData:
            if param["dtype"] == "Numerical-Continuous":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                if param["scale"] == "Linear":
                    samples = sampler.random(self.numExp)
                    param_list = qmc.scale(samples, min_bnd, max_bnd)
                    param_list = [sample[0] for sample in param_list]
                    
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    samples = sampler.random(self.numExp)
                    param_list = 10 ** qmc.scale(samples, log_min_bnd, log_max_bnd)
                    param_list = [sample[0] for sample in param_list]

            elif param["dtype"] == "Numerical-Integer":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                if param["scale"] == "Linear":
                    samples = sampler.random(self.numExp)
                    param_list = qmc.scale(samples, min_bnd, max_bnd)
                    param_list = [int(sample[0]) for sample in param_list]

                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    samples = sampler.random(self.numExp)
                    samples = [sample[0] for sample in samples]
                    param_list = 10 ** qmc.scale(samples, log_min_bnd, log_max_bnd)
                    param_list = [int(sample[0]) for sample in param_list]
            
            elif param["dtype"] == "Numerical-Discrete":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                levels = int(param["disc_levels"])
                if param["scale"] == "Linear":
                    possible_values = np.linspace(min_bnd, max_bnd, levels).tolist()
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    possible_values = np.logspace(log_min_bnd, log_max_bnd, levels).tolist()

                loop_values = possible_values.copy()
                param_list = []
                for ii in range(self.numExp):
                    if len(loop_values) == 0:
                        loop_values = possible_values.copy()
                    value = random.choice(loop_values)
                    loop_values.remove(value)
                    param_list.append(value)


            elif param["dtype"] == "Categorical":
                possible_values = param["categories"]
                loop_values = possible_values.copy()
                param_list = []
                for ii in range(self.numExp):
                    if len(loop_values) == 0:
                        loop_values = possible_values.copy()
                    value = random.choice(loop_values)
                    loop_values.remove(value)
                    param_list.append(value)

            print(param, param_list)
            param_lists.append(param_list)
        self.experimentSet = np.array(param_lists).transpose()
        print(self.experimentSet)

    def generateExperiments_Minimax(self):
        sampler = qmc.LatinHypercube(d=1)
        nondim_param_lists = []
        num_param_inds = []
        for param_ind, param in enumerate(self.designData):
            if param["dtype"] != "Categorical":
                num_param_inds.append(param_ind)
            
            if param["dtype"] in ["Numerical-Continuous", "Numerical-Integer"]:
                samples = sampler.random(self.numExp)
                nondim_param_list = [sample[0] for sample in samples]
                
            elif param["dtype"] == "Numerical-Discrete":
                levels = int(param["disc_levels"])
                possible_values = np.linspace(0, 1, levels).tolist()
                loop_values = possible_values.copy()
                nondim_param_list = []
                for ii in range(self.numExp):
                    if len(loop_values) == 0:
                        loop_values = possible_values.copy()
                    value = random.choice(loop_values)
                    loop_values.remove(value)
                    nondim_param_list.append(value)

            nondim_param_lists.append(nondim_param_list)
            nondim_experiments = np.array(nondim_param_lists).transpose()

        nondim_experiments = self.optimize_minimax_lhs(nondim_experiments, self.numExp, len(self.designData))
        nondim_experiments = np.array(nondim_experiments)
        
        param_lists = []
        for param_ind, param in enumerate(self.designData):
            if param["dtype"] == "Numerical-Continuous":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                nondim_ind = num_param_inds.index(param_ind)
                samples = [[sample for sample in nondim_experiments[:, nondim_ind]]]

                if param["scale"] == "Linear":
                    param_list = qmc.scale(samples, min_bnd, max_bnd)[0]
                    
                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    param_list = 10 ** qmc.scale(samples, log_min_bnd, log_max_bnd)[0]

            elif param["dtype"] == "Numerical-Integer":
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                nondim_ind = num_param_inds.index(param_ind)
                samples = [[sample for sample in nondim_experiments[:, nondim_ind]]]
                if param["scale"] == "Linear":
                    param_list = qmc.scale(samples, min_bnd, max_bnd)[0]
                    param_list = [int(sample) for sample in param_list]

                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    param_list = 10 ** qmc.scale(samples, log_min_bnd, log_max_bnd)[0]
                    param_list = [max([int(sample), 1]) for sample in param_list]
            
            elif param["dtype"] == "Numerical-Discrete":
                levels = int(param["disc_levels"])
                min_bnd = float(param["min_bnd"])
                max_bnd = float(param["max_bnd"])
                nondim_ind = num_param_inds.index(param_ind)
                samples = [[sample for sample in nondim_experiments[:, nondim_ind]]]
                levels = int(param["disc_levels"])
                if param["scale"] == "Linear":
                    possible_values = np.linspace(min_bnd, max_bnd, levels).tolist()
                    samples = qmc.scale(samples, min_bnd, max_bnd)[0]
                    param_list = [possible_values[np.abs(possible_values - sample).argmin()] for sample in samples]

                elif param["scale"] == "Log":
                    log_min_bnd = math.log10(min_bnd)
                    log_max_bnd = math.log10(max_bnd)
                    possible_values = np.linspace(log_min_bnd, log_max_bnd, levels).tolist()
                    samples = qmc.scale(samples, log_min_bnd, log_max_bnd)[0]
                    param_list = [10**possible_values[np.abs(possible_values - sample).argmin()] for sample in samples]


            elif param["dtype"] == "Categorical":
                possible_values = param["categories"]
                loop_values = possible_values.copy()
                param_list = []
                for ii in range(self.numExp):
                    if len(loop_values) == 0:
                        loop_values = possible_values.copy()
                    value = random.choice(loop_values)
                    loop_values.remove(value)
                    param_list.append(value)

            param_lists.append(param_list)

        self.experimentSet = np.array(param_lists).transpose()

    def calculate_min_pairwise_distance(self, samples):
        """
        Calculate the minimum pairwise distance in the sample set.
        """
        dist_matrix = distance_matrix(samples, samples)
        np.fill_diagonal(dist_matrix, np.inf)  # Ignore self-distance
        min_distance = dist_matrix.min()
        return min_distance

    def objective_function(self, flat_samples, num_samples, num_dimensions):
        """
        Objective function to maximize the minimum pairwise distance.
        We return the negative of this value because SciPy minimizes functions.
        """
        samples = flat_samples.reshape((num_samples, num_dimensions))
        return -self.calculate_min_pairwise_distance(samples)

    def optimize_minimax_lhs(self, nondim_experiments, num_samples, num_dimensions, num_iterations=10000):
        """
        Generate an LHS and optimize it to approximate a Minimax design.
        """
        # Generate initial LHS sample
        flat_samples = nondim_experiments.flatten()

        opt_bnds = [(0,1) for ii in range(num_dimensions*num_samples)]

        # Run optimization
        result = minimize(
            self.objective_function,
            flat_samples,
            args=(num_samples, num_dimensions),
            method='L-BFGS-B',
            options={'maxiter': num_iterations},
            bounds=opt_bnds
        )

        # Reshape optimized sample back to original dimensions
        optimized_samples = result.x.reshape((num_samples, num_dimensions))
        return optimized_samples


class BuildTableMapWindow(QWidget):
    windowSignal = Signal(object)
    def __init__(self, lankey='en'):
        super().__init__()
        
        self.lankey = lankey
        self.resize(400, 400)

        self.layout = QVBoxLayout()
        self.setWindowModality(Qt.ApplicationModal)
        self.file_path = ""
        self.fname = ""
        self.confirmed = False
        self.paramList = []
        
        self.addRootFileWidgets()
        self.addParamWidgets()
        self.addConfirmWidgets()

        self.layout.addItem(self.spacer("min"))
        self.setLayout(self.layout)


    def spacer(self, method="min"):
        if method == "min":
            spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        elif method == "hor-exp":
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        return spacer

    def addRootFileWidgets(self):
        self.layoutRootFile = QHBoxLayout()
        self.layoutRootFile.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Root UWL:')))

        self.filepathIndicatorWidget = QLabel(get_translation(babelFish, self.lankey, 'widgets', '** Select File to View Parameters **'))
        self.layoutRootFile.addWidget(self.filepathIndicatorWidget)
        
        self.browseRootFileWidget = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Browse'))
        self.browseRootFileWidget.clicked.connect(self.open_file_browser)
        self.layoutRootFile.addWidget(self.browseRootFileWidget)
        
        self.layoutRootFile.addItem(self.spacer("hor-exp"))
        
        self.layout.addLayout(self.layoutRootFile)
    
    def open_file_browser(self):
        # Open a file dialog and get the selected file path
        filter_string = get_translation(babelFish, self.lankey, 'widgets', 'UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)')
        temp_file_path, _ = QFileDialog.getOpenFileName(self, get_translation(babelFish, self.lankey, 'widgets', 'Open File'), "", filter_string)
        
        if temp_file_path != "" and temp_file_path != self.file_path:
            self.file_path = temp_file_path
            self.filepathIndicatorWidget.setText(self.file_path)
            self.fname = os.path.splitext(os.path.basename(self.file_path))[0]
            self.updateParameterWidget()
    
    def addParamWidgets(self):
        self.paramLayout = QGridLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.paramWidget = QWidget()
        self.paramWidget.setLayout(self.paramLayout)
        self.scrollArea.setWidget(self.paramWidget)
        self.layout.addWidget(self.scrollArea)

    def updateParameterWidget(self):
        """Update the parameter list and widgets based on the selected file."""
        self.getParameterList()
        
        if hasattr(self, 'paramLayout'):
            self.clear_grid_layout()
        else:
            self.addParamWidgets()
        
        self.addHeaderWidgets()
        self.addCheckBoxWidgets()

    def clear_grid_layout(self):
        # Loop through all the items in the grid layout and remove them
        while self.paramLayout.count():
            item = self.paramLayout.takeAt(0)  # Remove the first item from the layout

            # If the item is a widget, delete it
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            # If the item is a layout, clear it recursively
            layout = item.layout()
            if layout is not None:
                self.clear_layout(layout)  # Call recursive function to clear nested layout

            # Finally, remove the layout item itself
            self.paramLayout.removeItem(item)

    def addHeaderWidgets(self):
        self.paramLayout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Parameter')), 0, 0)
        self.paramLayout.addWidget(QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Notes (optional)')), 0, 1)

    def addCheckBoxWidgets(self):
        self.checkboxWidgets = []
        self.notesWidgets = []
        for row, param in enumerate(self.paramList):
            self.checkboxWidgets.append(QCheckBox(param))
            self.checkboxWidgets[row].setChecked(False)
            self.paramLayout.addWidget(self.checkboxWidgets[row], row+1, 0)

            self.notesWidgets.append(QLineEdit())
            self.paramLayout.addWidget(self.notesWidgets[row], row+1, 1)


    def getParameterList(self):
        workflow = loadjson(self.file_path)
        self.uwl = copy.deepcopy(workflow)
        
        paramListObj = TabViewController()
        paramListObj.entrynames, paramListObj.tableNames = [], []
        paramListObj.addSectionTableNames(workflow, keyPath=[])
        
        self.keyPathLists = paramListObj.keyPathLists
        self.paramList = paramListObj.tableNames

    def addConfirmWidgets(self):
        self.confirmLayout = QHBoxLayout()
        self.confirmBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Generate Table'))
        self.confirmBtn.clicked.connect(self.onConfirm)
        self.confirmLayout.addWidget(self.confirmBtn)
        
        self.cancelBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Cancel'))
        self.cancelBtn.clicked.connect(self.onCancel)
        self.confirmLayout.addWidget(self.cancelBtn)

        self.helpBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', '?'))
        self.helpBtn.clicked.connect(self.onHelp)
        self.confirmLayout.addWidget(self.helpBtn)

        self.confirmLayout.addItem(self.spacer("hor-exp"))
    
        self.layout.addLayout(self.confirmLayout)

    def onHelp(self):
        help_text = (
            get_translation(babelFish, self.lankey, 'widgets', "Use the file picker to select a base UWL, then select the parameters you want to include in the table by checking the boxes next to them. You can also add notes for each parameter if desired. Notes will be displayed in the generated Excel file."),
            get_translation(babelFish, self.lankey, 'widgets', "Click 'Generate Table' to create a formatted table with the selected parameters and notes. The table will be saved as an Excel file, which can be modified as a set of experiments and imported back into the UWLi.")
            )
        QMessageBox.information(self, get_translation(babelFish, self.lankey, 'widgets', 'Help'), "\n\n".join(help_text))

    def onConfirm(self, event):
        if self.file_path == "":
            QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'No file selected'), get_translation(babelFish, self.lankey, 'widgets', 'Please select a root UWL file.'))
            return
        
        self.confirmed = True
        file_path, _ = QFileDialog.getSaveFileName(self, get_translation(babelFish, self.lankey, 'widgets', 'Save Formatted Table'), "", get_translation(babelFish, self.lankey, 'widgets', 'Excel Files (*.xlsx);;All Files (*)'))
        if file_path:
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'

            self.splitRootUWL()
            self.getExportTableData()
            # Pad the lists so they are all the same length
            max_len = max(len(self.hidden_uwl), len(self.hidden_keymap), len(self.param_column))
            def pad_list(lst, fill=""):
                return lst + [fill] * (max_len - len(lst))
            df = pd.DataFrame({
                "hidden_rootuwl": pad_list(self.hidden_uwl),
                "hidden_keymap": pad_list(self.hidden_keymap),
                "Parameters": pad_list(self.param_column)
            })
            # Save the DataFrame to Excel, then hide the first two columns using openpyxl
            df.to_excel(file_path, index=False)

            # Hide the first two columns using openpyxl
            try:
                wb = load_workbook(file_path)
                ws = wb.active
                ws.column_dimensions['A'].hidden = True
                ws.column_dimensions['B'].hidden = True
                wb.save(file_path)
            except Exception as e:
                print("Warning: Could not hide columns in Excel file:", e)
            self.closeEvent(event)

    def splitRootUWL(self):
        uwl_str = str(copy.deepcopy(self.uwl))
        max_chunk_size = 20000
        self.hidden_uwl = [uwl_str[i:i+max_chunk_size] for i in range(0, len(uwl_str), max_chunk_size)]

    def getExportTableData(self):
        self.hidden_keymap = []
        self.param_column = []

        for table_ind, param in enumerate(self.paramList):
            if self.checkboxWidgets[table_ind].isChecked():
                self.hidden_keymap.append(self.keyPathLists[table_ind])
                if self.notesWidgets[table_ind].text() != "":
                    param += " - " + self.notesWidgets[table_ind].text()
                self.param_column.append(param)

    def onCancel(self, event):
        self.closeEvent(event)
    
    def closeEvent(self, event):
        """Emit blank data if not confirmed and close window."""
        if not self.confirmed:
            self.windowSignal.emit([])
        else:
            self.windowSignal.emit([])
        self.close()


class TableMapImportWindow(QWidget):
    windowSignal = Signal(object)
    def __init__(self, lankey='en'):
        super().__init__()
        
        self.lankey = lankey
        self.resize(400, 400)

        self.layout = QVBoxLayout()
        self.setWindowModality(Qt.ApplicationModal)

        self.file_path = ""
        self.fname = ""
        self.confirmed = False
        self.openImportFolder = False
        self.paramList = []

        self.setLayout(self.layout)
        self.addFilePickerWidget()
        self.addTableWidget()
        self.addConfirmWidgets()

        self.layout.addSpacerItem(self.spacer("min"))

    def addFilePickerWidget(self):
        self.filePickerLayout = QHBoxLayout()
        self.filePickerBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Browse Table File'))
        self.filePickerBtn.clicked.connect(self.open_file_picker)
        self.filePickerLayout.addWidget(self.filePickerBtn)


        self.selectedFileLabel = QLabel(get_translation(babelFish, self.lankey, 'widgets', 'Select a table file to view.'))
        self.filePickerLayout.addWidget(self.selectedFileLabel)

        self.filePickerLayout.addSpacerItem(self.spacer("hor-exp"))

        self.layout.addLayout(self.filePickerLayout)

    def open_file_picker(self):
        file_path, _ = QFileDialog.getOpenFileName(self, get_translation(babelFish, self.lankey, 'widgets', 'Select Excel File'), "", get_translation(babelFish, self.lankey, 'widgets', 'Excel Files (*.xlsx)'))
        if file_path:
            self.file_path = file_path
            self.fname = os.path.splitext(os.path.basename(self.file_path))[0]
            
            try:
                self.df = pd.read_excel(self.file_path)
                self.updateTablefromFile()
                self.selectedFileLabel.setText(self.file_path)
            except:
                QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'Invalid Table Format'), get_translation(babelFish, self.lankey, 'widgets', 'The selected Excel file could not be read. Please ensure the table is formatted correctly and try again.'))

    def addTableWidget(self):
        self.tableWidget = QTableWidget()
        header = self.tableWidget.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        header.sectionDoubleClicked.connect(self.editHeaderLabel)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.tableWidget)

        self.layout.addWidget(self.scrollArea)

    def editHeaderLabel(self, col):
        if col == 0:
            return
        old_label = self.tableWidget.horizontalHeaderItem(col).text()
        new_label, ok = QInputDialog.getText(self, get_translation(babelFish, self.lankey, 'widgets', 'Edit Column Label'), f"{get_translation(babelFish, self.lankey, 'widgets', 'Enter new label for column')} '{old_label}':", QLineEdit.Normal, old_label)
        if ok and new_label and new_label != old_label:
            self.tableWidget.setHorizontalHeaderItem(col, QTableWidgetItem(new_label))
            # Update self.df column name as well
            columns = list(self.param_df.columns)
            columns[col] = new_label
            self.param_df.columns = columns

    def contextMenuEvent(self, event):
        # Only trigger context menu if the event is on the header
        pos = self.tableWidget.viewport().mapFrom(self, event.pos())
        header = self.tableWidget.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        
        if logical_index <= 0:
            return  # Do not allow deleting the first column

        menu = QMenu(self)
        delete_action = QAction(get_translation(babelFish, self.lankey, 'widgets', 'Delete Column'), self)
        delete_action.triggered.connect(lambda: self.deleteColumn(logical_index))
        menu.addAction(delete_action)
        menu.exec_(header.mapToGlobal(pos))

    def deleteColumn(self, col):
        if col == 0:
            return  # Do not allow deleting the first column
        col_name = self.param_df.columns[col]
        self.param_df = self.param_df.drop(columns=[col_name])
        self.tableWidget.removeColumn(col)
   
        self.tableWidget.setHorizontalHeaderLabels([str(col) for col in self.param_df.columns])
        for row_idx, row in enumerate(self.param_df.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                if pd.isna(value):
                    value = ""
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)

    def updateTablefromFile(self):
        if hasattr(self, 'df'):
            if "Parameters" not in self.df.columns:
                QMessageBox.critical(self, get_translation(babelFish, self.lankey, 'widgets', 'Invalid Table Format'), get_translation(babelFish, self.lankey, 'widgets', 'The selected Excel file does not contain a \'Parameters\' column. Please ensure the table is formatted correctly and try again.'))
                self.tableWidget.setRowCount(0)
                self.tableWidget.setColumnCount(0)
                return
            
            if "hidden_rootuwl" not in self.df.columns or "hidden_keymap" not in self.df.columns:
                QMessageBox.critical(self, get_translation(babelFish, self.lankey, 'widgets', 'Invalid Table Format'), get_translation(babelFish, self.lankey, 'widgets', 'The selected Excel file does not contain the required hidden columns (\'hidden_rootuwl\', \'hidden_keymap\'). Please ensure the table was generated by the UWLi export tool and try again.'))
                self.tableWidget.setRowCount(0)
                self.tableWidget.setColumnCount(0)
                return
            
            # Reconstruct the hidden_rootuwl string and parse it as a dictionary
            hidden_uwl_chunks = self.df["hidden_rootuwl"].dropna().astype(str).tolist()
            uwl_str = "".join(hidden_uwl_chunks)
            try:
                self.uwl = eval(uwl_str)
            except Exception:
                try:
                    self.uwl = ast.literal_eval(uwl_str)
                except Exception:
                    self.uwl = {}

            if self.uwl == {}:
                QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'Invalid UWL'), get_translation(babelFish, self.lankey, 'widgets', 'The root UWL could not be loaded from the table file. Please ensure the file was generated by the UWLi export tool and try again.'))
                self.tableWidget.setRowCount(0)
                self.tableWidget.setColumnCount(0)
                return

            self.param_df = self.df.drop(columns=[col for col in self.df.columns if col in ["hidden_rootuwl", "hidden_keymap"]])
            
            cols = list(self.param_df.columns)

            if "Parameters" in cols:
                cols.insert(0, cols.pop(cols.index("Parameters")))
                self.param_df = self.param_df[cols]

            self.tableWidget.setRowCount(len(self.param_df))
            self.tableWidget.setColumnCount(len(self.param_df.columns))
            self.tableWidget.setHorizontalHeaderLabels([str(col) for col in self.param_df.columns])

            for row_idx, row in enumerate(self.param_df.itertuples(index=False)):
                for col_idx, value in enumerate(row):
                    if pd.isna(value):
                        value = ""
                    item = QTableWidgetItem(str(value))
                    self.tableWidget.setItem(row_idx, col_idx, item)

        else:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)

    def sanitize_filename(self, name):
        # Remove invalid characters and strip whitespace
        name = re.sub(r'[\\/*?:"<>|]', "_", str(name))
        name = name.strip()
        return name
            
    def addConfirmWidgets(self):
        self.confirmLayout = QHBoxLayout()

        self.importsaveBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Import and Save UWLs'))
        self.importsaveBtn.clicked.connect(self.onImportSave)
        self.confirmLayout.addWidget(self.importsaveBtn)

        # self.importNoSaveBtn = QPushButton("Import UWLs without Saving")
        # self.importNoSaveBtn.clicked.connect(self.onImportNoSave)
        # self.confirmLayout.addWidget(self.importNoSaveBtn)
        
        self.cancelBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', 'Cancel'))
        self.cancelBtn.clicked.connect(self.onCancel)
        self.confirmLayout.addWidget(self.cancelBtn)

        self.helpBtn = QPushButton(get_translation(babelFish, self.lankey, 'widgets', '?'))
        self.helpBtn.clicked.connect(self.onHelp)
        self.confirmLayout.addWidget(self.helpBtn)

        self.confirmLayout.addItem(self.spacer("hor-exp"))
    
        self.layout.addLayout(self.confirmLayout)

    def buildUWLsfromTable(self):
        self.uwl_list = []
        for col_idx in range(1, self.tableWidget.columnCount()):
            uwl_copy = copy.deepcopy(self.uwl)
            for row_idx in range(self.tableWidget.rowCount()):
                param_value = self.tableWidget.item(row_idx, col_idx)
                if param_value is not None:
                    value = param_value.text()
                    try:
                        keypath = self.df["hidden_keymap"].iloc[row_idx]
                        if isinstance(keypath, str):
                            keypath = ast.literal_eval(keypath)
                        section = uwl_copy
                        for k in keypath[:-1]:
                            section = section["Objects"][str(k)]
                        if section["Type"] == "Item" and section["Link"]:
                            print(section["Link"], section)
                            linkID = section["Link ID"]
                            self.propagateLinkValues(uwl_copy, linkID, keypath[-1], value)
                        else:
                            section["Values"][keypath[-1]] = value
                    except Exception as e:
                        print(f"Error assigning value for row {row_idx}, col {col_idx}: {e}")
            self.uwl_list.append(uwl_copy)
        
        self.uwl_names = [self.tableWidget.horizontalHeaderItem(col_idx).text() for col_idx in range(1, self.tableWidget.columnCount())]
        name_counts = {}
        unique_names = []
        for name in self.uwl_names:
            if name not in name_counts:
                name_counts[name] = 1
                unique_names.append(name)
            else:
                name_counts[name] += 1
                unique_name = f"{name} ({name_counts[name]})"
                unique_names.append(unique_name)
        self.uwl_names = unique_names

    def propagateLinkValues(self, uwl_copy, linkID, param_ind, value):
        for key in uwl_copy["Objects"].keys():
            if uwl_copy["Objects"][key]["Type"] == "Item":
                section = uwl_copy["Objects"][key]
                if section["Link"] and section["Link ID"] == linkID:
                    section["Values"][param_ind] = value
            elif uwl_copy["Objects"][key]["Type"] == "Section":
                self.propagateLinkValues(uwl_copy["Objects"][key], linkID, param_ind, value)


    def saveUWLsfromList(self):
        self.uwl_filepaths = []
        for uwl_ind, uwl_name in enumerate(self.uwl_names):
            uwl_name = self.sanitize_filename(uwl_name)
            uwl_filepath = os.path.join(self.dirpath, f"{uwl_name}.uwl")
            savejson(self.uwl_list[uwl_ind], uwl_filepath)
            self.uwl_filepaths.append(uwl_filepath)

    def onImportSave(self, event):
        if self.file_path == "":
            QMessageBox.warning(self, get_translation(babelFish, self.lankey, 'widgets', 'No File Selected'),
                                get_translation(babelFish, self.lankey, 'widgets', 'Please select a table file to import experiments.'))
            return
        
        self.confirmed = True
        parent_directory = QFileDialog.getExistingDirectory(self, get_translation(babelFish, self.lankey, 'widgets', 'Select Directory'))
        if parent_directory:
            self.buildUWLsfromTable()
            self.createDateTimeDir(parent_directory)
            self.saveUWLsfromList()
            self.openImportFolder = True
            self.closeEvent(event)

    def createDateTimeDir(self, parent_dir):
        dt_str = datetime.now().strftime("TableImport_%Y-%m-%d_%H-%M-%S")
        self.dirpath = os.path.join(parent_dir, dt_str)
        os.makedirs(self.dirpath)

    def onImportNoSave(self):
        pass

    def onCancel(self, event):
        self.closeEvent(event)
    
    def closeEvent(self, event):
        """Emit blank data if not confirmed and close window."""
        if not self.confirmed or not self.openImportFolder:
            self.windowSignal.emit([])
        elif self.openImportFolder:
            self.windowSignal.emit(self.uwl_filepaths)
        else:
            self.windowSignal.emit([])
        self.close()

    def onHelp(self):
        help_text = (
            get_translation(babelFish, self.lankey, 'widgets', "This window is used to import a batch of UWLs that are formatted in excel. Use the Build Table Map tool to create an excel file that can be manually edited to adjust parameter values. The file contains two hidden columns containing the root UWL and a map for each parameter to that root UWL. Files that were not originally created using the build tool will most likely fail to import here."),
            get_translation(babelFish, self.lankey, 'widgets', "'Import and Save UWLs' will prompt you for a directory path and save your imported UWLs in a time stamped folder with the column headers corresponding to the file names."),
            )
        QMessageBox.information(self, get_translation(babelFish, self.lankey, 'widgets', 'Help'), "\n\n".join(help_text))

    def spacer(self, method="min"):
        if method == "min":
            spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        elif method == "hor-exp":
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        elif method == "ver-exp":
            spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        return spacer

class autocompleteLineEdit(QLineEdit):
    """Modified QLineEdit that emits a mouse release event."""

    clicked = Signal(object)

    def mouseReleaseEvent(self, event):
        """Emit mouse release event when line edit box is clicked."""
        self.clicked.emit(event)





if __name__ == "__main__":
    
    myappid = 'NREL.UWLI.0.0'  # arbitrary string
    if os.name == 'posix':
        pass
    else:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    logo_path = os.path.dirname(os.path.abspath(__file__)) + "//Logo//Logo_v1f.png"
    if os.name == 'posix':
        pass
    else:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    app.setWindowIcon(QIcon(logo_path))
    qdarktheme.setup_theme('auto')
    window = WindowClass()
    window.setWindowIcon(QIcon(logo_path))
    window.show()
    app.exec_()
