from PySide2.QtGui import QStandardItem, QStandardItemModel
from spine_items.notebook.notebook_specifications import NotebookSpecification

SIMPLE_ITEM = {
    "type": "Notebook",
    "description": "simple correct spec",
    "x": 0,
    "y": 0,
    "specification": "simple_spec",
    "execute_in_work": False,
}

SIMPLE_ITEM_DIFF_LIST = {
    "type": "Notebook",
    "description": "simple correct spec with different input_vars list",
    "x": 0,
    "y": 0,
    "specification": "simple_spec_diff_input_vars",
    "execute_in_work": False,
}

SIMPLE_ITEM_DICT_DIFF_NAME = {
    "type": "Notebook",
    "description": "simple correct spec with different name",
    "x": 0,
    "y": 0,
    "specification": "simple_spec_diff_name",
    "execute_in_work": True,
}

BROKEN_ITEM = {
    "type": "Notebook",
    "description": "broken spec with input_vars should be list but is str",
    "x": 0,
    "y": 0,
    "specification": "broken_spec",
    "execute_in_work": False,
}


class _MockNotebookSpecModel(QStandardItemModel):
    # Create a dictionary of tool specifications to 'populate' the mock model
    def __init__(self, toolbox, path, nb_file):
        super().__init__()
        specifications = [
            NotebookSpecification(
                name="simple_spec",
                notebook_type="python",
                path=path,
                includes=[nb_file],
                settings=toolbox.qsettings(),
                logger=toolbox,
                description="A notebook item.",
                input_vars=['j', 'k'],
                output_vars=['x', 'y'],
                input_files=["input1.csv"],
                output_files=["output1.csv"],
                cmdline_args="<args>",
                execute_in_work=False,
            ),
            NotebookSpecification(
                name="simple_spec_diff_name",
                notebook_type="python",
                path=path,
                includes=["nb.ipynb"],
                settings=toolbox.qsettings(),
                logger=toolbox,
                description="A notebook item.",
                input_vars=['j', 'k'],
                output_vars=['x', 'y'],
                input_files=["input1.csv", "input2.csv"],
                output_files=["output1.csv", "output2.csv"],
                cmdline_args="<args>",
                execute_in_work=False,
            ),
            NotebookSpecification(
                name="simple_spec_diff_input_vars",
                notebook_type="python",
                path=path,
                includes=["nb.ipynb"],
                settings=toolbox.qsettings(),
                logger=toolbox,
                description="A notebook item.",
                input_vars=['a', 'b'],
                output_vars=['x', 'y'],
                input_files=["input1.csv", "input2.csv"],
                output_files=["output1.csv", "output2.csv"],
                cmdline_args="<args>",
                execute_in_work=False,
            ),
            NotebookSpecification(
                name="broken_spec",
                notebook_type="python",
                path=path,
                includes=["nb_broken.ipynb"],
                settings=toolbox.qsettings(),
                logger=toolbox,
                description="A broken spec.",
                input_vars="should be a list",
                output_vars=[],
                input_files=[],
                output_files=[],
                cmdline_args="",
                execute_in_work=True,
            ),
        ]
        specification_names = [x.name for x in specifications]
        specification_dict = dict(zip(specification_names, specifications))
        self.find_specification = specification_dict.get
        self.specification = specifications.__getitem__
        self.specification_row = specification_names.index
        self.invisibleRootItem().appendRows([QStandardItem(x) for x in specification_dict])

    def specification_index(self, spec_name):
        row = self.specification_row(spec_name)
        return self.invisibleRootItem().child(row)