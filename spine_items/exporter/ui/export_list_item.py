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
## Form generated from reading UI file 'export_list_item.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(306, 187)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.input_label_field = QLabel(self.frame)
        self.input_label_field.setObjectName(u"input_label_field")
        self.input_label_field.setTextFormat(Qt.RichText)

        self.verticalLayout.addWidget(self.input_label_field)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.out_label_label = QLabel(self.frame)
        self.out_label_label.setObjectName(u"out_label_label")
        self.out_label_label.setTextFormat(Qt.PlainText)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.out_label_label)

        self.out_label_edit = PropertyQLineEdit(self.frame)
        self.out_label_edit.setObjectName(u"out_label_edit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.out_label_edit)


        self.verticalLayout.addLayout(self.formLayout)

        self.out_url_status_label = QLabel(self.frame)
        self.out_url_status_label.setObjectName(u"out_url_status_label")

        self.verticalLayout.addWidget(self.out_url_status_label)

        self.out_url_widget = QWidget(self.frame)
        self.out_url_widget.setObjectName(u"out_url_widget")
        self.verticalLayout_3 = QVBoxLayout(self.out_url_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.out_url_setup_button = QPushButton(self.out_url_widget)
        self.out_url_setup_button.setObjectName(u"out_url_setup_button")

        self.horizontalLayout.addWidget(self.out_url_setup_button)

        self.out_url_clear_button = QPushButton(self.out_url_widget)
        self.out_url_clear_button.setObjectName(u"out_url_clear_button")

        self.horizontalLayout.addWidget(self.out_url_clear_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.out_url_widget)


        self.verticalLayout_2.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.input_label_field.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.out_label_label.setText(QCoreApplication.translate("Form", u"Output file/label:", None))
#if QT_CONFIG(tooltip)
        self.out_label_edit.setToolTip(QCoreApplication.translate("Form", u"Identifier for the output file(s). This is the  filename if a single file is exported.", None))
#endif // QT_CONFIG(tooltip)
        self.out_label_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Type output resource label here...", None))
#if QT_CONFIG(tooltip)
        self.out_url_setup_button.setToolTip(QCoreApplication.translate("Form", u"Opens a dialog where you can set the database URL.", None))
#endif // QT_CONFIG(tooltip)
        self.out_url_setup_button.setText(QCoreApplication.translate("Form", u"Set URL...", None))
        self.out_url_clear_button.setText(QCoreApplication.translate("Form", u"Clear URL", None))
    # retranslateUi

