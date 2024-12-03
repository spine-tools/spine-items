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
## Form generated from reading UI file 'data_connection_properties.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QScrollArea, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)

from spine_items.widgets import (DataTreeView, ReferencesTreeView)
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(274, 438)
        Form.setStyleSheet(u"QScrollArea { background: transparent; }\n"
"QScrollArea > QWidget > QWidget { background: transparent; }")
        self.action_new_file_reference = QAction(Form)
        self.action_new_file_reference.setObjectName(u"action_new_file_reference")
        icon = QIcon()
        icon.addFile(u":/icons/plus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_new_file_reference.setIcon(icon)
        self.action_new_db_reference = QAction(Form)
        self.action_new_db_reference.setObjectName(u"action_new_db_reference")
        self.action_new_db_reference.setIcon(icon)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 274, 438))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.treeView_dc_references = ReferencesTreeView(self.scrollAreaWidgetContents)
        self.treeView_dc_references.setObjectName(u"treeView_dc_references")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView_dc_references.sizePolicy().hasHeightForWidth())
        self.treeView_dc_references.setSizePolicy(sizePolicy)
        self.treeView_dc_references.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView_dc_references.setAcceptDrops(True)
        self.treeView_dc_references.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_dc_references.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.treeView_dc_references.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.treeView_dc_references.header().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.treeView_dc_references)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButton_add = QToolButton(self.scrollAreaWidgetContents)
        self.toolButton_add.setObjectName(u"toolButton_add")
        icon1 = QIcon()
        icon1.addFile(u":/icons/file-download.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_add.setIcon(icon1)
        self.toolButton_add.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.horizontalLayout_2.addWidget(self.toolButton_add)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.toolButton_minus = QToolButton(self.scrollAreaWidgetContents)
        self.toolButton_minus.setObjectName(u"toolButton_minus")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.toolButton_minus.sizePolicy().hasHeightForWidth())
        self.toolButton_minus.setSizePolicy(sizePolicy1)
        icon2 = QIcon()
        icon2.addFile(u":/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_minus.setIcon(icon2)
        self.toolButton_minus.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.horizontalLayout_2.addWidget(self.toolButton_minus)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.treeView_dc_data = DataTreeView(self.scrollAreaWidgetContents)
        self.treeView_dc_data.setObjectName(u"treeView_dc_data")
        sizePolicy.setHeightForWidth(self.treeView_dc_data.sizePolicy().hasHeightForWidth())
        self.treeView_dc_data.setSizePolicy(sizePolicy)
        self.treeView_dc_data.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView_dc_data.setAcceptDrops(True)
        self.treeView_dc_data.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView_dc_data.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.treeView_dc_data.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.treeView_dc_data.setIndentation(5)
        self.treeView_dc_data.setUniformRowHeights(True)
        self.treeView_dc_data.header().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.treeView_dc_data)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.action_new_file_reference.setText(QCoreApplication.translate("Form", u"New...", None))
#if QT_CONFIG(tooltip)
        self.action_new_file_reference.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add file reference</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.action_new_db_reference.setText(QCoreApplication.translate("Form", u"New...", None))
#if QT_CONFIG(tooltip)
        self.action_new_db_reference.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add DB reference</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.treeView_dc_references.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Drag-and-drop files here, they will be added as references.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_add.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy selected file references to this Data Connection's directory</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_add.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected references</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_dc_data.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Drag-and-drop files here, they will be copied to the data directory.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

