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

"""
Provides MainProgramTextEdit.

:author: M. Marin (KTH)
:date:   28.1.2020
"""

from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from pygments.token import Token
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit, QPlainTextDocumentLayout, QAction
from PySide2.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QBrush,
    QColor,
    QFontMetrics,
    QFontDatabase,
    QFont,
    QKeySequence,
)


class CustomSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.lexer = None
        self._formats = {}

    def set_style(self, style):
        self._formats.clear()
        for ttype, tstyle in style:
            text_format = self._formats[ttype] = QTextCharFormat()
            if tstyle['color']:
                brush = QBrush(QColor("#" + tstyle['color']))
                text_format.setForeground(brush)
            if tstyle['bgcolor']:
                brush = QBrush(QColor("#" + tstyle['bgcolor']))
                text_format.setBackground(brush)
            if tstyle['bold']:
                text_format.setFontWeight(QFont.Bold)
            if tstyle['italic']:
                text_format.setFontItalic(True)
            if tstyle['underline']:
                text_format.setFontUnderline(True)

    def highlightBlock(self, text):
        if self.lexer is None:
            return
        for start, ttype, subtext in self.lexer.get_tokens_unprocessed(text):
            while ttype not in self._formats:
                ttype = ttype.parent
            text_format = self._formats.get(ttype, QTextCharFormat())
            self.setFormat(start, len(subtext), text_format)


class MainProgramTextEdit(QPlainTextEdit):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self._highlighter = CustomSyntaxHighlighter(self)
        style = get_style_by_name("monokai")
        self._highlighter.set_style(style)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.setFont(font)
        foreground_color = style.styles[Token.Text]
        self.setStyleSheet(f"QPlainTextEdit {{background-color: {style.background_color}; color: {foreground_color};}}")
        self.save_action = QAction(self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setShortcutContext(Qt.WidgetShortcut)
        self.save_action.setEnabled(False)
        self.addAction(self.save_action)

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())

    def set_lexer_name(self, lexer_name):
        try:
            self._highlighter.lexer = get_lexer_by_name(lexer_name)
            self._highlighter.rehighlight()
        except ClassNotFound:
            # No lexer for aliases 'gams' nor 'executable'
            pass

    def setDocument(self, doc):
        doc.setDocumentLayout(QPlainTextDocumentLayout(doc))
        super().setDocument(doc)
        self._highlighter.setDocument(doc)
        doc.setDefaultFont(self.font())
        self.setTabStopDistance(QFontMetrics(self.font()).horizontalAdvance(4 * " "))
        doc.modificationChanged.connect(self.save_action.setEnabled)
