# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
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
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

from spine_items.widgets import ReferencesTreeView

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(274, 241)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.treeView_view = ReferencesTreeView(Form)
        self.treeView_view.setObjectName(u"treeView_view")
        font = QFont()
        font.setPointSize(9)
        self.treeView_view.setFont(font)
        self.treeView_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView_view.setAcceptDrops(True)
        self.treeView_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_view.setTextElideMode(Qt.ElideLeft)
        self.treeView_view.setRootIsDecorated(False)

        self.verticalLayout.addWidget(self.treeView_view)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_9)

        self.pushButton_view_open_editor = QPushButton(Form)
        self.pushButton_view_open_editor.setObjectName(u"pushButton_view_open_editor")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_view_open_editor.sizePolicy().hasHeightForWidth())
        self.pushButton_view_open_editor.setSizePolicy(sizePolicy)
        self.pushButton_view_open_editor.setMinimumSize(QSize(75, 23))
        self.pushButton_view_open_editor.setMaximumSize(QSize(16777215, 23))

        self.horizontalLayout_8.addWidget(self.pushButton_view_open_editor)


        self.verticalLayout.addLayout(self.horizontalLayout_8)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_view_open_editor.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open selected database in Spine database editor</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_view_open_editor.setText(QCoreApplication.translate("Form", u"Open editor...", None))
    # retranslateUi

