# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
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
    QDockWidget, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QListView, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTableView,
    QToolButton, QVBoxLayout, QWidget)

from spine_items.importer.widgets.multi_checkable_list_view import MultiCheckableListView
from spine_items.importer.widgets.table_view_with_button_header import TableViewWithButtonHeader
from spinetoolbox.widgets.custom_combobox import ElidedCombobox
from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(964, 665)
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
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidget_source_tables = QDockWidget(MainWindow)
        self.dockWidget_source_tables.setObjectName(u"dockWidget_source_tables")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.source_list = MultiCheckableListView(self.dockWidgetContents)
        self.source_list.setObjectName(u"source_list")
        self.source_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.source_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.source_list.setTextElideMode(Qt.ElideLeft)

        self.verticalLayout_2.addWidget(self.source_list)

        self.dockWidget_source_tables.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_source_tables)
        self.dockWidget_source_options = QDockWidget(MainWindow)
        self.dockWidget_source_options.setObjectName(u"dockWidget_source_options")
        self.source_options_contents = QWidget()
        self.source_options_contents.setObjectName(u"source_options_contents")
        self.verticalLayout_5 = QVBoxLayout(self.source_options_contents)
        self.verticalLayout_5.setSpacing(3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(3, 3, 3, 3)
        self.dockWidget_source_options.setWidget(self.source_options_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_source_options)
        self.dockWidget_source_data = QDockWidget(MainWindow)
        self.dockWidget_source_data.setObjectName(u"dockWidget_source_data")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.source_data_table = TableViewWithButtonHeader(self.dockWidgetContents_3)
        self.source_data_table.setObjectName(u"source_data_table")
        self.source_data_table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.verticalLayout_3.addWidget(self.source_data_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.dockWidgetContents_3)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.default_column_type_combo_box = QComboBox(self.dockWidgetContents_3)
        self.default_column_type_combo_box.setObjectName(u"default_column_type_combo_box")

        self.horizontalLayout.addWidget(self.default_column_type_combo_box)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.dockWidget_source_data.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_source_data)
        self.dockWidget_mappings = QDockWidget(MainWindow)
        self.dockWidget_mappings.setObjectName(u"dockWidget_mappings")
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_7.setSpacing(3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(3, 3, 3, 3)
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.new_button = QPushButton(self.dockWidgetContents_4)
        self.new_button.setObjectName(u"new_button")

        self.button_layout.addWidget(self.new_button)

        self.remove_button = QPushButton(self.dockWidgetContents_4)
        self.remove_button.setObjectName(u"remove_button")

        self.button_layout.addWidget(self.remove_button)

        self.duplicate_button = QPushButton(self.dockWidgetContents_4)
        self.duplicate_button.setObjectName(u"duplicate_button")

        self.button_layout.addWidget(self.duplicate_button)


        self.verticalLayout_7.addLayout(self.button_layout)

        self.mapping_list = QListView(self.dockWidgetContents_4)
        self.mapping_list.setObjectName(u"mapping_list")
        self.mapping_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mapping_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.verticalLayout_7.addWidget(self.mapping_list)

        self.dockWidget_mappings.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_mappings)
        self.dockWidget_mapping_options = QDockWidget(MainWindow)
        self.dockWidget_mapping_options.setObjectName(u"dockWidget_mapping_options")
        self.mapping_options_contents = QWidget()
        self.mapping_options_contents.setObjectName(u"mapping_options_contents")
        self.formLayout_2 = QFormLayout(self.mapping_options_contents)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setHorizontalSpacing(3)
        self.formLayout_2.setVerticalSpacing(6)
        self.formLayout_2.setContentsMargins(3, 3, 3, 3)
        self.class_type_label = QLabel(self.mapping_options_contents)
        self.class_type_label.setObjectName(u"class_type_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.class_type_label)

        self.class_type_combo_box = QComboBox(self.mapping_options_contents)
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.addItem("")
        self.class_type_combo_box.setObjectName(u"class_type_combo_box")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.class_type_combo_box)

        self.import_objects_check_box = QCheckBox(self.mapping_options_contents)
        self.import_objects_check_box.setObjectName(u"import_objects_check_box")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.import_objects_check_box)

        self.parameter_type_label = QLabel(self.mapping_options_contents)
        self.parameter_type_label.setObjectName(u"parameter_type_label")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.parameter_type_label)

        self.parameter_type_combo_box = QComboBox(self.mapping_options_contents)
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.setObjectName(u"parameter_type_combo_box")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.parameter_type_combo_box)

        self.value_type_label = QLabel(self.mapping_options_contents)
        self.value_type_label.setObjectName(u"value_type_label")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.value_type_label)

        self.value_type_combo_box = QComboBox(self.mapping_options_contents)
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.addItem("")
        self.value_type_combo_box.setObjectName(u"value_type_combo_box")

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.value_type_combo_box)

        self.before_alternative_check_box = QCheckBox(self.mapping_options_contents)
        self.before_alternative_check_box.setObjectName(u"before_alternative_check_box")

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.before_alternative_check_box)

        self.read_start_row_label = QLabel(self.mapping_options_contents)
        self.read_start_row_label.setObjectName(u"read_start_row_label")

        self.formLayout_2.setWidget(6, QFormLayout.LabelRole, self.read_start_row_label)

        self.start_read_row_spin_box = QSpinBox(self.mapping_options_contents)
        self.start_read_row_spin_box.setObjectName(u"start_read_row_spin_box")
        self.start_read_row_spin_box.setMinimum(1)

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.start_read_row_spin_box)

        self.ignore_columns_label = QLabel(self.mapping_options_contents)
        self.ignore_columns_label.setObjectName(u"ignore_columns_label")

        self.formLayout_2.setWidget(7, QFormLayout.LabelRole, self.ignore_columns_label)

        self.ignore_columns_button = QPushButton(self.mapping_options_contents)
        self.ignore_columns_button.setObjectName(u"ignore_columns_button")

        self.formLayout_2.setWidget(7, QFormLayout.FieldRole, self.ignore_columns_button)

        self.dimension_label = QLabel(self.mapping_options_contents)
        self.dimension_label.setObjectName(u"dimension_label")

        self.formLayout_2.setWidget(8, QFormLayout.LabelRole, self.dimension_label)

        self.dimension_spin_box = QSpinBox(self.mapping_options_contents)
        self.dimension_spin_box.setObjectName(u"dimension_spin_box")
        self.dimension_spin_box.setMinimum(1)

        self.formLayout_2.setWidget(8, QFormLayout.FieldRole, self.dimension_spin_box)

        self.time_series_repeat_check_box = QCheckBox(self.mapping_options_contents)
        self.time_series_repeat_check_box.setObjectName(u"time_series_repeat_check_box")

        self.formLayout_2.setWidget(9, QFormLayout.LabelRole, self.time_series_repeat_check_box)

        self.map_dimensions_label = QLabel(self.mapping_options_contents)
        self.map_dimensions_label.setObjectName(u"map_dimensions_label")

        self.formLayout_2.setWidget(10, QFormLayout.LabelRole, self.map_dimensions_label)

        self.map_dimension_spin_box = QSpinBox(self.mapping_options_contents)
        self.map_dimension_spin_box.setObjectName(u"map_dimension_spin_box")
        self.map_dimension_spin_box.setMinimum(1)

        self.formLayout_2.setWidget(10, QFormLayout.FieldRole, self.map_dimension_spin_box)

        self.map_compression_check_box = QCheckBox(self.mapping_options_contents)
        self.map_compression_check_box.setObjectName(u"map_compression_check_box")

        self.formLayout_2.setWidget(11, QFormLayout.LabelRole, self.map_compression_check_box)

        self.dockWidget_mapping_options.setWidget(self.mapping_options_contents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_mapping_options)
        self.dockWidget_mapping_spec = QDockWidget(MainWindow)
        self.dockWidget_mapping_spec.setObjectName(u"dockWidget_mapping_spec")
        self.dockWidgetContents_6 = QWidget()
        self.dockWidgetContents_6.setObjectName(u"dockWidgetContents_6")
        self.verticalLayout_8 = QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_8.setSpacing(3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(3, 3, 3, 3)
        self.mapping_spec_table = QTableView(self.dockWidgetContents_6)
        self.mapping_spec_table.setObjectName(u"mapping_spec_table")
        self.mapping_spec_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_8.addWidget(self.mapping_spec_table)

        self.dockWidget_mapping_spec.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_mapping_spec)
        self.dockWidget_source_files = QDockWidget(MainWindow)
        self.dockWidget_source_files.setObjectName(u"dockWidget_source_files")
        self.dockWidgetContents_7 = QWidget()
        self.dockWidgetContents_7.setObjectName(u"dockWidgetContents_7")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_7)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.file_path_label = QLabel(self.dockWidgetContents_7)
        self.file_path_label.setObjectName(u"file_path_label")
        font = QFont()
        font.setPointSize(10)
        self.file_path_label.setFont(font)

        self.horizontalLayout_2.addWidget(self.file_path_label)

        self.comboBox_source_file = ElidedCombobox(self.dockWidgetContents_7)
        self.comboBox_source_file.setObjectName(u"comboBox_source_file")
        self.comboBox_source_file.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_source_file.sizePolicy().hasHeightForWidth())
        self.comboBox_source_file.setSizePolicy(sizePolicy)
        self.comboBox_source_file.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.comboBox_source_file.setMinimumContentsLength(0)
        self.comboBox_source_file.setDuplicatesEnabled(True)

        self.horizontalLayout_2.addWidget(self.comboBox_source_file)

        self.toolButton_browse_source_file = QToolButton(self.dockWidgetContents_7)
        self.toolButton_browse_source_file.setObjectName(u"toolButton_browse_source_file")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_source_file.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_source_file)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 78, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.dockWidget_source_files.setWidget(self.dockWidgetContents_7)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_source_files)
        QWidget.setTabOrder(self.new_button, self.remove_button)
        QWidget.setTabOrder(self.remove_button, self.mapping_list)
        QWidget.setTabOrder(self.mapping_list, self.class_type_combo_box)
        QWidget.setTabOrder(self.class_type_combo_box, self.value_type_combo_box)
        QWidget.setTabOrder(self.value_type_combo_box, self.start_read_row_spin_box)
        QWidget.setTabOrder(self.start_read_row_spin_box, self.ignore_columns_button)
        QWidget.setTabOrder(self.ignore_columns_button, self.dimension_spin_box)
        QWidget.setTabOrder(self.dimension_spin_box, self.map_dimension_spin_box)
        QWidget.setTabOrder(self.map_dimension_spin_box, self.mapping_spec_table)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Import Editor", None))
        self.export_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Export mappings...", None))
        self.import_mappings_action.setText(QCoreApplication.translate("MainWindow", u"Import mappings...", None))
        self.actionSwitch_connector.setText(QCoreApplication.translate("MainWindow", u"Switch connector...", None))
        self.dockWidget_source_tables.setWindowTitle(QCoreApplication.translate("MainWindow", u"Source tables", None))
        self.dockWidget_source_options.setWindowTitle(QCoreApplication.translate("MainWindow", u"Source options", None))
        self.dockWidget_source_data.setWindowTitle(QCoreApplication.translate("MainWindow", u"Source data", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Surplus column data type:", None))
#if QT_CONFIG(tooltip)
        self.default_column_type_combo_box.setToolTip(QCoreApplication.translate("MainWindow", u"Select data type for additional columns in variable-length pivoted source data.", None))
#endif // QT_CONFIG(tooltip)
        self.dockWidget_mappings.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mappings", None))
        self.new_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.duplicate_button.setText(QCoreApplication.translate("MainWindow", u"Duplicate", None))
        self.dockWidget_mapping_options.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mapping options", None))
        self.class_type_label.setText(QCoreApplication.translate("MainWindow", u"Item type:", None))
        self.class_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Object class", None))
        self.class_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Relationship class", None))
        self.class_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Object group", None))
        self.class_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.class_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.class_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.class_type_combo_box.setItemText(6, QCoreApplication.translate("MainWindow", u"Parameter value list", None))
        self.class_type_combo_box.setItemText(7, QCoreApplication.translate("MainWindow", u"Feature", None))
        self.class_type_combo_box.setItemText(8, QCoreApplication.translate("MainWindow", u"Tool", None))
        self.class_type_combo_box.setItemText(9, QCoreApplication.translate("MainWindow", u"Tool feature", None))
        self.class_type_combo_box.setItemText(10, QCoreApplication.translate("MainWindow", u"Tool feature method", None))

        self.import_objects_check_box.setText(QCoreApplication.translate("MainWindow", u"Import objects", None))
        self.parameter_type_label.setText(QCoreApplication.translate("MainWindow", u"Parameter type:", None))
        self.parameter_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Value", None))
        self.parameter_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Definition", None))
        self.parameter_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"None", None))

        self.value_type_label.setText(QCoreApplication.translate("MainWindow", u"Default value type:", None))
        self.value_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Single value", None))
        self.value_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Time series", None))
        self.value_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Time pattern", None))
        self.value_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Map", None))
        self.value_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Array", None))

