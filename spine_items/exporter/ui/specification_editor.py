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
## Form generated from reading UI file 'specification_editor.ui'
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

from spinetoolbox.widgets.custom_combobox import ElidedCombobox


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(921, 758)
        self.save_and_close_action = QAction(MainWindow)
        self.save_and_close_action.setObjectName(u"save_and_close_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 921, 21))
        MainWindow.setMenuBar(self.menubar)
        self.preview_dock = QDockWidget(MainWindow)
        self.preview_dock.setObjectName(u"preview_dock")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(self.dockWidgetContents)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.preview_tree_view = QTreeView(self.splitter)
        self.preview_tree_view.setObjectName(u"preview_tree_view")
        self.splitter.addWidget(self.preview_tree_view)
        self.preview_tree_view.header().setVisible(False)
        self.preview_table_view = QTableView(self.splitter)
        self.preview_table_view.setObjectName(u"preview_table_view")
        self.splitter.addWidget(self.preview_table_view)

        self.verticalLayout_4.addWidget(self.splitter)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_9 = QLabel(self.dockWidgetContents)
        self.label_9.setObjectName(u"label_9")
        font = QFont()
        font.setPointSize(8)
        self.label_9.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_9)

        self.database_url_combo_box = ElidedCombobox(self.dockWidgetContents)
        self.database_url_combo_box.setObjectName(u"database_url_combo_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.database_url_combo_box.sizePolicy().hasHeightForWidth())
        self.database_url_combo_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.database_url_combo_box)

        self.load_url_from_fs_button = QToolButton(self.dockWidgetContents)
        self.load_url_from_fs_button.setObjectName(u"load_url_from_fs_button")
        icon = QIcon()
        icon.addFile(u":/icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.load_url_from_fs_button.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.load_url_from_fs_button)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.load_data_button = QPushButton(self.dockWidgetContents)
        self.load_data_button.setObjectName(u"load_data_button")
        self.load_data_button.setEnabled(False)

        self.horizontalLayout.addWidget(self.load_data_button)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.preview_dock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.preview_dock)
        self.mapping_options_dock = QDockWidget(MainWindow)
        self.mapping_options_dock.setObjectName(u"mapping_options_dock")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_3 = QSplitter(self.dockWidgetContents_2)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Horizontal)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.verticalLayoutWidget = QWidget(self.splitter_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_mapping_button = QPushButton(self.verticalLayoutWidget)
        self.add_mapping_button.setObjectName(u"add_mapping_button")

        self.horizontalLayout_2.addWidget(self.add_mapping_button)

        self.remove_mapping_button = QPushButton(self.verticalLayoutWidget)
        self.remove_mapping_button.setObjectName(u"remove_mapping_button")

        self.horizontalLayout_2.addWidget(self.remove_mapping_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.mapping_list = QListView(self.verticalLayoutWidget)
        self.mapping_list.setObjectName(u"mapping_list")

        self.verticalLayout_2.addWidget(self.mapping_list)

        self.splitter_2.addWidget(self.verticalLayoutWidget)
        self.layoutWidget = QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.export_objects_check_box = QCheckBox(self.layoutWidget)
        self.export_objects_check_box.setObjectName(u"export_objects_check_box")

        self.gridLayout_2.addWidget(self.export_objects_check_box, 2, 1, 1, 1)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)

        self.item_type_combo_box = QComboBox(self.layoutWidget)
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.addItem("")
        self.item_type_combo_box.setObjectName(u"item_type_combo_box")

        self.gridLayout_2.addWidget(self.item_type_combo_box, 0, 1, 1, 1)

        self.parameter_dimensions_spin_box = QSpinBox(self.layoutWidget)
        self.parameter_dimensions_spin_box.setObjectName(u"parameter_dimensions_spin_box")

        self.gridLayout_2.addWidget(self.parameter_dimensions_spin_box, 5, 1, 1, 1)

        self.relationship_dimensions_spin_box = QSpinBox(self.layoutWidget)
        self.relationship_dimensions_spin_box.setObjectName(u"relationship_dimensions_spin_box")
        self.relationship_dimensions_spin_box.setMinimum(1)

        self.gridLayout_2.addWidget(self.relationship_dimensions_spin_box, 3, 1, 1, 1)

        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 3, 0, 1, 1)

        self.parameter_type_combo_box = QComboBox(self.layoutWidget)
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.addItem("")
        self.parameter_type_combo_box.setObjectName(u"parameter_type_combo_box")

        self.gridLayout_2.addWidget(self.parameter_type_combo_box, 4, 1, 1, 1)

        self.label_10 = QLabel(self.layoutWidget)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 5, 0, 1, 1)

        self.fix_table_name_check_box = QCheckBox(self.layoutWidget)
        self.fix_table_name_check_box.setObjectName(u"fix_table_name_check_box")

        self.gridLayout_2.addWidget(self.fix_table_name_check_box, 6, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.splitter_2.addWidget(self.layoutWidget)
        self.splitter_3.addWidget(self.splitter_2)
        self.mapping_table_view = QTableView(self.splitter_3)
        self.mapping_table_view.setObjectName(u"mapping_table_view")
        self.mapping_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.splitter_3.addWidget(self.mapping_table_view)
        self.mapping_table_view.horizontalHeader().setStretchLastSection(True)
        self.mapping_table_view.verticalHeader().setVisible(False)

        self.verticalLayout_5.addWidget(self.splitter_3)

        self.mapping_options_dock.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mapping_options_dock)
        self.format_options_dock = QDockWidget(MainWindow)
        self.format_options_dock.setObjectName(u"format_options_dock")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.horizontalLayout_6 = QHBoxLayout(self.dockWidgetContents_3)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.groupBox = QGroupBox(self.dockWidgetContents_3)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy2)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.export_format_combo_box = QComboBox(self.groupBox)
        self.export_format_combo_box.setObjectName(u"export_format_combo_box")

        self.verticalLayout_3.addWidget(self.export_format_combo_box)


        self.horizontalLayout_5.addWidget(self.groupBox)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)

        self.format_options_dock.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.format_options_dock)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName(u"status_bar")
        self.status_bar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.status_bar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.save_and_close_action.setText(QCoreApplication.translate("MainWindow", u"Save and close", None))
