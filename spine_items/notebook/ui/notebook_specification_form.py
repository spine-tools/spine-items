# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'notebook_specification_form.ui'
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

from spinetoolbox.widgets.custom_qlineedits import CustomQLineEdit
from spinetoolbox.widgets.custom_qtreeview import CustomTreeView
from spinetoolbox.widgets.custom_qtreeview import SourcesTreeView
from spine_items.notebook.widgets.jupyter_notebook_text_edit import JupyterNotebookTextEdit

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.setWindowModality(Qt.ApplicationModal)
        Form.resize(600, 997)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_6 = QVBoxLayout(Form)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setSpacing(6)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_name = QLineEdit(Form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_name.setSizePolicy(sizePolicy1)
        self.lineEdit_name.setMinimumSize(QSize(220, 24))
        self.lineEdit_name.setMaximumSize(QSize(5000, 24))
        self.lineEdit_name.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.lineEdit_name)

        self.comboBox_notebook_type = QComboBox(Form)
        self.comboBox_notebook_type.setObjectName(u"comboBox_notebook_type")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox_notebook_type.sizePolicy().hasHeightForWidth())
        self.comboBox_notebook_type.setSizePolicy(sizePolicy2)
        self.comboBox_notebook_type.setMinimumSize(QSize(180, 24))
        self.comboBox_notebook_type.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout.addWidget(self.comboBox_notebook_type)


        self.verticalLayout_11.addLayout(self.horizontalLayout)

        self.textEdit_description = QTextEdit(Form)
        self.textEdit_description.setObjectName(u"textEdit_description")
        self.textEdit_description.setMaximumSize(QSize(16777215, 80))
        self.textEdit_description.setFocusPolicy(Qt.StrongFocus)
        self.textEdit_description.setTabChangesFocus(True)

        self.verticalLayout_11.addWidget(self.textEdit_description)

        self.checkBox_execute_in_work = QCheckBox(Form)
        self.checkBox_execute_in_work.setObjectName(u"checkBox_execute_in_work")
        self.checkBox_execute_in_work.setChecked(True)

        self.verticalLayout_11.addWidget(self.checkBox_execute_in_work)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_Jupyter_notebook = CustomQLineEdit(Form)
        self.lineEdit_Jupyter_notebook.setObjectName(u"lineEdit_Jupyter_notebook")
        self.lineEdit_Jupyter_notebook.setClearButtonEnabled(True)

        self.horizontalLayout_6.addWidget(self.lineEdit_Jupyter_notebook)

        self.toolButton_new_jupyter_notebook = QToolButton(Form)
        self.toolButton_new_jupyter_notebook.setObjectName(u"toolButton_new_jupyter_notebook")
        self.toolButton_new_jupyter_notebook.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_new_jupyter_notebook.setIcon(icon)
        self.toolButton_new_jupyter_notebook.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_6.addWidget(self.toolButton_new_jupyter_notebook)

        self.toolButton_browse_jupyter_notebook = QToolButton(Form)
        self.toolButton_browse_jupyter_notebook.setObjectName(u"toolButton_browse_jupyter_notebook")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_browse_jupyter_notebook.setIcon(icon1)

        self.horizontalLayout_6.addWidget(self.toolButton_browse_jupyter_notebook)


        self.verticalLayout_11.addLayout(self.horizontalLayout_6)


        self.verticalLayout_5.addLayout(self.verticalLayout_11)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.widget_main_program = QWidget(self.splitter)
        self.widget_main_program.setObjectName(u"widget_main_program")
        self.verticalLayout_2 = QVBoxLayout(self.widget_main_program)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textEdit_jupyter_notebook = JupyterNotebookTextEdit(self.widget_main_program)
        self.textEdit_jupyter_notebook.setObjectName(u"textEdit_jupyter_notebook")
        self.textEdit_jupyter_notebook.setEnabled(True)

        self.verticalLayout_2.addWidget(self.textEdit_jupyter_notebook)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 2, -1, 2)
        self.label = QLabel(self.widget_main_program)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)

        self.horizontalLayout_7.addWidget(self.label)

        self.label_mainpath = QLabel(self.widget_main_program)
        self.label_mainpath.setObjectName(u"label_mainpath")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_mainpath.sizePolicy().hasHeightForWidth())
        self.label_mainpath.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(True)
        font1.setWeight(75)
        self.label_mainpath.setFont(font1)

        self.horizontalLayout_7.addWidget(self.label_mainpath)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_4)

        self.toolButton_save_jupyter_notebook = QToolButton(self.widget_main_program)
        self.toolButton_save_jupyter_notebook.setObjectName(u"toolButton_save_jupyter_notebook")
        self.toolButton_save_jupyter_notebook.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/icons/save.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_save_jupyter_notebook.setIcon(icon2)

        self.horizontalLayout_7.addWidget(self.toolButton_save_jupyter_notebook)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.splitter.addWidget(self.widget_main_program)
        self.widget_2 = QWidget(self.splitter)
        self.widget_2.setObjectName(u"widget_2")
        self.gridLayout_3 = QGridLayout(self.widget_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.treeView_input_vars = CustomTreeView(self.widget_2)
        self.treeView_input_vars.setObjectName(u"treeView_input_vars")
        self.treeView_input_vars.setMaximumSize(QSize(16777215, 500))
        font2 = QFont()
        font2.setPointSize(10)
        self.treeView_input_vars.setFont(font2)
        self.treeView_input_vars.setFocusPolicy(Qt.StrongFocus)
        self.treeView_input_vars.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_input_vars.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_input_vars.setIndentation(5)

        self.verticalLayout_3.addWidget(self.treeView_input_vars)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButton_plus_input_vars = QToolButton(self.widget_2)
        self.toolButton_plus_input_vars.setObjectName(u"toolButton_plus_input_vars")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.toolButton_plus_input_vars.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_input_vars.setSizePolicy(sizePolicy4)
        self.toolButton_plus_input_vars.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_input_vars.setMaximumSize(QSize(22, 22))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        font3.setWeight(75)
        self.toolButton_plus_input_vars.setFont(font3)
        icon3 = QIcon()
        icon3.addFile(u":/icons/file-link.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_plus_input_vars.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.toolButton_plus_input_vars)

        self.toolButton_minus_input_vars = QToolButton(self.widget_2)
        self.toolButton_minus_input_vars.setObjectName(u"toolButton_minus_input_vars")
        sizePolicy4.setHeightForWidth(self.toolButton_minus_input_vars.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_input_vars.setSizePolicy(sizePolicy4)
        self.toolButton_minus_input_vars.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_input_vars.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_input_vars.setFont(font3)
        icon4 = QIcon()
        icon4.addFile(u":/icons/trash-alt.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_minus_input_vars.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.toolButton_minus_input_vars)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_9)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.gridLayout_3.addLayout(self.verticalLayout_3, 1, 0, 1, 1)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setSpacing(6)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.treeView_output_vars = CustomTreeView(self.widget_2)
        self.treeView_output_vars.setObjectName(u"treeView_output_vars")
        self.treeView_output_vars.setMaximumSize(QSize(16777215, 500))
        self.treeView_output_vars.setFont(font2)
        self.treeView_output_vars.setFocusPolicy(Qt.StrongFocus)
        self.treeView_output_vars.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_output_vars.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_output_vars.setIndentation(5)

        self.verticalLayout_15.addWidget(self.treeView_output_vars)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.toolButton_plus_output_vars = QToolButton(self.widget_2)
        self.toolButton_plus_output_vars.setObjectName(u"toolButton_plus_output_vars")
        sizePolicy4.setHeightForWidth(self.toolButton_plus_output_vars.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_output_vars.setSizePolicy(sizePolicy4)
        self.toolButton_plus_output_vars.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_output_vars.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_output_vars.setFont(font3)
        self.toolButton_plus_output_vars.setIcon(icon3)

        self.horizontalLayout_5.addWidget(self.toolButton_plus_output_vars)

        self.toolButton_minus_output_vars = QToolButton(self.widget_2)
        self.toolButton_minus_output_vars.setObjectName(u"toolButton_minus_output_vars")
        sizePolicy4.setHeightForWidth(self.toolButton_minus_output_vars.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_output_vars.setSizePolicy(sizePolicy4)
        self.toolButton_minus_output_vars.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_output_vars.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_output_vars.setFont(font3)
        self.toolButton_minus_output_vars.setIcon(icon4)

        self.horizontalLayout_5.addWidget(self.toolButton_minus_output_vars)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)


        self.verticalLayout_15.addLayout(self.horizontalLayout_5)


        self.gridLayout_3.addLayout(self.verticalLayout_15, 2, 0, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.treeView_input_files = CustomTreeView(self.widget_2)
        self.treeView_input_files.setObjectName(u"treeView_input_files")
        sizePolicy3.setHeightForWidth(self.treeView_input_files.sizePolicy().hasHeightForWidth())
        self.treeView_input_files.setSizePolicy(sizePolicy3)
        self.treeView_input_files.setMaximumSize(QSize(16777215, 500))
        self.treeView_input_files.setFont(font2)
        self.treeView_input_files.setFocusPolicy(Qt.StrongFocus)
        self.treeView_input_files.setLineWidth(1)
        self.treeView_input_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_input_files.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_input_files.setIndentation(5)
        self.treeView_input_files.setUniformRowHeights(False)

        self.verticalLayout_4.addWidget(self.treeView_input_files)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.toolButton_plus_input_files = QToolButton(self.widget_2)
        self.toolButton_plus_input_files.setObjectName(u"toolButton_plus_input_files")
        sizePolicy4.setHeightForWidth(self.toolButton_plus_input_files.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_input_files.setSizePolicy(sizePolicy4)
        self.toolButton_plus_input_files.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_input_files.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_input_files.setFont(font3)
        self.toolButton_plus_input_files.setIcon(icon3)

        self.horizontalLayout_4.addWidget(self.toolButton_plus_input_files)

        self.toolButton_minus_input_files = QToolButton(self.widget_2)
        self.toolButton_minus_input_files.setObjectName(u"toolButton_minus_input_files")
        sizePolicy4.setHeightForWidth(self.toolButton_minus_input_files.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_input_files.setSizePolicy(sizePolicy4)
        self.toolButton_minus_input_files.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_input_files.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_input_files.setFont(font3)
        self.toolButton_minus_input_files.setIcon(icon4)

        self.horizontalLayout_4.addWidget(self.toolButton_minus_input_files)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)


        self.gridLayout_3.addLayout(self.verticalLayout_4, 1, 1, 1, 1)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setSpacing(6)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.treeView_output_files = CustomTreeView(self.widget_2)
        self.treeView_output_files.setObjectName(u"treeView_output_files")
        self.treeView_output_files.setMaximumSize(QSize(16777215, 500))
        self.treeView_output_files.setFont(font2)
        self.treeView_output_files.setFocusPolicy(Qt.WheelFocus)
        self.treeView_output_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_output_files.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_output_files.setIndentation(5)

        self.verticalLayout_16.addWidget(self.treeView_output_files)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.toolButton_plus_output_files = QToolButton(self.widget_2)
        self.toolButton_plus_output_files.setObjectName(u"toolButton_plus_output_files")
        sizePolicy4.setHeightForWidth(self.toolButton_plus_output_files.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_output_files.setSizePolicy(sizePolicy4)
        self.toolButton_plus_output_files.setMinimumSize(QSize(22, 22))
        self.toolButton_plus_output_files.setMaximumSize(QSize(22, 22))
        self.toolButton_plus_output_files.setFont(font3)
        self.toolButton_plus_output_files.setIcon(icon3)

        self.horizontalLayout_3.addWidget(self.toolButton_plus_output_files)

        self.toolButton_minus_output_files = QToolButton(self.widget_2)
        self.toolButton_minus_output_files.setObjectName(u"toolButton_minus_output_files")
        sizePolicy4.setHeightForWidth(self.toolButton_minus_output_files.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_output_files.setSizePolicy(sizePolicy4)
        self.toolButton_minus_output_files.setMinimumSize(QSize(22, 22))
        self.toolButton_minus_output_files.setMaximumSize(QSize(22, 22))
        self.toolButton_minus_output_files.setFont(font3)
        self.toolButton_minus_output_files.setIcon(icon4)

        self.horizontalLayout_3.addWidget(self.toolButton_minus_output_files)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_13)


        self.verticalLayout_16.addLayout(self.horizontalLayout_3)


        self.gridLayout_3.addLayout(self.verticalLayout_16, 2, 1, 1, 1)

        self.lineEdit_args = QLineEdit(self.widget_2)
        self.lineEdit_args.setObjectName(u"lineEdit_args")
        sizePolicy1.setHeightForWidth(self.lineEdit_args.sizePolicy().hasHeightForWidth())
        self.lineEdit_args.setSizePolicy(sizePolicy1)
        self.lineEdit_args.setMinimumSize(QSize(220, 24))
        self.lineEdit_args.setMaximumSize(QSize(5000, 24))
        self.lineEdit_args.setClearButtonEnabled(True)

        self.gridLayout_3.addWidget(self.lineEdit_args, 0, 0, 1, 2)

        self.splitter.addWidget(self.widget_2)

        self.verticalLayout_5.addWidget(self.splitter)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(9, 9, 9, 9)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.pushButton_ok = QPushButton(Form)
        self.pushButton_ok.setObjectName(u"pushButton_ok")

        self.horizontalLayout_8.addWidget(self.pushButton_ok)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.pushButton_cancel = QPushButton(Form)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.horizontalLayout_8.addWidget(self.pushButton_cancel)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)


        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        self.horizontalLayout_statusbar_placeholder = QHBoxLayout()
        self.horizontalLayout_statusbar_placeholder.setObjectName(u"horizontalLayout_statusbar_placeholder")
        self.widget_invisible_dummy = QWidget(Form)
        self.widget_invisible_dummy.setObjectName(u"widget_invisible_dummy")

        self.horizontalLayout_statusbar_placeholder.addWidget(self.widget_invisible_dummy)


        self.verticalLayout_6.addLayout(self.horizontalLayout_statusbar_placeholder)

        QWidget.setTabOrder(self.pushButton_ok, self.pushButton_cancel)

        self.retranslateUi(Form)

        self.pushButton_ok.setDefault(True)
        self.pushButton_cancel.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Notebook Specification editor", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_name.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Notebook specification name (required)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("Form", u"Type name here...", None))
#if QT_CONFIG(tooltip)
        self.comboBox_notebook_type.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Notebook specification type</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_notebook_type.setCurrentText("")
#if QT_CONFIG(tooltip)
        self.textEdit_description.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Notebook specification description (optional)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.textEdit_description.setPlaceholderText(QCoreApplication.translate("Form", u"Type description here...", None))
#if QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>If checked, Notebook specification is executed in a work directory (default).</p><p>If unchecked, Notebook specification is executed in Jupyter notebook file directory.</p><p>It is recommended to uncheck this for <span style=\" font-weight:600;\">Executable</span> Notebook specifications.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_execute_in_work.setText(QCoreApplication.translate("Form", u"Execute in work directory", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_Jupyter_notebook.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Jupyter notebook file that is used to launch the Notebook specification (required)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_Jupyter_notebook.setPlaceholderText(QCoreApplication.translate("Form", u"Type path of Jupyter notebook file here...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_new_jupyter_notebook.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Create new Jupyter notebook file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_browse_jupyter_notebook.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select existing Jupyter notebook file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_browse_jupyter_notebook.setText(QCoreApplication.translate("Form", u"...", None))
        self.textEdit_jupyter_notebook.setPlaceholderText(QCoreApplication.translate("Form", u"Create Jupyter notebook file here...", None))
        self.label.setText(QCoreApplication.translate("Form", u"Main program directory", None))
        self.label_mainpath.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_save_jupyter_notebook.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Save</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_save_jupyter_notebook.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.treeView_input_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:600;\">Input</span> variable(s) declared in notebook \"parameters\" tagged cell.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_input_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add input variable.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_input_vars.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_input_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected input variable(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_input_vars.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_output_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:600;\">Output</span> variable(s) declared in notebook \"parameters\" tagged cell.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_output_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add output variable.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_output_vars.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_output_vars.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected variable(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_output_vars.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_input_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:600;\">Required</span> data files for the program.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_input_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add input filenames and/or directories required by the program. Examples:</p><p>'data.csv'</p><p>'input/data.csv'</p><p>'input/'</p><p>'output/'</p><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_input_files.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_input_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_input_files.setText("")
#if QT_CONFIG(tooltip)
        self.treeView_output_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Output files that may be used by other project items downstream. These files will be archived into a results directory after execution.</p><p><span style=\" font-weight:600;\">Tip</span>: Double-click or press F2 to edit selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_plus_output_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Add output filenames produced by your program that are saved to results after execution.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_plus_output_files.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_minus_output_files.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected item(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_minus_output_files.setText("")
#if QT_CONFIG(tooltip)
        self.lineEdit_args.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Command line arguments (space-delimited) for the main program (optional). Use '@@' tags to refer to input files or URLs, see the User Guide for details.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_args.setPlaceholderText(QCoreApplication.translate("Form", u"Type command line arguments here...", None))
        self.pushButton_ok.setText(QCoreApplication.translate("Form", u"Ok", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("Form", u"Cancel", None))
    # retranslateUi

