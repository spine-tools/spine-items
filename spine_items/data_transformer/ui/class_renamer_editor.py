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
## Form generated from reading UI file 'class_renamer_editor.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
    QTreeWidgetItem, QVBoxLayout, QWidget)

from spine_items.data_transformer.widgets.class_tree_widget import ClassTreeWidget
from spine_items.data_transformer.widgets.drop_target_table import DropTargetTable
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(619, 368)
        self.remove_class_action = QAction(Form)
        self.remove_class_action.setObjectName(u"remove_class_action")
        self.remove_class_action.setShortcutContext(Qt.WidgetShortcut)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.available_classes_tree_widget = ClassTreeWidget(self.splitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.available_classes_tree_widget.setHeaderItem(__qtreewidgetitem)
        self.available_classes_tree_widget.setObjectName(u"available_classes_tree_widget")
        self.available_classes_tree_widget.setDragEnabled(True)
        self.available_classes_tree_widget.setDragDropMode(QAbstractItemView.DragOnly)
        self.available_classes_tree_widget.setDefaultDropAction(Qt.CopyAction)
        self.available_classes_tree_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.splitter.addWidget(self.available_classes_tree_widget)
        self.available_classes_tree_widget.header().setVisible(False)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add_class_button = QPushButton(self.verticalLayoutWidget)
        self.add_class_button.setObjectName(u"add_class_button")

        self.horizontalLayout.addWidget(self.add_class_button)

        self.remove_class_button = QPushButton(self.verticalLayoutWidget)
        self.remove_class_button.setObjectName(u"remove_class_button")

        self.horizontalLayout.addWidget(self.remove_class_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.renaming_table_view = DropTargetTable(self.verticalLayoutWidget)
        self.renaming_table_view.setObjectName(u"renaming_table_view")
        self.renaming_table_view.setAcceptDrops(True)
        self.renaming_table_view.setDragDropMode(QAbstractItemView.DropOnly)

        self.verticalLayout.addWidget(self.renaming_table_view)

        self.splitter.addWidget(self.verticalLayoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.remove_class_action.setText(QCoreApplication.translate("Form", u"Remove class", None))
#if QT_CONFIG(shortcut)
        self.remove_class_action.setShortcut(QCoreApplication.translate("Form", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.add_class_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.remove_class_button.setText(QCoreApplication.translate("Form", u"Remove", None))
    # retranslateUi

