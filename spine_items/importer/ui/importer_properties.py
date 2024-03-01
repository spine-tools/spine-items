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
## Form generated from reading UI file 'importer_properties.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QRadioButton,
    QSizePolicy, QToolButton, QTreeView, QVBoxLayout,
    QWidget)
from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(375, 368)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_specification = QLabel(Form)
        self.label_specification.setObjectName(u"label_specification")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_specification.sizePolicy().hasHeightForWidth())
        self.label_specification.setSizePolicy(sizePolicy)
        self.label_specification.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_9.addWidget(self.label_specification)

        self.comboBox_specification = QComboBox(Form)
        self.comboBox_specification.setObjectName(u"comboBox_specification")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_specification.sizePolicy().hasHeightForWidth())
        self.comboBox_specification.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.comboBox_specification)

        self.toolButton_edit_specification = QToolButton(Form)
        self.toolButton_edit_specification.setObjectName(u"toolButton_edit_specification")
        icon = QIcon()
        icon.addFile(u":/icons/wrench.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_edit_specification.setIcon(icon)
        self.toolButton_edit_specification.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_9.addWidget(self.toolButton_edit_specification)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.treeView_files = QTreeView(Form)
        self.treeView_files.setObjectName(u"treeView_files")
        self.treeView_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView_files.setTextElideMode(Qt.ElideLeft)
        self.treeView_files.setUniformRowHeights(True)

        self.verticalLayout.addWidget(self.treeView_files)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.cancel_on_error_checkBox = QCheckBox(self.frame)
        self.cancel_on_error_checkBox.setObjectName(u"cancel_on_error_checkBox")
        self.cancel_on_error_checkBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.cancel_on_error_checkBox)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radioButton_on_conflict_keep = QRadioButton(self.frame)
        self.radioButton_on_conflict_keep.setObjectName(u"radioButton_on_conflict_keep")

        self.horizontalLayout.addWidget(self.radioButton_on_conflict_keep)

        self.radioButton_on_conflict_replace = QRadioButton(self.frame)
        self.radioButton_on_conflict_replace.setObjectName(u"radioButton_on_conflict_replace")

        self.horizontalLayout.addWidget(self.radioButton_on_conflict_replace)

        self.radioButton_on_conflict_merge = QRadioButton(self.frame)
        self.radioButton_on_conflict_merge.setObjectName(u"radioButton_on_conflict_merge")

        self.horizontalLayout.addWidget(self.radioButton_on_conflict_merge)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.frame)

        QWidget.setTabOrder(self.comboBox_specification, self.toolButton_edit_specification)
        QWidget.setTabOrder(self.toolButton_edit_specification, self.treeView_files)
        QWidget.setTabOrder(self.treeView_files, self.cancel_on_error_checkBox)
        QWidget.setTabOrder(self.cancel_on_error_checkBox, self.radioButton_on_conflict_keep)
        QWidget.setTabOrder(self.radioButton_on_conflict_keep, self.radioButton_on_conflict_replace)
        QWidget.setTabOrder(self.radioButton_on_conflict_replace, self.radioButton_on_conflict_merge)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_specification.setText(QCoreApplication.translate("Form", u"Specification:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_specification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Specification for this Importer</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_edit_specification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Edit specification.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cancel_on_error_checkBox.setToolTip(QCoreApplication.translate("Form", u"If there are any errors when trying to import data cancel the whole import.", None))
#endif // QT_CONFIG(tooltip)
        self.cancel_on_error_checkBox.setText(QCoreApplication.translate("Form", u"Cancel import on error", None))
        self.label.setText(QCoreApplication.translate("Form", u"If values already exist", None))
        self.radioButton_on_conflict_keep.setText(QCoreApplication.translate("Form", u"Keep existing", None))
        self.radioButton_on_conflict_replace.setText(QCoreApplication.translate("Form", u"Replace", None))
        self.radioButton_on_conflict_merge.setText(QCoreApplication.translate("Form", u"Merge indexes", None))
    # retranslateUi

