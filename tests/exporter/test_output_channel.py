######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Unit tests for the ``output_channel`` module."""
import unittest

from spine_items.exporter.output_channel import OutputChannel


class TestOutputChannel(unittest.TestCase):
    def test_initialization_with_out_label(self):
        channel = OutputChannel("In label", "Exporter 1", "Out label")
        self.assertEqual(channel.in_label, "In label")
        self.assertEqual(channel.out_label, "Out label")

    def test_initialization_without_out_label(self):
        channel = OutputChannel("In label", "Exporter 1")
        self.assertEqual(channel.in_label, "In label")
        self.assertEqual(channel.out_label, "In label_exported@Exporter 1")

    def test_serialization(self):
        channel = OutputChannel("In label", "Exporter 1", "Out label")
        channel_dict = channel.to_dict()
        restored = OutputChannel.from_dict(channel_dict, "Exporter 1")
        self.assertEqual(restored.in_label, "In label")
        self.assertEqual(restored.out_label, "Out label")


if __name__ == '__main__':
    unittest.main()
