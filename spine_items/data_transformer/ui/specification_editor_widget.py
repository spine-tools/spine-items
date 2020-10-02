# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

################################################################################
## Form generated from reading UI file 'specification_editor_widget.ui'
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


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(317, 553)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.specification_name_edit = QLineEdit(Form)
        self.specification_name_edit.setObjectName(u"specification_name_edit")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.specification_name_edit)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label)

        self.specification_description_edit = QLineEdit(Form)
        self.specification_description_edit.setObjectName(u"specification_description_edit")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.specification_description_edit)


        self.verticalLayout.addLayout(self.formLayout_2)

        self.renaming_table = QTableView(Form)
        self.renaming_table.setObjectName(u"renaming_table")

        self.verticalLayout.addWidget(self.renaming_table)

        self.database_url_combo_box = QComboBox(Form)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")

        self.verticalLayout.addWidget(self.database_url_combo_box)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.load_entity_classes_button = QPushButton(Form)
        self.load_entity_classes_button.setObjectName(u"load_entity_classes_button")

        self.horizontalLayout.addWidget(self.load_entity_classes_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.button_box = QDialogButtonBox(Form)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Name:", None))
        self.specification_name_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Enter specification name here", None))
        self.label.setText(QCoreApplication.translate("Form", u"Description:", None))
        self.specification_description_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Enter specification description here", None))
        self.load_entity_classes_button.setText(QCoreApplication.translate("Form", u"Load names from database", None))
    # retranslateUi

