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
## Form generated from reading UI file 'merger_properties.ui'
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

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(415, 382)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_merger_name = QLabel(Form)
        self.label_merger_name.setObjectName(u"label_merger_name")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_merger_name.sizePolicy().hasHeightForWidth())
        self.label_merger_name.setSizePolicy(sizePolicy)
        self.label_merger_name.setMinimumSize(QSize(0, 20))
        self.label_merger_name.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label_merger_name.setFont(font)
        self.label_merger_name.setStyleSheet(u"background-color: #ecd8c6;")
        self.label_merger_name.setFrameShape(QFrame.Box)
        self.label_merger_name.setFrameShadow(QFrame.Sunken)
        self.label_merger_name.setLineWidth(1)
        self.label_merger_name.setScaledContents(False)
        self.label_merger_name.setAlignment(Qt.AlignCenter)
        self.label_merger_name.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_merger_name)

        self.scrollArea_5 = QScrollArea(Form)
        self.scrollArea_5.setObjectName(u"scrollArea_5")
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setObjectName(u"scrollAreaWidgetContents_7")
        self.scrollAreaWidgetContents_7.setGeometry(QRect(0, 0, 413, 360))
        self.verticalLayout_25 = QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_25.addItem(self.verticalSpacer_2)

        self.cancel_on_error_checkBox = QCheckBox(self.scrollAreaWidgetContents_7)
        self.cancel_on_error_checkBox.setObjectName(u"cancel_on_error_checkBox")
        self.cancel_on_error_checkBox.setChecked(True)

        self.verticalLayout_25.addWidget(self.cancel_on_error_checkBox)

        self.line_8 = QFrame(self.scrollAreaWidgetContents_7)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.HLine)
        self.line_8.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_25.addWidget(self.line_8)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_16)

        self.toolButton_merger_open_dir = QToolButton(self.scrollAreaWidgetContents_7)
        self.toolButton_merger_open_dir.setObjectName(u"toolButton_merger_open_dir")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.toolButton_merger_open_dir.sizePolicy().hasHeightForWidth())
        self.toolButton_merger_open_dir.setSizePolicy(sizePolicy1)
        self.toolButton_merger_open_dir.setMinimumSize(QSize(22, 22))
        self.toolButton_merger_open_dir.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-regular.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_merger_open_dir.setIcon(icon)

        self.horizontalLayout_27.addWidget(self.toolButton_merger_open_dir)


        self.verticalLayout_25.addLayout(self.horizontalLayout_27)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_7)

        self.verticalLayout.addWidget(self.scrollArea_5)

        QWidget.setTabOrder(self.scrollArea_5, self.toolButton_merger_open_dir)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_merger_name.setText(QCoreApplication.translate("Form", u"Name", None))
#if QT_CONFIG(tooltip)
        self.cancel_on_error_checkBox.setToolTip(QCoreApplication.translate("Form", u"If there are any errors when trying to import data cancel the whole import.", None))
#endif // QT_CONFIG(tooltip)
        self.cancel_on_error_checkBox.setText(QCoreApplication.translate("Form", u"Cancel on error", None))
#if QT_CONFIG(tooltip)
        self.toolButton_merger_open_dir.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open this Data Store's project directory in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_merger_open_dir.setText("")
    # retranslateUi

