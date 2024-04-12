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
## Form generated from reading UI file 'python_kernel_spec_options.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QRadioButton, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget)
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(527, 73)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.line_3 = QFrame(Form)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, 6, -1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(6, -1, -1, -1)
        self.radioButton_basic_console = QRadioButton(Form)
        self.radioButton_basic_console.setObjectName(u"radioButton_basic_console")
        self.radioButton_basic_console.setChecked(True)

        self.verticalLayout.addWidget(self.radioButton_basic_console)

        self.radioButton_jupyter_console = QRadioButton(Form)
        self.radioButton_jupyter_console.setObjectName(u"radioButton_jupyter_console")

        self.verticalLayout.addWidget(self.radioButton_jupyter_console)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(6, -1, -1, -1)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_executable = QLineEdit(Form)
        self.lineEdit_executable.setObjectName(u"lineEdit_executable")
        self.lineEdit_executable.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.lineEdit_executable)

        self.toolButton_browse_python = QToolButton(Form)
        self.toolButton_browse_python.setObjectName(u"toolButton_browse_python")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_python.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_python)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(6, -1, -1, -1)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboBox_kernel_specs = QComboBox(Form)
        self.comboBox_kernel_specs.setObjectName(u"comboBox_kernel_specs")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_kernel_specs.sizePolicy().hasHeightForWidth())
        self.comboBox_kernel_specs.setSizePolicy(sizePolicy)
        self.comboBox_kernel_specs.setMinimumSize(QSize(100, 24))
        self.comboBox_kernel_specs.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout.addWidget(self.comboBox_kernel_specs)

        self.toolButton_refresh_kernel_specs = QToolButton(Form)
        self.toolButton_refresh_kernel_specs.setObjectName(u"toolButton_refresh_kernel_specs")
        icon1 = QIcon()
        icon1.addFile(u":/icons/sync.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_refresh_kernel_specs.setIcon(icon1)
        self.toolButton_refresh_kernel_specs.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.horizontalLayout.addWidget(self.toolButton_refresh_kernel_specs)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        self.radioButton_basic_console.setText(QCoreApplication.translate("Form", u"Basic Console", None))
        self.radioButton_jupyter_console.setText(QCoreApplication.translate("Form", u"Jupyter Console", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Interpreter:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_executable.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Python interpreter for <span style=\" font-weight:700;\">Basic Console</span> execution. Leave empty to use the Python that was used in launching Spine Toolbox.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_executable.setPlaceholderText(QCoreApplication.translate("Form", u"Using current Python interpreter", None))
#if QT_CONFIG(tooltip)
        self.toolButton_browse_python.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Python interpreter using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("Form", u"Kernel:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a Python kernel for <span style=\" font-weight:700;\">Jupyter Console</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_refresh_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Refresh kernel specs list</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_refresh_kernel_specs.setText("")
        pass
    # retranslateUi

