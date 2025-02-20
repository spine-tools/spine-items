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
## Form generated from reading UI file 'import_editor_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListView, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QSplitter, QTableView, QToolButton, QVBoxLayout,
    QWidget)

from spine_items.importer.widgets.multi_checkable_list_view import MultiCheckableListView
from spine_items.importer.widgets.table_view_with_button_header import TableViewWithButtonHeader
from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(929, 732)
        MainWindow.setDockNestingEnabled(True)
        self.export_mappings_action = QAction(MainWindow)
        self.export_mappings_action.setObjectName(u"export_mappings_action")
        self.export_mappings_action.setEnabled(False)
        self.import_mappings_action = QAction(MainWindow)
        self.import_mappings_action.setObjectName(u"import_mappings_action")
        self.import_mappings_action.setEnabled(False)
        self.switch_input_type_action = QAction(MainWindow)
        self.switch_input_type_action.setObjectName(u"switch_input_type_action")
        self.switch_input_type_action.setEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.input_path_label = QLabel(self.centralwidget)
        self.input_path_label.setObjectName(u"input_path_label")

        self.horizontalLayout_2.addWidget(self.input_path_label)

        self.input_path_line_edit = QLineEdit(self.centralwidget)
        self.input_path_line_edit.setObjectName(u"input_path_line_edit")
        self.input_path_line_edit.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.input_path_line_edit)

        self.browse_inputs_button = QToolButton(self.centralwidget)
        self.browse_inputs_button.setObjectName(u"browse_inputs_button")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.browse_inputs_button.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.browse_inputs_button)

        self.input_type_label = QLabel(self.centralwidget)
        self.input_type_label.setObjectName(u"input_type_label")

        self.horizontalLayout_2.addWidget(self.input_type_label)

        self.input_type_line_edit = QLineEdit(self.centralwidget)
        self.input_type_line_edit.setObjectName(u"input_type_line_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_type_line_edit.sizePolicy().hasHeightForWidth())
        self.input_type_line_edit.setSizePolicy(sizePolicy)
        self.input_type_line_edit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.input_type_line_edit)


        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.splitter_source_list = QSplitter(self.centralwidget)
        self.splitter_source_list.setObjectName(u"splitter_source_list")
        self.splitter_source_list.setOrientation(Qt.Orientation.Horizontal)
        self.source_list = MultiCheckableListView(self.splitter_source_list)
        self.source_list.setObjectName(u"source_list")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.source_list.sizePolicy().hasHeightForWidth())
        self.source_list.setSizePolicy(sizePolicy1)
        self.source_list.setMaximumSize(QSize(16777215, 16777215))
        self.source_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.source_list.setAcceptDrops(True)
        self.source_list.setDragEnabled(True)
        self.source_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.source_list.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.splitter_source_list.addWidget(self.source_list)
        self.splitter_source_data_mappings = QSplitter(self.splitter_source_list)
        self.splitter_source_data_mappings.setObjectName(u"splitter_source_data_mappings")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(5)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter_source_data_mappings.sizePolicy().hasHeightForWidth())
        self.splitter_source_data_mappings.setSizePolicy(sizePolicy2)
        self.splitter_source_data_mappings.setOrientation(Qt.Orientation.Horizontal)
        self.frame_source_data = QFrame(self.splitter_source_data_mappings)
        self.frame_source_data.setObjectName(u"frame_source_data")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_source_data.sizePolicy().hasHeightForWidth())
        self.frame_source_data.setSizePolicy(sizePolicy3)
        self.frame_source_data.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_source_data.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_source_data.setLineWidth(0)
        self.frame_source_data.setMidLineWidth(0)
        self.verticalLayout = QVBoxLayout(self.frame_source_data)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_source_options = QVBoxLayout()
        self.verticalLayout_source_options.setSpacing(0)
        self.verticalLayout_source_options.setObjectName(u"verticalLayout_source_options")

        self.verticalLayout.addLayout(self.verticalLayout_source_options)

        self.source_data_table = TableViewWithButtonHeader(self.frame_source_data)
        self.source_data_table.setObjectName(u"source_data_table")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.source_data_table.sizePolicy().hasHeightForWidth())
        self.source_data_table.setSizePolicy(sizePolicy4)
        self.source_data_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.verticalLayout.addWidget(self.source_data_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label = QLabel(self.frame_source_data)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.default_column_type_combo_box = QComboBox(self.frame_source_data)
        self.default_column_type_combo_box.setObjectName(u"default_column_type_combo_box")

        self.horizontalLayout.addWidget(self.default_column_type_combo_box)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter_source_data_mappings.addWidget(self.frame_source_data)
        self.splitter = QSplitter(self.splitter_source_data_mappings)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_4 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.mapping_list = QListView(self.verticalLayoutWidget_2)
        self.mapping_list.setObjectName(u"mapping_list")
        self.mapping_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.mapping_list.setAcceptDrops(True)
        self.mapping_list.setDragEnabled(True)
        self.mapping_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.mapping_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.verticalLayout_4.addWidget(self.mapping_list)

        self.splitter.addWidget(self.verticalLayoutWidget_2)
        self.frame_2 = QFrame(self.splitter)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_2.setLineWidth(0)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.new_button = QPushButton(self.frame_2)
        self.new_button.setObjectName(u"new_button")

        self.button_layout.addWidget(self.new_button)

        self.remove_button = QPushButton(self.frame_2)
        self.remove_button.setObjectName(u"remove_button")

        self.button_layout.addWidget(self.remove_button)

        self.duplicate_button = QPushButton(self.frame_2)
        self.duplicate_button.setObjectName(u"duplicate_button")

        self.button_layout.addWidget(self.duplicate_button)


        self.verticalLayout_2.addLayout(self.button_layout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.mapping_options_contents = QGridLayout()
        self.mapping_options_contents.setSpacing(3)
        self.mapping_options_contents.setObjectName(u"mapping_options_contents")
        self.mapping_options_contents.setContentsMargins(3, 3, 3, 3)
        self.class_type_combo_box = QComboBox(self.frame_2)
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.setObjectName(u"class_type_combo_box")

        self.mapping_options_contents.addWidget(self.class_type_combo_box, 0, 1, 1, 1)

        self.value_type_label = QLabel(self.frame_2)
        self.value_type_label.setObjectName(u"value_type_label")

        self.mapping_options_contents.addWidget(self.value_type_label, 3, 0, 1, 1)

        self.value_type_combo_box = QComboBox(self.frame_2)
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.setObjectName(u"value_type_combo_box")

        self.mapping_options_contents.addWidget(self.value_type_combo_box, 3, 1, 1, 1)

        self.start_read_row_spin_box = QSpinBox(self.frame_2)
        self.start_read_row_spin_box.setObjectName(u"start_read_row_spin_box")
        self.start_read_row_spin_box.setMinimum(1)

        self.mapping_options_contents.addWidget(self.start_read_row_spin_box, 7, 1, 1, 1)

        self.class_type_label = QLabel(self.frame_2)
        self.class_type_label.setObjectName(u"class_type_label")

        self.mapping_options_contents.addWidget(self.class_type_label, 0, 0, 1, 1)

        self.dimension_spin_box = QSpinBox(self.frame_2)
        self.dimension_spin_box.setObjectName(u"dimension_spin_box")
        self.dimension_spin_box.setValue(0)

        self.mapping_options_contents.addWidget(self.dimension_spin_box, 4, 1, 1, 1)

        self.parameter_type_label = QLabel(self.frame_2)
        self.parameter_type_label.setObjectName(u"parameter_type_label")

        self.mapping_options_contents.addWidget(self.parameter_type_label, 2, 0, 1, 1)

        self.dimension_label = QLabel(self.frame_2)
        self.dimension_label.setObjectName(u"dimension_label")

        self.mapping_options_contents.addWidget(self.dimension_label, 4, 0, 1, 1)

        self.ignore_columns_button = QPushButton(self.frame_2)
        self.ignore_columns_button.setObjectName(u"ignore_columns_button")

        self.mapping_options_contents.addWidget(self.ignore_columns_button, 8, 1, 1, 1)

        self.import_entity_alternatives_check_box = QCheckBox(self.frame_2)
        self.import_entity_alternatives_check_box.setObjectName(u"import_entity_alternatives_check_box")

        self.mapping_options_contents.addWidget(self.import_entity_alternatives_check_box, 9, 0, 1, 1)

        self.map_dimension_spin_box = QSpinBox(self.frame_2)
        self.map_dimension_spin_box.setObjectName(u"map_dimension_spin_box")
        self.map_dimension_spin_box.setMinimum(1)

        self.mapping_options_contents.addWidget(self.map_dimension_spin_box, 5, 1, 1, 1)

        self.parameter_type_combo_box = QComboBox(self.frame_2)
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.setObjectName(u"parameter_type_combo_box")

        self.mapping_options_contents.addWidget(self.parameter_type_combo_box, 2, 1, 1, 1)

        self.read_start_row_label = QLabel(self.frame_2)
        self.read_start_row_label.setObjectName(u"read_start_row_label")

        self.mapping_options_contents.addWidget(self.read_start_row_label, 7, 0, 1, 1)

        self.ignore_columns_label = QLabel(self.frame_2)
        self.ignore_columns_label.setObjectName(u"ignore_columns_label")

        self.mapping_options_contents.addWidget(self.ignore_columns_label, 8, 0, 1, 1)

        self.map_dimensions_label = QLabel(self.frame_2)
        self.map_dimensions_label.setObjectName(u"map_dimensions_label")

        self.mapping_options_contents.addWidget(self.map_dimensions_label, 5, 0, 1, 1)

        self.import_entities_check_box = QCheckBox(self.frame_2)
        self.import_entities_check_box.setObjectName(u"import_entities_check_box")

        self.mapping_options_contents.addWidget(self.import_entities_check_box, 10, 0, 1, 1)

        self.time_series_repeat_check_box = QCheckBox(self.frame_2)
        self.time_series_repeat_check_box.setObjectName(u"time_series_repeat_check_box")

        self.mapping_options_contents.addWidget(self.time_series_repeat_check_box, 9, 1, 1, 1)

        self.map_compression_check_box = QCheckBox(self.frame_2)
        self.map_compression_check_box.setObjectName(u"map_compression_check_box")

        self.mapping_options_contents.addWidget(self.map_compression_check_box, 10, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.mapping_options_contents)

        self.mapping_spec_table = QTableView(self.frame_2)
        self.mapping_spec_table.setObjectName(u"mapping_spec_table")
        self.mapping_spec_table.setLineWidth(0)
        self.mapping_spec_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.mapping_spec_table)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.splitter.addWidget(self.frame_2)
        self.splitter_source_data_mappings.addWidget(self.splitter)
        self.splitter_source_list.addWidget(self.splitter_source_data_mappings)

        self.verticalLayout_6.addWidget(self.splitter_source_list)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.input_path_line_edit, self.browse_inputs_button)
        QWidget.setTabOrder(self.browse_inputs_button, self.input_type_line_edit)
        QWidget.setTabOrder(self.input_type_line_edit, self.source_list)
        QWidget.setTabOrder(self.source_list, self.source_data_table)
        QWidget.setTabOrder(self.source_data_table, self.default_column_type_combo_box)
        QWidget.setTabOrder(self.default_column_type_combo_box, self.mapping_list)
        QWidget.setTabOrder(self.mapping_list, self.new_button)
        QWidget.setTabOrder(self.new_button, self.remove_button)
        QWidget.setTabOrder(self.remove_button, self.duplicate_button)
        QWidget.setTabOrder(self.duplicate_button, self.class_type_combo_box)
        QWidget.setTabOrder(self.class_type_combo_box, self.parameter_type_combo_box)
        QWidget.setTabOrder(self.parameter_type_combo_box, self.value_type_combo_box)
        QWidget.setTabOrder(self.value_type_combo_box, self.dimension_spin_box)
        QWidget.setTabOrder(self.dimension_spin_box, self.map_dimension_spin_box)
        QWidget.setTabOrder(self.map_dimension_spin_box, self.start_read_row_spin_box)
        QWidget.setTabOrder(self.start_read_row_spin_box, self.ignore_columns_button)
        QWidget.setTabOrder(self.ignore_columns_button, self.mapping_spec_table)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Import Editor", None))
        self.export_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Export mappings...", None))
        self.import_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Import mappings...", None))
        self.switch_input_type_action.setText(QCoreApplication.translate("MainWindow", u"Switch input type...", None))
