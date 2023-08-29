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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget)

from spine_items.widgets import FileDropTargetLineEdit
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(381, 221)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(3, 3, 3, 3)
        self.lineEdit_password = QLineEdit(self.frame)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy)
        self.lineEdit_password.setMinimumSize(QSize(0, 24))
        self.lineEdit_password.setMaximumSize(QSize(5000, 24))
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_password, 3, 1, 1, 5)

        self.label_port = QLabel(self.frame)
        self.label_port.setObjectName(u"label_port")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_port.sizePolicy().hasHeightForWidth())
        self.label_port.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_port, 4, 4, 1, 1)

        self.comboBox_dialect = QComboBox(self.frame)
        self.comboBox_dialect.setObjectName(u"comboBox_dialect")
        sizePolicy.setHeightForWidth(self.comboBox_dialect.sizePolicy().hasHeightForWidth())
        self.comboBox_dialect.setSizePolicy(sizePolicy)
        self.comboBox_dialect.setMinimumSize(QSize(0, 24))
        self.comboBox_dialect.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.comboBox_dialect, 0, 1, 1, 5)

        self.label_dsn = QLabel(self.frame)
        self.label_dsn.setObjectName(u"label_dsn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_dsn.sizePolicy().hasHeightForWidth())
        self.label_dsn.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_dsn, 1, 0, 1, 1)

        self.label_dialect = QLabel(self.frame)
        self.label_dialect.setObjectName(u"label_dialect")
        sizePolicy2.setHeightForWidth(self.label_dialect.sizePolicy().hasHeightForWidth())
        self.label_dialect.setSizePolicy(sizePolicy2)
        self.label_dialect.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_dialect, 0, 0, 1, 1)

        self.lineEdit_port = QLineEdit(self.frame)
        self.lineEdit_port.setObjectName(u"lineEdit_port")
        self.lineEdit_port.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_port.sizePolicy().hasHeightForWidth())
        self.lineEdit_port.setSizePolicy(sizePolicy)
        self.lineEdit_port.setMinimumSize(QSize(0, 24))
        self.lineEdit_port.setMaximumSize(QSize(80, 24))
        self.lineEdit_port.setInputMethodHints(Qt.ImhNone)

        self.gridLayout.addWidget(self.lineEdit_port, 4, 5, 1, 1)

        self.label_username = QLabel(self.frame)
        self.label_username.setObjectName(u"label_username")
        sizePolicy2.setHeightForWidth(self.label_username.sizePolicy().hasHeightForWidth())
        self.label_username.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_username, 2, 0, 1, 1)

        self.label_database = QLabel(self.frame)
        self.label_database.setObjectName(u"label_database")
        sizePolicy2.setHeightForWidth(self.label_database.sizePolicy().hasHeightForWidth())
        self.label_database.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_database, 6, 0, 1, 1)

        self.comboBox_dsn = QComboBox(self.frame)
        self.comboBox_dsn.setObjectName(u"comboBox_dsn")
        self.comboBox_dsn.setEnabled(False)
        sizePolicy.setHeightForWidth(self.comboBox_dsn.sizePolicy().hasHeightForWidth())
        self.comboBox_dsn.setSizePolicy(sizePolicy)
        self.comboBox_dsn.setMinimumSize(QSize(0, 24))
        self.comboBox_dsn.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.comboBox_dsn, 1, 1, 1, 5)

        self.lineEdit_host = QLineEdit(self.frame)
        self.lineEdit_host.setObjectName(u"lineEdit_host")
        self.lineEdit_host.setEnabled(False)
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(3)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEdit_host.sizePolicy().hasHeightForWidth())
        self.lineEdit_host.setSizePolicy(sizePolicy3)
        self.lineEdit_host.setMinimumSize(QSize(0, 24))
        self.lineEdit_host.setMaximumSize(QSize(5000, 24))
        self.lineEdit_host.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_host, 4, 1, 1, 3)

        self.label_password = QLabel(self.frame)
        self.label_password.setObjectName(u"label_password")
        sizePolicy2.setHeightForWidth(self.label_password.sizePolicy().hasHeightForWidth())
        self.label_password.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_password, 3, 0, 1, 1)

        self.lineEdit_username = QLineEdit(self.frame)
        self.lineEdit_username.setObjectName(u"lineEdit_username")
        self.lineEdit_username.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_username.sizePolicy().hasHeightForWidth())
        self.lineEdit_username.setSizePolicy(sizePolicy)
        self.lineEdit_username.setMinimumSize(QSize(0, 24))
        self.lineEdit_username.setMaximumSize(QSize(5000, 24))
        self.lineEdit_username.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_username, 2, 1, 1, 5)

        self.label_host = QLabel(self.frame)
        self.label_host.setObjectName(u"label_host")
        sizePolicy2.setHeightForWidth(self.label_host.sizePolicy().hasHeightForWidth())
        self.label_host.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_host, 4, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lineEdit_database = FileDropTargetLineEdit(self.frame)
        self.lineEdit_database.setObjectName(u"lineEdit_database")
        self.lineEdit_database.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_database.sizePolicy().hasHeightForWidth())
        self.lineEdit_database.setSizePolicy(sizePolicy)
        self.lineEdit_database.setMinimumSize(QSize(0, 24))
        self.lineEdit_database.setMaximumSize(QSize(16777215, 24))
        self.lineEdit_database.setCursor(QCursor(Qt.IBeamCursor))
        self.lineEdit_database.setClearButtonEnabled(True)

        self.horizontalLayout_4.addWidget(self.lineEdit_database)

        self.toolButton_select_sqlite_file = QToolButton(self.frame)
        self.toolButton_select_sqlite_file.setObjectName(u"toolButton_select_sqlite_file")
        self.toolButton_select_sqlite_file.setEnabled(False)
        sizePolicy.setHeightForWidth(self.toolButton_select_sqlite_file.sizePolicy().hasHeightForWidth())
        self.toolButton_select_sqlite_file.setSizePolicy(sizePolicy)
        self.toolButton_select_sqlite_file.setMinimumSize(QSize(22, 22))
        self.toolButton_select_sqlite_file.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_select_sqlite_file.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.toolButton_select_sqlite_file)


        self.gridLayout.addLayout(self.horizontalLayout_4, 6, 1, 1, 5)


        self.verticalLayout.addWidget(self.frame)

        QWidget.setTabOrder(self.comboBox_dialect, self.comboBox_dsn)
        QWidget.setTabOrder(self.comboBox_dsn, self.lineEdit_username)
        QWidget.setTabOrder(self.lineEdit_username, self.lineEdit_password)
        QWidget.setTabOrder(self.lineEdit_password, self.lineEdit_host)
        QWidget.setTabOrder(self.lineEdit_host, self.lineEdit_port)
        QWidget.setTabOrder(self.lineEdit_port, self.lineEdit_database)
        QWidget.setTabOrder(self.lineEdit_database, self.toolButton_select_sqlite_file)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lineEdit_password.setPlaceholderText("")
        self.label_port.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.label_dsn.setText(QCoreApplication.translate("Form", u"DSN:", None))
        self.label_dialect.setText(QCoreApplication.translate("Form", u"Dialect:", None))
        self.lineEdit_port.setPlaceholderText("")
        self.label_username.setText(QCoreApplication.translate("Form", u"Username:", None))
        self.label_database.setText(QCoreApplication.translate("Form", u"Database:", None))
        self.lineEdit_host.setPlaceholderText("")
        self.label_password.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.lineEdit_username.setPlaceholderText("")
        self.label_host.setText(QCoreApplication.translate("Form", u"Host:", None))
        self.lineEdit_database.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.toolButton_select_sqlite_file.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select SQLite file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

