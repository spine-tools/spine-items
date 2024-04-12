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
## Created by: Qt User Interface Compiler version 6.5.2
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
        self.actionSwitch_connector = QAction(MainWindow)
        self.actionSwitch_connector.setObjectName(u"actionSwitch_connector")
        self.actionSwitch_connector.setEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.source_label = QLabel(self.centralwidget)
        self.source_label.setObjectName(u"source_label")

        self.horizontalLayout_2.addWidget(self.source_label)

        self.source_line_edit = QLineEdit(self.centralwidget)
        self.source_line_edit.setObjectName(u"source_line_edit")
        self.source_line_edit.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.source_line_edit)

        self.browse_source_button = QToolButton(self.centralwidget)
        self.browse_source_button.setObjectName(u"browse_source_button")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.browse_source_button.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.browse_source_button)

        self.connector_label = QLabel(self.centralwidget)
        self.connector_label.setObjectName(u"connector_label")

        self.horizontalLayout_2.addWidget(self.connector_label)

        self.connector_line_edit = QLineEdit(self.centralwidget)
        self.connector_line_edit.setObjectName(u"connector_line_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connector_line_edit.sizePolicy().hasHeightForWidth())
        self.connector_line_edit.setSizePolicy(sizePolicy)
        self.connector_line_edit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.connector_line_edit)


        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.splitter_source_list = QSplitter(self.centralwidget)
        self.splitter_source_list.setObjectName(u"splitter_source_list")
        self.splitter_source_list.setOrientation(Qt.Horizontal)
        self.source_list = MultiCheckableListView(self.splitter_source_list)
        self.source_list.setObjectName(u"source_list")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.source_list.sizePolicy().hasHeightForWidth())
        self.source_list.setSizePolicy(sizePolicy1)
        self.source_list.setMaximumSize(QSize(16777215, 16777215))
        self.source_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.source_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.source_list.setTextElideMode(Qt.ElideLeft)
        self.splitter_source_list.addWidget(self.source_list)
        self.splitter_source_data_mappings = QSplitter(self.splitter_source_list)
        self.splitter_source_data_mappings.setObjectName(u"splitter_source_data_mappings")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(5)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter_source_data_mappings.sizePolicy().hasHeightForWidth())
        self.splitter_source_data_mappings.setSizePolicy(sizePolicy2)
        self.splitter_source_data_mappings.setOrientation(Qt.Horizontal)
        self.frame_source_data = QFrame(self.splitter_source_data_mappings)
        self.frame_source_data.setObjectName(u"frame_source_data")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_source_data.sizePolicy().hasHeightForWidth())
        self.frame_source_data.setSizePolicy(sizePolicy3)
        self.frame_source_data.setFrameShape(QFrame.NoFrame)
        self.frame_source_data.setFrameShadow(QFrame.Raised)
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
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.source_data_table.sizePolicy().hasHeightForWidth())
        self.source_data_table.setSizePolicy(sizePolicy4)
        self.source_data_table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.verticalLayout.addWidget(self.source_data_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

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
        self.splitter.setOrientation(Qt.Vertical)
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
        self.mapping_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mapping_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.verticalLayout_4.addWidget(self.mapping_list)

        self.splitter.addWidget(self.verticalLayoutWidget_2)
        self.frame_2 = QFrame(self.splitter)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
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
        self.ignore_columns_button = QPushButton(self.frame_2)
        self.ignore_columns_button.setObjectName(u"ignore_columns_button")

        self.mapping_options_contents.addWidget(self.ignore_columns_button, 9, 1, 1, 1)

        self.value_type_label = QLabel(self.frame_2)
        self.value_type_label.setObjectName(u"value_type_label")

        self.mapping_options_contents.addWidget(self.value_type_label, 4, 0, 1, 1)

        self.class_type_label = QLabel(self.frame_2)
        self.class_type_label.setObjectName(u"class_type_label")

        self.mapping_options_contents.addWidget(self.class_type_label, 0, 0, 1, 1)

        self.read_start_row_label = QLabel(self.frame_2)
        self.read_start_row_label.setObjectName(u"read_start_row_label")

        self.mapping_options_contents.addWidget(self.read_start_row_label, 8, 0, 1, 1)

        self.map_dimensions_label = QLabel(self.frame_2)
        self.map_dimensions_label.setObjectName(u"map_dimensions_label")

        self.mapping_options_contents.addWidget(self.map_dimensions_label, 6, 0, 1, 1)

        self.before_alternative_check_box = QCheckBox(self.frame_2)
        self.before_alternative_check_box.setObjectName(u"before_alternative_check_box")

        self.mapping_options_contents.addWidget(self.before_alternative_check_box, 10, 1, 1, 1)

        self.ignore_columns_label = QLabel(self.frame_2)
        self.ignore_columns_label.setObjectName(u"ignore_columns_label")

        self.mapping_options_contents.addWidget(self.ignore_columns_label, 9, 0, 1, 1)

        self.class_type_combo_box = QComboBox(self.frame_2)
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.setObjectName(u"class_type_combo_box")

        self.mapping_options_contents.addWidget(self.class_type_combo_box, 0, 1, 1, 1)

        self.start_read_row_spin_box = QSpinBox(self.frame_2)
        self.start_read_row_spin_box.setObjectName(u"start_read_row_spin_box")
        self.start_read_row_spin_box.setMinimum(1)

        self.mapping_options_contents.addWidget(self.start_read_row_spin_box, 8, 1, 1, 1)

        self.map_dimension_spin_box = QSpinBox(self.frame_2)
        self.map_dimension_spin_box.setObjectName(u"map_dimension_spin_box")
        self.map_dimension_spin_box.setMinimum(1)

        self.mapping_options_contents.addWidget(self.map_dimension_spin_box, 6, 1, 1, 1)

        self.parameter_type_combo_box = QComboBox(self.frame_2)
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.setObjectName(u"parameter_type_combo_box")

        self.mapping_options_contents.addWidget(self.parameter_type_combo_box, 3, 1, 1, 1)

        self.map_compression_check_box = QCheckBox(self.frame_2)
        self.map_compression_check_box.setObjectName(u"map_compression_check_box")

        self.mapping_options_contents.addWidget(self.map_compression_check_box, 11, 1, 1, 1)

        self.import_entities_check_box = QCheckBox(self.frame_2)
        self.import_entities_check_box.setObjectName(u"import_entities_check_box")

        self.mapping_options_contents.addWidget(self.import_entities_check_box, 10, 0, 1, 1)

        self.value_type_combo_box = QComboBox(self.frame_2)
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.setObjectName(u"value_type_combo_box")

        self.mapping_options_contents.addWidget(self.value_type_combo_box, 4, 1, 1, 1)

        self.time_series_repeat_check_box = QCheckBox(self.frame_2)
        self.time_series_repeat_check_box.setObjectName(u"time_series_repeat_check_box")

        self.mapping_options_contents.addWidget(self.time_series_repeat_check_box, 11, 0, 1, 1)

        self.parameter_type_label = QLabel(self.frame_2)
        self.parameter_type_label.setObjectName(u"parameter_type_label")

        self.mapping_options_contents.addWidget(self.parameter_type_label, 3, 0, 1, 1)

        self.dimension_label = QLabel(self.frame_2)
        self.dimension_label.setObjectName(u"dimension_label")

        self.mapping_options_contents.addWidget(self.dimension_label, 5, 0, 1, 1)

        self.dimension_spin_box = QSpinBox(self.frame_2)
        self.dimension_spin_box.setObjectName(u"dimension_spin_box")
        self.dimension_spin_box.setValue(0)

        self.mapping_options_contents.addWidget(self.dimension_spin_box, 5, 1, 1, 1)


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
        QWidget.setTabOrder(self.source_line_edit, self.browse_source_button)
        QWidget.setTabOrder(self.browse_source_button, self.connector_line_edit)
        QWidget.setTabOrder(self.connector_line_edit, self.source_list)
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
        QWidget.setTabOrder(self.ignore_columns_button, self.import_entities_check_box)
        QWidget.setTabOrder(self.import_entities_check_box, self.before_alternative_check_box)
        QWidget.setTabOrder(self.before_alternative_check_box, self.time_series_repeat_check_box)
        QWidget.setTabOrder(self.time_series_repeat_check_box, self.map_compression_check_box)
        QWidget.setTabOrder(self.map_compression_check_box, self.mapping_spec_table)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Import Editor", None))
        self.export_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Export mappings...", None))
        self.import_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Import mappings...", None))
        self.actionSwitch_connector.setText(QCoreApplication.translate("MainWindow", u"Switch connector...", None))
        self.source_label.setText(QCoreApplication.translate("MainWindow", u"File path:", None))
        self.source_line_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select source from the browse button...", None))
#if QT_CONFIG(tooltip)
        self.browse_source_button.setToolTip(QCoreApplication.translate("MainWindow", u"Browse source files or specify database URL.", None))
#endif // QT_CONFIG(tooltip)
        self.browse_source_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.connector_label.setText(QCoreApplication.translate("MainWindow", u"Connector:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Surplus column data type:", None))
#if QT_CONFIG(tooltip)
        self.default_column_type_combo_box.setToolTip(QCoreApplication.translate("MainWindow", u"Select data type for additional columns in variable-length pivoted source data.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Mappings", None))
        self.new_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.duplicate_button.setText(QCoreApplication.translate("MainWindow", u"Duplicate", None))
        self.ignore_columns_button.setText("")
        self.value_type_label.setText(QCoreApplication.translate("MainWindow", u"Default value type:", None))
        self.class_type_label.setText(QCoreApplication.translate("MainWindow", u"Item type:", None))
        self.read_start_row_label.setText(QCoreApplication.translate("MainWindow", u"Read data from row:", None))
        self.map_dimensions_label.setText(QCoreApplication.translate("MainWindow", u"Map dimensions:", None))
#if QT_CONFIG(tooltip)
        self.before_alternative_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Enable or disable 'Before alternative name' mapping for scenario alternative item type.", None))
#endif // QT_CONFIG(tooltip)
        self.before_alternative_check_box.setText(QCoreApplication.translate("MainWindow", u"Use before alternative", None))
        self.ignore_columns_label.setText(QCoreApplication.translate("MainWindow", u"Ignore columns:", None))
        self.class_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Entity class", None))
        self.class_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Entity group", None))
        self.class_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.class_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.class_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.class_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Parameter value list", None))

#if QT_CONFIG(tooltip)
        self.map_dimension_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of dimensions when value type is Map.", None))
#endif // QT_CONFIG(tooltip)
        self.parameter_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Value", None))
        self.parameter_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Definition", None))
        self.parameter_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"None", None))

        self.map_compression_check_box.setText(QCoreApplication.translate("MainWindow", u"Compress Maps", None))
        self.import_entities_check_box.setText(QCoreApplication.translate("MainWindow", u"Import entities", None))
        self.value_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Single value", None))
        self.value_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Time series", None))
        self.value_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Time pattern", None))
        self.value_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Map", None))
        self.value_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Array", None))

#if QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Set the repeat flag for all imported time series", None))
#endif // QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setText(QCoreApplication.translate("MainWindow", u"Repeat time series", None))
        self.parameter_type_label.setText(QCoreApplication.translate("MainWindow", u"Parameter type:", None))
        self.dimension_label.setText(QCoreApplication.translate("MainWindow", u"Number of dimensions:", None))
#if QT_CONFIG(tooltip)
        self.dimension_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of entity dimensions.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

