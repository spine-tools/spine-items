import os
import unittest
from tempfile import TemporaryDirectory, TemporaryFile

from PySide2.QtWidgets import QApplication

from spine_items.notebook.executable_item import ExecutableItem
from spine_items.notebook.notebook_factory import NotebookFactory
from spine_items.notebook.notebook_instance import NotebookInstance
from spine_items.notebook.notebook_specifications import NotebookSpecification
from tests.mock_helpers import create_mock_toolbox, create_mock_project, mock_finish_project_item_construction
from .mock_notebook_specification_model import _MockNotebookSpecModel as mock_model
from.mock_notebook_specification_model import (SIMPLE_ITEM, SIMPLE_ITEM_DIFF_LIST, SIMPLE_ITEM_DICT_DIFF_NAME,
                                               BROKEN_ITEM)


class TestNotebookSpecifications(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._temp_file = TemporaryFile(prefix="nb", suffix=".ipynb", dir=self._temp_dir.name)
        self._temp_file_not_ipynb = TemporaryFile(prefix="nb", suffix=".txt", dir=self._temp_dir.name)
        self._temp_definition_file_path = TemporaryFile(prefix="nb", suffix=".json", dir=self._temp_dir.name)
        self.toolbox = create_mock_toolbox()
        self.project = create_mock_project(self._temp_dir.name)
        self.model = self.toolbox.specification_model = mock_model(self.toolbox, self._temp_dir.name,
                                                                   self._temp_file.name)

    def tearDown(self):
        self._temp_file_not_ipynb.close()
        self._temp_file.close()
        self._temp_definition_file_path.close()
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def _add_notebook(self, item_dict=None):
        if item_dict is None:
            item_dict = {"type": "Notebook", "description": "", "x": 0, "y": 0}
        factory = NotebookFactory()
        notebook = factory.make_item("NB", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, notebook, self.toolbox)
        # Set model for tool combo box
        notebook._properties_ui.comboBox_notebook.setModel(self.model)
        return notebook

    # Test notebook_specifications.py
    def test_specification_to_dict(self):
        notebook = self._add_notebook(SIMPLE_ITEM)
        nb_spec = notebook.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        spec_dict = nb_spec.to_dict()
        self.assertIsInstance(spec_dict, dict)
        # TODO check keys in spec dict

    def test_specification_check_definition(self):
        """Test all cases in NotebookSpecification.check_definition()"""
        # Test a correct notebook spec check_definition() should return a dict
        notebook = self._add_notebook(SIMPLE_ITEM)
        nb_spec = notebook.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        spec_dict = nb_spec.to_dict()
        self.assertIsInstance(spec_dict, dict)
        kwargs = NotebookSpecification.check_definition(spec_dict, self.toolbox)
        self.assertIsInstance(kwargs, dict)
        # Test a broken notebook
        broke_notebook = self._add_notebook(BROKEN_ITEM)
        # input_vars should be a list check_definition() should return none with msg_error
        broke_nb_spec = broke_notebook.specification()
        self.assertIsInstance(broke_nb_spec, NotebookSpecification)
        broke_spec_dict = broke_nb_spec.to_dict()
        self.assertIsInstance(broke_spec_dict, dict)
        kwargs = NotebookSpecification.check_definition(broke_spec_dict, self.toolbox)
        self.toolbox.msg_error.emit.assert_called_with("Keyword 'input_vars' value must be a list")
        self.assertIsNone(kwargs)
        # remove required keyword check_definition() should return none with msg_error
        del spec_dict['name']
        kwargs = NotebookSpecification.check_definition(spec_dict, self.toolbox)
        self.toolbox.msg_error.emit.assert_called_with("Required keyword 'name' missing")
        self.assertIsNone(kwargs)

    def test_specification_save(self):
        # not possible due to permissions?
        """Test both cases in NotebookSpecification.save() returns True or False"""
        # Test a correct notebook spec check_definition() should return a dict
        # notebook = self._add_notebook(SIMPLE_ITEM)
        # notebook.specification().definition_file_path = self._temp_definition_file_path.name
        # was_saved = notebook.specification().save()
        # self.assertTrue(was_saved)
        pass

    def test_specification_load(self):
        # Test a correct notebook spec load() should return a NotebookSpecification object
        notebook = self._add_notebook(SIMPLE_ITEM)
        nb_spec = notebook.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        simple_spec_dict = nb_spec.to_dict()
        self.assertIsInstance(simple_spec_dict, dict)
        loaded_nb_spec = NotebookSpecification.load(self._temp_dir.name, simple_spec_dict, self.toolbox.qsettings(),
                                                    self.toolbox)
        self.assertIsInstance(loaded_nb_spec, NotebookSpecification)
        # Test a broken notebook spec load() should return None
        notebook = self._add_notebook(BROKEN_ITEM)
        broke_nb_spec = notebook.specification()
        self.assertIsInstance(broke_nb_spec, NotebookSpecification)
        broke_spec_dict = notebook.specification().to_dict()
        self.assertIsInstance(broke_spec_dict, dict)
        loaded_broke_nb_spec = NotebookSpecification.load(self._temp_dir.name, broke_spec_dict,
                                                          self.toolbox.qsettings(),
                                                          self.toolbox)
        self.assertIsNone(loaded_broke_nb_spec)

    #def test_specification_create_instance(self):
    #    # Test a correct notebook spec load() should return a NotebookSpecification object
    #    notebook = self._add_notebook(SIMPLE_ITEM)
    #    nb_spec = notebook.specification()
    #    self.assertIsInstance(nb_spec, NotebookSpecification)
    #    nb_exec = notebook.execution_item()
    #    self.assertIsInstance(nb_exec, ExecutableItem)
    #    nb_instance = nb_spec.create_instance(self._temp_dir.name, self.toolbox, nb_exec)
    #    self.assertIsInstance(nb_instance, NotebookInstance)

    def test_specification_is_equivalent(self):
        """Test all cases in NotebookSpecification is_equivalent()"""
        notebook = self._add_notebook(SIMPLE_ITEM)
        notebook_1 = self._add_notebook(SIMPLE_ITEM)
        notebook_diff_name = self._add_notebook(SIMPLE_ITEM_DICT_DIFF_NAME)
        notebook_diff_input_vars = self._add_notebook(SIMPLE_ITEM_DIFF_LIST)
        nb_spec = notebook.specification()
        nb_spec_1 = notebook_1.specification()
        nb_spec_diff_name = notebook_diff_name.specification()
        nb_spec_diff_input_vars = notebook_diff_input_vars.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        self.assertIsInstance(nb_spec_1, NotebookSpecification)
        self.assertIsInstance(nb_spec_diff_name, NotebookSpecification)
        self.assertIsInstance(nb_spec_diff_input_vars, NotebookSpecification)
        # test case when notebook specs are equivalent
        is_same = nb_spec.is_equivalent(nb_spec_1)
        self.assertTrue(is_same)
        # test case when notebook specs have same key but different value
        is_diff_name = nb_spec.is_equivalent(nb_spec_diff_name)
        self.assertFalse(is_diff_name)
        # test case when notebook specs have different values when key is in LIST_REQUIRED_KEYS
        is_diff_input_vars = nb_spec.is_equivalent(nb_spec_diff_input_vars)
        self.assertFalse(is_diff_input_vars)

    def test_specification_get_jupyter_notebook_path(self):
        notebook = self._add_notebook(SIMPLE_ITEM)
        nb_spec = notebook.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        file_path = nb_spec.get_jupyter_notebook_path()
        self.assertTrue(os.path.isfile(file_path))
        self.assertEqual(file_path, self._temp_file.name)
        nb_spec.path = "not_a_path"
        not_file_path = nb_spec.get_jupyter_notebook_path()
        self.toolbox.msg_error.emit.assert_called_with(
            f"Opening Notebook spec for Jupyter notebook <b>{nb_spec.includes[0]}</b> failed. "
            f"Jupyter notebook directory does not exist."
        )
        self.assertIsNone(not_file_path)
        # reset spec path to correct dir
        nb_spec.path = self._temp_dir.name
        # set main file to arbitrary string
        nb_spec.includes[0] = "not_file"
        not_file_path = nb_spec.get_jupyter_notebook_path()
        false_file_path = os.path.join(self._temp_dir.name, "not_file")
        self.toolbox.msg_error.emit.assert_called_with(
            f"Notebook spec Jupyter notebook <b>{false_file_path}</b> not "
            f"found.")
        self.assertIsNone(not_file_path)
        # set main file to be a file that exists but does not have extension .ipynb
        nb_spec.includes[0] = self._temp_file_not_ipynb.name
        not_file_path = nb_spec.get_jupyter_notebook_path()
        self.toolbox.msg_warning.emit.assert_called_with("Sorry, opening files with extension <b>.txt</b> not "
                                                         "supported. Please open the file manually.")
        self.assertIsNone(not_file_path)

    def test_make_specification(self):
        pass
