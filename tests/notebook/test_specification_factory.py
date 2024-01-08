import unittest
from tempfile import TemporaryDirectory, TemporaryFile

from PySide2.QtWidgets import QApplication

from spine_items.notebook.notebook_factory import NotebookFactory
from spine_items.notebook.notebook_specifications import NotebookSpecification
from spine_items.notebook.specification_factory import SpecificationFactory
from tests.mock_helpers import create_mock_toolbox, create_mock_project, mock_finish_project_item_construction
from .mock_notebook_specification_model import _MockNotebookSpecModel as mock_model, SIMPLE_ITEM


class TestSpecificationFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._temp_file = TemporaryFile(prefix="nb", suffix=".ipynb", dir=self._temp_dir.name)
        self.toolbox = create_mock_toolbox()
        self.project = create_mock_project(self._temp_dir.name)
        self.model = self.toolbox.specification_model = mock_model(self.toolbox, self._temp_dir.name,
                                                                   self._temp_file.name)
        self.specification_factory = SpecificationFactory()

    def tearDown(self):
        self._temp_file.close()
        self._temp_dir.cleanup()

    def _add_notebook(self, item_dict=None):
        if item_dict is None:
            item_dict = {"type": "Notebook", "description": "", "x": 0, "y": 0}
        factory = NotebookFactory()
        notebook = factory.make_item("NB", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, notebook, self.toolbox)
        # Set model for tool combo box
        notebook._properties_ui.comboBox_notebook.setModel(self.model)
        return notebook

    def test_specification_factory_item_type(self):
        self.assertEqual(self.specification_factory.item_type(), "Notebook")

    def test_specification_factory_make_specification(self):
        notebook = self._add_notebook(SIMPLE_ITEM)
        nb_spec = notebook.specification()
        self.assertIsInstance(nb_spec, NotebookSpecification)
        simple_spec_dict = nb_spec.to_dict()
        self.assertIsInstance(simple_spec_dict, dict)
        factory_nb_spec = self.specification_factory.make_specification(simple_spec_dict, self.toolbox.qsettings(), self.toolbox)
        self.assertIsInstance(factory_nb_spec, NotebookSpecification)