#if QT_CONFIG(tooltip)
        self.save_and_close_action.setToolTip(QCoreApplication.translate("MainWindow", u"Save specification and close the editor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.save_and_close_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Return", None))
#endif // QT_CONFIG(shortcut)
        self.preview_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Database url:", None))
#if QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Browse file system</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.load_url_from_fs_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.load_data_button.setText(QCoreApplication.translate("MainWindow", u"Load preview data", None))
        self.mapping_options_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mapping options", None))
        self.add_mapping_button.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.remove_mapping_button.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Item type:", None))
        self.export_objects_check_box.setText(QCoreApplication.translate("MainWindow", u"Export objects", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Parameter type:", None))
        self.item_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Object class", None))
        self.item_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Relationship class", None))
        self.item_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"Object group", None))
        self.item_type_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"Alternative", None))
        self.item_type_combo_box.setItemText(4, QCoreApplication.translate("MainWindow", u"Scenario", None))
        self.item_type_combo_box.setItemText(5, QCoreApplication.translate("MainWindow", u"Scenario alternative", None))
        self.item_type_combo_box.setItemText(6, QCoreApplication.translate("MainWindow", u"Parameter value list", None))
        self.item_type_combo_box.setItemText(7, QCoreApplication.translate("MainWindow", u"Feature", None))
        self.item_type_combo_box.setItemText(8, QCoreApplication.translate("MainWindow", u"Tool", None))
        self.item_type_combo_box.setItemText(9, QCoreApplication.translate("MainWindow", u"Tool feature", None))
        self.item_type_combo_box.setItemText(10, QCoreApplication.translate("MainWindow", u"Tool feature method", None))

        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Number of dimensions:", None))
        self.parameter_type_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"Value", None))
        self.parameter_type_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"Default value", None))
        self.parameter_type_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"None", None))

        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Parameter dimensions:", None))
        self.fix_table_name_check_box.setText(QCoreApplication.translate("MainWindow", u"Fixed table name", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Export format settings", None))
    # retranslateUi

