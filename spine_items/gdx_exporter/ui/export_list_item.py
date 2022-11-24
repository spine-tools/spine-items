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
## Form generated from reading UI file 'export_list_item.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QLabel,
    QLineEdit, QSizePolicy, QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(349, 146)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.url_field = QLineEdit(self.frame)
        self.url_field.setObjectName(u"url_field")
        font = QFont()
        font.setBold(True)
        self.url_field.setFont(font)
        self.url_field.setFrame(False)
        self.url_field.setReadOnly(True)

        self.verticalLayout.addWidget(self.url_field)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.file_name_label = QLabel(self.frame)
        self.file_name_label.setObjectName(u"file_name_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.file_name_label)

        self.out_file_name_edit = PropertyQLineEdit(self.frame)
        self.out_file_name_edit.setObjectName(u"out_file_name_edit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.out_file_name_edit)


        self.verticalLayout.addLayout(self.formLayout)


        self.verticalLayout_2.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.file_name_label.setText(QCoreApplication.translate("Form", u"Filename:", None))
        self.out_file_name_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Type output file name here...", None))
    # retranslateUi

