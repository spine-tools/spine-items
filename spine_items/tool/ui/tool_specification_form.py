# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

################################################################################
## Form generated from reading UI file 'tool_specification_form.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

from spinetoolbox.widgets.custom_qtreeview import CustomTreeView
from spinetoolbox.widgets.custom_qtreeview import SourcesTreeView
from spine_items.tool.widgets.main_program_text_edit import MainProgramTextEdit

from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(991, 829)
        MainWindow.setDockNestingEnabled(True)
        self.actionSaveAndClose = QAction(MainWindow)
        self.actionSaveAndClose.setObjectName(u"actionSaveAndClose")
        self.actionNew_main_program_file = QAction(MainWindow)
        self.actionNew_main_program_file.setObjectName(u"actionNew_main_program_file")
        icon = QIcon()
        icon.addFile(u":/icons/file-regular.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionNew_main_program_file.setIcon(icon)
        self.actionSelect_main_program_file = QAction(MainWindow)
        self.actionSelect_main_program_file.setObjectName(u"actionSelect_main_program_file")
        icon1 = QIcon()
        icon1.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSelect_main_program_file.setIcon(icon1)
        self.actionAdd_program_file = QAction(MainWindow)
        self.actionAdd_program_file.setObjectName(u"actionAdd_program_file")
        self.actionAdd_program_file.setIcon(icon1)
        self.actionAdd_program_directory = QAction(MainWindow)
        self.actionAdd_program_directory.setObjectName(u"actionAdd_program_directory")
        icon2 = QIcon()
        icon2.addFile(u":/icons/folder.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAdd_program_directory.setIcon(icon2)
        self.actionRemove_selected_program_files = QAction(MainWindow)
        self.actionRemove_selected_program_files.setObjectName(u"actionRemove_selected_program_files")
        self.actionRemove_selected_program_files.setEnabled(False)
        icon3 = QIcon()
        icon3.addFile(u":/icons/trash-alt.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRemove_selected_program_files.setIcon(icon3)
        self.actionAdd_input_files = QAction(MainWindow)
        self.actionAdd_input_files.setObjectName(u"actionAdd_input_files")
        icon4 = QIcon()
        icon4.addFile(u":/icons/file-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAdd_input_files.setIcon(icon4)
        self.actionRemove_selected_input_files = QAction(MainWindow)
        self.actionRemove_selected_input_files.setObjectName(u"actionRemove_selected_input_files")
        self.actionRemove_selected_input_files.setEnabled(False)
        self.actionRemove_selected_input_files.setIcon(icon3)
        self.actionAdd_opt_input_files = QAction(MainWindow)
        self.actionAdd_opt_input_files.setObjectName(u"actionAdd_opt_input_files")
        self.actionAdd_opt_input_files.setIcon(icon4)
        self.actionRemove_selected_opt_input_files = QAction(MainWindow)
        self.actionRemove_selected_opt_input_files.setObjectName(u"actionRemove_selected_opt_input_files")
        self.actionRemove_selected_opt_input_files.setEnabled(False)
        self.actionRemove_selected_opt_input_files.setIcon(icon3)
        self.actionAdd_output_files = QAction(MainWindow)
        self.actionAdd_output_files.setObjectName(u"actionAdd_output_files")
        self.actionAdd_output_files.setIcon(icon4)
        self.actionRemove_selected_output_files = QAction(MainWindow)
        self.actionRemove_selected_output_files.setObjectName(u"actionRemove_selected_output_files")
        self.actionRemove_selected_output_files.setEnabled(False)
        self.actionRemove_selected_output_files.setIcon(icon3)
        self.actionNew_program_file = QAction(MainWindow)
        self.actionNew_program_file.setObjectName(u"actionNew_program_file")
        self.actionNew_program_file.setIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_7 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_7.setSpacing(4)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(6, 6, 6, 6)
        self.label_tooltype = QLabel(self.centralwidget)
        self.label_tooltype.setObjectName(u"label_tooltype")

        self.horizontalLayout_7.addWidget(self.label_tooltype)

        self.comboBox_tooltype = QComboBox(self.centralwidget)
        self.comboBox_tooltype.setObjectName(u"comboBox_tooltype")
        sizePolicy.setHeightForWidth(self.comboBox_tooltype.sizePolicy().hasHeightForWidth())
        self.comboBox_tooltype.setSizePolicy(sizePolicy)
        self.comboBox_tooltype.setMinimumSize(QSize(180, 24))
        self.comboBox_tooltype.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout_7.addWidget(self.comboBox_tooltype)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_7.addWidget(self.line)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.lineEdit_args = QLineEdit(self.centralwidget)
        self.lineEdit_args.setObjectName(u"lineEdit_args")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_args.sizePolicy().hasHeightForWidth())
        self.lineEdit_args.setSizePolicy(sizePolicy1)
        self.lineEdit_args.setMinimumSize(QSize(220, 24))
        self.lineEdit_args.setMaximumSize(QSize(5000, 24))
        self.lineEdit_args.setClearButtonEnabled(True)

        self.horizontalLayout_7.addWidget(self.lineEdit_args)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_7.addWidget(self.line_2)

        self.checkBox_execute_in_work = QCheckBox(self.centralwidget)
        self.checkBox_execute_in_work.setObjectName(u"checkBox_execute_in_work")
        self.checkBox_execute_in_work.setChecked(True)

        self.horizontalLayout_7.addWidget(self.checkBox_execute_in_work)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 991, 27))
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_program_files = QDockWidget(MainWindow)
        self.dockWidget_program_files.setObjectName(u"dockWidget_program_files")
        self.dockWidget_program_files.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.treeView_programfiles = SourcesTreeView(self.dockWidgetContents_4)
        self.treeView_programfiles.setObjectName(u"treeView_programfiles")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(100)
        sizePolicy2.setHeightForWidth(self.treeView_programfiles.sizePolicy().hasHeightForWidth())
        self.treeView_programfiles.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(11)
        self.treeView_programfiles.setFont(font)
        self.treeView_programfiles.setFocusPolicy(Qt.StrongFocus)
        self.treeView_programfiles.setAcceptDrops(True)
        self.treeView_programfiles.setLineWidth(1)
        self.treeView_programfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_programfiles.setTextElideMode(Qt.ElideLeft)
        self.treeView_programfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_programfiles.header().setVisible(False)

        self.verticalLayout.addWidget(self.treeView_programfiles)

        self.dockWidget_program_files.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_program_files)
        self.dockWidget_io_files = QDockWidget(MainWindow)
        self.dockWidget_io_files.setObjectName(u"dockWidget_io_files")
        self.dockWidget_io_files.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_7.setSpacing(2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(3, 3, 3, 3)
        self.treeView_io_files = CustomTreeView(self.dockWidgetContents_2)
        self.treeView_io_files.setObjectName(u"treeView_io_files")
        self.treeView_io_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_io_files.setTextElideMode(Qt.ElideLeft)
        self.treeView_io_files.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_io_files.header().setVisible(False)

        self.verticalLayout_7.addWidget(self.treeView_io_files)

        self.dockWidget_io_files.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_io_files)
        self.dockWidget_program = QDockWidget(MainWindow)
        self.dockWidget_program.setObjectName(u"dockWidget_program")
        self.dockWidget_program.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_8 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(3, 3, 3, 3)
        self.textEdit_program = MainProgramTextEdit(self.dockWidgetContents)
        self.textEdit_program.setObjectName(u"textEdit_program")
        self.textEdit_program.setEnabled(True)

        self.verticalLayout_8.addWidget(self.textEdit_program)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label = QLabel(self.dockWidgetContents)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setPointSize(10)
        self.label.setFont(font1)

        self.horizontalLayout_6.addWidget(self.label)

        self.label_mainpath = QLabel(self.dockWidgetContents)
        self.label_mainpath.setObjectName(u"label_mainpath")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_mainpath.sizePolicy().hasHeightForWidth())
        self.label_mainpath.setSizePolicy(sizePolicy3)
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setWeight(75)
        self.label_mainpath.setFont(font2)

        self.horizontalLayout_6.addWidget(self.label_mainpath)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.toolButton_save_program = QToolButton(self.dockWidgetContents)
        self.toolButton_save_program.setObjectName(u"toolButton_save_program")
        self.toolButton_save_program.setEnabled(False)
        icon5 = QIcon()
        icon5.addFile(u":/icons/save.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_save_program.setIcon(icon5)

        self.horizontalLayout_6.addWidget(self.toolButton_save_program)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.dockWidget_program.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_program)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuEdit.addAction(self.actionNew_main_program_file)
        self.menuEdit.addAction(self.actionSelect_main_program_file)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionNew_program_file)
        self.menuEdit.addAction(self.actionAdd_program_file)
        self.menuEdit.addAction(self.actionAdd_program_directory)
        self.menuEdit.addAction(self.actionRemove_selected_program_files)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_input_files)
        self.menuEdit.addAction(self.actionRemove_selected_input_files)
        self.menuEdit.addAction(self.actionAdd_opt_input_files)
        self.menuEdit.addAction(self.actionRemove_selected_opt_input_files)
        self.menuEdit.addAction(self.actionAdd_output_files)
        self.menuEdit.addAction(self.actionRemove_selected_output_files)
        self.menuFile.addAction(self.actionSaveAndClose)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tool Specification Editor", None))
        self.actionSaveAndClose.setText(QCoreApplication.translate("MainWindow", u"Save and close", None))
