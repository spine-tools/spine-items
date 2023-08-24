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
## Form generated from reading UI file 'value_transformer_editor.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFormLayout,
    QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QTreeWidgetItem, QVBoxLayout, QWidget)

from ..widgets.parameter_tree_widget import ParameterTreeWidget
from spine_items.data_transformer.widgets.drop_target_table import DropTargetTable

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(938, 368)
        self.remove_parameter_action = QAction(Form)
        self.remove_parameter_action.setObjectName(u"remove_parameter_action")
        self.remove_parameter_action.setShortcutContext(Qt.WidgetShortcut)
        self.remove_instruction_action = QAction(Form)
        self.remove_instruction_action.setObjectName(u"remove_instruction_action")
        self.remove_instruction_action.setShortcutContext(Qt.WidgetShortcut)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.available_parameters_tree_view = ParameterTreeWidget(self.splitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.available_parameters_tree_view.setHeaderItem(__qtreewidgetitem)
        self.available_parameters_tree_view.setObjectName(u"available_parameters_tree_view")
        self.available_parameters_tree_view.setDragEnabled(True)
        self.available_parameters_tree_view.setDragDropMode(QAbstractItemView.DragOnly)
        self.available_parameters_tree_view.setDefaultDropAction(Qt.CopyAction)
        self.splitter.addWidget(self.available_parameters_tree_view)
        self.available_parameters_tree_view.header().setVisible(False)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_parameter_button = QPushButton(self.verticalLayoutWidget_2)
        self.add_parameter_button.setObjectName(u"add_parameter_button")

        self.horizontalLayout_2.addWidget(self.add_parameter_button)

        self.remove_parameter_button = QPushButton(self.verticalLayoutWidget_2)
        self.remove_parameter_button.setObjectName(u"remove_parameter_button")

        self.horizontalLayout_2.addWidget(self.remove_parameter_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.transformations_table_view = DropTargetTable(self.verticalLayoutWidget_2)
        self.transformations_table_view.setObjectName(u"transformations_table_view")
        self.transformations_table_view.setAcceptDrops(True)
        self.transformations_table_view.setDragDropMode(QAbstractItemView.DropOnly)
        self.transformations_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transformations_table_view.setShowGrid(False)
        self.transformations_table_view.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.transformations_table_view)

        self.splitter.addWidget(self.verticalLayoutWidget_2)

        self.horizontalLayout.addWidget(self.splitter)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.add_instruction_button = QPushButton(Form)
        self.add_instruction_button.setObjectName(u"add_instruction_button")
        self.add_instruction_button.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.add_instruction_button)

        self.remove_instruction_button = QPushButton(Form)
        self.remove_instruction_button.setObjectName(u"remove_instruction_button")
        self.remove_instruction_button.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.remove_instruction_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.instructions_list_view = QListWidget(Form)
        self.instructions_list_view.setObjectName(u"instructions_list_view")
        self.instructions_list_view.setEnabled(False)

        self.verticalLayout_3.addWidget(self.instructions_list_view)

        self.instruction_options_layout = QFormLayout()
        self.instruction_options_layout.setObjectName(u"instruction_options_layout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.instruction_options_layout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.operation_combo_box = QComboBox(Form)
        self.operation_combo_box.addItem("")
        self.operation_combo_box.addItem("")
        self.operation_combo_box.addItem("")
        self.operation_combo_box.setObjectName(u"operation_combo_box")

        self.instruction_options_layout.setWidget(0, QFormLayout.FieldRole, self.operation_combo_box)


        self.verticalLayout_3.addLayout(self.instruction_options_layout)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.remove_parameter_action.setText(QCoreApplication.translate("Form", u"Remove parameter", None))
#if QT_CONFIG(shortcut)
        self.remove_parameter_action.setShortcut(QCoreApplication.translate("Form", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.remove_instruction_action.setText(QCoreApplication.translate("Form", u"Remove instruction", None))
#if QT_CONFIG(shortcut)
        self.remove_instruction_action.setShortcut(QCoreApplication.translate("Form", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.add_parameter_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.remove_parameter_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.add_instruction_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.remove_instruction_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.label.setText(QCoreApplication.translate("Form", u"Operation:", None))
        self.operation_combo_box.setItemText(0, QCoreApplication.translate("Form", u"multiply", None))
        self.operation_combo_box.setItemText(1, QCoreApplication.translate("Form", u"negate", None))
        self.operation_combo_box.setItemText(2, QCoreApplication.translate("Form", u"invert", None))

    # retranslateUi

