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
## Form generated from reading UI file 'specification_editor.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
    QDockWidget, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTableView,
    QToolButton, QTreeView, QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_combobox import ElidedCombobox
from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1146, 801)
        MainWindow.setDockNestingEnabled(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.mappings_dock = QDockWidget(MainWindow)
        self.mappings_dock.setObjectName(u"mappings_dock")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_mapping_button = QPushButton(self.dockWidgetContents)
        self.add_mapping_button.setObjectName(u"add_mapping_button")

        self.horizontalLayout_2.addWidget(self.add_mapping_button)

        self.remove_mapping_button = QPushButton(self.dockWidgetContents)
        self.remove_mapping_button.setObjectName(u"remove_mapping_button")

        self.horizontalLayout_2.addWidget(self.remove_mapping_button)

        self.toggle_enabled_button = QPushButton(self.dockWidgetContents)
        self.toggle_enabled_button.setObjectName(u"toggle_enabled_button")

        self.horizontalLayout_2.addWidget(self.toggle_enabled_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.mappings_table = QTableView(self.dockWidgetContents)
        self.mappings_table.setObjectName(u"mappings_table")
        self.mappings_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mappings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mappings_table.setShowGrid(False)
        self.mappings_table.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.mappings_table)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)

        self.write_earlier_button = QPushButton(self.dockWidgetContents)
        self.write_earlier_button.setObjectName(u"write_earlier_button")

        self.horizontalLayout_6.addWidget(self.write_earlier_button)

        self.write_later_button = QPushButton(self.dockWidgetContents)
        self.write_later_button.setObjectName(u"write_later_button")

        self.horizontalLayout_6.addWidget(self.write_later_button)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.mappings_dock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mappings_dock)
        self.mapping_options_dock = QDockWidget(MainWindow)
        self.mapping_options_dock.setObjectName(u"mapping_options_dock")
        self.mapping_options_contents = QWidget()
        self.mapping_options_contents.setObjectName(u"mapping_options_contents")
        self.verticalLayout_7 = QVBoxLayout(self.mapping_options_contents)
        self.verticalLayout_7.setSpacing(3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(3, 3, 3, 3)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_4 = QLabel(self.mapping_options_contents)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.item_type_combo_box = QComboBox(self.mapping_options_contents)
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.setObjectName(u"item_type_combo_box")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.item_type_combo_box)

        self.always_export_header_check_box = QCheckBox(self.mapping_options_contents)
        self.always_export_header_check_box.setObjectName(u"always_export_header_check_box")

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.always_export_header_check_box)

        self.label_8 = QLabel(self.mapping_options_contents)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_8)

        self.relationship_dimensions_spin_box = QSpinBox(self.mapping_options_contents)
        self.relationship_dimensions_spin_box.setObjectName(u"relationship_dimensions_spin_box")
        self.relationship_dimensions_spin_box.setMinimum(1)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.relationship_dimensions_spin_box)

        self.label_7 = QLabel(self.mapping_options_contents)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_7)

        self.highlight_dimension_spin_box = QSpinBox(self.mapping_options_contents)
        self.highlight_dimension_spin_box.setObjectName(u"highlight_dimension_spin_box")
        self.highlight_dimension_spin_box.setMinimum(1)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.highlight_dimension_spin_box)

        self.label_5 = QLabel(self.mapping_options_contents)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.parameter_type_combo_box = QComboBox(self.mapping_options_contents)
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.setObjectName(u"parameter_type_combo_box")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.parameter_type_combo_box)

        self.label_10 = QLabel(self.mapping_options_contents)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_10)

        self.parameter_dimensions_spin_box = QSpinBox(self.mapping_options_contents)
        self.parameter_dimensions_spin_box.setObjectName(u"parameter_dimensions_spin_box")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.parameter_dimensions_spin_box)

        self.fix_table_name_check_box = QCheckBox(self.mapping_options_contents)
        self.fix_table_name_check_box.setObjectName(u"fix_table_name_check_box")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.fix_table_name_check_box)

        self.fix_table_name_line_edit = QLineEdit(self.mapping_options_contents)
        self.fix_table_name_line_edit.setObjectName(u"fix_table_name_line_edit")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.fix_table_name_line_edit)

        self.label_6 = QLabel(self.mapping_options_contents)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_6)

        self.group_fn_combo_box = QComboBox(self.mapping_options_contents)
        self.group_fn_combo_box.setObjectName(u"group_fn_combo_box")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.group_fn_combo_box)


        self.verticalLayout_7.addLayout(self.formLayout)

        self.verticalSpacer_3 = QSpacerItem(20, 12, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_3)

        self.mapping_options_dock.setWidget(self.mapping_options_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mapping_options_dock)
        self.mapping_spec_dock = QDockWidget(MainWindow)
        self.mapping_spec_dock.setObjectName(u"mapping_spec_dock")
        self.mapping_spec_contents = QWidget()
        self.mapping_spec_contents.setObjectName(u"mapping_spec_contents")
        self.mapping_spec_contents.setEnabled(False)
        self.verticalLayout_2 = QVBoxLayout(self.mapping_spec_contents)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.mapping_table_view = QTableView(self.mapping_spec_contents)
        self.mapping_table_view.setObjectName(u"mapping_table_view")
        self.mapping_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mapping_table_view.horizontalHeader().setStretchLastSection(True)
        self.mapping_table_view.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.mapping_table_view)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.compact_button = QPushButton(self.mapping_spec_contents)
        self.compact_button.setObjectName(u"compact_button")

        self.horizontalLayout_5.addWidget(self.compact_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.mapping_spec_dock.setWidget(self.mapping_spec_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mapping_spec_dock)
        self.preview_tables_dock = QDockWidget(MainWindow)
        self.preview_tables_dock.setObjectName(u"preview_tables_dock")
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(3, 3, 3, 3)
        self.preview_tree_view = QTreeView(self.dockWidgetContents_5)
        self.preview_tree_view.setObjectName(u"preview_tree_view")
        self.preview_tree_view.header().setVisible(False)

        self.verticalLayout_3.addWidget(self.preview_tree_view)

        self.preview_tables_dock.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.preview_tables_dock)
        self.preview_contents_dock = QDockWidget(MainWindow)
        self.preview_contents_dock.setObjectName(u"preview_contents_dock")
        self.dockWidgetContents_6 = QWidget()
        self.dockWidgetContents_6.setObjectName(u"dockWidgetContents_6")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_4.setSpacing(3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(3, 3, 3, 3)
        self.preview_table_view = QTableView(self.dockWidgetContents_6)
        self.preview_table_view.setObjectName(u"preview_table_view")

        self.verticalLayout_4.addWidget(self.preview_table_view)

        self.preview_contents_dock.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.preview_contents_dock)
        self.export_options_dock = QDockWidget(MainWindow)
        self.export_options_dock.setObjectName(u"export_options_dock")
        self.export_options_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockWidgetContents_7 = QWidget()
        self.dockWidgetContents_7.setObjectName(u"dockWidgetContents_7")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_7)
        self.verticalLayout_5.setSpacing(3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.dockWidgetContents_7)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)

        self.horizontalLayout_4.addWidget(self.label)

        self.export_format_combo_box = QComboBox(self.dockWidgetContents_7)
        self.export_format_combo_box.setObjectName(u"export_format_combo_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.export_format_combo_box.sizePolicy().hasHeightForWidth())
        self.export_format_combo_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.export_format_combo_box)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.export_options_dock.setWidget(self.dockWidgetContents_7)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.export_options_dock)
        self.preview_controls_dock = QDockWidget(MainWindow)
        self.preview_controls_dock.setObjectName(u"preview_controls_dock")
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout_6 = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_6.setSpacing(3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_9 = QLabel(self.dockWidgetContents_4)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_9)

        self.database_url_combo_box = ElidedCombobox(self.dockWidgetContents_4)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.database_url_combo_box.sizePolicy().hasHeightForWidth())
        self.database_url_combo_box.setSizePolicy(sizePolicy2)
        self.database_url_combo_box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.database_url_combo_box.setMinimumContentsLength(0)

        self.horizontalLayout_3.addWidget(self.database_url_combo_box)

        self.load_url_from_fs_button = QToolButton(self.dockWidgetContents_4)
        self.load_url_from_fs_button.setObjectName(u"load_url_from_fs_button")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.load_url_from_fs_button.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.load_url_from_fs_button)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.live_preview_check_box = QCheckBox(self.dockWidgetContents_4)
        self.live_preview_check_box.setObjectName(u"live_preview_check_box")
        self.live_preview_check_box.setChecked(False)

        self.horizontalLayout.addWidget(self.live_preview_check_box)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.label_3 = QLabel(self.dockWidgetContents_4)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.max_preview_tables_spin_box = QSpinBox(self.dockWidgetContents_4)
        self.max_preview_tables_spin_box.setObjectName(u"max_preview_tables_spin_box")
        self.max_preview_tables_spin_box.setMaximum(16777215)
        self.max_preview_tables_spin_box.setSingleStep(10)
        self.max_preview_tables_spin_box.setValue(20)

        self.horizontalLayout.addWidget(self.max_preview_tables_spin_box)

        self.label_2 = QLabel(self.dockWidgetContents_4)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.max_preview_rows_spin_box = QSpinBox(self.dockWidgetContents_4)
        self.max_preview_rows_spin_box.setObjectName(u"max_preview_rows_spin_box")
        self.max_preview_rows_spin_box.setMaximum(16777215)
        self.max_preview_rows_spin_box.setSingleStep(10)
        self.max_preview_rows_spin_box.setValue(20)

        self.horizontalLayout.addWidget(self.max_preview_rows_spin_box)


        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

        self.preview_controls_dock.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.preview_controls_dock)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.mappings_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mappings", None))
        self.add_mapping_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_mapping_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
