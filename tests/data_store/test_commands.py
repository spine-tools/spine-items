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
from unittest import mock
from spine_items.data_store.commands import UpdateDSURLCommand


class TestUpdateDSURLCommand(unittest.TestCase):
    def test_merging_with_command_that_modifies_same_fields_works(self):
        mock_ds = mock.MagicMock()
        mock_ds.url.return_value = {"username": "c"}
        mock_project = mock.MagicMock()
        mock_project.get_item.return_value = mock_ds
        command1 = UpdateDSURLCommand("DS 1", False, mock_project, username="ca")
        mock_ds.url.return_value = {"username": "ca"}
        command2 = UpdateDSURLCommand("DS 1", False, mock_project, username="cat")
        self.assertTrue(command1.mergeWith(command2))
        command1.redo()
        mock_ds.do_update_url.assert_called_once_with(username="cat")

    def test_merging_is_rejected_when_commands_modify_different_fields(self):
        mock_ds = mock.MagicMock()
        mock_ds.url.return_value = {"username": "c", "host": ""}
        mock_project = mock.MagicMock()
        mock_project.get_item.return_value = mock_ds
        command1 = UpdateDSURLCommand("DS 1", False, mock_project, username="ca")
        mock_ds.url.return_value = {"username": "ca", "host": ""}
        command2 = UpdateDSURLCommand("DS 1", False, mock_project, host="q")
        self.assertFalse(command1.mergeWith(command2))


if __name__ == "__main__":
    unittest.main()
