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

"""Provides OptionsWidget classes for Python and Julia tool types."""
import os
import sys
import uuid
from PySide6.QtCore import QPointF, Qt, QVariantAnimation, Slot
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPalette
from PySide6.QtWidgets import QFileDialog, QWidget, QApplication
from spine_items.tool.utils import get_julia_path_and_project
from spine_items.utils import escape_backward_slashes
from spinetoolbox.execution_managers import QProcessExecutionManager
from spinetoolbox.helpers import (
    CharIconEngine,
    get_open_file_name_in_last_dir,
    make_settings_dict_for_engine,
    file_is_valid,
    select_file_path,
    select_dir,
)
from spinetoolbox.spine_engine_worker import SpineEngineWorker
from spine_engine.utils.helpers import resolve_current_python_interpreter, resolve_default_julia_executable


class OptionsWidget(QWidget):
    def __init__(self, Ui_Form, models):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._models = models  # Models containing saved Pythons and Julias
        self._tool = None

    def set_tool(self, tool):
        """Init class.

        Args:
            tool (Tool)
        """
        self._tool = tool

    @property
    def _project(self):
        return self._tool.project

    @property
    def settings(self):
        return self._project.app_settings

    @property
    def _logger(self):
        return self._tool.logger

    @property
    def models(self):
        return self._models


