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
## Form generated from reading UI file 'specification_editor_widget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDockWidget,
    QFormLayout, QHBoxLayout, QHeaderView, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QToolButton, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from ..widgets.parameter_tree_widget import ParameterTreeWidget
from spine_items.data_transformer.widgets.class_tree_widget import ClassTreeWidget
from spine_items.data_transformer.widgets.drop_target_table import DropTargetTable
from spinetoolbox.widgets.custom_combobox import ElidedCombobox
from spine_items import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 735)
        self.remove_parameter_rename_action = QAction(MainWindow)
        self.remove_parameter_rename_action.setObjectName(u"remove_parameter_rename_action")
        self.remove_parameter_rename_action.setShortcutContext(Qt.WidgetShortcut)
        self.remove_value_transformation_action = QAction(MainWindow)
        self.remove_value_transformation_action.setObjectName(u"remove_value_transformation_action")
        self.remove_value_transformation_action.setShortcutContext(Qt.WidgetShortcut)
        self.remove_class_rename_action = QAction(MainWindow)
        self.remove_class_rename_action.setObjectName(u"remove_class_rename_action")
        self.remove_class_rename_action.setShortcutContext(Qt.WidgetShortcut)
        self.remove_instruction_action = QAction(MainWindow)
        self.remove_instruction_action.setObjectName(u"remove_instruction_action")
        self.remove_instruction_action.setShortcutContext(Qt.WidgetShortcut)
        self.copy_parameter_rename_data_action = QAction(MainWindow)
        self.copy_parameter_rename_data_action.setObjectName(u"copy_parameter_rename_data_action")
        self.copy_parameter_rename_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.paste_parameter_rename_data_action = QAction(MainWindow)
        self.paste_parameter_rename_data_action.setObjectName(u"paste_parameter_rename_data_action")
        self.paste_parameter_rename_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.copy_class_rename_data_action = QAction(MainWindow)
        self.copy_class_rename_data_action.setObjectName(u"copy_class_rename_data_action")
        self.copy_class_rename_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.paste_class_rename_data_action = QAction(MainWindow)
        self.paste_class_rename_data_action.setObjectName(u"paste_class_rename_data_action")
        self.paste_class_rename_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.copy_value_transformation_data_action = QAction(MainWindow)
        self.copy_value_transformation_data_action.setObjectName(u"copy_value_transformation_data_action")
        self.copy_value_transformation_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.paste_value_transformation_data_action = QAction(MainWindow)
        self.paste_value_transformation_data_action.setObjectName(u"paste_value_transformation_data_action")
        self.paste_value_transformation_data_action.setShortcutContext(Qt.WidgetShortcut)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.type_dock = QDockWidget(MainWindow)
        self.type_dock.setObjectName(u"type_dock")
        self.type_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.dockWidgetContents)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.horizontalLayout_3.addWidget(self.label)

        self.filter_combo_box = QComboBox(self.dockWidgetContents)
        self.filter_combo_box.setObjectName(u"filter_combo_box")

        self.horizontalLayout_3.addWidget(self.filter_combo_box)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.type_dock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.type_dock)
        self.load_database_dock = QDockWidget(MainWindow)
        self.load_database_dock.setObjectName(u"load_database_dock")
        self.load_database_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.dockWidgetContents_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.database_url_combo_box = ElidedCombobox(self.dockWidgetContents_2)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.database_url_combo_box.sizePolicy().hasHeightForWidth())
        self.database_url_combo_box.setSizePolicy(sizePolicy)
        self.database_url_combo_box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.database_url_combo_box.setMinimumContentsLength(0)

        self.horizontalLayout_4.addWidget(self.database_url_combo_box)

        self.load_url_from_fs_button = QToolButton(self.dockWidgetContents_2)
        self.load_url_from_fs_button.setObjectName(u"load_url_from_fs_button")
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.load_url_from_fs_button.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.load_url_from_fs_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.load_data_button = QPushButton(self.dockWidgetContents_2)
        self.load_data_button.setObjectName(u"load_data_button")
        self.load_data_button.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.load_data_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.verticalSpacer_2 = QSpacerItem(20, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.load_database_dock.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.load_database_dock)
        self.possible_parameters_dock = QDockWidget(MainWindow)
        self.possible_parameters_dock.setObjectName(u"possible_parameters_dock")
        self.possible_parameters_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(3, 3, 3, 3)
        self.available_parameters_tree_view = ParameterTreeWidget(self.dockWidgetContents_3)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.available_parameters_tree_view.setHeaderItem(__qtreewidgetitem)
        self.available_parameters_tree_view.setObjectName(u"available_parameters_tree_view")
        self.available_parameters_tree_view.setDragEnabled(True)
        self.available_parameters_tree_view.setDragDropMode(QAbstractItemView.DragOnly)
        self.available_parameters_tree_view.setDefaultDropAction(Qt.CopyAction)
        self.available_parameters_tree_view.header().setVisible(False)

        self.verticalLayout_3.addWidget(self.available_parameters_tree_view)

        self.possible_parameters_dock.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.possible_parameters_dock)
        self.parameter_rename_dock = QDockWidget(MainWindow)
        self.parameter_rename_dock.setObjectName(u"parameter_rename_dock")
        self.parameter_rename_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_4.setSpacing(3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add_parameter_button = QPushButton(self.dockWidgetContents_4)
        self.add_parameter_button.setObjectName(u"add_parameter_button")

        self.horizontalLayout.addWidget(self.add_parameter_button)

        self.remove_parameter_button = QPushButton(self.dockWidgetContents_4)
        self.remove_parameter_button.setObjectName(u"remove_parameter_button")

        self.horizontalLayout.addWidget(self.remove_parameter_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.parameter_rename_table_view = DropTargetTable(self.dockWidgetContents_4)
        self.parameter_rename_table_view.setObjectName(u"parameter_rename_table_view")
        self.parameter_rename_table_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.parameter_rename_table_view.setSortingEnabled(True)
        self.parameter_rename_table_view.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_4.addWidget(self.parameter_rename_table_view)

        self.parameter_rename_dock.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.parameter_rename_dock)
        self.value_transformation_dock = QDockWidget(MainWindow)
        self.value_transformation_dock.setObjectName(u"value_transformation_dock")
        self.value_transformation_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_5.setSpacing(3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_transformation_button = QPushButton(self.dockWidgetContents_5)
        self.add_transformation_button.setObjectName(u"add_transformation_button")

        self.horizontalLayout_2.addWidget(self.add_transformation_button)

        self.remove_transformation_button = QPushButton(self.dockWidgetContents_5)
        self.remove_transformation_button.setObjectName(u"remove_transformation_button")

        self.horizontalLayout_2.addWidget(self.remove_transformation_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.transformations_table_view = DropTargetTable(self.dockWidgetContents_5)
        self.transformations_table_view.setObjectName(u"transformations_table_view")
        self.transformations_table_view.setAcceptDrops(True)
        self.transformations_table_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.transformations_table_view.setShowGrid(False)
        self.transformations_table_view.setSortingEnabled(True)
        self.transformations_table_view.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_5.addWidget(self.transformations_table_view)

        self.value_transformation_dock.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.value_transformation_dock)
        self.value_instructions_dock = QDockWidget(MainWindow)
        self.value_instructions_dock.setObjectName(u"value_instructions_dock")
        self.value_instructions_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_6 = QWidget()
        self.dockWidgetContents_6.setObjectName(u"dockWidgetContents_6")
        self.verticalLayout_6 = QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_6.setSpacing(3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.add_instruction_button = QPushButton(self.dockWidgetContents_6)
        self.add_instruction_button.setObjectName(u"add_instruction_button")
        self.add_instruction_button.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.add_instruction_button)

        self.remove_instruction_button = QPushButton(self.dockWidgetContents_6)
        self.remove_instruction_button.setObjectName(u"remove_instruction_button")
        self.remove_instruction_button.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.remove_instruction_button)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)


        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.instructions_list_view = QListWidget(self.dockWidgetContents_6)
        self.instructions_list_view.setObjectName(u"instructions_list_view")
        self.instructions_list_view.setEnabled(False)

        self.verticalLayout_6.addWidget(self.instructions_list_view)

        self.instruction_options_layout = QFormLayout()
        self.instruction_options_layout.setObjectName(u"instruction_options_layout")
        self.label_2 = QLabel(self.dockWidgetContents_6)
        self.label_2.setObjectName(u"label_2")

        self.instruction_options_layout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.operation_combo_box = QComboBox(self.dockWidgetContents_6)
        self.operation_combo_box.setObjectName(u"operation_combo_box")

        self.instruction_options_layout.setWidget(0, QFormLayout.FieldRole, self.operation_combo_box)


        self.verticalLayout_6.addLayout(self.instruction_options_layout)

        self.value_instructions_dock.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.value_instructions_dock)
        self.possible_classes_dock = QDockWidget(MainWindow)
        self.possible_classes_dock.setObjectName(u"possible_classes_dock")
        self.possible_classes_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_7 = QWidget()
        self.dockWidgetContents_7.setObjectName(u"dockWidgetContents_7")
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_7)
        self.verticalLayout_7.setSpacing(3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(3, 3, 3, 3)
        self.available_classes_tree_widget = ClassTreeWidget(self.dockWidgetContents_7)
        __qtreewidgetitem1 = QTreeWidgetItem()
        __qtreewidgetitem1.setText(0, u"1");
        self.available_classes_tree_widget.setHeaderItem(__qtreewidgetitem1)
        self.available_classes_tree_widget.setObjectName(u"available_classes_tree_widget")
        self.available_classes_tree_widget.setDragEnabled(True)
        self.available_classes_tree_widget.setDragDropMode(QAbstractItemView.DragOnly)
        self.available_classes_tree_widget.setDefaultDropAction(Qt.CopyAction)
        self.available_classes_tree_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.available_classes_tree_widget.header().setVisible(False)

        self.verticalLayout_7.addWidget(self.available_classes_tree_widget)

        self.possible_classes_dock.setWidget(self.dockWidgetContents_7)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.possible_classes_dock)
        self.class_rename_dock = QDockWidget(MainWindow)
        self.class_rename_dock.setObjectName(u"class_rename_dock")
        self.class_rename_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_8 = QWidget()
        self.dockWidgetContents_8.setObjectName(u"dockWidgetContents_8")
        self.verticalLayout_8 = QVBoxLayout(self.dockWidgetContents_8)
        self.verticalLayout_8.setSpacing(3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.add_class_button = QPushButton(self.dockWidgetContents_8)
        self.add_class_button.setObjectName(u"add_class_button")

        self.horizontalLayout_7.addWidget(self.add_class_button)

        self.remove_class_button = QPushButton(self.dockWidgetContents_8)
        self.remove_class_button.setObjectName(u"remove_class_button")

        self.horizontalLayout_7.addWidget(self.remove_class_button)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_6)


        self.verticalLayout_8.addLayout(self.horizontalLayout_7)

        self.class_rename_table_view = DropTargetTable(self.dockWidgetContents_8)
        self.class_rename_table_view.setObjectName(u"class_rename_table_view")
        self.class_rename_table_view.setAcceptDrops(True)
        self.class_rename_table_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.class_rename_table_view.setSortingEnabled(True)
        self.class_rename_table_view.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_8.addWidget(self.class_rename_table_view)

        self.class_rename_dock.setWidget(self.dockWidgetContents_8)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.class_rename_dock)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.remove_parameter_rename_action.setText(QCoreApplication.translate("MainWindow", u"Remove parameter", None))
