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
## Created by: Qt User Interface Compiler version 6.11.1
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
    QLabel, QSizePolicy, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget)

from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(547, 190)
        self.verticalLayout_4 = QVBoxLayout(Form)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.line_3 = QFrame(Form)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line_3)

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


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboBox_julia_execution_method = QComboBox(Form)
        self.comboBox_julia_execution_method.setObjectName(u"comboBox_julia_execution_method")

        self.horizontalLayout.addWidget(self.comboBox_julia_execution_method)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.stackedWidget_julia_options = QStackedWidget(Form)
        self.stackedWidget_julia_options.setObjectName(u"stackedWidget_julia_options")
        self.page_0 = QWidget()
        self.page_0.setObjectName(u"page_0")
        self.verticalLayout = QVBoxLayout(self.page_0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_execution_method = QLabel(self.page_0)
        self.label_execution_method.setObjectName(u"label_execution_method")

        self.verticalLayout.addWidget(self.label_execution_method)

        self.label_executable_or_kernel = QLabel(self.page_0)
        self.label_executable_or_kernel.setObjectName(u"label_executable_or_kernel")

        self.verticalLayout.addWidget(self.label_executable_or_kernel)

        self.label_environment = QLabel(self.page_0)
        self.label_environment.setObjectName(u"label_environment")

        self.verticalLayout.addWidget(self.label_environment)

        self.stackedWidget_julia_options.addWidget(self.page_0)
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.verticalLayout_2 = QVBoxLayout(self.page_1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.comboBox_executable = QComboBox(self.page_1)
        self.comboBox_executable.setObjectName(u"comboBox_executable")

        self.horizontalLayout_2.addWidget(self.comboBox_executable)

        self.toolButton_browse_julia = QToolButton(self.page_1)
        self.toolButton_browse_julia.setObjectName(u"toolButton_browse_julia")
        icon2 = QIcon()
        icon2.addFile(u":/icons/item_icons/julia-logo.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_julia.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_julia)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.comboBox_julia_project = QComboBox(self.page_1)
        self.comboBox_julia_project.setObjectName(u"comboBox_julia_project")

        self.horizontalLayout_4.addWidget(self.comboBox_julia_project)

        self.toolButton_browse_julia_project = QToolButton(self.page_1)
        self.toolButton_browse_julia_project.setObjectName(u"toolButton_browse_julia_project")
        icon3 = QIcon()
        icon3.addFile(u":/icons/folder.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_julia_project.setIcon(icon3)

        self.horizontalLayout_4.addWidget(self.toolButton_browse_julia_project)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.stackedWidget_julia_options.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.comboBox_kernel_specs = QComboBox(self.page_2)
        self.comboBox_kernel_specs.setObjectName(u"comboBox_kernel_specs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_kernel_specs.sizePolicy().hasHeightForWidth())
        self.comboBox_kernel_specs.setSizePolicy(sizePolicy)
        self.comboBox_kernel_specs.setMinimumSize(QSize(100, 24))
        self.comboBox_kernel_specs.setMaximumSize(QSize(16777215, 24))

        self.verticalLayout_3.addWidget(self.comboBox_kernel_specs)

        self.stackedWidget_julia_options.addWidget(self.page_2)

        self.verticalLayout_4.addWidget(self.stackedWidget_julia_options)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        QWidget.setTabOrder(self.lineEdit_sysimage, self.toolButton_abort_sysimage)
        QWidget.setTabOrder(self.toolButton_abort_sysimage, self.toolButton_new_sysimage)
        QWidget.setTabOrder(self.toolButton_new_sysimage, self.toolButton_open_sysimage)
        QWidget.setTabOrder(self.toolButton_open_sysimage, self.comboBox_julia_execution_method)
        QWidget.setTabOrder(self.comboBox_julia_execution_method, self.comboBox_executable)
        QWidget.setTabOrder(self.comboBox_executable, self.toolButton_browse_julia)
        QWidget.setTabOrder(self.toolButton_browse_julia, self.comboBox_julia_project)
        QWidget.setTabOrder(self.comboBox_julia_project, self.toolButton_browse_julia_project)
        QWidget.setTabOrder(self.toolButton_browse_julia_project, self.comboBox_kernel_specs)

        self.retranslateUi(Form)

        self.stackedWidget_julia_options.setCurrentIndex(0)


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
        self.label.setText(QCoreApplication.translate("Form", u"Execution method", None))
        self.label_execution_method.setText(QCoreApplication.translate("Form", u"Execution mode placeholder", None))
        self.label_executable_or_kernel.setText(QCoreApplication.translate("Form", u"executable or kernel name placeholder", None))
        self.label_environment.setText(QCoreApplication.translate("Form", u"environment placeholder", None))
#if QT_CONFIG(tooltip)
        self.toolButton_browse_julia.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Julia executable using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_browse_julia_project.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Julia project using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBox_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a Julia kernel for <span style=\" font-weight:700;\">Jupyter Console</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

