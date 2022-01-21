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
## Form generated from reading UI file 'data_store_properties.ui'
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

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit
from spinetoolbox.widgets.custom_qlineedits import CustomQLineEdit

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(314, 333)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.toolButton_copy_url = QToolButton(Form)
        self.toolButton_copy_url.setObjectName(u"toolButton_copy_url")
        icon = QIcon()
        icon.addFile(u":/icons/copy.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_copy_url.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButton_copy_url)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.frame_3)
        self.verticalLayout_26.setSpacing(6)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(3, 3, 3, 3)
        self.comboBox_dsn = QComboBox(self.frame_3)
        self.comboBox_dsn.setObjectName(u"comboBox_dsn")
        self.comboBox_dsn.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_dsn.sizePolicy().hasHeightForWidth())
        self.comboBox_dsn.setSizePolicy(sizePolicy)
        self.comboBox_dsn.setMinimumSize(QSize(0, 24))
        self.comboBox_dsn.setMaximumSize(QSize(16777215, 24))
        font = QFont()
        font.setPointSize(9)
        self.comboBox_dsn.setFont(font)

        self.gridLayout_3.addWidget(self.comboBox_dsn, 1, 2, 1, 2)

        self.label_dsn = QLabel(self.frame_3)
        self.label_dsn.setObjectName(u"label_dsn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_dsn.sizePolicy().hasHeightForWidth())
        self.label_dsn.setSizePolicy(sizePolicy1)
        self.label_dsn.setFont(font)

        self.gridLayout_3.addWidget(self.label_dsn, 1, 0, 1, 1)

        self.label_username = QLabel(self.frame_3)
        self.label_username.setObjectName(u"label_username")
        sizePolicy1.setHeightForWidth(self.label_username.sizePolicy().hasHeightForWidth())
        self.label_username.setSizePolicy(sizePolicy1)
        self.label_username.setFont(font)

        self.gridLayout_3.addWidget(self.label_username, 2, 0, 1, 1)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setSpacing(0)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.lineEdit_database = CustomQLineEdit(self.frame_3)
        self.lineEdit_database.setObjectName(u"lineEdit_database")
        self.lineEdit_database.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_database.sizePolicy().hasHeightForWidth())
        self.lineEdit_database.setSizePolicy(sizePolicy)
        self.lineEdit_database.setMinimumSize(QSize(0, 24))
        self.lineEdit_database.setMaximumSize(QSize(16777215, 24))
        self.lineEdit_database.setFont(font)
        self.lineEdit_database.setCursor(QCursor(Qt.IBeamCursor))
        self.lineEdit_database.setClearButtonEnabled(True)

        self.horizontalLayout_24.addWidget(self.lineEdit_database)

        self.toolButton_select_sqlite_file = QToolButton(self.frame_3)
        self.toolButton_select_sqlite_file.setObjectName(u"toolButton_select_sqlite_file")
        self.toolButton_select_sqlite_file.setEnabled(False)
        sizePolicy.setHeightForWidth(self.toolButton_select_sqlite_file.sizePolicy().hasHeightForWidth())
        self.toolButton_select_sqlite_file.setSizePolicy(sizePolicy)
        self.toolButton_select_sqlite_file.setMinimumSize(QSize(22, 22))
        self.toolButton_select_sqlite_file.setMaximumSize(QSize(22, 22))
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_select_sqlite_file.setIcon(icon1)

        self.horizontalLayout_24.addWidget(self.toolButton_select_sqlite_file)


        self.gridLayout_3.addLayout(self.horizontalLayout_24, 5, 2, 1, 2)

        self.lineEdit_password = PropertyQLineEdit(self.frame_3)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy)
        self.lineEdit_password.setMinimumSize(QSize(0, 24))
        self.lineEdit_password.setMaximumSize(QSize(5000, 24))
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setClearButtonEnabled(True)

        self.gridLayout_3.addWidget(self.lineEdit_password, 3, 2, 1, 2)

        self.lineEdit_username = PropertyQLineEdit(self.frame_3)
        self.lineEdit_username.setObjectName(u"lineEdit_username")
        self.lineEdit_username.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_username.sizePolicy().hasHeightForWidth())
        self.lineEdit_username.setSizePolicy(sizePolicy)
        self.lineEdit_username.setMinimumSize(QSize(0, 24))
        self.lineEdit_username.setMaximumSize(QSize(5000, 24))
        self.lineEdit_username.setFont(font)
        self.lineEdit_username.setClearButtonEnabled(True)

        self.gridLayout_3.addWidget(self.lineEdit_username, 2, 2, 1, 2)

        self.label_password = QLabel(self.frame_3)
        self.label_password.setObjectName(u"label_password")
        sizePolicy1.setHeightForWidth(self.label_password.sizePolicy().hasHeightForWidth())
        self.label_password.setSizePolicy(sizePolicy1)
        self.label_password.setFont(font)

        self.gridLayout_3.addWidget(self.label_password, 3, 0, 1, 1)

        self.label_host = QLabel(self.frame_3)
        self.label_host.setObjectName(u"label_host")
        sizePolicy1.setHeightForWidth(self.label_host.sizePolicy().hasHeightForWidth())
        self.label_host.setSizePolicy(sizePolicy1)
        self.label_host.setFont(font)

        self.gridLayout_3.addWidget(self.label_host, 4, 0, 1, 1)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.comboBox_dialect = QComboBox(self.frame_3)
        self.comboBox_dialect.setObjectName(u"comboBox_dialect")
        sizePolicy.setHeightForWidth(self.comboBox_dialect.sizePolicy().hasHeightForWidth())
        self.comboBox_dialect.setSizePolicy(sizePolicy)
        self.comboBox_dialect.setMinimumSize(QSize(0, 24))
        self.comboBox_dialect.setMaximumSize(QSize(16777215, 24))
        self.comboBox_dialect.setFont(font)

        self.horizontalLayout_12.addWidget(self.comboBox_dialect)


        self.gridLayout_3.addLayout(self.horizontalLayout_12, 0, 2, 1, 2)

        self.label_dialect = QLabel(self.frame_3)
        self.label_dialect.setObjectName(u"label_dialect")
        sizePolicy1.setHeightForWidth(self.label_dialect.sizePolicy().hasHeightForWidth())
        self.label_dialect.setSizePolicy(sizePolicy1)
        self.label_dialect.setMaximumSize(QSize(16777215, 16777215))
        self.label_dialect.setFont(font)

        self.gridLayout_3.addWidget(self.label_dialect, 0, 0, 1, 1)

        self.label_database = QLabel(self.frame_3)
        self.label_database.setObjectName(u"label_database")
        sizePolicy1.setHeightForWidth(self.label_database.sizePolicy().hasHeightForWidth())
        self.label_database.setSizePolicy(sizePolicy1)
        self.label_database.setFont(font)

        self.gridLayout_3.addWidget(self.label_database, 5, 0, 1, 1)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.lineEdit_host = PropertyQLineEdit(self.frame_3)
        self.lineEdit_host.setObjectName(u"lineEdit_host")
        self.lineEdit_host.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(3)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_host.sizePolicy().hasHeightForWidth())
        self.lineEdit_host.setSizePolicy(sizePolicy2)
        self.lineEdit_host.setMinimumSize(QSize(0, 24))
        self.lineEdit_host.setMaximumSize(QSize(5000, 24))
        self.lineEdit_host.setFont(font)
        self.lineEdit_host.setClearButtonEnabled(True)

        self.horizontalLayout_23.addWidget(self.lineEdit_host)

        self.label_port = QLabel(self.frame_3)
        self.label_port.setObjectName(u"label_port")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_port.sizePolicy().hasHeightForWidth())
        self.label_port.setSizePolicy(sizePolicy3)
        self.label_port.setFont(font)

        self.horizontalLayout_23.addWidget(self.label_port)

        self.lineEdit_port = PropertyQLineEdit(self.frame_3)
        self.lineEdit_port.setObjectName(u"lineEdit_port")
        self.lineEdit_port.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_port.sizePolicy().hasHeightForWidth())
        self.lineEdit_port.setSizePolicy(sizePolicy)
        self.lineEdit_port.setMinimumSize(QSize(0, 24))
        self.lineEdit_port.setMaximumSize(QSize(80, 24))
        self.lineEdit_port.setFont(font)
        self.lineEdit_port.setInputMethodHints(Qt.ImhNone)

        self.horizontalLayout_23.addWidget(self.lineEdit_port)


        self.gridLayout_3.addLayout(self.horizontalLayout_23, 4, 2, 1, 2)


        self.verticalLayout_26.addLayout(self.gridLayout_3)


        self.verticalLayout_2.addWidget(self.frame_3)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_create_new_spine_db = QPushButton(Form)
        self.pushButton_create_new_spine_db.setObjectName(u"pushButton_create_new_spine_db")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_create_new_spine_db.sizePolicy().hasHeightForWidth())
        self.pushButton_create_new_spine_db.setSizePolicy(sizePolicy4)
        icon2 = QIcon()
        icon2.addFile(u":/icons/Spine_symbol.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_create_new_spine_db.setIcon(icon2)

        self.horizontalLayout.addWidget(self.pushButton_create_new_spine_db)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_ds_open_editor = QPushButton(Form)
        self.pushButton_ds_open_editor.setObjectName(u"pushButton_ds_open_editor")
        sizePolicy4.setHeightForWidth(self.pushButton_ds_open_editor.sizePolicy().hasHeightForWidth())
        self.pushButton_ds_open_editor.setSizePolicy(sizePolicy4)

        self.horizontalLayout.addWidget(self.pushButton_ds_open_editor)


        self.verticalLayout.addLayout(self.horizontalLayout)

        QWidget.setTabOrder(self.comboBox_dialect, self.comboBox_dsn)
        QWidget.setTabOrder(self.comboBox_dsn, self.lineEdit_username)
        QWidget.setTabOrder(self.lineEdit_username, self.lineEdit_password)
        QWidget.setTabOrder(self.lineEdit_password, self.lineEdit_host)
        QWidget.setTabOrder(self.lineEdit_host, self.lineEdit_port)
        QWidget.setTabOrder(self.lineEdit_port, self.lineEdit_database)
        QWidget.setTabOrder(self.lineEdit_database, self.toolButton_select_sqlite_file)
        QWidget.setTabOrder(self.toolButton_select_sqlite_file, self.pushButton_create_new_spine_db)
        QWidget.setTabOrder(self.pushButton_create_new_spine_db, self.pushButton_ds_open_editor)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"URL", None))
