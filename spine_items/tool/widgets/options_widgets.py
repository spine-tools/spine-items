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

"""Provides OptionsWidget and subclasses for each tool type (julia, python, executable, gams)."""
import os
import sys
import uuid
from PySide6.QtCore import QPointF, Qt, QVariantAnimation, Slot
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPalette, QStandardItemModel
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
    get_current_item_data,
)
from spinetoolbox.spine_engine_worker import SpineEngineWorker
from spine_engine.utils.helpers import resolve_current_python_interpreter


class OptionsWidget(QWidget):
    def __init__(self):
        super().__init__()
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
    def _settings(self):
        return self._project.app_settings

    @property
    def _logger(self):
        return self._tool.logger

    @property
    def _models(self):
        return self._project.toolbox().exec_compound_models


class SharedToolSpecOptionalWidget(OptionsWidget):
    """Superclass for Python and Julia Tool Spec optional widgets."""

    def __init__(self, Ui_Form, fetch_mode):
        """
        Args:
            Ui_Form (Form): Optional widget UI form
            fetch_mode (int): Kernel fetch mode (see KernelFetcher class)
        """
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # self.fetch_mode = fetch_mode
        # self.kernel_spec_model = QStandardItemModel(self)
        # self.ui.comboBox_kernel_specs.setModel(self.kernel_spec_model)
        # self._kernel_spec_editor = None
        # self._kernel_spec_model_initialized = False
        # self._saved_kernel = None
        # self._selected_kernel = None
        # self.kernel_fetcher = None

    def connect_signals(self):
        """Connects signals."""
        # self.ui.toolButton_refresh_kernel_specs.clicked.connect(self.start_kernel_fetcher)
        # self.ui.comboBox_kernel_specs.activated.connect(self._specification_editor.push_change_kernel_spec_command)
        # self.ui.radioButton_jupyter_console.toggled.connect(self._specification_editor.push_set_jupyter_console_mode)
        # self.ui.lineEdit_executable.textEdited.connect(self._specification_editor.push_change_executable)
        # self.ui.lineEdit_executable.editingFinished.connect(self._specification_editor.finish_changing_executable)
        # QApplication.aboutToQuit.connect(self.stop_fetching_kernels)  # pylint: disable=undefined-variable

    def init_widget(self, specification):
        """Initializes UI elements based on specification

        Args:
            specification (ToolSpecification): Specification to load
        """
        use_jupyter_console = specification.execution_settings["use_jupyter_console"]
        self.ui.radioButton_jupyter_console.blockSignals(True)
        self.ui.radioButton_basic_console.blockSignals(True)
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
        else:
            self.ui.radioButton_basic_console.setChecked(True)
        self.ui.radioButton_jupyter_console.blockSignals(False)
        self.ui.radioButton_basic_console.blockSignals(False)
        self._saved_kernel = specification.execution_settings["kernel_spec_name"]
        self.set_executable(specification.execution_settings["executable"])
        self.set_ui_for_jupyter_console(use_jupyter_console)

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.comboBox_executable.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.comboBox_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        self.ui.toolButton_refresh_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        # if use_jupyter_console and not self._kernel_spec_model_initialized:
        #     self.start_kernel_fetcher(restore_saved_kernel=True)

    def add_execution_settings(self, tool_spec_type):
        """See base class."""
        idx = self.ui.comboBox_kernel_specs.currentIndex()
        if idx < 1:
            d = {"kernel_spec_name": "", "env": ""}
        else:
            item = self.ui.comboBox_kernel_specs.model().item(idx)
            k_spec_data = item.data()
            d = k_spec_data
        d["use_jupyter_console"] = self.ui.radioButton_jupyter_console.isChecked()
        p = self.get_executable()
        self.validate_executable(p, tool_spec_type)  # Raises NameError if Python or Julia path is not valid
        d["executable"] = p
        return d

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

    def set_executable(self, p):
        """Sets given path p to either Python or Julia line edit."""
        if p == self.get_executable():
            return
        self.ui.lineEdit_executable.setText(p)

    def get_executable(self):
        """Returns either Python or Julia executable path."""
        return self.ui.lineEdit_executable.text().strip()

    def find_index_by_data(self, string):
        """Searches the kernel spec model for the first item whose data matches the given string.
        Returns the items row number or -1 if not found."""
        if string == "":
            return 0
        for row in range(1, self.kernel_spec_model.rowCount()):  # Start from index 1
            index = self.kernel_spec_model.index(row, 0)
            item = self.kernel_spec_model.itemFromIndex(index)
            d = item.data()
            if d["kernel_spec_name"] == string:
                return row
        return -1


