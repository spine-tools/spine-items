# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

################################################################################
## Form generated from reading UI file 'tool_properties.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
    QToolButton, QTreeView, QVBoxLayout, QWidget)

from ...widgets import ArgsTreeView
from spinetoolbox.widgets.custom_qwidgets import ElidedLabel
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(312, 612)
        Form.setStyleSheet(u"QScrollArea { background: transparent; }\n"
"QScrollArea > QWidget > QWidget { background: transparent; }")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 312, 612))
        self.scrollAreaWidgetContents.setAutoFillBackground(False)
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(6)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(-1, -1, -1, 6)
        self.label_tool_specification = QLabel(self.scrollAreaWidgetContents)
        self.label_tool_specification.setObjectName(u"label_tool_specification")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_tool_specification.sizePolicy().hasHeightForWidth())
        self.label_tool_specification.setSizePolicy(sizePolicy)
        self.label_tool_specification.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_9.addWidget(self.label_tool_specification)

        self.comboBox_tool = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_tool.setObjectName(u"comboBox_tool")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_tool.sizePolicy().hasHeightForWidth())
        self.comboBox_tool.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.comboBox_tool)

        self.toolButton_tool_specification = QToolButton(self.scrollAreaWidgetContents)
        self.toolButton_tool_specification.setObjectName(u"toolButton_tool_specification")
        icon = QIcon()
        icon.addFile(u":/icons/wrench.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_tool_specification.setIcon(icon)
        self.toolButton_tool_specification.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.horizontalLayout_9.addWidget(self.toolButton_tool_specification)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_options = QHBoxLayout()
        self.horizontalLayout_options.setObjectName(u"horizontalLayout_options")
        self.horizontalLayout_options.setContentsMargins(-1, 0, -1, 6)

        self.verticalLayout_3.addLayout(self.horizontalLayout_options)

        self.splitter = QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.treeView_cmdline_args = ArgsTreeView(self.splitter)
        self.treeView_cmdline_args.setObjectName(u"treeView_cmdline_args")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.treeView_cmdline_args.sizePolicy().hasHeightForWidth())
        self.treeView_cmdline_args.setSizePolicy(sizePolicy2)
        self.treeView_cmdline_args.setAcceptDrops(True)
        self.treeView_cmdline_args.setEditTriggers(QAbstractItemView.EditTrigger.AnyKeyPressed|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.treeView_cmdline_args.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.treeView_cmdline_args.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_cmdline_args.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.splitter.addWidget(self.treeView_cmdline_args)
        self.treeView_cmdline_args.header().setMinimumSectionSize(26)
        self.gridLayoutWidget = QWidget(self.splitter)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.toolButton_remove_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_remove_arg.setObjectName(u"toolButton_remove_arg")
        icon1 = QIcon()
        icon1.addFile(u":/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_remove_arg.setIcon(icon1)

        self.gridLayout.addWidget(self.toolButton_remove_arg, 0, 2, 1, 1)

        self.toolButton_add_file_path_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_add_file_path_arg.setObjectName(u"toolButton_add_file_path_arg")
        icon2 = QIcon()
        icon2.addFile(u":/icons/file-upload.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_add_file_path_arg.setIcon(icon2)
        self.toolButton_add_file_path_arg.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.gridLayout.addWidget(self.toolButton_add_file_path_arg, 0, 0, 1, 1)

        self.treeView_input_files = QTreeView(self.gridLayoutWidget)
        self.treeView_input_files.setObjectName(u"treeView_input_files")
        sizePolicy2.setHeightForWidth(self.treeView_input_files.sizePolicy().hasHeightForWidth())
        self.treeView_input_files.setSizePolicy(sizePolicy2)
        self.treeView_input_files.setDragEnabled(False)
        self.treeView_input_files.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.treeView_input_files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_input_files.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.treeView_input_files.setUniformRowHeights(True)
        self.treeView_input_files.setAnimated(False)
        self.treeView_input_files.header().setMinimumSectionSize(26)

        self.gridLayout.addWidget(self.treeView_input_files, 1, 0, 1, 3)

        self.splitter.addWidget(self.gridLayoutWidget)

        self.verticalLayout_3.addWidget(self.splitter)

        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.radioButton_execute_in_source = QRadioButton(self.frame)
        self.radioButton_execute_in_source.setObjectName(u"radioButton_execute_in_source")

        self.horizontalLayout.addWidget(self.radioButton_execute_in_source)

        self.radioButton_execute_in_work = QRadioButton(self.frame)
        self.radioButton_execute_in_work.setObjectName(u"radioButton_execute_in_work")
        self.radioButton_execute_in_work.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButton_execute_in_work)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lineEdit_root_directory = QLineEdit(self.frame)
        self.lineEdit_root_directory.setObjectName(u"lineEdit_root_directory")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEdit_root_directory.sizePolicy().hasHeightForWidth())
        self.lineEdit_root_directory.setSizePolicy(sizePolicy3)
        self.lineEdit_root_directory.setClearButtonEnabled(True)

        self.horizontalLayout_3.addWidget(self.lineEdit_root_directory)

        self.toolButton_browse_root_directory = QToolButton(self.frame)
        self.toolButton_browse_root_directory.setObjectName(u"toolButton_browse_root_directory")
        icon3 = QIcon()
        icon3.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_root_directory.setIcon(icon3)

        self.horizontalLayout_3.addWidget(self.toolButton_browse_root_directory)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.label_group_id = QLabel(self.frame)
        self.label_group_id.setObjectName(u"label_group_id")

        self.verticalLayout_2.addWidget(self.label_group_id)

        self.lineEdit_group_id = QLineEdit(self.frame)
        self.lineEdit_group_id.setObjectName(u"lineEdit_group_id")
        sizePolicy3.setHeightForWidth(self.lineEdit_group_id.sizePolicy().hasHeightForWidth())
        self.lineEdit_group_id.setSizePolicy(sizePolicy3)
        self.lineEdit_group_id.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.lineEdit_group_id)

        self.label_jupyter = ElidedLabel(self.frame)
        self.label_jupyter.setObjectName(u"label_jupyter")

        self.verticalLayout_2.addWidget(self.label_jupyter)

        self.kill_consoles_check_box = QCheckBox(self.frame)
        self.kill_consoles_check_box.setObjectName(u"kill_consoles_check_box")

        self.verticalLayout_2.addWidget(self.kill_consoles_check_box)

        self.log_process_output_check_box = QCheckBox(self.frame)
        self.log_process_output_check_box.setObjectName(u"log_process_output_check_box")

        self.verticalLayout_2.addWidget(self.log_process_output_check_box)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setSpacing(6)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.pushButton_tool_results = QPushButton(self.frame)
        self.pushButton_tool_results.setObjectName(u"pushButton_tool_results")
        sizePolicy3.setHeightForWidth(self.pushButton_tool_results.sizePolicy().hasHeightForWidth())
        self.pushButton_tool_results.setSizePolicy(sizePolicy3)

        self.horizontalLayout_11.addWidget(self.pushButton_tool_results)

        self.lineEdit_result_directory = QLineEdit(self.frame)
        self.lineEdit_result_directory.setObjectName(u"lineEdit_result_directory")
        self.lineEdit_result_directory.setReadOnly(False)
        self.lineEdit_result_directory.setClearButtonEnabled(True)

        self.horizontalLayout_11.addWidget(self.lineEdit_result_directory)

        self.toolButton_browse_result_directory = QToolButton(self.frame)
        self.toolButton_browse_result_directory.setObjectName(u"toolButton_browse_result_directory")
        self.toolButton_browse_result_directory.setIcon(icon3)

        self.horizontalLayout_11.addWidget(self.toolButton_browse_result_directory)


        self.verticalLayout_2.addLayout(self.horizontalLayout_11)


        self.verticalLayout_3.addWidget(self.frame)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.comboBox_tool, self.toolButton_tool_specification)
        QWidget.setTabOrder(self.toolButton_tool_specification, self.treeView_cmdline_args)
        QWidget.setTabOrder(self.treeView_cmdline_args, self.toolButton_add_file_path_arg)
        QWidget.setTabOrder(self.toolButton_add_file_path_arg, self.toolButton_remove_arg)
        QWidget.setTabOrder(self.toolButton_remove_arg, self.treeView_input_files)
        QWidget.setTabOrder(self.treeView_input_files, self.radioButton_execute_in_source)
        QWidget.setTabOrder(self.radioButton_execute_in_source, self.radioButton_execute_in_work)
        QWidget.setTabOrder(self.radioButton_execute_in_work, self.lineEdit_root_directory)
        QWidget.setTabOrder(self.lineEdit_root_directory, self.toolButton_browse_root_directory)
        QWidget.setTabOrder(self.toolButton_browse_root_directory, self.lineEdit_group_id)
        QWidget.setTabOrder(self.lineEdit_group_id, self.kill_consoles_check_box)
        QWidget.setTabOrder(self.kill_consoles_check_box, self.log_process_output_check_box)
        QWidget.setTabOrder(self.log_process_output_check_box, self.pushButton_tool_results)
        QWidget.setTabOrder(self.pushButton_tool_results, self.lineEdit_result_directory)
        QWidget.setTabOrder(self.lineEdit_result_directory, self.toolButton_browse_result_directory)
        QWidget.setTabOrder(self.toolButton_browse_result_directory, self.scrollArea)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_tool_specification.setText(QCoreApplication.translate("Form", u"Specification:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_tool.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tool specification for this Tool</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_tool_specification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tool specification options.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected tool command line args</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Append selected Available resources to Tool arguments</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"Execute in", None))
        self.radioButton_execute_in_source.setText(QCoreApplication.translate("Form", u"Source dir", None))
        self.radioButton_execute_in_work.setText(QCoreApplication.translate("Form", u"Work dir", None))
        self.label.setText(QCoreApplication.translate("Form", u"Source code root directory:", None))
        self.lineEdit_root_directory.setText("")
        self.lineEdit_root_directory.setPlaceholderText(QCoreApplication.translate("Form", u"Root directory path...", None))
        self.label_group_id.setText(QCoreApplication.translate("Form", u"Reuse console id:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_group_id.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Enter an id for sharing a console with other Tools in this project. Leave empty to run this Tool in isolation.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_jupyter.setText(QCoreApplication.translate("Form", u"Console info", None))
#if QT_CONFIG(tooltip)
        self.kill_consoles_check_box.setToolTip(QCoreApplication.translate("Form", u"If checked, console processes will be killed automatically after execution finishes freeing memory and other resources.", None))
#endif // QT_CONFIG(tooltip)
        self.kill_consoles_check_box.setText(QCoreApplication.translate("Form", u"Kill consoles at the end of execution", None))
        self.log_process_output_check_box.setText(QCoreApplication.translate("Form", u"Log process output to a file", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tool_results.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open results archive in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tool_results.setText(QCoreApplication.translate("Form", u"Results...", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_result_directory.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Result directory</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_result_directory.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_browse_result_directory.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select Result directory using file browser. Leave blank to use default directory.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

