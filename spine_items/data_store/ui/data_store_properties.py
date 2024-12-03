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
## Form generated from reading UI file 'data_store_properties.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from spine_items.widgets import UrlSelectorWidget
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(369, 337)
        Form.setStyleSheet(u"QScrollArea { background: transparent; }\n"
"QScrollArea > QWidget > QWidget { background: transparent; }")
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 369, 337))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.url_selector_widget = UrlSelectorWidget(self.groupBox)
        self.url_selector_widget.setObjectName(u"url_selector_widget")

        self.verticalLayout_2.addWidget(self.url_selector_widget)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.purge_button = QPushButton(self.scrollAreaWidgetContents)
        self.purge_button.setObjectName(u"purge_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.purge_button.sizePolicy().hasHeightForWidth())
        self.purge_button.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/icons/bolt-lightning.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.purge_button.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.purge_button)

        self.toolButton_vacuum = QPushButton(self.scrollAreaWidgetContents)
        self.toolButton_vacuum.setObjectName(u"toolButton_vacuum")
        icon1 = QIcon()
        icon1.addFile(u":/icons/broom.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_vacuum.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.toolButton_vacuum)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.toolButton_copy_url = QPushButton(self.scrollAreaWidgetContents)
        self.toolButton_copy_url.setObjectName(u"toolButton_copy_url")
        icon2 = QIcon()
        icon2.addFile(u":/icons/copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_copy_url.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.toolButton_copy_url)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_2 = QSpacerItem(20, 228, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_create_new_spine_db = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_create_new_spine_db.setObjectName(u"pushButton_create_new_spine_db")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_create_new_spine_db.sizePolicy().hasHeightForWidth())
        self.pushButton_create_new_spine_db.setSizePolicy(sizePolicy1)
        icon3 = QIcon()
        icon3.addFile(u":/icons/Spine_symbol.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_create_new_spine_db.setIcon(icon3)

        self.horizontalLayout.addWidget(self.pushButton_create_new_spine_db)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_ds_open_editor = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_ds_open_editor.setObjectName(u"pushButton_ds_open_editor")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_ds_open_editor.sizePolicy().hasHeightForWidth())
        self.pushButton_ds_open_editor.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pushButton_ds_open_editor)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.purge_button, self.toolButton_vacuum)
        QWidget.setTabOrder(self.toolButton_vacuum, self.toolButton_copy_url)
        QWidget.setTabOrder(self.toolButton_copy_url, self.pushButton_create_new_spine_db)
        QWidget.setTabOrder(self.pushButton_create_new_spine_db, self.pushButton_ds_open_editor)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"URL", None))
#if QT_CONFIG(tooltip)
        self.purge_button.setToolTip(QCoreApplication.translate("Form", u"Mass remove database items.", None))
#endif // QT_CONFIG(tooltip)
        self.purge_button.setText(QCoreApplication.translate("Form", u"Purge...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_vacuum.setToolTip(QCoreApplication.translate("Form", u"Remove outdated data from the database potentially freeing disk space.", None))
#endif // QT_CONFIG(tooltip)
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