#if QT_CONFIG(tooltip)
        self.toggle_enabled_button.setToolTip(QCoreApplication.translate("MainWindow", u"Enable or disable all mappings at once.", None))
#endif // QT_CONFIG(tooltip)
        self.toggle_enabled_button.setText(QCoreApplication.translate("MainWindow", u"Toggle enabled", None))
#if QT_CONFIG(tooltip)
        self.write_earlier_button.setToolTip(QCoreApplication.translate("MainWindow", u"Prioratize mapping.", None))
#endif // QT_CONFIG(tooltip)
        self.write_earlier_button.setText(QCoreApplication.translate("MainWindow", u"Write earlier", None))
#if QT_CONFIG(tooltip)
        self.write_later_button.setToolTip(QCoreApplication.translate("MainWindow", u"Deprioratize mapping.", None))
#endif // QT_CONFIG(tooltip)
        self.write_later_button.setText(QCoreApplication.translate("MainWindow", u"Write later", None))
        self.mapping_options_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mapping options", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Item type:", None))
        self.item_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Object class", None))
        self.item_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Relationship class", None))
        self.item_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Relationship class with object parameter", None))
        self.item_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Object group", None))
        self.item_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.item_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.item_type_combo_box.setItemText(6, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.item_type_combo_box.setItemText(7, QCoreApplication.translate("MainWindow", u"Parameter value list", None))
        self.item_type_combo_box.setItemText(8, QCoreApplication.translate("MainWindow", u"Feature", None))
        self.item_type_combo_box.setItemText(9, QCoreApplication.translate("MainWindow", u"Tool", None))
        self.item_type_combo_box.setItemText(10, QCoreApplication.translate("MainWindow", u"Tool feature", None))
        self.item_type_combo_box.setItemText(11, QCoreApplication.translate("MainWindow", u"Tool feature method", None))

#if QT_CONFIG(tooltip)
        self.always_export_header_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Export header even when a table is otherwise empty.", None))
#endif // QT_CONFIG(tooltip)
        self.always_export_header_check_box.setText(QCoreApplication.translate("MainWindow", u"Always export header", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Relationship dimensions:", None))
#if QT_CONFIG(tooltip)
        self.relationship_dimensions_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of expected relationship dimensions.", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Selected dimension:", None))
#if QT_CONFIG(tooltip)
        self.highlight_dimension_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Relationship dimension used to select object parameters for export.", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Parameter type:", None))
        self.parameter_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Value", None))
        self.parameter_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Default value", None))
        self.parameter_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"None", None))

        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Parameter dimensions:", None))
