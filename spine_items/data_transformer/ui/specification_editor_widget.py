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

from spinetoolbox.widgets.custom_combobox import ElidedCombobox

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(596, 553)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
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


        self.verticalLayout_2.addLayout(self.formLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.filter_combo_box = QComboBox(Form)
        self.filter_combo_box.setObjectName(u"filter_combo_box")

        self.horizontalLayout_3.addWidget(self.filter_combo_box)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.filter_stack = QStackedWidget(Form)
        self.filter_stack.setObjectName(u"filter_stack")
        self.no_filter_page = QWidget()
        self.no_filter_page.setObjectName(u"no_filter_page")
        self.verticalLayout = QVBoxLayout(self.no_filter_page)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.no_filter_label = QLabel(self.no_filter_page)
        self.no_filter_label.setObjectName(u"no_filter_label")
        self.no_filter_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.no_filter_label)

        self.verticalSpacer = QSpacerItem(20, 184, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.filter_stack.addWidget(self.no_filter_page)
        self.fitle_page = QWidget()
        self.fitle_page.setObjectName(u"fitle_page")
        self.verticalLayout_4 = QVBoxLayout(self.fitle_page)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.filter_widget = QWidget(self.fitle_page)
        self.filter_widget.setObjectName(u"filter_widget")

        self.verticalLayout_4.addWidget(self.filter_widget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.fitle_page)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.database_url_combo_box = ElidedCombobox(self.fitle_page)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.database_url_combo_box.sizePolicy().hasHeightForWidth())
        self.database_url_combo_box.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.database_url_combo_box)

        self.load_url_from_fs_button = QToolButton(self.fitle_page)
        self.load_url_from_fs_button.setObjectName(u"load_url_from_fs_button")
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.load_url_from_fs_button.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.load_url_from_fs_button)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.load_data_button = QPushButton(self.fitle_page)
        self.load_data_button.setObjectName(u"load_data_button")
        self.load_data_button.setEnabled(False)

        self.horizontalLayout.addWidget(self.load_data_button)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.filter_stack.addWidget(self.fitle_page)

        self.verticalLayout_2.addWidget(self.filter_stack)

        self.button_box = QDialogButtonBox(Form)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.button_box)


        self.retranslateUi(Form)

        self.filter_stack.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Name:", None))
        self.specification_name_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Enter specification name here", None))
        self.label.setText(QCoreApplication.translate("Form", u"Description:", None))
        self.specification_description_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Enter specification description here", None))
        self.no_filter_label.setText(QCoreApplication.translate("Form", u"No filter selected.", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Database url:", None))
#if QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Browse file system</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setText(QCoreApplication.translate("Form", u"...", None))
        self.load_data_button.setText(QCoreApplication.translate("Form", u"Load filter data from database", None))
    # retranslateUi

