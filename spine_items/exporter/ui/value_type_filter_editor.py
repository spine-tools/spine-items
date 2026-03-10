# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'value_type_filter_editor.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(354, 138)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.regexp_line_edit = QLineEdit(Form)
        self.regexp_line_edit.setObjectName(u"regexp_line_edit")
        self.regexp_line_edit.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.regexp_line_edit)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setTextFormat(Qt.RichText)
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_2.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.label_2)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setTextFormat(Qt.RichText)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.regexp_line_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Type regular expression here...", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><a href=\"https://docs.python.org/3/library/re.html#regular-expression-syntax\"><span style=\" text-decoration: underline;\">Link</span></a> to regular expression syntax.</p></body></html>", None))
        self.label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p>Available types for filtering:<br/><span style=\" font-weight:700;\">float</span>, <span style=\" font-weight:700;\">str</span>, <span style=\" font-weight:700;\">bool</span> - numbers, strings, booleans<br/><span style=\" font-weight:700;\">array</span>, <span style=\" font-weight:700;\">time_series</span>, <span style=\" font-weight:700;\">time_pattern</span><br/><span style=\" font-weight:700;\">1d_map</span>, <span style=\" font-weight:700;\">2d_map</span>,... - maps of <span style=\" font-style:italic;\">n</span>d dimensions</p></body></html>", None))
    # retranslateUi

