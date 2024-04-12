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
from PySide6.QtCore import Qt, Slot, QVariantAnimation, QPointF
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtGui import QIcon, QLinearGradient, QPalette, QBrush
from spine_items.utils import escape_backward_slashes
from spine_items.tool.utils import get_julia_path_and_project
from spinetoolbox.spine_engine_worker import SpineEngineWorker
from spinetoolbox.execution_managers import QProcessExecutionManager
from spinetoolbox.helpers import get_open_file_name_in_last_dir, CharIconEngine, make_settings_dict_for_engine


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


class JuliaOptionsWidget(OptionsWidget):
    def __init__(self):
        from ..ui.julia_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._last_sysimage_paths = {}
        self._sysimage_paths = {}
        self._sysimage_workers = {}
        self._work_animation = self._make_work_animation()
        icon_abort = QIcon(CharIconEngine("\uf057", Qt.red))
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
        settings = make_settings_dict_for_engine(self._settings, self._project.settings)
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
        engine_data["specifications"].setdefault(self._tool.item_type(), list()).append(spec_dict)
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
