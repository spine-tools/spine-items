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
        self.frame = QFrame(self.dockWidgetContents_4)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.treeView_main_programfile = QTreeView(self.frame)
        self.treeView_main_programfile.setObjectName(u"treeView_main_programfile")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.treeView_main_programfile.sizePolicy().hasHeightForWidth())
        self.treeView_main_programfile.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(11)
        self.treeView_main_programfile.setFont(font)
        self.treeView_main_programfile.setTextElideMode(Qt.ElideLeft)
        self.treeView_main_programfile.setIndentation(5)
        self.treeView_main_programfile.header().setMinimumSectionSize(27)

        self.verticalLayout_9.addWidget(self.treeView_main_programfile)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButton_new_main_program = QToolButton(self.frame)
        self.toolButton_new_main_program.setObjectName(u"toolButton_new_main_program")
        self.toolButton_new_main_program.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_new_main_program.setIcon(icon)
        self.toolButton_new_main_program.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout.addWidget(self.toolButton_new_main_program)

        self.toolButton_browse_main_program = QToolButton(self.frame)
        self.toolButton_browse_main_program.setObjectName(u"toolButton_browse_main_program")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_main_program.setIcon(icon1)

        self.horizontalLayout.addWidget(self.toolButton_browse_main_program)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.verticalLayout_9.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.dockWidgetContents_4)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(100)
        sizePolicy4.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy4)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_2)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.treeView_programfiles = SourcesTreeView(self.frame_2)
        self.treeView_programfiles.setObjectName(u"treeView_programfiles")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(100)
        sizePolicy5.setHeightForWidth(self.treeView_programfiles.sizePolicy().hasHeightForWidth())
        self.treeView_programfiles.setSizePolicy(sizePolicy5)
        self.treeView_programfiles.setFont(font)
        self.treeView_programfiles.setFocusPolicy(Qt.StrongFocus)
        self.treeView_programfiles.setAcceptDrops(True)
        self.treeView_programfiles.setLineWidth(1)
        self.treeView_programfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_programfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_programfiles.setIndentation(5)

        self.verticalLayout_10.addWidget(self.treeView_programfiles)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButton_add_program_files = QToolButton(self.frame_2)
        self.toolButton_add_program_files.setObjectName(u"toolButton_add_program_files")
        sizePolicy6 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.toolButton_add_program_files.sizePolicy().hasHeightForWidth())
        self.toolButton_add_program_files.setSizePolicy(sizePolicy6)
        self.toolButton_add_program_files.setMinimumSize(QSize(22, 22))
        self.toolButton_add_program_files.setMaximumSize(QSize(22, 22))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setWeight(75)
        self.toolButton_add_program_files.setFont(font1)
        icon2 = QIcon()
        icon2.addFile(u":/icons/file-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_program_files.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.toolButton_add_program_files)

        self.toolButton_add_program_dirs = QToolButton(self.frame_2)
        self.toolButton_add_program_dirs.setObjectName(u"toolButton_add_program_dirs")
        self.toolButton_add_program_dirs.setMinimumSize(QSize(22, 22))
        self.toolButton_add_program_dirs.setMaximumSize(QSize(22, 22))
        icon3 = QIcon()
        icon3.addFile(u":/icons/folder-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_program_dirs.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.toolButton_add_program_dirs)

        self.toolButton_minus_program_files = QToolButton(self.frame_2)
        self.toolButton_minus_program_files.setObjectName(u"toolButton_minus_program_files")
        sizePolicy6.setHeightForWidth(self.toolButton_minus_program_files.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_program_files.setSizePolicy(sizePolicy6)
        self.toolButton_minus_program_files.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_program_files.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_program_files.setFont(font1)
        icon4 = QIcon()
        icon4.addFile(u":/icons/trash-alt.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_minus_program_files.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.toolButton_minus_program_files)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_15)


        self.verticalLayout_10.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.frame_2)

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
        self.splitter = QSplitter(self.dockWidgetContents_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.widget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_3)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.treeView_inputfiles = CustomTreeView(self.frame_3)
        self.treeView_inputfiles.setObjectName(u"treeView_inputfiles")
        font2 = QFont()
        font2.setPointSize(10)
        self.treeView_inputfiles.setFont(font2)
        self.treeView_inputfiles.setFocusPolicy(Qt.StrongFocus)
        self.treeView_inputfiles.setLineWidth(1)
        self.treeView_inputfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_inputfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_inputfiles.setIndentation(5)
        self.treeView_inputfiles.setUniformRowHeights(False)

        self.verticalLayout_11.addWidget(self.treeView_inputfiles)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.toolButton_plus_inputfiles = QToolButton(self.frame_3)
        self.toolButton_plus_inputfiles.setObjectName(u"toolButton_plus_inputfiles")
        sizePolicy6.setHeightForWidth(self.toolButton_plus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles.setSizePolicy(sizePolicy6)
        self.toolButton_plus_inputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles.setFont(font1)
        self.toolButton_plus_inputfiles.setIcon(icon2)

        self.horizontalLayout_4.addWidget(self.toolButton_plus_inputfiles)

        self.toolButton_minus_inputfiles = QToolButton(self.frame_3)
        self.toolButton_minus_inputfiles.setObjectName(u"toolButton_minus_inputfiles")
        sizePolicy6.setHeightForWidth(self.toolButton_minus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles.setSizePolicy(sizePolicy6)
        self.toolButton_minus_inputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles.setFont(font1)
        self.toolButton_minus_inputfiles.setIcon(icon4)

        self.horizontalLayout_4.addWidget(self.toolButton_minus_inputfiles)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.verticalLayout_11.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.splitter.addWidget(self.widget)
        self.widget1 = QWidget(self.splitter)
        self.widget1.setObjectName(u"widget1")
        self.verticalLayout_3 = QVBoxLayout(self.widget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.widget1)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_4)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.treeView_inputfiles_opt = CustomTreeView(self.frame_4)
        self.treeView_inputfiles_opt.setObjectName(u"treeView_inputfiles_opt")
        self.treeView_inputfiles_opt.setFont(font2)
        self.treeView_inputfiles_opt.setFocusPolicy(Qt.StrongFocus)
        self.treeView_inputfiles_opt.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_inputfiles_opt.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_inputfiles_opt.setIndentation(5)

        self.verticalLayout_12.addWidget(self.treeView_inputfiles_opt)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.toolButton_plus_inputfiles_opt = QToolButton(self.frame_4)
        self.toolButton_plus_inputfiles_opt.setObjectName(u"toolButton_plus_inputfiles_opt")
        sizePolicy6.setHeightForWidth(self.toolButton_plus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles_opt.setSizePolicy(sizePolicy6)
        self.toolButton_plus_inputfiles_opt.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles_opt.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_inputfiles_opt.setFont(font1)
        self.toolButton_plus_inputfiles_opt.setIcon(icon2)

        self.horizontalLayout_5.addWidget(self.toolButton_plus_inputfiles_opt)

        self.toolButton_minus_inputfiles_opt = QToolButton(self.frame_4)
        self.toolButton_minus_inputfiles_opt.setObjectName(u"toolButton_minus_inputfiles_opt")
        sizePolicy6.setHeightForWidth(self.toolButton_minus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles_opt.setSizePolicy(sizePolicy6)
        self.toolButton_minus_inputfiles_opt.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles_opt.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_inputfiles_opt.setFont(font1)
        self.toolButton_minus_inputfiles_opt.setIcon(icon4)

        self.horizontalLayout_5.addWidget(self.toolButton_minus_inputfiles_opt)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)


        self.verticalLayout_12.addLayout(self.horizontalLayout_5)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.splitter.addWidget(self.widget1)
        self.widget2 = QWidget(self.splitter)
        self.widget2.setObjectName(u"widget2")
        self.verticalLayout_4 = QVBoxLayout(self.widget2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.widget2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_5)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.treeView_outputfiles = CustomTreeView(self.frame_5)
        self.treeView_outputfiles.setObjectName(u"treeView_outputfiles")
        self.treeView_outputfiles.setFont(font2)
        self.treeView_outputfiles.setFocusPolicy(Qt.WheelFocus)
        self.treeView_outputfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_outputfiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_outputfiles.setIndentation(5)

        self.verticalLayout_13.addWidget(self.treeView_outputfiles)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.toolButton_plus_outputfiles = QToolButton(self.frame_5)
        self.toolButton_plus_outputfiles.setObjectName(u"toolButton_plus_outputfiles")
        sizePolicy6.setHeightForWidth(self.toolButton_plus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_outputfiles.setSizePolicy(sizePolicy6)
        self.toolButton_plus_outputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_outputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_outputfiles.setFont(font1)
        self.toolButton_plus_outputfiles.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.toolButton_plus_outputfiles)

        self.toolButton_minus_outputfiles = QToolButton(self.frame_5)
        self.toolButton_minus_outputfiles.setObjectName(u"toolButton_minus_outputfiles")
        sizePolicy6.setHeightForWidth(self.toolButton_minus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_outputfiles.setSizePolicy(sizePolicy6)
        self.toolButton_minus_outputfiles.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_outputfiles.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_outputfiles.setFont(font1)
        self.toolButton_minus_outputfiles.setIcon(icon4)

        self.horizontalLayout_3.addWidget(self.toolButton_minus_outputfiles)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_13.addLayout(self.horizontalLayout_3)


        self.verticalLayout_4.addWidget(self.frame_5)

        self.splitter.addWidget(self.widget2)

        self.verticalLayout_7.addWidget(self.splitter)

        self.dockWidget_io_files.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_io_files)
        self.dockWidget_editor = QDockWidget(MainWindow)
        self.dockWidget_editor.setObjectName(u"dockWidget_editor")
        self.dockWidget_editor.setAllowedAreas(Qt.BottomDockWidgetArea)
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
        self.label.setFont(font2)

        self.horizontalLayout_6.addWidget(self.label)

        self.label_mainpath = QLabel(self.dockWidgetContents)
        self.label_mainpath.setObjectName(u"label_mainpath")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.label_mainpath.sizePolicy().hasHeightForWidth())
        self.label_mainpath.setSizePolicy(sizePolicy7)
        self.label_mainpath.setFont(font1)

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

        self.dockWidget_editor.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_editor)

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
#if QT_CONFIG(tooltip)
        self.toolButton_new_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new main program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_browse_main_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select existing main program file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_browse_main_program.setText(QCoreApplication.translate("MainWindow", u"...", None))
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
        self.dockWidget_io_files.setWindowTitle(QCoreApplication.translate("MainWindow", u"Input & output files", None))
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
        self.dockWidget_editor.setWindowTitle(QCoreApplication.translate("MainWindow", u"Editor", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Main program directory:", None))
        self.label_mainpath.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_save_program.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Save</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_save_program.setText(QCoreApplication.translate("MainWindow", u"...", None))
    # retranslateUi

