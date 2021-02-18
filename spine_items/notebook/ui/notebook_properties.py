# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'notebook_properties.ui'
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

from ...widgets import ArgsTreeView

from spine_items import resources_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(408, 451)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_notebook_name = QLabel(Form)
        self.label_notebook_name.setObjectName(u"label_notebook_name")
        self.label_notebook_name.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_notebook_name.sizePolicy().hasHeightForWidth())
        self.label_notebook_name.setSizePolicy(sizePolicy)
        self.label_notebook_name.setMinimumSize(QSize(0, 20))
        self.label_notebook_name.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_notebook_name.setFont(font)
        self.label_notebook_name.setStyleSheet(u"background-color: #ecd8c6;")
        self.label_notebook_name.setFrameShape(QFrame.Box)
        self.label_notebook_name.setFrameShadow(QFrame.Sunken)
        self.label_notebook_name.setAlignment(Qt.AlignCenter)
        self.label_notebook_name.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_notebook_name)

        self.scrollArea_3 = QScrollArea(Form)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 406, 429))
        self.verticalLayout_17 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_notebook_specification = QLabel(self.scrollAreaWidgetContents_3)
        self.label_notebook_specification.setObjectName(u"label_notebook_specification")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_notebook_specification.sizePolicy().hasHeightForWidth())
        self.label_notebook_specification.setSizePolicy(sizePolicy1)
        self.label_notebook_specification.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setPointSize(10)
        self.label_notebook_specification.setFont(font1)

        self.horizontalLayout_9.addWidget(self.label_notebook_specification)

        self.comboBox_notebook = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_notebook.setObjectName(u"comboBox_notebook")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox_notebook.sizePolicy().hasHeightForWidth())
        self.comboBox_notebook.setSizePolicy(sizePolicy2)

        self.horizontalLayout_9.addWidget(self.comboBox_notebook)

        self.toolButton_notebook_specification = QToolButton(self.scrollAreaWidgetContents_3)
        self.toolButton_notebook_specification.setObjectName(u"toolButton_notebook_specification")
        self.toolButton_notebook_specification.setMinimumSize(QSize(22, 22))
        self.toolButton_notebook_specification.setMaximumSize(QSize(22, 22))
        icon = QIcon()
        icon.addFile(u":/icons/wrench.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_notebook_specification.setIcon(icon)
        self.toolButton_notebook_specification.setIconSize(QSize(16, 16))
        self.toolButton_notebook_specification.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_9.addWidget(self.toolButton_notebook_specification)


        self.verticalLayout_17.addLayout(self.horizontalLayout_9)

        self.splitter = QSplitter(self.scrollAreaWidgetContents_3)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.treeView_cmdline_args = ArgsTreeView(self.splitter)
        self.treeView_cmdline_args.setObjectName(u"treeView_cmdline_args")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.treeView_cmdline_args.sizePolicy().hasHeightForWidth())
        self.treeView_cmdline_args.setSizePolicy(sizePolicy3)
        self.treeView_cmdline_args.setFont(font1)
        self.treeView_cmdline_args.setAcceptDrops(True)
        self.treeView_cmdline_args.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.treeView_cmdline_args.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeView_cmdline_args.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_cmdline_args.setTextElideMode(Qt.ElideLeft)
        self.splitter.addWidget(self.treeView_cmdline_args)
        self.treeView_cmdline_args.header().setMinimumSectionSize(26)
        self.gridLayoutWidget = QWidget(self.splitter)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.toolButton_add_file_path_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_add_file_path_arg.setObjectName(u"toolButton_add_file_path_arg")
        self.toolButton_add_file_path_arg.setMinimumSize(QSize(22, 22))
        self.toolButton_add_file_path_arg.setMaximumSize(QSize(22, 22))
        icon1 = QIcon()
        icon1.addFile(u":/icons/file-upload.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_add_file_path_arg.setIcon(icon1)
        self.toolButton_add_file_path_arg.setIconSize(QSize(16, 16))
        self.toolButton_add_file_path_arg.setPopupMode(QToolButton.InstantPopup)

        self.gridLayout.addWidget(self.toolButton_add_file_path_arg, 0, 0, 1, 1)

        self.toolButton_remove_arg = QToolButton(self.gridLayoutWidget)
        self.toolButton_remove_arg.setObjectName(u"toolButton_remove_arg")
        icon2 = QIcon()
        icon2.addFile(u":/icons/minus.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_remove_arg.setIcon(icon2)

        self.gridLayout.addWidget(self.toolButton_remove_arg, 0, 2, 1, 1)

        self.treeView_input_files = QTreeView(self.gridLayoutWidget)
        self.treeView_input_files.setObjectName(u"treeView_input_files")
        sizePolicy3.setHeightForWidth(self.treeView_input_files.sizePolicy().hasHeightForWidth())
        self.treeView_input_files.setSizePolicy(sizePolicy3)
        self.treeView_input_files.setFont(font1)
        self.treeView_input_files.setDragEnabled(False)
        self.treeView_input_files.setDragDropMode(QAbstractItemView.DragOnly)
        self.treeView_input_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_input_files.setTextElideMode(Qt.ElideLeft)
        self.treeView_input_files.setIndentation(5)
        self.treeView_input_files.setRootIsDecorated(False)
        self.treeView_input_files.setUniformRowHeights(True)
        self.treeView_input_files.setAnimated(False)
        self.treeView_input_files.header().setMinimumSectionSize(26)

        self.gridLayout.addWidget(self.treeView_input_files, 1, 0, 1, 3)

        self.splitter.addWidget(self.gridLayoutWidget)

        self.verticalLayout_17.addWidget(self.splitter)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setSpacing(6)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_6)

        self.pushButton_notebook_results = QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_notebook_results.setObjectName(u"pushButton_notebook_results")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_notebook_results.sizePolicy().hasHeightForWidth())
        self.pushButton_notebook_results.setSizePolicy(sizePolicy4)
        self.pushButton_notebook_results.setMinimumSize(QSize(75, 23))
        self.pushButton_notebook_results.setMaximumSize(QSize(75, 23))

        self.horizontalLayout_11.addWidget(self.pushButton_notebook_results)


        self.verticalLayout_17.addLayout(self.horizontalLayout_11)

        self.line_4 = QFrame(self.scrollAreaWidgetContents_3)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_17.addWidget(self.line_4)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_2 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_15.addWidget(self.label_2)

        self.radioButton_execute_in_work = QRadioButton(self.scrollAreaWidgetContents_3)
        self.radioButton_execute_in_work.setObjectName(u"radioButton_execute_in_work")
        self.radioButton_execute_in_work.setChecked(True)

        self.horizontalLayout_15.addWidget(self.radioButton_execute_in_work)

        self.radioButton_execute_in_source = QRadioButton(self.scrollAreaWidgetContents_3)
        self.radioButton_execute_in_source.setObjectName(u"radioButton_execute_in_source")

        self.horizontalLayout_15.addWidget(self.radioButton_execute_in_source)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_8)

        self.toolButton_notebook_open_dir = QToolButton(self.scrollAreaWidgetContents_3)
        self.toolButton_notebook_open_dir.setObjectName(u"toolButton_notebook_open_dir")
        self.toolButton_notebook_open_dir.setMinimumSize(QSize(22, 22))
        self.toolButton_notebook_open_dir.setMaximumSize(QSize(22, 22))
        icon3 = QIcon()
        icon3.addFile(u":/icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButton_notebook_open_dir.setIcon(icon3)

        self.horizontalLayout_15.addWidget(self.toolButton_notebook_open_dir)


        self.verticalLayout_17.addLayout(self.horizontalLayout_15)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout.addWidget(self.scrollArea_3)

        QWidget.setTabOrder(self.scrollArea_3, self.comboBox_notebook)
        QWidget.setTabOrder(self.comboBox_notebook, self.toolButton_notebook_specification)
        QWidget.setTabOrder(self.toolButton_notebook_specification, self.pushButton_notebook_results)
        QWidget.setTabOrder(self.pushButton_notebook_results, self.toolButton_notebook_open_dir)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_notebook_name.setText(QCoreApplication.translate("Form", u"Name", None))
        self.label_notebook_specification.setText(QCoreApplication.translate("Form", u"Specification", None))
#if QT_CONFIG(tooltip)
        self.comboBox_notebook.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Notebook specification for this Notebook</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_notebook_specification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Notebook specification options.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Append selected input file paths to the list of command line args</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_add_file_path_arg.setText("")
#if QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Remove selected notebook command line args</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_remove_arg.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.pushButton_notebook_results.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open results archive in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_notebook_results.setText(QCoreApplication.translate("Form", u"Results...", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Execute in", None))
        self.radioButton_execute_in_work.setText(QCoreApplication.translate("Form", u"Work directory", None))
        self.radioButton_execute_in_source.setText(QCoreApplication.translate("Form", u"Source directory", None))
#if QT_CONFIG(tooltip)
        self.toolButton_notebook_open_dir.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Open Notebook project directory in file browser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