#if QT_CONFIG(tooltip)
        self.parameter_dimensions_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of expected parameter value dimensions.", None))
#endif // QT_CONFIG(tooltip)
        self.fix_table_name_check_box.setText(QCoreApplication.translate("MainWindow", u"Fixed table name:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Group function:", None))
#if QT_CONFIG(tooltip)
        self.group_fn_combo_box.setToolTip(QCoreApplication.translate("MainWindow", u"Group/aggregate data that ends up in the same cell in pivot tables.", None))
#endif // QT_CONFIG(tooltip)
        self.mapping_spec_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mapping specification", None))
#if QT_CONFIG(tooltip)
        self.compact_button.setToolTip(QCoreApplication.translate("MainWindow", u"Compact mapping by removing empty columns and rows.", None))
#endif // QT_CONFIG(tooltip)
        self.compact_button.setText(QCoreApplication.translate("MainWindow", u"Compact", None))
        self.preview_tables_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Preview tables", None))
        self.preview_contents_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Preview contents", None))
        self.export_options_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Export options", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Format:", None))
        self.preview_controls_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Preview controls", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Database url:", None))
#if QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Browse file system</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.live_preview_check_box.setText(QCoreApplication.translate("MainWindow", u"Live preview", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Max. tables", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Max. content rows:", None))
    # retranslateUi

