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
## Form generated from reading UI file 'gdx_exporter_properties.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(250, 180)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.settings_button = QPushButton(Form)
        self.settings_button.setObjectName(u"settings_button")

        self.horizontalLayout_2.addWidget(self.settings_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.issues_label = QLabel(Form)
        self.issues_label.setObjectName(u"issues_label")

        self.verticalLayout.addWidget(self.issues_label)

        self.databases_list_layout = QVBoxLayout()
        self.databases_list_layout.setObjectName(u"databases_list_layout")

        self.verticalLayout.addLayout(self.databases_list_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.output_time_stamps_check_box = QCheckBox(Form)
        self.output_time_stamps_check_box.setObjectName(u"output_time_stamps_check_box")

        self.verticalLayout.addWidget(self.output_time_stamps_check_box)

        self.cancel_on_error_check_box = QCheckBox(Form)
        self.cancel_on_error_check_box.setObjectName(u"cancel_on_error_check_box")
        self.cancel_on_error_check_box.setChecked(True)

        self.verticalLayout.addWidget(self.cancel_on_error_check_box)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.settings_button.setText(QCoreApplication.translate("Form", u"Settings...", None))
        self.issues_label.setText("")
#if QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setToolTip(QCoreApplication.translate("Form", u"Checking this will add time stamps to output directory names.", None))
#endif // QT_CONFIG(tooltip)
        self.output_time_stamps_check_box.setText(QCoreApplication.translate("Form", u"Time stamp output directories", None))
        self.cancel_on_error_check_box.setText(QCoreApplication.translate("Form", u"Cancel export on error", None))
    # retranslateUi

