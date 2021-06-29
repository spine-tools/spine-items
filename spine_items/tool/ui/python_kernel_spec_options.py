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
## Form generated from reading UI file 'python_kernel_spec_options.ui'
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

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(506, 72)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 6, 0, 0)
        self.line_2 = QFrame(Form)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_python_path = QLineEdit(Form)
        self.lineEdit_python_path.setObjectName(u"lineEdit_python_path")
        self.lineEdit_python_path.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.lineEdit_python_path)

        self.toolButton_browse_python = QToolButton(Form)
        self.toolButton_browse_python.setObjectName(u"toolButton_browse_python")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_python.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButton_browse_python)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_jupyter_console = QCheckBox(Form)
        self.checkBox_jupyter_console.setObjectName(u"checkBox_jupyter_console")

        self.horizontalLayout.addWidget(self.checkBox_jupyter_console)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)

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

        self.pushButton_open_kernel_spec_viewer = QPushButton(Form)
        self.pushButton_open_kernel_spec_viewer.setObjectName(u"pushButton_open_kernel_spec_viewer")

        self.horizontalLayout.addWidget(self.pushButton_open_kernel_spec_viewer)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        self.label_2.setText(QCoreApplication.translate("Form", u"Interpreter", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_python_path.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Python interpreter for executing this Tool specification. Leave empty to select the Python that was used in launching Spine Toolbox.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_python_path.setPlaceholderText(QCoreApplication.translate("Form", u"Using current Python interpreter", None))
#if QT_CONFIG(tooltip)
        self.toolButton_browse_python.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Pick a Python interpreter using a file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_jupyter_console.setText(QCoreApplication.translate("Form", u"Jupyter Console", None))
        self.label.setText(QCoreApplication.translate("Form", u"Kernel spec", None))
#if QT_CONFIG(tooltip)
        self.comboBox_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a Python Jupyter kernel spec for Jupyter Console.</p><p>Both Conda and Jupyter kernel specs are shown.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_refresh_kernel_specs.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Create Julia sysimage for this Tool</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_refresh_kernel_specs.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_open_kernel_spec_viewer.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Opens a kernel spec editor/viewer</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_open_kernel_spec_viewer.setText(QCoreApplication.translate("Form", u"View/Edit kernel specs", None))
        pass
    # retranslateUi