#if QT_CONFIG(tooltip)
        self.switch_input_type_action.setToolTip(QCoreApplication.translate("MainWindow", u"Open a dialog to change input type.", None))
#endif // QT_CONFIG(tooltip)
        self.input_path_label.setText(QCoreApplication.translate("MainWindow", u"Input file/URL:", None))
        self.input_path_line_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select input file from the browse button...", None))
#if QT_CONFIG(tooltip)
        self.browse_inputs_button.setToolTip(QCoreApplication.translate("MainWindow", u"Browse input files or specify database URL.", None))
#endif // QT_CONFIG(tooltip)
        self.browse_inputs_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.input_type_label.setText(QCoreApplication.translate("MainWindow", u"Input type:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Surplus column data type:", None))
#if QT_CONFIG(tooltip)
        self.default_column_type_combo_box.setToolTip(QCoreApplication.translate("MainWindow", u"Select data type for additional columns in variable-length pivoted source data.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Mappings", None))
        self.new_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.duplicate_button.setText(QCoreApplication.translate("MainWindow", u"Duplicate", None))
        self.class_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Entity class", None))
        self.class_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Entity group", None))
        self.class_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.class_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.class_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.class_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Parameter value list", None))

        self.value_type_label.setText(QCoreApplication.translate("MainWindow", u"Default value type:", None))
        self.value_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Single value", None))
        self.value_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Time series", None))
        self.value_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Time pattern", None))
        self.value_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Map", None))
        self.value_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Array", None))

        self.class_type_label.setText(QCoreApplication.translate("MainWindow", u"Item type:", None))
