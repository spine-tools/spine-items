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
Provides OptionsWidget and subclasses for each tool type (julia, python, executable, gams).

:author: M. Marin (KTH)
:date:   12.2.2021
"""
import os
import sys
import uuid
from spine_engine.utils.helpers import get_julia_command
from PySide2.QtCore import Qt, Slot, QVariantAnimation, QPointF
from PySide2.QtWidgets import QWidget, QFileDialog
from PySide2.QtGui import QIcon, QLinearGradient, QPalette, QBrush
from spinetoolbox.spine_engine_worker import SpineEngineWorker
from spinetoolbox.execution_managers import QProcessExecutionManager
from spinetoolbox.helpers import get_open_file_name_in_last_dir, CharIconEngine


class OptionsWidget(QWidget):
    def __init__(self, tool, project, settings, logger):
        super().__init__()
        self._tool = tool
        self._project = project
        self._settings = settings
        self._logger = logger


class JuliaOptionsWidget(OptionsWidget):
    def __init__(self, tool, project, settings, logger):
        """Init class.

        Args:
            tool (Tool)
            project (SpineToolboxProject)
            settings (QSettings)
            logger (LoggerInterface)
        """
        from ..ui.julia_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(tool, project, settings, logger)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._last_sysimage_path = None
        self._sysimage_path = None
        self._sysimage_worker = None
        self._icon_new = QIcon(CharIconEngine("\uf15b"))
        self._icon_stop = QIcon(CharIconEngine("\uf04d", Qt.red))
        self._tool_tip_new = "<html>Create Julia Sysimage for this Tool</html>"
        self._tool_tip_stop = "<html>Stop Sysimage creation process</html>"
        self._work_animation = self._make_work_animation()
        self.ui.toolButton_new_sysimage.setIcon(self._icon_new)
        self.ui.toolButton_new_sysimage.setToolTip(self._tool_tip_new)
        self.ui.toolButton_new_sysimage.clicked.connect(self._create_or_stop_sysimage)
        self.ui.toolButton_open_sysimage.clicked.connect(self._open_sysimage)
        self.ui.lineEdit_sysimage.editingFinished.connect(self._handle_le_sysimage_editing_finished)

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

    def _begin_create_sysimage(self):
        self._work_animation.start()
        self.ui.toolButton_new_sysimage.setIcon(self._icon_stop)
        self.ui.toolButton_new_sysimage.setToolTip(self._tool_tip_stop)
        self.ui.toolButton_open_sysimage.setEnabled(False)
        self.ui.lineEdit_sysimage.setEnabled(False)
        self.ui.lineEdit_sysimage.setPlaceholderText(self._sysimage_path)
        self.ui.lineEdit_sysimage.setText(None)

    def _end_create_sysimage(self):
        self._work_animation.stop()
        self.ui.toolButton_new_sysimage.setIcon(self._icon_new)
        self.ui.toolButton_new_sysimage.setToolTip(self._tool_tip_new)
        self.ui.toolButton_open_sysimage.setEnabled(True)
        self.ui.lineEdit_sysimage.setEnabled(True)
        self.ui.lineEdit_sysimage.setPlaceholderText(None)
        if self._sysimage_path != self._last_sysimage_path:
            self._tool.update_options({"julia_sysimage": self._sysimage_path})
        else:
            self.ui.lineEdit_sysimage.setText(self._last_sysimage_path)

    def do_update_options(self, options):
        self._last_sysimage_path = options.get("julia_sysimage")
        self.ui.lineEdit_sysimage.setText(self._last_sysimage_path)

    @property
    def _sysimage_basename(self):
        return os.path.basename(self._sysimage_path)

    @Slot()
    def _handle_le_sysimage_editing_finished(self):
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
    def _create_or_stop_sysimage(self, _checked=False):
        """Creates or stops the process that creates the julia sysimage."""
        if self._sysimage_worker is not None:
            self._stop_sysimage()
        else:
            self._create_sysimage()

    def _stop_sysimage(self):
        if isinstance(self._sysimage_worker, SpineEngineWorker):
            self._sysimage_worker.stop_engine()
        elif isinstance(self._sysimage_worker, QProcessExecutionManager):
            self._sysimage_worker.stop_execution()

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

    def _create_sysimage(self):
        """Creates a Julia system image for the specification associated with this tool.
        The process consists of two steps:
            (i) executing the Tool to collect necessary arguments for ``PackageCompiler.create_sysimage()``, and
            (ii) running a process that calls that function.
        """
        if self._tool.specification() is None or self._tool.specification().tooltype.lower() != "julia":
            self._logger.msg_error.emit(
                f"No Julia specification set for Tool <b>{self._tool.name}</b>. Can't create sysimage."
            )
            return
        dag = self._project.dag_with_node(self._tool.name)
        if not dag:
            return
        dag_identifier = f"containing {self._tool.name}"
        node_successors = self._project.get_node_successors(dag, dag_identifier)
        if node_successors is None:
            return
        self._sysimage_path = self._get_sysimage_path()
        if self._sysimage_path is None:
            return
        execution_permits = {item_name: item_name == self._tool.name for item_name in dag.nodes}
        settings = self._project.make_settings_dict()
        settings["appSettings/useEmbeddedJulia"] = "1"  # Don't use repl
        self._sysimage_worker = self._project.create_engine_worker(dag, execution_permits, dag_identifier, settings)
        # Use the modified spec
        engine_data = self._sysimage_worker.get_engine_data()
        spec_names = {spec["name"] for type_specs in engine_data["specifications"].values() for spec in type_specs}
        spec = self._make_sysimage_spec(spec_names)
        item_dict = engine_data["items"][self._tool.name]
        item_dict["specification"] = spec.name
        options = item_dict.get("options")
        if options:
            options["julia_sysimage"] = ""  # Don't use any previous sysimages
        engine_data["specifications"].setdefault(self._tool.item_type(), list()).append(spec.to_dict())
        self._sysimage_worker.set_engine_data(engine_data)
        self._sysimage_worker.finished.connect(self._do_create_sysimage)
        self._begin_create_sysimage()
        self._sysimage_worker.start(silent=True)
        self._logger.msg_success.emit(
            f"Process to create <b>{self._sysimage_basename}</b> sucessfully started.\n"
            "The process might take a long time, but you can keep using Spine Toolbox as normal while it runs."
            "You will see a notification here whenever it's done."
        )

    def _make_sysimage_spec(self, spec_names):
        """Returns a tool specification that collects information about the *actual* tool spec.
        This spec writes two files to the item's data dir:
            - one containing a single line with the Julia modules that are loaded by the tool
            - the other containing precompile statements collected by the option `--trace-compile`

        Returns:
            ToolSpecification
        """
        spec = self._tool.specification().clone()
        original_program_file = os.path.join(spec.path, spec.includes.pop(0))
        loaded_modules_file = self._get_loaded_modules_filepath()
        precompile_statements_file = self._get_precompile_statements_filepath()
        with open(original_program_file, 'r') as original:
            original_code = original.read()
        new_code = f"""
        macro loaded_modules(ex)
            return quote
                local before = copy(Base.loaded_modules)
                local val = $(esc(ex))
                local after = copy(Base.loaded_modules)
                open("{loaded_modules_file}", "w") do f
                    print(f, join(setdiff(values(after), values(before)), " "))
                end
                val
            end
        end
        @loaded_modules begin {original_code} end
        """
        spec.includes.insert(0, "")
        spec.cmdline_args += [f"--trace-compile={precompile_statements_file}", "-e", new_code]
        while True:
            spec.name = str(uuid.uuid4)
            if spec.name not in spec_names:
                break
        return spec

    @Slot()
    def _do_create_sysimage(self):
        self._sysimage_worker.clean_up()
        state = self._sysimage_worker.engine_final_state()
        if state != "COMPLETED":
            user_stopped = state == "USER_STOPPED"
            errors = "\n".join(self._sysimage_worker.process_messages.get("msg_error", []))
            msg = self._make_failure_message(user_stopped, errors)
            self._logger.msg_error.emit(msg)
            self._sysimage_worker = None
            self._sysimage_path = self._last_sysimage_path
            self._end_create_sysimage()
            return
        julia_command = get_julia_command(self._settings)
        loaded_modules_file = self._get_loaded_modules_filepath()
        precompile_statements_file = self._get_precompile_statements_filepath()
        with open(loaded_modules_file, 'r') as f:
            modules = f.read()
        code = f"""
            using Pkg;
            pkg"add PackageCompiler {modules}";
            using PackageCompiler;
            PackageCompiler.create_sysimage(
                Symbol.(split("{modules}", " "));
                sysimage_path="{self._sysimage_path}",
                precompile_statements_file="{precompile_statements_file}"
            )
        """
        julia, *args = julia_command
        args += ["-e", code]
        self._sysimage_worker = QProcessExecutionManager(self._logger, julia, args, silent=True)
        self._sysimage_worker.execution_finished.connect(self._handle_sysimage_process_finished)
        self._sysimage_worker.start_execution()

    @Slot(int)
    def _handle_sysimage_process_finished(self, ret):
        user_stopped = self._sysimage_worker.user_stopped
        error = self._sysimage_worker.error_output
        self._sysimage_worker.deleteLater()
        self._sysimage_worker = None
        if ret != 0:
            msg = self._make_failure_message(user_stopped, error)
            self._logger.msg_error.emit(msg)
            self._sysimage_path = self._last_sysimage_path
        else:
            self._logger.msg_success.emit(f"<b>{self._sysimage_basename}</b> created successfully.\n")
        self._end_create_sysimage()

    def _make_failure_message(self, user_stopped, errors):
        msg = f"Process to create <b>{self._sysimage_basename}</b> "
        if user_stopped:
            msg += "stopped by the user"
        else:
            msg += "failed"
            if errors:
                msg += f" with the following error(s):\n{errors}"
        return msg

    def _get_precompile_statements_filepath(self):
        return os.path.join(self._tool.data_dir, "precompile_statements_file.jl")

    def _get_loaded_modules_filepath(self):
        return os.path.join(self._tool.data_dir, "loaded_modules.txt")