#if QT_CONFIG(shortcut)
        self.remove_parameter_rename_action.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.remove_value_transformation_action.setText(QCoreApplication.translate("MainWindow", u"Remove transformation", None))
#if QT_CONFIG(shortcut)
        self.remove_value_transformation_action.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.remove_class_rename_action.setText(QCoreApplication.translate("MainWindow", u"Remove class", None))
#if QT_CONFIG(shortcut)
        self.remove_class_rename_action.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.remove_instruction_action.setText(QCoreApplication.translate("MainWindow", u"Remove instruction", None))
#if QT_CONFIG(shortcut)
        self.remove_instruction_action.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.copy_parameter_rename_data_action.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
#if QT_CONFIG(shortcut)
        self.copy_parameter_rename_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.paste_parameter_rename_data_action.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
#if QT_CONFIG(shortcut)
        self.paste_parameter_rename_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.copy_class_rename_data_action.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
#if QT_CONFIG(shortcut)
        self.copy_class_rename_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.paste_class_rename_data_action.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
#if QT_CONFIG(shortcut)
        self.paste_class_rename_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.copy_value_transformation_data_action.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
#if QT_CONFIG(shortcut)
        self.copy_value_transformation_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.paste_value_transformation_data_action.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
#if QT_CONFIG(shortcut)
        self.paste_value_transformation_data_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.type_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Select transformation", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Transformation type:", None))
        self.load_database_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Load from database", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Database url:", None))
#if QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Browse file system</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.load_data_button.setText(QCoreApplication.translate("MainWindow", u"Load filter data from database", None))
        self.possible_parameters_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Possible parameters", None))
        self.parameter_rename_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Rename parameters", None))
        self.add_parameter_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_parameter_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.value_transformation_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Parameter value transformation", None))
        self.add_transformation_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_transformation_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.value_instructions_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Transformation instructions", None))
        self.add_instruction_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_instruction_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Operation:", None))
        self.possible_classes_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Possible classes", None))
        self.class_rename_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Rename classes", None))
        self.add_class_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_class_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
    # retranslateUi