class SharedToolOptionsWidget(OptionsWidget):
    """Superclass for Python and Julia Tool optional widgets."""

    def __init__(self, Ui_Form, models):
        """
        Args:
            Ui_Form (Form): Optional widget UI form
        """
        super().__init__(Ui_Form, models)

    def connect_signals(self):
        """Connects signals."""

    def _enable_widgets(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.comboBox_executable.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.comboBox_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console

    def validate_executable(self, p, tool_spec_type):
        """Check that given Python or Julia path is a file, it exists, and the
        file name starts with either 'python' or 'julia'.

        Args:
            p (str): Abs. path to check
            tool_spec_type (str): 'python' or 'julia'

        Raises:
            NameError: If the python path in the line edit is not valid
        """
        if not file_is_valid(
            self,
            p,
            f"Invalid {tool_spec_type.capitalize()} Interpreter",
            extra_check=tool_spec_type,
        ):
            raise NameError

    def do_update_options(self, options):
        raise NotImplementedError()

    def get_executable(self):
        raise NotImplementedError()

    def get_current_kernel_item_data(self):
        raise NotImplementedError()

    def get_kernel_name(self):
        raise NotImplementedError()

    def is_conda(self):
        raise NotImplementedError()


class PythonOptionsWidget(SharedToolOptionsWidget):
    def __init__(self, models):
        from ..ui.python_tool_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(Ui_Form, models)
        self.ui.comboBox_executable.setModel(self._models.python_interpreters_model)
        self.ui.comboBox_kernel_specs.setModel(self._models.python_kernel_model)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.radioButton_jupyter_console.toggled.connect(self._update_use_jupyter_console)
        self.ui.toolButton_browse_python.clicked.connect(self._add_python_interpreter)
        self.ui.comboBox_executable.currentIndexChanged.connect(self._update_executable)
        self.ui.comboBox_kernel_specs.currentIndexChanged.connect(self._update_python_kernel)

    @Slot(int)
    def _update_executable(self, _row):
        """Updates Python executable."""
        self._tool.update_options({"executable": self.get_executable()})

    @Slot(int)
    def _update_python_kernel(self, _row):
        self._tool.update_options({"kernel_spec_name": self.get_kernel_name(), "env": self.is_conda()})

    @Slot(bool)
    def _update_use_jupyter_console(self, checked):
        self._tool.update_options({"use_jupyter_console": checked})

    def do_update_options(self, options):
        self._block_signals(True)
        self._enable_widgets(options["use_jupyter_console"])
        (
            self.ui.radioButton_jupyter_console.setChecked(True)
            if options["use_jupyter_console"]
            else self.ui.radioButton_basic_console.setChecked(True)
        )
        kernel_index = self.models.find_python_kernel_index(options["kernel_spec_name"])
        if not kernel_index.isValid():
            kernel_index = self.models.python_kernel_model.index(0, 0)
        self.ui.comboBox_kernel_specs.setCurrentIndex(kernel_index.row())
        exec_index = self._models.find_python_interpreter_index(options["executable"])
        if not exec_index.isValid():
            exec_index = self.models.python_interpreters_model.index(0, 0)
        self.ui.comboBox_executable.setCurrentIndex(exec_index.row())
        self._block_signals(False)

    def _block_signals(self, block):
        self.ui.radioButton_jupyter_console.blockSignals(block)
        self.ui.comboBox_executable.blockSignals(block)
        self.ui.comboBox_kernel_specs.blockSignals(block)

    def get_executable(self):
        """Returns the Python executable path of the currently selected item in the combobox."""
        current_index = self.models.python_interpreters_model.index(self.ui.comboBox_executable.currentIndex(), 0)
        item = self.models.python_interpreters_model.itemFromIndex(current_index)
        return item.data()["exe"]

    def get_current_kernel_item_data(self):
        current_index = self.models.python_kernel_model.index(self.ui.comboBox_kernel_specs.currentIndex(), 0)
        item = self.models.python_kernel_model.itemFromIndex(current_index)
        return item.data()

    def get_kernel_name(self):
        """Returns the selected Python kernel name in the combobox."""
        data = self.get_current_kernel_item_data()
        return data["kernel_name"]

    def is_conda(self):
        data = self.get_current_kernel_item_data()
        return "conda" if data["is_conda"] else ""

    @Slot(bool)
    def _add_python_interpreter(self, _=False):
        """Calls static method that shows a file browser for selecting a Python interpreter."""
        current_path = self.ui.comboBox_executable.currentText()
        if not current_path:
            current_path = resolve_current_python_interpreter()
        init_dir, _ = os.path.split(current_path)
        new_python = select_file_path(self._project.toolbox(), "Add Python Interpreter...", init_dir, "python")
        if not new_python:
            return
        self._block_signals(True)
        ind = self.models.add_python_interpreter(new_python)
        self._block_signals(False)
        if not ind.isValid():
            self._logger.msg_error.emit(f"Adding Python {new_python} failed")
            ind = self.models.python_interpreters_model.index(0, 0)
        self.ui.comboBox_executable.setCurrentIndex(ind.row())

    def _enable_widgets(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.toolButton_browse_python.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        super()._enable_widgets(use_jupyter_console)


class JuliaOptionsWidget(SharedToolOptionsWidget):
    def __init__(self, models):
        from ..ui.julia_tool_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(Ui_Form, models)
        self._last_sysimage_paths = {}
        self._sysimage_paths = {}
        self._sysimage_workers = {}
        self._work_animation = self._make_work_animation()
        icon_abort = QIcon(CharIconEngine("\uf057", Qt.GlobalColor.red))
        self.ui.toolButton_abort_sysimage.setIcon(icon_abort)
        self.ui.toolButton_new_sysimage.clicked.connect(self._create_sysimage)
        self.ui.toolButton_open_sysimage.clicked.connect(self._open_sysimage)
        self.ui.toolButton_abort_sysimage.clicked.connect(self._abort_sysimage)
        self.ui.toolButton_abort_sysimage.setVisible(False)
        self.ui.lineEdit_sysimage.editingFinished.connect(self._handle_sysimage_editing_finished)
        self.ui.comboBox_executable.setModel(self.models.julia_executables_model)
        self.ui.comboBox_julia_project.setModel(self.models.julia_projects_model)
        self.ui.comboBox_kernel_specs.setModel(self.models.julia_kernel_model)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.radioButton_jupyter_console.toggled.connect(self._update_use_jupyter_console)
        self.ui.toolButton_browse_julia.clicked.connect(self._add_julia_executable)
        self.ui.toolButton_browse_julia_project.clicked.connect(self._add_julia_project)
        self.ui.comboBox_executable.currentIndexChanged.connect(self._update_executable)
        self.ui.comboBox_julia_project.currentIndexChanged.connect(self._update_project)
        self.ui.comboBox_kernel_specs.currentIndexChanged.connect(self._update_julia_kernel)

    @Slot(bool)
    def _update_use_jupyter_console(self, checked):
        self._tool.update_options({"use_jupyter_console": checked})

    @Slot(int)
    def _update_executable(self, _row):
        """Updates Julia executable."""
        self._tool.update_options({"executable": self.get_executable()})

    @Slot(int)
    def _update_project(self, _row):
        """Updates Julia project."""
        self._tool.update_options({"project": self.get_project()})

    @Slot(int)
    def _update_julia_kernel(self, _row):
        self._tool.update_options({"kernel_spec_name": self.get_kernel_name(), "env": self.is_conda()})

    def do_update_options(self, options):
        self.last_sysimage_path = options.get("julia_sysimage")
        self.ui.lineEdit_sysimage.setText(self.last_sysimage_path)
        self._block_signals(True)
        self._enable_widgets(options["use_jupyter_console"])
        (
            self.ui.radioButton_jupyter_console.setChecked(True)
            if options["use_jupyter_console"]
            else self.ui.radioButton_basic_console.setChecked(True)
        )
        ind = self.models.find_julia_kernel_index(options["kernel_spec_name"])
        if not ind.isValid():
            ind = self.models.julia_kernel_model.index(0, 0)
        self.ui.comboBox_kernel_specs.setCurrentIndex(ind.row())
        ind = self.models.find_julia_executable_index(options["executable"])
        self.ui.comboBox_executable.setCurrentIndex(ind.row())
        proj_ind = self.models.find_julia_project_index(options["project"])
        self.ui.comboBox_julia_project.setCurrentIndex(proj_ind.row())
        self._block_signals(False)

    def _block_signals(self, block):
        self.ui.radioButton_jupyter_console.blockSignals(block)
        self.ui.comboBox_executable.blockSignals(block)
        self.ui.comboBox_julia_project.blockSignals(block)
        self.ui.comboBox_kernel_specs.blockSignals(block)

    def get_executable(self):
        """Returns the Julia executable path of the currently selected item in the combobox."""
        current_index = self.models.julia_executables_model.index(self.ui.comboBox_executable.currentIndex(), 0)
        item = self.models.julia_executables_model.itemFromIndex(current_index)
        if not item.data():  # Happens when Julia is not in PATH and the julia_executables_model is empty
            return ""
        return item.data()["exe"]

    def get_project(self):
        """Returns the Julia project path of the currently selected item in the combobox."""
        current_index = self.models.julia_projects_model.index(self.ui.comboBox_julia_project.currentIndex(), 0)
        item = self.models.julia_projects_model.itemFromIndex(current_index)
        return item.data()["path"]

    def get_kernel_name(self):
        """Returns the selected Julia kernel name in the combobox."""
        data = self.get_current_kernel_item_data()
        return data["kernel_name"]

    def is_conda(self):
        data = self.get_current_kernel_item_data()
        return "conda" if data["is_conda"] else ""

    def get_current_kernel_item_data(self):
        current_index = self.models.julia_kernel_model.index(self.ui.comboBox_kernel_specs.currentIndex(), 0)
        item = self.models.julia_kernel_model.itemFromIndex(current_index)
        return item.data()

    @Slot(bool)
    def _add_julia_executable(self, _=False):
        """Calls static method that shows a file browser for selecting a Julia path."""
        current_path = self.ui.comboBox_executable.currentText()
        if not current_path:
            current_path = resolve_default_julia_executable()
        init_dir, _ = os.path.split(current_path)
        fpath = select_file_path(self, "Add Julia Executable...", init_dir, "julia")
        if not fpath:
            return
        self._block_signals(True)
        ind = self.models.add_julia_executable(fpath)
        self._block_signals(False)
        if not ind.isValid():
            self._logger.msg_error.emit(f"Adding Julia executable {fpath} failed")
            ind = self.models.julia_executables_model.index(0, 0)
        self.ui.comboBox_executable.setCurrentIndex(ind.row())

    @Slot(bool)
    def _add_julia_project(self, _=False):
        """Calls static method that shows a folder browser for adding a Julia project."""
        dpath = select_dir(self, "Add Julia project directory...")
        if not dpath:
            return
        self._block_signals(True)
        ind = self.models.add_julia_project(dpath)
        self._block_signals(False)
        if not ind.isValid():
            self._logger.msg_error.emit(f"Adding Julia Project {dpath} failed")
            ind = self.models.julia_projects_model.index(0, 0)
        self.ui.comboBox_julia_project.setCurrentIndex(ind.row())

    def _enable_widgets(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.toolButton_browse_julia.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.toolButton_browse_julia_project.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.comboBox_julia_project.setEnabled(not use_jupyter_console)
        super()._enable_widgets(use_jupyter_console)

    def _make_work_animation(self):
        """
        Returns:
            QVariantAnimation
        """
        animation = QVariantAnimation()
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setDuration(3000)
        animation.setLoopCount(-1)
        animation.valueChanged.connect(self._handle_work_animation_value_changed)
        animation.finished.connect(self._handle_work_animation_finished)
        return animation

    @property
    def sysimage_path(self):
        return self._sysimage_paths.get(self._tool)

    @sysimage_path.setter
    def sysimage_path(self, sysimage_path):
        self._sysimage_paths[self._tool] = sysimage_path

    @property
    def sysimage_worker(self):
        return self._sysimage_workers.get(self._tool)

    @sysimage_worker.setter
    def sysimage_worker(self, sysimage_worker):
        self._sysimage_workers[self._tool] = sysimage_worker

    @property
    def last_sysimage_path(self):
        return self._last_sysimage_paths.get(self._tool)

    @last_sysimage_path.setter
    def last_sysimage_path(self, last_sysimage_path):
        self._last_sysimage_paths[self._tool] = last_sysimage_path

    @property
    def sysimage_basename(self):
        return os.path.basename(self.sysimage_path)

    @Slot()
    def _handle_work_animation_finished(self):
        # pylint: disable=undefined-variable
        self.ui.lineEdit_sysimage.setPalette(QApplication.palette())

    @Slot(object)
    def _handle_work_animation_value_changed(self, step):
        width = self.ui.lineEdit_sysimage.width()
        start = QPointF(-2 * width, 0)
        stop = QPointF(3 * width, 0)
        gradient = QLinearGradient(start, stop)
        # pylint: disable=undefined-variable
        highlight_color = QApplication.palette().highlight().color()
        base_color = QApplication.palette().base().color()
        gradient.setColorAt((step + 0) % 1, base_color)
        gradient.setColorAt((step + 0.2) % 1, base_color)
        gradient.setColorAt((step + 0.5) % 1, highlight_color)
        gradient.setColorAt((step + 0.8) % 1, highlight_color)
        gradient.setColorAt((step + 1) % 1, base_color)
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Base, QBrush(gradient))
        self.ui.lineEdit_sysimage.setPalette(palette)

    def set_tool(self, tool):
        super().set_tool(tool)
        self._update_ui()

    def _update_ui(self):
        if self.sysimage_worker is not None:
            self._set_ui_at_work()
        else:
            self._set_ui_at_rest()

    def _set_ui_at_work(self):
        self._work_animation.start()
        self.ui.toolButton_abort_sysimage.setVisible(True)
        self.ui.toolButton_new_sysimage.setVisible(False)
        self.ui.toolButton_open_sysimage.setVisible(False)
        self.ui.lineEdit_sysimage.setEnabled(False)
        self.ui.lineEdit_sysimage.setText(self.sysimage_path)

    def _set_ui_at_rest(self):
        self._work_animation.stop()
        self.ui.toolButton_abort_sysimage.setVisible(False)
        self.ui.toolButton_new_sysimage.setVisible(True)
        self.ui.toolButton_open_sysimage.setVisible(True)
        self.ui.lineEdit_sysimage.setEnabled(True)
        if self.sysimage_path is None:
            self.ui.lineEdit_sysimage.setText(self.last_sysimage_path)

    @Slot()
    def _handle_sysimage_editing_finished(self):
        sysimage_path = self.ui.lineEdit_sysimage.text()
        self._tool.update_options({"julia_sysimage": sysimage_path})

    @Slot(bool)
    def _open_sysimage(self, _checked=False):
        """Shows a file dialog where the user can select a julia sysimage."""
        ext = "dll" if sys.platform == "win32" else "so"
        sysimage_path, _ = get_open_file_name_in_last_dir(
            self.settings,
            "openJuliaSysimage",
            self,
            "Select Julia Sysimage file",
            self._project.project_dir,
            f"Library (*.{ext})",
        )
        if not sysimage_path:
            return
        self._tool.update_options({"julia_sysimage": sysimage_path})

    @Slot(bool)
    def _abort_sysimage(self, _checked=False):
        if isinstance(self.sysimage_worker, SpineEngineWorker):
            self.sysimage_worker.stop_engine()
        elif isinstance(self.sysimage_worker, QProcessExecutionManager):
            self.sysimage_worker.stop_execution()

    def _get_sysimage_path(self):
        ext = "dll" if sys.platform == "win32" else "so"
        spec_name = self._tool.specification().name
        suggested_file_path = os.path.join(self._project.project_dir, f"{spec_name}_JuliaSysimage.{ext}")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Julia Sysimage file", suggested_file_path, f"Library (*.{ext})"
        )
        if not file_path:
            return None
        return file_path

    @Slot(bool)
    def _create_sysimage(self, _checked=False):
        """Creates a Julia sysimage for the specification associated with this tool.

        Executes a workflow with a modified version of this tool spec, and all its dependencies.
        See ``self._make_sysimage_spec()`` for details about the modified spec.

        The results of the workflow are used by ``self._do_create_sysimage()` to finally create the sysimage.
        """
        if self._tool.specification() is None or self._tool.specification().tooltype.lower() != "julia":
            self._logger.msg_error.emit(
                f"No Julia specification set for Tool <b>{self._tool.name}</b>. Can't create sysimage."
            )
            return
        dag = self._project.dag_with_node(self._tool.name)
        if not dag:
            return
        self.sysimage_path = self._get_sysimage_path()
        if self.sysimage_path is None:
            return
        execution_permits = {item_name: item_name == self._tool.name for item_name in dag.nodes}
        settings = make_settings_dict_for_engine(self.settings)
        settings["appSettings/makeSysImage"] = "true"  # See JuliaToolInstance.prepare()
        dag_identifier = f"containing {self._tool.name}"
        job_id = self._project.LOCAL_EXECUTION_JOB_ID
        self.sysimage_worker = self._project.create_engine_worker(
            dag, execution_permits, dag_identifier, settings, job_id
        )
        # Use the modified spec
        engine_data = self.sysimage_worker.get_engine_data()
        spec_names = {spec["name"] for type_specs in engine_data["specifications"].values() for spec in type_specs}
        spec = self._make_sysimage_spec(spec_names)
        item_dict = engine_data["items"][self._tool.name]
        item_dict["specification"] = spec.name
        options = item_dict.get("options")
        if options:
            options["julia_sysimage"] = ""  # Don't use any previous sysimages
        spec_dict = spec.to_dict()
        spec_dict["definition_file_path"] = spec.definition_file_path
        engine_data["specifications"].setdefault(self._tool.item_type(), []).append(spec_dict)
        self.sysimage_worker.set_engine_data(engine_data)
        self.sysimage_worker.finished.connect(lambda tool=self._tool: self._do_create_sysimage(tool))
        self._update_ui()
        self.sysimage_worker.start(silent=True)
        self._logger.msg_success.emit(
            f"Process to create <b>{self.sysimage_basename}</b> successfully started.\n"
            "This process might take a while, but you can keep using Spine Toolbox as normal in the meantime."
        )

    def _get_precompile_statements_filepath(self):
        return os.path.join(self._tool.data_dir, "precompile_statements_file.jl")

    def _get_loaded_modules_filepath(self):
        return os.path.join(self._tool.data_dir, "loaded_modules.txt")

    def _make_sysimage_spec(self, spec_names):
        """Returns a modified version of this tool specification that collects necessary information
        for creating the sysimage.

        This information is written into two files in the item's data dir:
            - one containing a single line with the Julia modules that are loaded by the tool
            - the other containing precompile statements collected by the option `--trace-compile`

        Returns:
            ToolSpecification
        """
        spec = self._tool.specification().clone()
        original_program_file = os.path.join(spec.path, spec.includes.pop(0))
        loaded_modules_file = self._get_loaded_modules_filepath()
        precompile_statements_file = self._get_precompile_statements_filepath()
        with open(original_program_file, "r") as original:
            original_code = original.read()
        new_code = f"""macro write_loaded_modules(ex)
    return quote
        local before = copy(Base.loaded_modules)
        local val = $(esc(ex))
        local after = copy(Base.loaded_modules)
        open("{escape_backward_slashes(loaded_modules_file)}", "w") do f
            print(f, join(setdiff(values(after), values(before)), " "))
        end
        val
    end
end
@write_loaded_modules begin 
    {original_code}
end"""
        spec.includes.insert(0, "")
        spec.cmdline_args += [f"--trace-compile={precompile_statements_file}", "-e", new_code]
        while True:
            spec.name = str(uuid.uuid4())
            if spec.name not in spec_names:
                break
        return spec

    def _do_create_sysimage(self, tool):
        """Runs when the workflow started by ``self._create_sysimage()`` has completed.

        Launches a julia process that calls ``PackageCompiler.create_sysimage()`` using the info
        collected by the referred workflow.

        Args:
            tool (Tool): The Tool that started the sysimage creation process.
                It may be different from the Tool currently using the widget.
        """
        # Replace self._tool while we run this method
        current_tool = self._tool
        self._tool = tool
        self.sysimage_worker.clean_up()
        state = self.sysimage_worker.engine_final_state()
        if state != "COMPLETED":
            user_stopped = state == "USER_STOPPED"
            errors = "\n".join(self.sysimage_worker.process_messages.get("msg_error", []))
            msg = self._make_failure_message(user_stopped, errors)
            self._logger.msg_error.emit(msg)
            self.sysimage_worker = None
            self.sysimage_path = None
            if tool is current_tool:
                self._update_ui()
            return
        loaded_modules_file = self._get_loaded_modules_filepath()
        precompile_statements_file = self._get_precompile_statements_filepath()
        _string_in_brackets = "{String}"
        with open(loaded_modules_file, "r") as f:
            modules = f.read()
        code = f"""using Pkg;
project_dir = dirname(Base.active_project());
cp(joinpath(project_dir, "Project.toml"), joinpath(project_dir, "Project.backup"); force=true);
cp(joinpath(project_dir, "Manifest.toml"), joinpath(project_dir, "Manifest.backup"); force=true);
packages = Vector{_string_in_brackets}()
try
    modules = split("{modules}", " ");
    for m in modules
        if strip(m) == ""
            continue
        end
        if any(x -> x.name == m && x.is_direct_dep, values(Pkg.dependencies())) == true
            println("Package " * m * " already installed")
        else
            try
                Pkg.add(m)
            catch e
                if isa(e, Pkg.Types.PkgError)
                    println(m * " is not a package")
                    continue
                end
            end
        end
        println("Package " * m * " installed")
        push!(packages, m)
    end
    println("Packages to add to sysimage: " * string(packages))
    Pkg.add("PackageCompiler");
    @eval import PackageCompiler
    Base.invokelatest(
        PackageCompiler.create_sysimage,
        Symbol.(packages);
        sysimage_path="{escape_backward_slashes(self.sysimage_path)}",
        project=project_dir,
        precompile_statements_file="{escape_backward_slashes(precompile_statements_file)}"
    )
finally
    cp(joinpath(project_dir, "Project.backup"), joinpath(project_dir, "Project.toml"); force=true);
    cp(joinpath(project_dir, "Manifest.backup"), joinpath(project_dir, "Manifest.toml"); force=true);
end"""
        julia, *args = get_julia_path_and_project(current_tool.specification().execution_settings, self.settings)
        args += ["-e", code]
        self.sysimage_worker = QProcessExecutionManager(self._logger, julia, args, silent=False)
        self.sysimage_worker.execution_finished.connect(lambda ret: self._handle_sysimage_process_finished(ret, tool))
        self.sysimage_worker.start_execution(workdir=self._tool.specification().path)
        # Restore the current self._tool
        self._tool = current_tool

    def _handle_sysimage_process_finished(self, ret, tool):
        """Runs when the Julia process started by ``self._do_create_sysimage()`` finishes.
        Wraps up everything.

        Args:
            ret (int): The return code of the process, 0 indicates success.
            tool (Tool): The Tool that started the sysimage creation process.
                It may be different from the Tool currently using the widget.
        """
        # Replace self._tool while we run this method
        self._tool, current_tool = tool, self._tool
        user_stopped = self.sysimage_worker.user_stopped
        error = self.sysimage_worker.process_error
        self.sysimage_worker.deleteLater()
        self.sysimage_worker = None
        if ret != 0:
            msg = self._make_failure_message(user_stopped, error)
            self._logger.msg_error.emit(msg)
            self.sysimage_path = None
        else:
            self._tool.update_options({"julia_sysimage": self.sysimage_path})
            self._logger.msg_success.emit(f"<b>{self.sysimage_basename}</b> created successfully.\n")
        if tool is current_tool:
            self._update_ui()
        # Restore the current self._tool
        self._tool = current_tool

    def _make_failure_message(self, user_stopped, errors):
        msg = f"Process to create <b>{self.sysimage_basename}</b> "
        if user_stopped:
            msg += "stopped by the user"
        else:
            msg += "failed"
            if errors:
                msg += f" with the following error(s):\n{errors}"
        return msg


class ExecutableOptionsWidget(OptionsWidget):
    def __init__(self, models):
        from ..ui.executable_tool_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(Ui_Form, models)
        self.shells = ["No shell", "cmd.exe", "powershell.exe", "bash"]
        self.ui.comboBox_shell.addItems(self.shells)
        # Disable shell selections that are not compatible with the os running toolbox
        msg = f"<p>Selection not available for platform {sys.platform}</p>"
        if sys.platform == "win32":
            # No bash for windows
            self.ui.comboBox_shell.model().item(3).setEnabled(False)
            self.ui.comboBox_shell.model().item(3).setToolTip(msg)
        else:
            # For other systems no cmd or powershell
            self.ui.comboBox_shell.model().item(1).setEnabled(False)
            self.ui.comboBox_shell.model().item(1).setToolTip(msg)
            self.ui.comboBox_shell.model().item(2).setEnabled(False)
            self.ui.comboBox_shell.model().item(2).setToolTip(msg)
        self.connect_signals()

    def connect_signals(self):
        self.ui.lineEdit_command.textEdited.connect(self._update_command)
        # self.ui.lineEdit_command.editingFinished.connect(self._specification_editor._finish_updating_command)
        self.ui.comboBox_shell.activated.connect(self._update_shell)

    def do_update_options(self, options):
        print(f"[{self._tool.name}] restoring options:{options}")
        self._block_signals(True)
        self.ui.lineEdit_command.setText(options["cmd"])
        shell = options["shell"]
        ind = next(iter(k for k, t in enumerate(self.shells) if t.lower() == shell), 0)
        self.ui.comboBox_shell.setCurrentIndex(ind)
        self._block_signals(False)

    def _block_signals(self, block):
        self.ui.lineEdit_command.blockSignals(block)
        self.ui.comboBox_shell.blockSignals(block)

    def get_shell(self):
        """Returns the selected shell in the shell combo box."""
        ind = self.ui.comboBox_shell.currentIndex()
        if ind < 1:
            return ""
        return self.ui.comboBox_shell.currentText()

    @Slot(str)
    def _update_command(self, cmd):
        """Updates command."""
        self._tool.update_options({"cmd": cmd})

    # @Slot()
    # def _finish_updating_command(self):
    #     """Seals latest undo stack command."""
    #     self._undo_stack.push(SealCommand(CommandId.COMMAND_UPDATE.value))

    @Slot(int)
    def _update_shell(self, _row):
        """Updates shell."""
        self._tool.update_options({"shell": self.get_shell()})

    def set_command_and_shell_edit_disabled_state(self, enabled):
        """Sets the enabled state for the Command line edit and the Shell combobox.
        # TODO: Use this when tool spec does have or does not have a main file. (In do_update_options())
        """
        self.ui.comboBox_shell.setDisabled(enabled)
        self.ui.lineEdit_command.setDisabled(enabled)
