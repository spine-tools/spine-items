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

from spinetoolbox.widgets.custom_qlineedits import CustomQLineEdit
from spinetoolbox.widgets.custom_qtreeview import CustomTreeView
from spinetoolbox.widgets.custom_qtreeview import SourcesTreeView
from spine_items.tool.widgets.main_program_text_edit import MainProgramTextEdit

from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(991, 545)
        MainWindow.setDockNestingEnabled(True)
        self.actionSaveAndClose = QAction(MainWindow)
        self.actionSaveAndClose.setObjectName(u"actionSaveAndClose")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 991, 27))
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.dockWidget_type_and_program = QDockWidget(MainWindow)
        self.dockWidget_type_and_program.setObjectName(u"dockWidget_type_and_program")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout_2 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.comboBox_tooltype = QComboBox(self.dockWidgetContents)
        self.comboBox_tooltype.setObjectName(u"comboBox_tooltype")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_tooltype.sizePolicy().hasHeightForWidth())
        self.comboBox_tooltype.setSizePolicy(sizePolicy)
        self.comboBox_tooltype.setMinimumSize(QSize(180, 24))
        self.comboBox_tooltype.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout.addWidget(self.comboBox_tooltype)

        self.checkBox_execute_in_work = QCheckBox(self.dockWidgetContents)
        self.checkBox_execute_in_work.setObjectName(u"checkBox_execute_in_work")
        self.checkBox_execute_in_work.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_execute_in_work)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_main_program = CustomQLineEdit(self.dockWidgetContents)
        self.lineEdit_main_program.setObjectName(u"lineEdit_main_program")
        self.lineEdit_main_program.setClearButtonEnabled(True)

        self.horizontalLayout_6.addWidget(self.lineEdit_main_program)

        self.toolButton_new_main_program = QToolButton(self.dockWidgetContents)
        self.toolButton_new_main_program.setObjectName(u"toolButton_new_main_program")
        self.toolButton_new_main_program.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_new_main_program.setIcon(icon)
        self.toolButton_new_main_program.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_6.addWidget(self.toolButton_new_main_program)

        self.toolButton_browse_main_program = QToolButton(self.dockWidgetContents)
        self.toolButton_browse_main_program.setObjectName(u"toolButton_browse_main_program")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_main_program.setIcon(icon1)

        self.horizontalLayout_6.addWidget(self.toolButton_browse_main_program)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 1, 0, 1, 1)

        self.textEdit_main_program = MainProgramTextEdit(self.dockWidgetContents)
        self.textEdit_main_program.setObjectName(u"textEdit_main_program")
        self.textEdit_main_program.setEnabled(True)

        self.gridLayout_2.addWidget(self.textEdit_main_program, 2, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 0, -1, 0)
        self.label = QLabel(self.dockWidgetContents)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(9)
        self.label.setFont(font)

        self.horizontalLayout_8.addWidget(self.label)

        self.label_mainpath = QLabel(self.dockWidgetContents)
        self.label_mainpath.setObjectName(u"label_mainpath")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_mainpath.sizePolicy().hasHeightForWidth())
        self.label_mainpath.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(True)
        font1.setWeight(75)
        self.label_mainpath.setFont(font1)

        self.horizontalLayout_8.addWidget(self.label_mainpath)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.toolButton_save_main_program = QToolButton(self.dockWidgetContents)
        self.toolButton_save_main_program.setObjectName(u"toolButton_save_main_program")
        self.toolButton_save_main_program.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/icons/save.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_save_main_program.setIcon(icon2)

        self.horizontalLayout_8.addWidget(self.toolButton_save_main_program)


        self.gridLayout_2.addLayout(self.horizontalLayout_8, 3, 0, 1, 1)

        self.lineEdit_args = QLineEdit(self.dockWidgetContents)
        self.lineEdit_args.setObjectName(u"lineEdit_args")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_args.sizePolicy().hasHeightForWidth())
        self.lineEdit_args.setSizePolicy(sizePolicy2)
        self.lineEdit_args.setMinimumSize(QSize(220, 24))
        self.lineEdit_args.setMaximumSize(QSize(5000, 24))
        self.lineEdit_args.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.lineEdit_args, 4, 0, 1, 1)

        self.dockWidget_type_and_program.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_type_and_program)
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.gridLayout = QGridLayout(self.dockWidgetContents_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.treeView_programfiles = SourcesTreeView(self.dockWidgetContents_3)
        self.treeView_programfiles.setObjectName(u"treeView_programfiles")
        sizePolicy1.setHeightForWidth(self.treeView_programfiles.sizePolicy().hasHeightForWidth())
        self.treeView_programfiles.setSizePolicy(sizePolicy1)
        self.treeView_programfiles.setMaximumSize(QSize(16777215, 200))
        font2 = QFont()
        font2.setPointSize(10)
        self.treeView_programfiles.setFont(font2)
        self.treeView_programfiles.setFocusPolicy(Qt.StrongFocus)
        self.treeView_programfiles.setAcceptDrops(True)
        self.treeView_programfiles.setLineWidth(1)
        self.treeView_programfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_programfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_programfiles.setIndentation(5)

        self.verticalLayout_3.addWidget(self.treeView_programfiles)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButton_add_program_files = QToolButton(self.dockWidgetContents_3)
        self.toolButton_add_program_files.setObjectName(u"toolButton_add_program_files")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.toolButton_add_program_files.sizePolicy().hasHeightForWidth())
        self.toolButton_add_program_files.setSizePolicy(sizePolicy3)
        self.toolButton_add_program_files.setMinimumSize(QSize(22, 22))
        self.toolButton_add_program_files.setMaximumSize(QSize(22, 22))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        font3.setWeight(75)
        self.toolButton_add_program_files.setFont(font3)
        icon3 = QIcon()
        icon3.addFile(u":/icons/file-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_program_files.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.toolButton_add_program_files)

        self.toolButton_add_program_dirs = QToolButton(self.dockWidgetContents_3)
        self.toolButton_add_program_dirs.setObjectName(u"toolButton_add_program_dirs")
        self.toolButton_add_program_dirs.setMinimumSize(QSize(22, 22))
        self.toolButton_add_program_dirs.setMaximumSize(QSize(22, 22))
        icon4 = QIcon()
        icon4.addFile(u":/icons/folder-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_program_dirs.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.toolButton_add_program_dirs)

        self.toolButton_minus_program_files = QToolButton(self.dockWidgetContents_3)
        self.toolButton_minus_program_files.setObjectName(u"toolButton_minus_program_files")
        sizePolicy3.setHeightForWidth(self.toolButton_minus_program_files.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_program_files.setSizePolicy(sizePolicy3)
        self.toolButton_minus_program_files.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_program_files.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_program_files.setFont(font3)
        icon5 = QIcon()
        icon5.addFile(u":/icons/trash-alt.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_minus_program_files.setIcon(icon5)

        self.horizontalLayout_2.addWidget(self.toolButton_minus_program_files)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_15)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.treeView_inputfiles = CustomTreeView(self.dockWidgetContents_3)
        self.treeView_inputfiles.setObjectName(u"treeView_inputfiles")
        sizePolicy1.setHeightForWidth(self.treeView_inputfiles.sizePolicy().hasHeightForWidth())
        self.treeView_inputfiles.setSizePolicy(sizePolicy1)
        self.treeView_inputfiles.setMaximumSize(QSize(16777215, 500))
        self.treeView_inputfiles.setFont(font2)
        self.treeView_inputfiles.setFocusPolicy(Qt.StrongFocus)
        self.treeView_inputfiles.setLineWidth(1)
        self.treeView_inputfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_inputfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_inputfiles.setIndentation(5)
        self.treeView_inputfiles.setUniformRowHeights(False)

        self.verticalLayout_4.addWidget(self.treeView_inputfiles)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.toolButton_plus_inputfiles = QToolButton(self.dockWidgetContents_3)
        self.toolButton_plus_inputfiles.setObjectName(u"toolButton_plus_inputfiles")
        sizePolicy3.setHeightForWidth(self.toolButton_plus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles.setSizePolicy(sizePolicy3)
        self.toolButton_plus_inputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles.setFont(font3)
        self.toolButton_plus_inputfiles.setIcon(icon3)

        self.horizontalLayout_4.addWidget(self.toolButton_plus_inputfiles)

        self.toolButton_minus_inputfiles = QToolButton(self.dockWidgetContents_3)
        self.toolButton_minus_inputfiles.setObjectName(u"toolButton_minus_inputfiles")
        sizePolicy3.setHeightForWidth(self.toolButton_minus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles.setSizePolicy(sizePolicy3)
        self.toolButton_minus_inputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles.setFont(font3)
        self.toolButton_minus_inputfiles.setIcon(icon5)

        self.horizontalLayout_4.addWidget(self.toolButton_minus_inputfiles)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)


        self.gridLayout.addLayout(self.verticalLayout_4, 0, 1, 1, 1)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setSpacing(6)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.treeView_outputfiles = CustomTreeView(self.dockWidgetContents_3)
        self.treeView_outputfiles.setObjectName(u"treeView_outputfiles")
        self.treeView_outputfiles.setMaximumSize(QSize(16777215, 500))
        self.treeView_outputfiles.setFont(font2)
        self.treeView_outputfiles.setFocusPolicy(Qt.WheelFocus)
        self.treeView_outputfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_outputfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_outputfiles.setIndentation(5)

        self.verticalLayout_16.addWidget(self.treeView_outputfiles)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.toolButton_plus_outputfiles = QToolButton(self.dockWidgetContents_3)
        self.toolButton_plus_outputfiles.setObjectName(u"toolButton_plus_outputfiles")
        sizePolicy3.setHeightForWidth(self.toolButton_plus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_outputfiles.setSizePolicy(sizePolicy3)
        self.toolButton_plus_outputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_outputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_outputfiles.setFont(font3)
        self.toolButton_plus_outputfiles.setIcon(icon3)

        self.horizontalLayout_3.addWidget(self.toolButton_plus_outputfiles)

        self.toolButton_minus_outputfiles = QToolButton(self.dockWidgetContents_3)
        self.toolButton_minus_outputfiles.setObjectName(u"toolButton_minus_outputfiles")
        sizePolicy3.setHeightForWidth(self.toolButton_minus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_outputfiles.setSizePolicy(sizePolicy3)
        self.toolButton_minus_outputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_outputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_outputfiles.setFont(font3)
        self.toolButton_minus_outputfiles.setIcon(icon5)

        self.horizontalLayout_3.addWidget(self.toolButton_minus_outputfiles)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_13)


        self.verticalLayout_16.addLayout(self.horizontalLayout_3)


        self.gridLayout.addLayout(self.verticalLayout_16, 1, 1, 1, 1)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setSpacing(6)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.treeView_inputfiles_opt = CustomTreeView(self.dockWidgetContents_3)
        self.treeView_inputfiles_opt.setObjectName(u"treeView_inputfiles_opt")
        self.treeView_inputfiles_opt.setMaximumSize(QSize(16777215, 500))
        self.treeView_inputfiles_opt.setFont(font2)
        self.treeView_inputfiles_opt.setFocusPolicy(Qt.StrongFocus)
        self.treeView_inputfiles_opt.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_inputfiles_opt.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_inputfiles_opt.setIndentation(5)

        self.verticalLayout_15.addWidget(self.treeView_inputfiles_opt)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.toolButton_plus_inputfiles_opt = QToolButton(self.dockWidgetContents_3)
        self.toolButton_plus_inputfiles_opt.setObjectName(u"toolButton_plus_inputfiles_opt")
        sizePolicy3.setHeightForWidth(self.toolButton_plus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles_opt.setSizePolicy(sizePolicy3)
        self.toolButton_plus_inputfiles_opt.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles_opt.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles_opt.setFont(font3)
        self.toolButton_plus_inputfiles_opt.setIcon(icon3)

        self.horizontalLayout_5.addWidget(self.toolButton_plus_inputfiles_opt)

        self.toolButton_minus_inputfiles_opt = QToolButton(self.dockWidgetContents_3)
        self.toolButton_minus_inputfiles_opt.setObjectName(u"toolButton_minus_inputfiles_opt")
        sizePolicy3.setHeightForWidth(self.toolButton_minus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles_opt.setSizePolicy(sizePolicy3)
        self.toolButton_minus_inputfiles_opt.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles_opt.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles_opt.setFont(font3)
        self.toolButton_minus_inputfiles_opt.setIcon(icon5)

        self.horizontalLayout_5.addWidget(self.toolButton_minus_inputfiles_opt)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)


        self.verticalLayout_15.addLayout(self.horizontalLayout_5)


        self.gridLayout.addLayout(self.verticalLayout_15, 1, 0, 1, 1)

        self.dockWidget_2.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_2)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
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
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.dockWidget_type_and_program.setWindowTitle(QCoreApplication.translate("MainWindow", u"Type and program", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Tool type", None))
#if QT_CONFIG(tooltip)
        self.comboBox_tooltype.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Tool specification type</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_tooltype.setCurrentText("")
#if QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If checked, Tool specification is executed in a work directory (default).</p><p>If unchecked, Tool specification is executed in main program file directory.</p><p>It is recommended to uncheck this for <span style=\" font-weight:600;\">Executable</span> Tool specifications.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setText(QCoreApplication.translate("MainWindow", u"Execute in work directory", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Main program file that is used to launch the Tool specification (required)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_main_program.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type path of main program file here...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_new_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new main program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_browse_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select existing main program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_browse_main_program.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.textEdit_main_program.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Create main program file here...", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Main program directory", None))
        self.label_mainpath.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_save_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Save</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_save_main_program.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_args.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Command line arguments (space-delimited) for the main program (optional). Use '@@' tags to refer to input files or URLs, see the User Guide for details.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_args.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type command line arguments here...", None))
        self.dockWidget_2.setWindowTitle(QCoreApplication.translate("MainWindow", u"Input and output", None))
#if QT_CONFIG(tooltip)
        self.treeView_programfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Other source files and/or directories (in addition to the main program file) <span style=\" font-weight:600;\">required</span> by the program.</p><p><span style=\" font-weight:600;\">Tip</span>: You can Drag &amp; Drop files and/or directories here from File Explorer.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_add_program_files.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add source code <span style=\" font-weight:600;\">files</span> that your program requires in order to run.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_add_program_files.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_add_program_dirs.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add source code <span style=\" font-weight:600;\">directory</span> and all its contents.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_minus_program_files.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_program_files.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_inputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Required</span> data files for the program.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_inputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add input filenames and/or directories required by the program. Examples:</p><p>'data.csv'</p><p>'input/data.csv'</p><p>'input/'</p><p>'output/'</p><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_inputfiles.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_inputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_inputfiles.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_outputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Output files that may be used by other project items downstream. These files will be archived into a results directory after execution.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_outputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add output filenames produced by your program that are saved to results after execution.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_outputfiles.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_outputfiles.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_outputfiles.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_inputfiles_opt.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Optional</span> data files for the program.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_inputfiles_opt.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add optional input filenames and/or directories.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_inputfiles_opt.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_inputfiles_opt.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_inputfiles_opt.setText("")
    # retranslateUi