#if QT_CONFIG(tooltip)
        self.before_alternative_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Enable or disable 'Before alternative name' mapping for scenario alternative item type.", None))
#endif // QT_CONFIG(tooltip)
        self.before_alternative_check_box.setText(QCoreApplication.translate("MainWindow", u"Use before alternative", None))
        self.read_start_row_label.setText(QCoreApplication.translate("MainWindow", u"Read data from row:", None))
        self.ignore_columns_label.setText(QCoreApplication.translate("MainWindow", u"Ignore columns:", None))
        self.ignore_columns_button.setText("")
        self.dimension_label.setText(QCoreApplication.translate("MainWindow", u"Number of dimensions:", None))
#if QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Set the repeat flag for all imported time series", None))
#endif // QT_CONFIG(tooltip)
        self.time_series_repeat_check_box.setText(QCoreApplication.translate("MainWindow", u"Repeat time series", None))
        self.map_dimensions_label.setText(QCoreApplication.translate("MainWindow", u"Map dimensions:", None))
        self.map_compression_check_box.setText(QCoreApplication.translate("MainWindow", u"Compress Maps", None))
        self.dockWidget_mapping_spec.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mapping specification", None))
        self.dockWidget_source_files.setWindowTitle(QCoreApplication.translate("MainWindow", u"Source files", None))
        self.file_path_label.setText(QCoreApplication.translate("MainWindow", u"File path:", None))
        self.toolButton_browse_source_file.setText(QCoreApplication.translate("MainWindow", u"...", None))
    # retranslateUi

