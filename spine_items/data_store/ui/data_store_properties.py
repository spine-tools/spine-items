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
        Form.resize(369, 337)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(3, 3, 3, 3)
        self.label_dialect = QLabel(self.groupBox)
        self.label_dialect.setObjectName(u"label_dialect")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_dialect.sizePolicy().hasHeightForWidth())
        self.label_dialect.setSizePolicy(sizePolicy)
        self.label_dialect.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_dialect, 0, 0, 1, 1)

        self.lineEdit_port = PropertyQLineEdit(self.groupBox)
        self.lineEdit_port.setObjectName(u"lineEdit_port")
        self.lineEdit_port.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_port.sizePolicy().hasHeightForWidth())
        self.lineEdit_port.setSizePolicy(sizePolicy1)
        self.lineEdit_port.setMinimumSize(QSize(0, 24))
        self.lineEdit_port.setMaximumSize(QSize(80, 24))
        self.lineEdit_port.setInputMethodHints(Qt.ImhNone)

        self.gridLayout.addWidget(self.lineEdit_port, 4, 5, 1, 1)

        self.label_dsn = QLabel(self.groupBox)
        self.label_dsn.setObjectName(u"label_dsn")
        sizePolicy.setHeightForWidth(self.label_dsn.sizePolicy().hasHeightForWidth())
        self.label_dsn.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_dsn, 1, 0, 1, 1)

        self.label_password = QLabel(self.groupBox)
        self.label_password.setObjectName(u"label_password")
        sizePolicy.setHeightForWidth(self.label_password.sizePolicy().hasHeightForWidth())
        self.label_password.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_password, 3, 0, 1, 1)

        self.label_host = QLabel(self.groupBox)
        self.label_host.setObjectName(u"label_host")
        sizePolicy.setHeightForWidth(self.label_host.sizePolicy().hasHeightForWidth())
        self.label_host.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_host, 4, 0, 1, 1)

        self.label_username = QLabel(self.groupBox)
        self.label_username.setObjectName(u"label_username")
        sizePolicy.setHeightForWidth(self.label_username.sizePolicy().hasHeightForWidth())
        self.label_username.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_username, 2, 0, 1, 1)

        self.label_port = QLabel(self.groupBox)
        self.label_port.setObjectName(u"label_port")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_port.sizePolicy().hasHeightForWidth())
        self.label_port.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_port, 4, 4, 1, 1)

        self.label_database = QLabel(self.groupBox)
        self.label_database.setObjectName(u"label_database")
        sizePolicy.setHeightForWidth(self.label_database.sizePolicy().hasHeightForWidth())
        self.label_database.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_database, 6, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lineEdit_database = CustomQLineEdit(self.groupBox)
        self.lineEdit_database.setObjectName(u"lineEdit_database")
        self.lineEdit_database.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.lineEdit_database.sizePolicy().hasHeightForWidth())
        self.lineEdit_database.setSizePolicy(sizePolicy1)
        self.lineEdit_database.setMinimumSize(QSize(0, 24))
        self.lineEdit_database.setMaximumSize(QSize(16777215, 24))
        self.lineEdit_database.setCursor(QCursor(Qt.IBeamCursor))
        self.lineEdit_database.setClearButtonEnabled(True)

        self.horizontalLayout_4.addWidget(self.lineEdit_database)

        self.toolButton_select_sqlite_file = QToolButton(self.groupBox)
        self.toolButton_select_sqlite_file.setObjectName(u"toolButton_select_sqlite_file")
        self.toolButton_select_sqlite_file.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.toolButton_select_sqlite_file.sizePolicy().hasHeightForWidth())
        self.toolButton_select_sqlite_file.setSizePolicy(sizePolicy1)
        self.toolButton_select_sqlite_file.setMinimumSize(QSize(22, 22))
        self.toolButton_select_sqlite_file.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_select_sqlite_file.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.toolButton_select_sqlite_file)


        self.gridLayout.addLayout(self.horizontalLayout_4, 6, 1, 1, 5)

        self.lineEdit_host = PropertyQLineEdit(self.groupBox)
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

        self.lineEdit_password = PropertyQLineEdit(self.groupBox)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy1)
        self.lineEdit_password.setMinimumSize(QSize(0, 24))
        self.lineEdit_password.setMaximumSize(QSize(5000, 24))
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_password, 3, 1, 1, 5)

        self.lineEdit_username = PropertyQLineEdit(self.groupBox)
        self.lineEdit_username.setObjectName(u"lineEdit_username")
        self.lineEdit_username.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.lineEdit_username.sizePolicy().hasHeightForWidth())
        self.lineEdit_username.setSizePolicy(sizePolicy1)
        self.lineEdit_username.setMinimumSize(QSize(0, 24))
        self.lineEdit_username.setMaximumSize(QSize(5000, 24))
        self.lineEdit_username.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_username, 2, 1, 1, 5)

        self.comboBox_dsn = QComboBox(self.groupBox)
        self.comboBox_dsn.setObjectName(u"comboBox_dsn")
        self.comboBox_dsn.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.comboBox_dsn.sizePolicy().hasHeightForWidth())
        self.comboBox_dsn.setSizePolicy(sizePolicy1)
        self.comboBox_dsn.setMinimumSize(QSize(0, 24))
        self.comboBox_dsn.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.comboBox_dsn, 1, 1, 1, 5)

        self.comboBox_dialect = QComboBox(self.groupBox)
        self.comboBox_dialect.setObjectName(u"comboBox_dialect")
        sizePolicy1.setHeightForWidth(self.comboBox_dialect.sizePolicy().hasHeightForWidth())
        self.comboBox_dialect.setSizePolicy(sizePolicy1)
        self.comboBox_dialect.setMinimumSize(QSize(0, 24))
        self.comboBox_dialect.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.comboBox_dialect, 0, 1, 1, 5)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.toolButton_vacuum = QPushButton(Form)
        self.toolButton_vacuum.setObjectName(u"toolButton_vacuum")
        icon1 = QIcon()
        icon1.addFile(u":/icons/broom.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_vacuum.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.toolButton_vacuum)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.toolButton_copy_url = QPushButton(Form)
        self.toolButton_copy_url.setObjectName(u"toolButton_copy_url")
        icon2 = QIcon()
        icon2.addFile(u":/icons/copy.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_copy_url.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.toolButton_copy_url)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

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
        icon3 = QIcon()
        icon3.addFile(u":/icons/Spine_symbol.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_create_new_spine_db.setIcon(icon3)

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
        QWidget.setTabOrder(self.toolButton_select_sqlite_file, self.toolButton_vacuum)
        QWidget.setTabOrder(self.toolButton_vacuum, self.toolButton_copy_url)
        QWidget.setTabOrder(self.toolButton_copy_url, self.pushButton_create_new_spine_db)
        QWidget.setTabOrder(self.pushButton_create_new_spine_db, self.pushButton_ds_open_editor)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"URL", None))
        self.label_dialect.setText(QCoreApplication.translate("Form", u"Dialect", None))
        self.lineEdit_port.setPlaceholderText("")
        self.label_dsn.setText(QCoreApplication.translate("Form", u"DSN", None))
        self.label_password.setText(QCoreApplication.translate("Form", u"Password", None))
        self.label_host.setText(QCoreApplication.translate("Form", u"Host", None))
        self.label_username.setText(QCoreApplication.translate("Form", u"Username", None))
        self.label_port.setText(QCoreApplication.translate("Form", u"Port", None))
        self.label_database.setText(QCoreApplication.translate("Form", u"Database", None))
        self.lineEdit_database.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.toolButton_select_sqlite_file.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select SQLite file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_host.setPlaceholderText("")
        self.lineEdit_password.setPlaceholderText("")
        self.lineEdit_username.setPlaceholderText("")
        self.toolButton_vacuum.setText(QCoreApplication.translate("Form", u"Vacuum", None))
#if QT_CONFIG(tooltip)
        self.toolButton_copy_url.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy current database url to clipboard.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_copy_url.setText(QCoreApplication.translate("Form", u"Copy URL", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_new_spine_db.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Create new Spine database at the selected URL, or at a default one if the selected is not valid.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_new_spine_db.setText(QCoreApplication.translate("Form", u"New Spine db", None))
#if QT_CONFIG(tooltip)
        self.pushButton_ds_open_editor.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open URL in Spine database editor</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_ds_open_editor.setText(QCoreApplication.translate("Form", u"Open editor...", None))
    # retranslateUi

