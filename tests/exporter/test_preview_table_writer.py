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
import unittest
import numpy
from spine_items.exporter.preview_table_writer import TableWriter


class TestTableWriter(unittest.TestCase):
    def setUp(self):
        self._writer = TableWriter()
        self._writer.start()

    def tearDown(self):
        self._writer.finish()

    def test_write_row_float64_converted_to_float(self):
        self.assertTrue(self._writer.start_table("My table", {}))
        self.assertTrue(self._writer.write_row([numpy.float64(2.3)]))
        self._writer.finish_table()
        tables = self._writer.tables
        self.assertEqual(tables, {"My table": [[2.3]]})


if __name__ == "__main__":
    unittest.main()