#if QT_CONFIG(tooltip)
        self.toolButton_copy_url.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy current database url to clipboard.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_copy_url.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_dsn.setText(QCoreApplication.translate("Form", u"DSN", None))
        self.label_username.setText(QCoreApplication.translate("Form", u"Username", None))
        self.lineEdit_database.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.toolButton_select_sqlite_file.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select SQLite file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_password.setPlaceholderText("")
        self.lineEdit_username.setPlaceholderText("")
        self.label_password.setText(QCoreApplication.translate("Form", u"Password", None))
        self.label_host.setText(QCoreApplication.translate("Form", u"Host", None))
        self.label_dialect.setText(QCoreApplication.translate("Form", u"Dialect", None))
        self.label_database.setText(QCoreApplication.translate("Form", u"Database", None))
        self.lineEdit_host.setPlaceholderText("")
        self.label_port.setText(QCoreApplication.translate("Form", u"Port", None))
        self.lineEdit_port.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.pushButton_create_new_spine_db.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Create new Spine database at the selected URL, or at a default one if the selected is not valid.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_new_spine_db.setText(QCoreApplication.translate("Form", u"New Spine db", None))
#if QT_CONFIG(tooltip)
        self.pushButton_ds_open_editor.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open URL in Spine database editor</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_ds_open_editor.setText(QCoreApplication.translate("Form", u"Open editor...", None))
    # retranslateUi