#if QT_CONFIG(shortcut)
        self.actionSaveAndClose.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Return", None))
#endif // QT_CONFIG(shortcut)
        self.actionNew_main_program_file.setText(QCoreApplication.translate("MainWindow", u"New main program file", None))
#if QT_CONFIG(tooltip)
        self.actionNew_main_program_file.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new main program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionSelect_main_program_file.setText(QCoreApplication.translate("MainWindow", u"Select main program file", None))
#if QT_CONFIG(tooltip)
        self.actionSelect_main_program_file.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select existing main program file from your computer</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_program_file.setText(QCoreApplication.translate("MainWindow", u"Add program files", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_program_file.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add additional program files from your computer</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_program_directory.setText(QCoreApplication.translate("MainWindow", u"Add program directory", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_program_directory.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add additional program directory from your computer</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionRemove_selected_program_files.setText(QCoreApplication.translate("MainWindow", u"Remove selected program files", None))
#if QT_CONFIG(tooltip)
        self.actionRemove_selected_program_files.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected additional program files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_input_files.setText(QCoreApplication.translate("MainWindow", u"Add input files", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_input_files.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add input filenames and/or directories required by the program. Examples:</p><p>'data.csv'</p><p>'input/data.csv'</p><p>'input/'</p><p>'output/'</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionRemove_selected_input_files.setText(QCoreApplication.translate("MainWindow", u"Remove selected input files", None))
#if QT_CONFIG(tooltip)
        self.actionRemove_selected_input_files.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove selected input files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_opt_input_files.setText(QCoreApplication.translate("MainWindow", u"Add optional input files", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_opt_input_files.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add optional input files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionRemove_selected_opt_input_files.setText(QCoreApplication.translate("MainWindow", u"Remove selected optional input files", None))
#if QT_CONFIG(tooltip)
        self.actionRemove_selected_opt_input_files.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected optional input files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_output_files.setText(QCoreApplication.translate("MainWindow", u"Add output files", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_output_files.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add output files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionRemove_selected_output_files.setText(QCoreApplication.translate("MainWindow", u"Remove selected output files", None))
#if QT_CONFIG(tooltip)
        self.actionRemove_selected_output_files.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected output files</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionNew_program_file.setText(QCoreApplication.translate("MainWindow", u"New program file", None))
#if QT_CONFIG(tooltip)
        self.actionNew_program_file.setToolTip(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Create new additional program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_tooltype.setText(QCoreApplication.translate("MainWindow", u"Tool type", None))
#if QT_CONFIG(tooltip)
        self.comboBox_tooltype.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Tool specification type</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_tooltype.setCurrentText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Command line arguments:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_args.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Command line arguments (space-delimited) for the main program (optional). Use '@@' tags to refer to input files or URLs, see the User Guide for details.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_args.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type arguments here...", None))
#if QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If checked, Tool specification is executed in a work directory (default).</p><p>If unchecked, Tool specification is executed in main program file directory.</p><p>It is recommended to uncheck this for <span style=\" font-weight:600;\">Executable</span> Tool specifications.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setText(QCoreApplication.translate("MainWindow", u"Execute in work directory", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.dockWidget_program_files.setWindowTitle(QCoreApplication.translate("MainWindow", u"Program files", None))
        self.dockWidget_io_files.setWindowTitle(QCoreApplication.translate("MainWindow", u"Input & output files", None))
        self.dockWidget_program.setWindowTitle(QCoreApplication.translate("MainWindow", u"Program source code", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Main program directory:", None))
        self.label_mainpath.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_save_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Save</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_save_program.setText(QCoreApplication.translate("MainWindow", u"...", None))
    # retranslateUi

