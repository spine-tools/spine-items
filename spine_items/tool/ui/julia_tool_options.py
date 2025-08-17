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
## Form generated from reading UI file 'julia_tool_options.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QRadioButton, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(536, 171)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.line_3 = QFrame(Form)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_sysimage = QLabel(Form)
        self.label_sysimage.setObjectName(u"label_sysimage")

        self.horizontalLayout_3.addWidget(self.label_sysimage)

        self.lineEdit_sysimage = PropertyQLineEdit(Form)
        self.lineEdit_sysimage.setObjectName(u"lineEdit_sysimage")
        self.lineEdit_sysimage.setMaximumSize(QSize(16777215, 24))
        self.lineEdit_sysimage.setReadOnly(False)
        self.lineEdit_sysimage.setClearButtonEnabled(True)

        self.horizontalLayout_3.addWidget(self.lineEdit_sysimage)

        self.toolButton_abort_sysimage = QToolButton(Form)
        self.toolButton_abort_sysimage.setObjectName(u"toolButton_abort_sysimage")

        self.horizontalLayout_3.addWidget(self.toolButton_abort_sysimage)

        self.toolButton_new_sysimage = QToolButton(Form)
        self.toolButton_new_sysimage.setObjectName(u"toolButton_new_sysimage")
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_new_sysimage.setIcon(icon)
        self.toolButton_new_sysimage.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.horizontalLayout_3.addWidget(self.toolButton_new_sysimage)

        self.toolButton_open_sysimage = QToolButton(Form)
        self.toolButton_open_sysimage.setObjectName(u"toolButton_open_sysimage")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_open_sysimage.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.toolButton_open_sysimage)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.radioButton_basic_console = QRadioButton(Form)
        self.radioButton_basic_console.setObjectName(u"radioButton_basic_console")
        self.radioButton_basic_console.setChecked(True)

        self.verticalLayout.addWidget(self.radioButton_basic_console)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.comboBox_executable = QComboBox(Form)
        self.comboBox_executable.setObjectName(u"comboBox_executable")

        self.horizontalLayout_2.addWidget(self.comboBox_executable)

        self.toolButton_browse_julia = QToolButton(Form)
        self.toolButton_browse_julia.setObjectName(u"toolButton_browse_julia")
        icon2 = QIcon()
        icon2.addFile(u":/icons/item_icons/julia-logo.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_julia.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_julia)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.comboBox_julia_project = QComboBox(Form)
        self.comboBox_julia_project.setObjectName(u"comboBox_julia_project")

        self.horizontalLayout_4.addWidget(self.comboBox_julia_project)

        self.toolButton_browse_julia_project = QToolButton(Form)
        self.toolButton_browse_julia_project.setObjectName(u"toolButton_browse_julia_project")
        icon3 = QIcon()
        icon3.addFile(u":/icons/folder.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_julia_project.setIcon(icon3)

        self.horizontalLayout_4.addWidget(self.toolButton_browse_julia_project)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.radioButton_jupyter_console = QRadioButton(Form)
        self.radioButton_jupyter_console.setObjectName(u"radioButton_jupyter_console")

        self.verticalLayout.addWidget(self.radioButton_jupyter_console)

        self.comboBox_kernel_specs = QComboBox(Form)
        self.comboBox_kernel_specs.setObjectName(u"comboBox_kernel_specs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_kernel_specs.sizePolicy().hasHeightForWidth())
        self.comboBox_kernel_specs.setSizePolicy(sizePolicy)
        self.comboBox_kernel_specs.setMinimumSize(QSize(100, 24))
        self.comboBox_kernel_specs.setMaximumSize(QSize(16777215, 24))

        self.verticalLayout.addWidget(self.comboBox_kernel_specs)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        QWidget.setTabOrder(self.radioButton_basic_console, self.radioButton_jupyter_console)
        QWidget.setTabOrder(self.radioButton_jupyter_console, self.toolButton_browse_julia)
        QWidget.setTabOrder(self.toolButton_browse_julia, self.toolButton_browse_julia_project)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        self.label_sysimage.setText(QCoreApplication.translate("Form", u"Sysimage:", None))
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
        self.radioButton_basic_console.setText(QCoreApplication.translate("Form", u"Use Julia executable / Julia project", None))
#if QT_CONFIG(tooltip)
        self.toolButton_browse_julia.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Julia executable using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_browse_julia_project.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Julia project using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.radioButton_jupyter_console.setText(QCoreApplication.translate("Form", u"Use Jupyter kernel", None))
#if QT_CONFIG(tooltip)
        self.comboBox_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a Julia kernel for <span style=\" font-weight:700;\">Jupyter Console</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

