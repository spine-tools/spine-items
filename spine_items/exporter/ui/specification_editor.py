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
    QFormLayout, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QSplitter, QTableView, QToolButton, QTreeView,
    QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_combobox import ElidedCombobox
from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1086, 780)
        MainWindow.setDockNestingEnabled(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_10 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.label)

        self.export_format_combo_box = QComboBox(self.centralwidget)
        self.export_format_combo_box.setObjectName(u"export_format_combo_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.export_format_combo_box.sizePolicy().hasHeightForWidth())
        self.export_format_combo_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.export_format_combo_box)

        self.live_preview_check_box = QCheckBox(self.centralwidget)
        self.live_preview_check_box.setObjectName(u"live_preview_check_box")
        self.live_preview_check_box.setChecked(False)

        self.horizontalLayout_3.addWidget(self.live_preview_check_box)

        self.frame_preview = QFrame(self.centralwidget)
        self.frame_preview.setObjectName(u"frame_preview")
        self.frame_preview.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_preview.sizePolicy().hasHeightForWidth())
        self.frame_preview.setSizePolicy(sizePolicy2)
        self.frame_preview.setFrameShape(QFrame.StyledPanel)
        self.frame_preview.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_preview)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(3, 0, 3, 0)
        self.label_9 = QLabel(self.frame_preview)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout.addWidget(self.label_9)

        self.database_url_combo_box = ElidedCombobox(self.frame_preview)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.database_url_combo_box.sizePolicy().hasHeightForWidth())
        self.database_url_combo_box.setSizePolicy(sizePolicy3)
        self.database_url_combo_box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.database_url_combo_box.setMinimumContentsLength(16)

        self.horizontalLayout.addWidget(self.database_url_combo_box)

        self.load_url_from_fs_button = QToolButton(self.frame_preview)
        self.load_url_from_fs_button.setObjectName(u"load_url_from_fs_button")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.load_url_from_fs_button.setIcon(icon)

        self.horizontalLayout.addWidget(self.load_url_from_fs_button)

        self.label_3 = QLabel(self.frame_preview)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.max_preview_tables_spin_box = QSpinBox(self.frame_preview)
        self.max_preview_tables_spin_box.setObjectName(u"max_preview_tables_spin_box")
        self.max_preview_tables_spin_box.setMaximum(16777215)
        self.max_preview_tables_spin_box.setSingleStep(10)
        self.max_preview_tables_spin_box.setValue(20)

        self.horizontalLayout.addWidget(self.max_preview_tables_spin_box)

        self.label_2 = QLabel(self.frame_preview)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.max_preview_rows_spin_box = QSpinBox(self.frame_preview)
        self.max_preview_rows_spin_box.setObjectName(u"max_preview_rows_spin_box")
        self.max_preview_rows_spin_box.setMaximum(16777215)
        self.max_preview_rows_spin_box.setSingleStep(10)
        self.max_preview_rows_spin_box.setValue(20)

        self.horizontalLayout.addWidget(self.max_preview_rows_spin_box)


        self.horizontalLayout_3.addWidget(self.frame_preview)


        self.verticalLayout_10.addLayout(self.horizontalLayout_3)

        self.splitter_3 = QSplitter(self.centralwidget)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Horizontal)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.mapping_list_layout_widget = QWidget(self.splitter_2)
        self.mapping_list_layout_widget.setObjectName(u"mapping_list_layout_widget")
        self.verticalLayout_9 = QVBoxLayout(self.mapping_list_layout_widget)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.frame = QFrame(self.mapping_list_layout_widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(3, 3, 3, 3)
        self.label_11 = QLabel(self.frame)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_11.addWidget(self.label_11)


        self.verticalLayout_9.addWidget(self.frame)

        self.mappings_table = QTableView(self.mapping_list_layout_widget)
        self.mappings_table.setObjectName(u"mappings_table")
        self.mappings_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mappings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mappings_table.setShowGrid(False)
        self.mappings_table.verticalHeader().setVisible(False)

        self.verticalLayout_9.addWidget(self.mappings_table)

        self.splitter_2.addWidget(self.mapping_list_layout_widget)
        self.mapping_controls_layout_widget = QWidget(self.splitter_2)
        self.mapping_controls_layout_widget.setObjectName(u"mapping_controls_layout_widget")
        self.verticalLayout_8 = QVBoxLayout(self.mapping_controls_layout_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_mapping_button = QPushButton(self.mapping_controls_layout_widget)
        self.add_mapping_button.setObjectName(u"add_mapping_button")

        self.horizontalLayout_2.addWidget(self.add_mapping_button)

        self.remove_mapping_button = QPushButton(self.mapping_controls_layout_widget)
        self.remove_mapping_button.setObjectName(u"remove_mapping_button")

        self.horizontalLayout_2.addWidget(self.remove_mapping_button)

        self.toggle_enabled_button = QPushButton(self.mapping_controls_layout_widget)
        self.toggle_enabled_button.setObjectName(u"toggle_enabled_button")

        self.horizontalLayout_2.addWidget(self.toggle_enabled_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.write_earlier_button = QPushButton(self.mapping_controls_layout_widget)
        self.write_earlier_button.setObjectName(u"write_earlier_button")

        self.horizontalLayout_2.addWidget(self.write_earlier_button)

        self.write_later_button = QPushButton(self.mapping_controls_layout_widget)
        self.write_later_button.setObjectName(u"write_later_button")

        self.horizontalLayout_2.addWidget(self.write_later_button)


        self.verticalLayout_8.addLayout(self.horizontalLayout_2)

        self.mapping_options_contents = QFrame(self.mapping_controls_layout_widget)
        self.mapping_options_contents.setObjectName(u"mapping_options_contents")
        self.formLayout = QFormLayout(self.mapping_options_contents)
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
        self.item_type_combo_box.setObjectName(u"item_type_combo_box")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.item_type_combo_box)

        self.label_8 = QLabel(self.mapping_options_contents)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_8)

        self.entity_dimensions_spin_box = QSpinBox(self.mapping_options_contents)
        self.entity_dimensions_spin_box.setObjectName(u"entity_dimensions_spin_box")
        self.entity_dimensions_spin_box.setMinimum(0)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.entity_dimensions_spin_box)

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

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.fix_table_name_check_box)

        self.fix_table_name_line_edit = QLineEdit(self.mapping_options_contents)
        self.fix_table_name_line_edit.setObjectName(u"fix_table_name_line_edit")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.fix_table_name_line_edit)

        self.always_export_header_check_box = QCheckBox(self.mapping_options_contents)
        self.always_export_header_check_box.setObjectName(u"always_export_header_check_box")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.always_export_header_check_box)

        self.compact_button = QPushButton(self.mapping_options_contents)
        self.compact_button.setObjectName(u"compact_button")

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.compact_button)

        self.label_6 = QLabel(self.mapping_options_contents)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_6)

        self.group_fn_combo_box = QComboBox(self.mapping_options_contents)
        self.group_fn_combo_box.setObjectName(u"group_fn_combo_box")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.group_fn_combo_box)


        self.verticalLayout_8.addWidget(self.mapping_options_contents)

        self.mapping_table_view = QTableView(self.mapping_controls_layout_widget)
        self.mapping_table_view.setObjectName(u"mapping_table_view")
        self.mapping_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mapping_table_view.horizontalHeader().setStretchLastSection(True)
        self.mapping_table_view.verticalHeader().setVisible(False)

        self.verticalLayout_8.addWidget(self.mapping_table_view)

        self.splitter_2.addWidget(self.mapping_controls_layout_widget)
        self.splitter_3.addWidget(self.splitter_2)
        self.splitter = QSplitter(self.splitter_3)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.preview_tree_view = QTreeView(self.splitter)
        self.preview_tree_view.setObjectName(u"preview_tree_view")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.preview_tree_view.sizePolicy().hasHeightForWidth())
        self.preview_tree_view.setSizePolicy(sizePolicy4)
        self.splitter.addWidget(self.preview_tree_view)
        self.preview_tree_view.header().setVisible(False)
        self.preview_table_view = QTableView(self.splitter)
        self.preview_table_view.setObjectName(u"preview_table_view")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(5)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.preview_table_view.sizePolicy().hasHeightForWidth())
        self.preview_table_view.setSizePolicy(sizePolicy5)
        self.splitter.addWidget(self.preview_table_view)
        self.splitter_3.addWidget(self.splitter)

        self.verticalLayout_10.addWidget(self.splitter_3)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.export_format_combo_box, self.live_preview_check_box)
        QWidget.setTabOrder(self.live_preview_check_box, self.database_url_combo_box)
        QWidget.setTabOrder(self.database_url_combo_box, self.load_url_from_fs_button)
        QWidget.setTabOrder(self.load_url_from_fs_button, self.max_preview_tables_spin_box)
        QWidget.setTabOrder(self.max_preview_tables_spin_box, self.max_preview_rows_spin_box)
        QWidget.setTabOrder(self.max_preview_rows_spin_box, self.mappings_table)
        QWidget.setTabOrder(self.mappings_table, self.add_mapping_button)
        QWidget.setTabOrder(self.add_mapping_button, self.remove_mapping_button)
        QWidget.setTabOrder(self.remove_mapping_button, self.toggle_enabled_button)
        QWidget.setTabOrder(self.toggle_enabled_button, self.write_earlier_button)
        QWidget.setTabOrder(self.write_earlier_button, self.write_later_button)
        QWidget.setTabOrder(self.write_later_button, self.item_type_combo_box)
        QWidget.setTabOrder(self.item_type_combo_box, self.entity_dimensions_spin_box)
        QWidget.setTabOrder(self.entity_dimensions_spin_box, self.highlight_dimension_spin_box)
        QWidget.setTabOrder(self.highlight_dimension_spin_box, self.parameter_type_combo_box)
        QWidget.setTabOrder(self.parameter_type_combo_box, self.parameter_dimensions_spin_box)
        QWidget.setTabOrder(self.parameter_dimensions_spin_box, self.group_fn_combo_box)
        QWidget.setTabOrder(self.group_fn_combo_box, self.fix_table_name_check_box)
        QWidget.setTabOrder(self.fix_table_name_check_box, self.fix_table_name_line_edit)
        QWidget.setTabOrder(self.fix_table_name_line_edit, self.always_export_header_check_box)
        QWidget.setTabOrder(self.always_export_header_check_box, self.compact_button)
        QWidget.setTabOrder(self.compact_button, self.mapping_table_view)
        QWidget.setTabOrder(self.mapping_table_view, self.preview_tree_view)
        QWidget.setTabOrder(self.preview_tree_view, self.preview_table_view)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Export format:", None))
        self.live_preview_check_box.setText(QCoreApplication.translate("MainWindow", u"Live preview", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Database url:", None))
#if QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Browse file system</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Max. tables", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Max. content rows:", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Mappings", None))
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
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.item_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Entity class", None))
        self.item_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Entity class with dimension parameter", None))
        self.item_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Entity group", None))
        self.item_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.item_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.item_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.item_type_combo_box.setItemText(6, QCoreApplication.translate("MainWindow", u"Parameter value list", None))

        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Entity dimensions:", None))
#if QT_CONFIG(tooltip)
        self.entity_dimensions_spin_box.setToolTip(QCoreApplication.translate("MainWindow", u"Number of expected relationship dimensions.", None))
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
#if QT_CONFIG(tooltip)
        self.always_export_header_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"Export header even when a table is otherwise empty.", None))
#endif // QT_CONFIG(tooltip)
        self.always_export_header_check_box.setText(QCoreApplication.translate("MainWindow", u"Always export header", None))
#if QT_CONFIG(tooltip)
        self.compact_button.setToolTip(QCoreApplication.translate("MainWindow", u"Compact mapping by removing empty columns and rows.", None))
#endif // QT_CONFIG(tooltip)
        self.compact_button.setText(QCoreApplication.translate("MainWindow", u"Compact", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Group function:", None))
#if QT_CONFIG(tooltip)
        self.group_fn_combo_box.setToolTip(QCoreApplication.translate("MainWindow", u"Group/aggregate data that ends up in the same cell in pivot tables.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