class PythonToolSpecOptionalWidget(SharedToolSpecOptionalWidget):
    def __init__(self):
        from ..ui.python_tool_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(Ui_Form, 2)
        # Initialize UI elements with defaults
        self.ui.radioButton_basic_console.setChecked(True)
        # default_python_path = resolve_current_python_interpreter()
        self.set_ui_for_jupyter_console(False)
        self._saved_python_kernel = None
        self.connect_signals()

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.radioButton_jupyter_console.toggled.connect(self.set_ui_for_jupyter_console)
        self.ui.toolButton_browse_python.clicked.connect(self._add_python_interpreter)

    def do_update_options(self, options):
        print(f"Restoring options:{options}")
        self.ui.comboBox_executable.setModel(self._models.python_interpreters_model)
        self._models.refresh_python_interpreters_model()
        self.ui.comboBox_kernel_specs.setModel(self._models.python_kernel_model)
        use_jupyter_console, python_exe, python_kernel = self._get_python_settings()
        self._saved_python_kernel = python_kernel
        self._models.start_fetching_python_kernels(self._set_saved_python_kernel_selected)

    def _get_python_settings(self):
        """Returns current Python settings in the Python optional widget."""
        use_python_jupyter_console = "2" if self.ui.radioButton_jupyter_console.isChecked() else "0"
        data = get_current_item_data(self.ui.comboBox_executable, self._models.python_interpreters_model)
        python_exe = data["exe"]
        python_kernel = ""
        if self.ui.comboBox_kernel_specs.currentIndex() != 0:
            kernel_data = get_current_item_data(self.ui.comboBox_kernel_specs, self._models.python_kernel_model)
            try:
                python_kernel = kernel_data["kernel_name"]
            except KeyError:  # Happens when conda kernel is selected and user clears the conda line edit path
                python_kernel = ""
            except TypeError:  # Happens when kernel_data is None
                python_kernel = ""
        return use_python_jupyter_console, python_exe, python_kernel

    @Slot()
    def _set_saved_python_kernel_selected(self):
        """Sets saved python as selected after Pythons have been (re)loaded."""
        ind = self._models.find_python_kernel_index(self._saved_python_kernel, self)
        self.ui.comboBox_kernel_specs.setCurrentIndex(ind.row())
        self._saved_python_kernel = None

    def default_execution_settings(self):
        """See base class."""
        print("default_execution_settings() called")
        return
        use_jupyter_cons = bool(int(self._settings.value("appSettings/usePythonKernel", defaultValue="0")))
        k_name = self._settings.value("appSettings/pythonKernel", defaultValue="")
        env = ""
        if use_jupyter_cons:
            # Check if the kernel is a Conda kernel by matching the name with the one that is in kernel_spec_model
            # Find k_name in kernel_spec_model and check it's data
            row = self.find_index_by_data(k_name)
            if row == -1:
                pass  # kernel not found
            else:
                index = self.kernel_spec_model.index(row, 0)
                item_data = self.kernel_spec_model.itemFromIndex(index).data()
                env = item_data["env"]
        d = dict()
        d["kernel_spec_name"] = k_name
        d["env"] = env
        d["use_jupyter_console"] = use_jupyter_cons
        d["executable"] = self._settings.value("appSettings/pythonPath", defaultValue="")
        return d

    @Slot(bool)
    def _add_python_interpreter(self, _=False):
        """Calls static method that shows a file browser for selecting a Python interpreter."""
        current_path = self.ui.comboBox_executable.currentText()
        if not current_path:
            current_path = resolve_current_python_interpreter()
        init_dir, _ = os.path.split(current_path)
        new_python = select_file_path(self._project.toolbox(), "Select Python Interpreter", init_dir, "python")
        if not new_python:
            return
        ind = self._models.add_python_interpreter(new_python, self._project.toolbox())
        self.ui.comboBox_executable.setCurrentIndex(ind.row())

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.toolButton_browse_python.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        super().set_ui_for_jupyter_console(use_jupyter_console)

    def get_widgets_in_tab_order(self):
        """See base class."""
        return (
            self.ui.radioButton_basic_console,
            self.ui.comboBox_executable,
            self.ui.toolButton_browse_python,
            self.ui.radioButton_jupyter_console,
            self.ui.comboBox_kernel_specs,
            self.ui.toolButton_refresh_kernel_specs,
        )


class JuliaOptionsWidget(OptionsWidget):
    def __init__(self):
        from ..ui.julia_tool_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
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
        self.ui.lineEdit_sysimage.setPalette(qApp.palette())

    @Slot(object)
    def _handle_work_animation_value_changed(self, step):
        width = self.ui.lineEdit_sysimage.width()
        start = QPointF(-2 * width, 0)
        stop = QPointF(3 * width, 0)
        gradient = QLinearGradient(start, stop)
        # pylint: disable=undefined-variable
        highlight_color = qApp.palette().highlight().color()
        base_color = qApp.palette().base().color()
        gradient.setColorAt((step + 0) % 1, base_color)
        gradient.setColorAt((step + 0.2) % 1, base_color)
        gradient.setColorAt((step + 0.5) % 1, highlight_color)
        gradient.setColorAt((step + 0.8) % 1, highlight_color)
        gradient.setColorAt((step + 1) % 1, base_color)
        palette = QPalette()
        palette.setBrush(QPalette.Base, QBrush(gradient))
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

    def do_update_options(self, options):
        self.last_sysimage_path = options.get("julia_sysimage")
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
            self._settings,
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
        settings = make_settings_dict_for_engine(self._settings)
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
        julia, *args = get_julia_path_and_project(current_tool.specification().execution_settings, self._settings)
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