#if QT_CONFIG(tooltip)
        self.dimension_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of entity dimensions.", None))
#endif // QT_CONFIG(tooltip)
        self.parameter_type_label.setText(QCoreApplication.translate("MainWindow", u"Parameter type:", None))
        self.dimension_label.setText(QCoreApplication.translate("MainWindow", u"Number of dimensions:", None))
        self.ignore_columns_button.setText("")
        self.import_entity_alternatives_check_box.setText(QCoreApplication.translate("MainWindow", u"Import entity alternatives", None))
#if QT_CONFIG(tooltip)
        self.map_dimension_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of dimensions when value type is Map.", None))
#endif // QT_CONFIG(tooltip)
        self.parameter_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Value", None))
        self.parameter_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Definition", None))
        self.parameter_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"None", None))

        self.read_start_row_label.setText(QCoreApplication.translate("MainWindow", u"Read data from row:", None))
        self.ignore_columns_label.setText(QCoreApplication.translate("MainWindow", u"Ignore columns:", None))
        self.map_dimensions_label.setText(QCoreApplication.translate("MainWindow", u"Map dimensions:", None))
        self.import_entities_check_box.setText(QCoreApplication.translate("MainWindow", u"Import entities", None))
#if QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Set the repeat flag for all imported time series", None))
#endif // QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setText(QCoreApplication.translate("MainWindow", u"Repeat time series", None))
        self.map_compression_check_box.setText(QCoreApplication.translate("MainWindow", u"Compress Maps", None))
    # retranslateUi

