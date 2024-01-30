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
## Form generated from reading UI file 'url_selector_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QToolButton,
    QWidget)

from spine_items.widgets import FileDropTargetLineEdit
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(386, 212)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName(u"formLayout")
        self.label_dialect = QLabel(Form)
        self.label_dialect.setObjectName(u"label_dialect")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_dialect)

        self.comboBox_dialect = QComboBox(Form)
        self.comboBox_dialect.setObjectName(u"comboBox_dialect")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_dialect)

        self.label_dsn = QLabel(Form)
        self.label_dsn.setObjectName(u"label_dsn")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_dsn)

        self.comboBox_dsn = QComboBox(Form)
        self.comboBox_dsn.setObjectName(u"comboBox_dsn")
        self.comboBox_dsn.setEnabled(False)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.comboBox_dsn)

        self.label_username = QLabel(Form)
        self.label_username.setObjectName(u"label_username")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_username)

        self.lineEdit_username = QLineEdit(Form)
        self.lineEdit_username.setObjectName(u"lineEdit_username")
        self.lineEdit_username.setEnabled(False)
        self.lineEdit_username.setClearButtonEnabled(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_username)

        self.label_password = QLabel(Form)
        self.label_password.setObjectName(u"label_password")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_password)

        self.lineEdit_password = QLineEdit(Form)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEnabled(False)
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setClearButtonEnabled(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_password)

        self.label_host = QLabel(Form)
        self.label_host.setObjectName(u"label_host")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_host)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_host = QLineEdit(Form)
        self.lineEdit_host.setObjectName(u"lineEdit_host")
        self.lineEdit_host.setEnabled(False)
        self.lineEdit_host.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.lineEdit_host)

        self.label_port = QLabel(Form)
        self.label_port.setObjectName(u"label_port")

        self.horizontalLayout.addWidget(self.label_port)

        self.lineEdit_port = QLineEdit(Form)
        self.lineEdit_port.setObjectName(u"lineEdit_port")
        self.lineEdit_port.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_port.sizePolicy().hasHeightForWidth())
        self.lineEdit_port.setSizePolicy(sizePolicy)
        self.lineEdit_port.setInputMethodHints(Qt.ImhNone)

        self.horizontalLayout.addWidget(self.lineEdit_port)


        self.formLayout.setLayout(4, QFormLayout.FieldRole, self.horizontalLayout)

        self.schema_label = QLabel(Form)
        self.schema_label.setObjectName(u"schema_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.schema_label)

        self.schema_line_edit = QLineEdit(Form)
        self.schema_line_edit.setObjectName(u"schema_line_edit")
        self.schema_line_edit.setEnabled(False)
        self.schema_line_edit.setClearButtonEnabled(True)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.schema_line_edit)

        self.label_database = QLabel(Form)
        self.label_database.setObjectName(u"label_database")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_database)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lineEdit_database = FileDropTargetLineEdit(Form)
        self.lineEdit_database.setObjectName(u"lineEdit_database")
        self.lineEdit_database.setEnabled(False)
        self.lineEdit_database.setCursor(QCursor(Qt.IBeamCursor))
        self.lineEdit_database.setClearButtonEnabled(True)

        self.horizontalLayout_4.addWidget(self.lineEdit_database)

        self.toolButton_select_sqlite_file = QToolButton(Form)
        self.toolButton_select_sqlite_file.setObjectName(u"toolButton_select_sqlite_file")
        self.toolButton_select_sqlite_file.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.toolButton_select_sqlite_file.sizePolicy().hasHeightForWidth())
        self.toolButton_select_sqlite_file.setSizePolicy(sizePolicy1)
        self.toolButton_select_sqlite_file.setMinimumSize(QSize(22, 22))
        self.toolButton_select_sqlite_file.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_select_sqlite_file.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.toolButton_select_sqlite_file)


        self.formLayout.setLayout(6, QFormLayout.FieldRole, self.horizontalLayout_4)

        QWidget.setTabOrder(self.comboBox_dialect, self.comboBox_dsn)
        QWidget.setTabOrder(self.comboBox_dsn, self.lineEdit_username)
        QWidget.setTabOrder(self.lineEdit_username, self.lineEdit_password)
        QWidget.setTabOrder(self.lineEdit_password, self.lineEdit_host)
        QWidget.setTabOrder(self.lineEdit_host, self.lineEdit_port)
        QWidget.setTabOrder(self.lineEdit_port, self.schema_line_edit)
        QWidget.setTabOrder(self.schema_line_edit, self.lineEdit_database)
        QWidget.setTabOrder(self.lineEdit_database, self.toolButton_select_sqlite_file)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_dialect.setText(QCoreApplication.translate("Form", u"Dialect:", None))
        self.label_dsn.setText(QCoreApplication.translate("Form", u"DSN:", None))
        self.label_username.setText(QCoreApplication.translate("Form", u"Username:", None))
        self.label_password.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.label_host.setText(QCoreApplication.translate("Form", u"Host:", None))
        self.label_port.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.schema_label.setText(QCoreApplication.translate("Form", u"Schema:", None))
        self.label_database.setText(QCoreApplication.translate("Form", u"Database:", None))
#if QT_CONFIG(tooltip)
        self.toolButton_select_sqlite_file.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select SQLite file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

