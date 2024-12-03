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
## Form generated from reading UI file 'view_properties.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTreeView, QVBoxLayout, QWidget)

from spine_items.widgets import ReferencesTreeView
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(262, 346)
        Form.setStyleSheet(u"QScrollArea { background: transparent; }\n"
"QScrollArea > QWidget > QWidget { background: transparent; }")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 262, 346))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.treeView_references = ReferencesTreeView(self.scrollAreaWidgetContents)
        self.treeView_references.setObjectName(u"treeView_references")
        self.treeView_references.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView_references.setAcceptDrops(True)
        self.treeView_references.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_references.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.treeView_references.setRootIsDecorated(False)

        self.verticalLayout.addWidget(self.treeView_references)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_pin_values = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_pin_values.setObjectName(u"pushButton_pin_values")

        self.horizontalLayout_8.addWidget(self.pushButton_pin_values)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_9)

        self.pushButton_open_editor = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_open_editor.setObjectName(u"pushButton_open_editor")

        self.horizontalLayout_8.addWidget(self.pushButton_open_editor)


        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.treeView_pinned_values = QTreeView(self.scrollAreaWidgetContents)
        self.treeView_pinned_values.setObjectName(u"treeView_pinned_values")
        self.treeView_pinned_values.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView_pinned_values.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_pinned_values.setRootIsDecorated(False)

        self.verticalLayout.addWidget(self.treeView_pinned_values)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_plot_pinned = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_plot_pinned.setObjectName(u"pushButton_plot_pinned")

        self.horizontalLayout.addWidget(self.pushButton_plot_pinned)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_pin_values.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open selected database in Spine database editor</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_pin_values.setText(QCoreApplication.translate("Form", u"Pin values...", None))
        self.pushButton_open_editor.setText(QCoreApplication.translate("Form", u"Open editor...", None))
        self.pushButton_plot_pinned.setText(QCoreApplication.translate("Form", u"Plot", None))
    # retranslateUi

