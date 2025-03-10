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
## Form generated from reading UI file 'exporter_properties.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLabel, QScrollArea, QSizePolicy,
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(272, 202)
        Form.setStyleSheet(u"QScrollArea { background: transparent; }\n"
"QScrollArea > QWidget > QWidget { background: transparent; }")
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 272, 202))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.specification_label = QLabel(self.scrollAreaWidgetContents)
        self.specification_label.setObjectName(u"specification_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.specification_label.sizePolicy().hasHeightForWidth())
        self.specification_label.setSizePolicy(sizePolicy)
        self.specification_label.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_9.addWidget(self.specification_label)

        self.specification_combo_box = QComboBox(self.scrollAreaWidgetContents)
        self.specification_combo_box.setObjectName(u"specification_combo_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.specification_combo_box.sizePolicy().hasHeightForWidth())
        self.specification_combo_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.specification_combo_box)

        self.specification_button = QToolButton(self.scrollAreaWidgetContents)
        self.specification_button.setObjectName(u"specification_button")
        icon = QIcon()
        icon.addFile(u":/icons/wrench.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.specification_button.setIcon(icon)
        self.specification_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.horizontalLayout_9.addWidget(self.specification_button)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.message_label = QLabel(self.scrollAreaWidgetContents)
        self.message_label.setObjectName(u"message_label")
        self.message_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.message_label)

        self.outputs_list_layout = QVBoxLayout()
        self.outputs_list_layout.setSpacing(0)
        self.outputs_list_layout.setObjectName(u"outputs_list_layout")

        self.verticalLayout.addLayout(self.outputs_list_layout)

        self.verticalSpacer = QSpacerItem(20, 71, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.output_time_stamps_check_box = QCheckBox(self.frame)
        self.output_time_stamps_check_box.setObjectName(u"output_time_stamps_check_box")

        self.verticalLayout_2.addWidget(self.output_time_stamps_check_box)

        self.cancel_on_error_check_box = QCheckBox(self.frame)
        self.cancel_on_error_check_box.setObjectName(u"cancel_on_error_check_box")
        self.cancel_on_error_check_box.setChecked(True)

        self.verticalLayout_2.addWidget(self.cancel_on_error_check_box)


        self.verticalLayout.addWidget(self.frame)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.specification_label.setText(QCoreApplication.translate("Form", u"Specification:", None))
#if QT_CONFIG(tooltip)
        self.specification_combo_box.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tool specification for this Tool</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.specification_button.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Edit specification.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.message_label.setText("")
#if QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setToolTip(QCoreApplication.translate("Form", u"Checking this will add time stamps to output directory names.", None))
#endif // QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setText(QCoreApplication.translate("Form", u"Time stamp output directories", None))
        self.cancel_on_error_check_box.setText(QCoreApplication.translate("Form", u"Cancel export on error", None))
    # retranslateUi

