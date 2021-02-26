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
## Form generated from reading UI file 'gimlet_properties.ui'
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

from ...widgets import ArgsTreeView
from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(395, 396)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_gimlet_name = QLabel(Form)
        self.label_gimlet_name.setObjectName(u"label_gimlet_name")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_gimlet_name.sizePolicy().hasHeightForWidth())
        self.label_gimlet_name.setSizePolicy(sizePolicy)
        self.label_gimlet_name.setMinimumSize(QSize(0, 20))
        self.label_gimlet_name.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_gimlet_name.setFont(font)
        self.label_gimlet_name.setStyleSheet(u"background-color: #ecd8c6;")
        self.label_gimlet_name.setFrameShape(QFrame.Box)
        self.label_gimlet_name.setFrameShadow(QFrame.Sunken)
        self.label_gimlet_name.setAlignment(Qt.AlignCenter)
        self.label_gimlet_name.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_gimlet_name)

        self.scrollArea_4 = QScrollArea(Form)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 393, 374))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.checkBox_shell = QCheckBox(self.scrollAreaWidgetContents_4)
        self.checkBox_shell.setObjectName(u"checkBox_shell")
        font1 = QFont()
        font1.setPointSize(10)
        self.checkBox_shell.setFont(font1)
        self.checkBox_shell.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.checkBox_shell)

        self.comboBox_shell = QComboBox(self.scrollAreaWidgetContents_4)
        self.comboBox_shell.setObjectName(u"comboBox_shell")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_shell.sizePolicy().hasHeightForWidth())
        self.comboBox_shell.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_shell)

        self.label_2 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.lineEdit_cmd = PropertyQLineEdit(self.scrollAreaWidgetContents_4)
        self.lineEdit_cmd.setObjectName(u"lineEdit_cmd")
        self.lineEdit_cmd.setClearButtonEnabled(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_cmd)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.splitter = QSplitter(self.scrollAreaWidgetContents_4)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.treeView_cmdline_args = ArgsTreeView(self.splitter)
        self.treeView_cmdline_args.setObjectName(u"treeView_cmdline_args")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.treeView_cmdline_args.sizePolicy().hasHeightForWidth())
        self.treeView_cmdline_args.setSizePolicy(sizePolicy2)
        self.treeView_cmdline_args.setFont(font1)
        self.treeView_cmdline_args.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView_cmdline_args.setAcceptDrops(True)
        self.treeView_cmdline_args.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.treeView_cmdline_args.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeView_cmdline_args.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_cmdline_args.setTextElideMode(Qt.ElideLeft)
        self.splitter.addWidget(self.treeView_cmdline_args)
        self.treeView_cmdline_args.header().setMinimumSectionSize(26)
        self.gridLayoutWidget = QWidget(self.splitter)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButton_remove_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_remove_arg.setObjectName(u"toolButton_remove_arg")
        icon = QIcon()
        icon.addFile(u":/icons/minus.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_remove_arg.setIcon(icon)

        self.gridLayout.addWidget(self.toolButton_remove_arg, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.toolButton_add_file_path_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_add_file_path_arg.setObjectName(u"toolButton_add_file_path_arg")
        self.toolButton_add_file_path_arg.setMinimumSize(QSize(22, 22))
        self.toolButton_add_file_path_arg.setMaximumSize(QSize(22, 22))
        icon1 = QIcon()
        icon1.addFile(u":/icons/file-upload.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_file_path_arg.setIcon(icon1)
        self.toolButton_add_file_path_arg.setIconSize(QSize(16, 16))
        self.toolButton_add_file_path_arg.setPopupMode(QToolButton.InstantPopup)

        self.gridLayout.addWidget(self.toolButton_add_file_path_arg, 0, 0, 1, 1)

        self.treeView_files = QTreeView(self.gridLayoutWidget)
        self.treeView_files.setObjectName(u"treeView_files")
        self.treeView_files.setFont(font1)
        self.treeView_files.setDragDropMode(QAbstractItemView.DragOnly)
        self.treeView_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_files.setTextElideMode(Qt.ElideLeft)
        self.treeView_files.setUniformRowHeights(True)
        self.treeView_files.header().setMinimumSectionSize(54)

        self.gridLayout.addWidget(self.treeView_files, 1, 0, 1, 3)

        self.splitter.addWidget(self.gridLayoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        self.line_5 = QFrame(self.scrollAreaWidgetContents_4)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line_5)

        self.label = QLabel(self.scrollAreaWidgetContents_4)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.radioButton_default = QRadioButton(self.scrollAreaWidgetContents_4)
        self.radioButton_default.setObjectName(u"radioButton_default")
        self.radioButton_default.setChecked(True)

        self.horizontalLayout_16.addWidget(self.radioButton_default)

        self.radioButton_unique = QRadioButton(self.scrollAreaWidgetContents_4)
        self.radioButton_unique.setObjectName(u"radioButton_unique")

        self.horizontalLayout_16.addWidget(self.radioButton_unique)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_12)

        self.toolButton_gimlet_open_dir = QToolButton(self.scrollAreaWidgetContents_4)
        self.toolButton_gimlet_open_dir.setObjectName(u"toolButton_gimlet_open_dir")
        self.toolButton_gimlet_open_dir.setMinimumSize(QSize(22, 22))
        self.toolButton_gimlet_open_dir.setMaximumSize(QSize(22, 22))
        icon2 = QIcon()
        icon2.addFile(u":/icons/folder-open-regular.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_gimlet_open_dir.setIcon(icon2)

        self.horizontalLayout_16.addWidget(self.toolButton_gimlet_open_dir)


        self.verticalLayout_2.addLayout(self.horizontalLayout_16)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)

        self.verticalLayout.addWidget(self.scrollArea_4)

        QWidget.setTabOrder(self.scrollArea_4, self.radioButton_default)
        QWidget.setTabOrder(self.radioButton_default, self.radioButton_unique)
        QWidget.setTabOrder(self.radioButton_unique, self.toolButton_gimlet_open_dir)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_gimlet_name.setText(QCoreApplication.translate("Form", u"Name", None))
#if QT_CONFIG(tooltip)
        self.checkBox_shell.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>If checked, command is executed with the specified shell.</p><p>If unchecked, command is executed without a shell.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_shell.setText(QCoreApplication.translate("Form", u"Shell", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Command", None))
#if QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected command line args</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Append selected input file paths to the list of command line args</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setText("")
        self.label.setText(QCoreApplication.translate("Form", u"Work directory", None))
        self.radioButton_default.setText(QCoreApplication.translate("Form", u"Default", None))
        self.radioButton_unique.setText(QCoreApplication.translate("Form", u"Unique", None))
#if QT_CONFIG(tooltip)
        self.toolButton_gimlet_open_dir.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open this View's project directory in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

