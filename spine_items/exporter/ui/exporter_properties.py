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
## Form generated from reading UI file 'exporter_properties.ui'
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
        Form.resize(294, 370)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_item_name = QLabel(Form)
        self.label_item_name.setObjectName(u"label_item_name")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_item_name.sizePolicy().hasHeightForWidth())
        self.label_item_name.setSizePolicy(sizePolicy)
        self.label_item_name.setMinimumSize(QSize(0, 20))
        self.label_item_name.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_item_name.setFont(font)
        self.label_item_name.setStyleSheet(u"background-color: #ecd8c6;")
        self.label_item_name.setFrameShape(QFrame.Box)
        self.label_item_name.setFrameShadow(QFrame.Sunken)
        self.label_item_name.setAlignment(Qt.AlignCenter)
        self.label_item_name.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_item_name)

        self.scrollArea_6 = QScrollArea(Form)
        self.scrollArea_6.setObjectName(u"scrollArea_6")
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 292, 348))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.specification_label = QLabel(self.scrollAreaWidgetContents_5)
        self.specification_label.setObjectName(u"specification_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.specification_label.sizePolicy().hasHeightForWidth())
        self.specification_label.setSizePolicy(sizePolicy1)
        self.specification_label.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setPointSize(8)
        self.specification_label.setFont(font1)

        self.horizontalLayout_9.addWidget(self.specification_label)

        self.specification_combo_box = QComboBox(self.scrollAreaWidgetContents_5)
        self.specification_combo_box.setObjectName(u"specification_combo_box")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.specification_combo_box.sizePolicy().hasHeightForWidth())
        self.specification_combo_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_9.addWidget(self.specification_combo_box)

        self.specification_button = QToolButton(self.scrollAreaWidgetContents_5)
        self.specification_button.setObjectName(u"specification_button")
        self.specification_button.setMinimumSize(QSize(22, 22))
        self.specification_button.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/wrench.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.specification_button.setIcon(icon)
        self.specification_button.setIconSize(QSize(16, 16))
        self.specification_button.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_9.addWidget(self.specification_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.issues_label = QLabel(self.scrollAreaWidgetContents_5)
        self.issues_label.setObjectName(u"issues_label")

        self.verticalLayout_2.addWidget(self.issues_label)

        self.outputs_list_layout = QVBoxLayout()
        self.outputs_list_layout.setObjectName(u"outputs_list_layout")

        self.verticalLayout_2.addLayout(self.outputs_list_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.output_time_stamps_check_box = QCheckBox(self.scrollAreaWidgetContents_5)
        self.output_time_stamps_check_box.setObjectName(u"output_time_stamps_check_box")

        self.verticalLayout_2.addWidget(self.output_time_stamps_check_box)

        self.cancel_on_error_check_box = QCheckBox(self.scrollAreaWidgetContents_5)
        self.cancel_on_error_check_box.setObjectName(u"cancel_on_error_check_box")
        self.cancel_on_error_check_box.setChecked(True)

        self.verticalLayout_2.addWidget(self.cancel_on_error_check_box)

        self.line_6 = QFrame(self.scrollAreaWidgetContents_5)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.HLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line_6)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_17)

        self.open_directory_button = QToolButton(self.scrollAreaWidgetContents_5)
        self.open_directory_button.setObjectName(u"open_directory_button")
        sizePolicy1.setHeightForWidth(self.open_directory_button.sizePolicy().hasHeightForWidth())
        self.open_directory_button.setSizePolicy(sizePolicy1)
        self.open_directory_button.setMinimumSize(QSize(22, 22))
        self.open_directory_button.setMaximumSize(QSize(22, 22))
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-regular.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.open_directory_button.setIcon(icon1)

        self.horizontalLayout_13.addWidget(self.open_directory_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_13)

        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_5)

        self.verticalLayout.addWidget(self.scrollArea_6)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_item_name.setText(QCoreApplication.translate("Form", u"Name", None))
        self.specification_label.setText(QCoreApplication.translate("Form", u"Specification:", None))
#if QT_CONFIG(tooltip)
        self.specification_combo_box.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tool specification for this Tool</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.specification_button.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Edit specification.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.issues_label.setText("")
#if QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setToolTip(QCoreApplication.translate("Form", u"Checking this will add time stamps to output directory names.", None))
#endif // QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setText(QCoreApplication.translate("Form", u"Time stamp output directories", None))
        self.cancel_on_error_check_box.setText(QCoreApplication.translate("Form", u"Cancel export on error", None))
#if QT_CONFIG(tooltip)
        self.open_directory_button.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open this GdxExporter's project directory in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

