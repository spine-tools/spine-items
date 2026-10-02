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
## Form generated from reading UI file 'python_tool_options.ui'
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
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(568, 138)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.line_3 = QFrame(Form)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.comboBox_python_execution_method = QComboBox(Form)
        self.comboBox_python_execution_method.setObjectName(u"comboBox_python_execution_method")

        self.horizontalLayout_3.addWidget(self.comboBox_python_execution_method)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.stackedWidget_python_options = QStackedWidget(Form)
        self.stackedWidget_python_options.setObjectName(u"stackedWidget_python_options")
        self.page_0 = QWidget()
        self.page_0.setObjectName(u"page_0")
        self.verticalLayout_4 = QVBoxLayout(self.page_0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_execution_method = QLabel(self.page_0)
        self.label_execution_method.setObjectName(u"label_execution_method")

        self.verticalLayout_4.addWidget(self.label_execution_method)

        self.label_interpreter_or_kernel = QLabel(self.page_0)
        self.label_interpreter_or_kernel.setObjectName(u"label_interpreter_or_kernel")

        self.verticalLayout_4.addWidget(self.label_interpreter_or_kernel)

        self.stackedWidget_python_options.addWidget(self.page_0)
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.verticalLayout = QVBoxLayout(self.page_1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.page_1)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.comboBox_executable = QComboBox(self.page_1)
        self.comboBox_executable.setObjectName(u"comboBox_executable")

        self.horizontalLayout_2.addWidget(self.comboBox_executable)

        self.toolButton_browse_python = QToolButton(self.page_1)
        self.toolButton_browse_python.setObjectName(u"toolButton_browse_python")
        icon = QIcon()
        icon.addFile(u":/icons/item_icons/python-logo.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_browse_python.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_python)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.stackedWidget_python_options.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_2 = QVBoxLayout(self.page_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.page_2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.comboBox_kernel_specs = QComboBox(self.page_2)
        self.comboBox_kernel_specs.setObjectName(u"comboBox_kernel_specs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_kernel_specs.sizePolicy().hasHeightForWidth())
        self.comboBox_kernel_specs.setSizePolicy(sizePolicy)
        self.comboBox_kernel_specs.setMinimumSize(QSize(100, 24))
        self.comboBox_kernel_specs.setMaximumSize(QSize(16777215, 24))

        self.verticalLayout_2.addWidget(self.comboBox_kernel_specs)

        self.stackedWidget_python_options.addWidget(self.page_2)

        self.verticalLayout_3.addWidget(self.stackedWidget_python_options)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line)


        self.retranslateUi(Form)

        self.stackedWidget_python_options.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        self.label.setText(QCoreApplication.translate("Form", u"Execution method", None))
        self.label_execution_method.setText(QCoreApplication.translate("Form", u"execution mode placeholder", None))
        self.label_interpreter_or_kernel.setText(QCoreApplication.translate("Form", u"interpreter or kernel name placeholder", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Python interpreter", None))
#if QT_CONFIG(tooltip)
        self.toolButton_browse_python.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Python interpreter using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("Form", u"Jupyter kernel", None))
#if QT_CONFIG(tooltip)
        self.comboBox_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a Python kernel for <span style=\" font-weight:700;\">Jupyter Console</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

