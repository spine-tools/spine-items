# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_notebook.ui'
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


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.setWindowModality(Qt.ApplicationModal)
        Form.resize(320, 278)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 0)
        self.lineEdit_name = QLineEdit(Form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_name.setSizePolicy(sizePolicy1)
        self.lineEdit_name.setMinimumSize(QSize(220, 20))
        self.lineEdit_name.setMaximumSize(QSize(5000, 20))
        self.lineEdit_name.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.lineEdit_name)

        self.lineEdit_description = QLineEdit(Form)
        self.lineEdit_description.setObjectName(u"lineEdit_description")
        sizePolicy1.setHeightForWidth(self.lineEdit_description.sizePolicy().hasHeightForWidth())
        self.lineEdit_description.setSizePolicy(sizePolicy1)
        self.lineEdit_description.setMinimumSize(QSize(220, 20))
        self.lineEdit_description.setMaximumSize(QSize(5000, 20))
        self.lineEdit_description.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.lineEdit_description)

        self.verticalSpacer = QSpacerItem(20, 72, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.comboBox_specification = QComboBox(Form)
        self.comboBox_specification.setObjectName(u"comboBox_specification")

        self.verticalLayout.addWidget(self.comboBox_specification)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_notebook_specification_args = QLineEdit(Form)
        self.lineEdit_notebook_specification_args.setObjectName(u"lineEdit_notebook_specification_args")
        self.lineEdit_notebook_specification_args.setEnabled(False)
        self.lineEdit_notebook_specification_args.setCursor(QCursor(Qt.ArrowCursor))
        self.lineEdit_notebook_specification_args.setFocusPolicy(Qt.NoFocus)
        self.lineEdit_notebook_specification_args.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineEdit_notebook_specification_args)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label_folder = QLabel(Form)
        self.label_folder.setObjectName(u"label_folder")
        self.label_folder.setEnabled(False)
        self.label_folder.setIndent(-1)

        self.verticalLayout.addWidget(self.label_folder)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 6, 0, 6)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_ok = QPushButton(Form)
        self.pushButton_ok.setObjectName(u"pushButton_ok")

        self.horizontalLayout_2.addWidget(self.pushButton_ok)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.pushButton_cancel = QPushButton(Form)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.horizontalLayout_2.addWidget(self.pushButton_cancel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_statusbar_placeholder = QHBoxLayout()
        self.horizontalLayout_statusbar_placeholder.setObjectName(u"horizontalLayout_statusbar_placeholder")
        self.horizontalLayout_statusbar_placeholder.setContentsMargins(-1, -1, -1, 0)
        self.widget_invisible_dummy = QWidget(Form)
        self.widget_invisible_dummy.setObjectName(u"widget_invisible_dummy")
        sizePolicy.setHeightForWidth(self.widget_invisible_dummy.sizePolicy().hasHeightForWidth())
        self.widget_invisible_dummy.setSizePolicy(sizePolicy)
        self.widget_invisible_dummy.setMinimumSize(QSize(0, 20))
        self.widget_invisible_dummy.setMaximumSize(QSize(0, 20))

        self.horizontalLayout_statusbar_placeholder.addWidget(self.widget_invisible_dummy)


        self.verticalLayout_2.addLayout(self.horizontalLayout_statusbar_placeholder)

        QWidget.setTabOrder(self.lineEdit_name, self.lineEdit_description)
        QWidget.setTabOrder(self.lineEdit_description, self.comboBox_specification)
        QWidget.setTabOrder(self.comboBox_specification, self.lineEdit_notebook_specification_args)
        QWidget.setTabOrder(self.lineEdit_notebook_specification_args, self.pushButton_ok)
        QWidget.setTabOrder(self.pushButton_ok, self.pushButton_cancel)

        self.retranslateUi(Form)

        self.pushButton_ok.setDefault(True)
        self.pushButton_cancel.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Add Notebook", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_name.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Item name (required)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("Form", u"Type item name here...", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_description.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Item description (optional)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_description.setPlaceholderText(QCoreApplication.translate("Form", u"Type item description here...", None))
        self.label.setText(QCoreApplication.translate("Form", u"Args", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_notebook_specification_args.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Command line arguments of the selected Notebook specification</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_folder.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Folder name that is created to project folder</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_folder.setText(QCoreApplication.translate("Form", u"Folder:", None))
        self.pushButton_ok.setText(QCoreApplication.translate("Form", u"Ok", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("Form", u"Cancel", None))
    # retranslateUi

