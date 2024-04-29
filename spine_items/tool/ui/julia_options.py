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
## Form generated from reading UI file 'julia_options.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QToolButton, QWidget)

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(282, 47)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_sysimage = QLabel(Form)
        self.label_sysimage.setObjectName(u"label_sysimage")

        self.horizontalLayout.addWidget(self.label_sysimage)

        self.lineEdit_sysimage = PropertyQLineEdit(Form)
        self.lineEdit_sysimage.setObjectName(u"lineEdit_sysimage")
        self.lineEdit_sysimage.setMaximumSize(QSize(16777215, 24))
        self.lineEdit_sysimage.setReadOnly(False)
        self.lineEdit_sysimage.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.lineEdit_sysimage)

        self.toolButton_abort_sysimage = QToolButton(Form)
        self.toolButton_abort_sysimage.setObjectName(u"toolButton_abort_sysimage")

        self.horizontalLayout.addWidget(self.toolButton_abort_sysimage)

        self.toolButton_new_sysimage = QToolButton(Form)
        self.toolButton_new_sysimage.setObjectName(u"toolButton_new_sysimage")
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_new_sysimage.setIcon(icon)
        self.toolButton_new_sysimage.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.horizontalLayout.addWidget(self.toolButton_new_sysimage)

        self.toolButton_open_sysimage = QToolButton(Form)
        self.toolButton_open_sysimage.setObjectName(u"toolButton_open_sysimage")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_open_sysimage.setIcon(icon1)

        self.horizontalLayout.addWidget(self.toolButton_open_sysimage)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_sysimage.setText(QCoreApplication.translate("Form", u"Sysimage", None))
#if QT_CONFIG(tooltip)
        self.toolButton_abort_sysimage.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Abort sysimage creation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_abort_sysimage.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_new_sysimage.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>New Julia sysimage</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_new_sysimage.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_open_sysimage.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open Julia sysimage</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_open_sysimage.setText(QCoreApplication.translate("Form", u"...", None))
    # retranslateUi

